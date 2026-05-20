"""
LangChain RAG API服务
基于FastAPI，支持RESTful接口
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# 本地模块
from workflow_langchain import RAGWorkflow
from config import Config

# ============== 数据模型 ==============
class QueryRequest(BaseModel):
    """查询请求模型"""
    question: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    session_id: Optional[str] = Field(None, description="会话ID（可选）")
    user_id: Optional[str] = Field(None, description="用户ID（可选）")

class QueryResponse(BaseModel):
    """查询响应模型"""
    answer: str = Field(..., description="回答内容")
    sources: List[str] = Field(default_factory=list, description="来源文档")
    success: bool = Field(True, description="是否成功")
    processing_time: Optional[float] = Field(None, description="处理时间（秒）")
    token_usage: Optional[Dict[str, Any]] = Field(None, description="Token使用情况")

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    service: str = Field(..., description="服务名称")
    version: str = Field(..., description="版本号")
    timestamp: float = Field(..., description="时间戳")

class StatsResponse(BaseModel):
    """统计信息响应"""
    status: str = Field(..., description="状态")
    document_count: Optional[int] = Field(None, description="文档数量")
    llm_model: Optional[str] = Field(None, description="LLM模型")
    embedding_model: Optional[str] = Field(None, description="嵌入模型")

# ============== 缓存实现 ==============
class SimpleCache:
    """简单内存缓存"""
    
    def __init__(self, ttl_seconds: int = 300):
        """
        初始化缓存
        
        Args:
            ttl_seconds: 缓存生存时间（秒）
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry['timestamp'] < self.ttl:
                    return entry['value']
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: str):
        """设置缓存值"""
        with self.lock:
            self.cache[key] = {
                'value': value,
                'timestamp': time.time()
            }
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        with self.lock:
            return len(self.cache)

# ============== 应用初始化 ==============
app = FastAPI(
    title="LangChain RAG API",
    description="基于LangChain的RAG问答系统API",
    version="1.0.0"
)

# 配置CORS（允许跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
workflow = None
cache = None
executor = None

# ============== 启动/关闭事件 ==============
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global workflow, cache, executor
    
    print("🚀 启动RAG API服务...")
    
    # 初始化工作流
    workflow = RAGWorkflow()
    
    # 初始化缓存
    cache = SimpleCache(ttl_seconds=Config.CACHE_TTL)
    
    # 初始化线程池
    executor = ThreadPoolExecutor(max_workers=Config.MAX_WORKERS)
    
    print(f"✅ 服务初始化完成，缓存TTL: {Config.CACHE_TTL}秒")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    global executor
    
    print("🛑 关闭RAG API服务...")
    
    if executor:
        executor.shutdown(wait=True)
    
    print("✅ 清理完成")

# ============== API接口 ==============
@app.get("/", response_class=JSONResponse)
async def root():
    """根路径"""
    return {
        "message": "LangChain RAG API Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        service="rag-api",
        version="1.0.0",
        timestamp=time.time()
    )

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """获取系统统计信息"""
    if not workflow:
        raise HTTPException(status_code=503, detail="服务未就绪")
    
    stats = workflow.get_stats()
    return StatsResponse(**stats)

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    查询RAG系统
    
    Args:
        request: 包含问题和可选的会话ID、用户ID
    
    Returns:
        包含回答、来源文档、处理时间等信息
    """
    start_time = time.time()
    
    # 检查工作流是否就绪
    if not workflow:
        raise HTTPException(status_code=503, detail="RAG服务未就绪")
    
    # 检查缓存
    cache_key = f"query:{request.question}"
    cached_answer = cache.get(cache_key)
    
    if cached_answer:
        print(f"🎯 缓存命中: {request.question[:30]}...")
        processing_time = time.time() - start_time
        return QueryResponse(
            answer=cached_answer,
            sources=[],
            success=True,
            processing_time=processing_time,
            token_usage={"cached": True}
        )
    
    # 执行查询（在新线程中运行）
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            executor,
            lambda: workflow.query(request.question)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    
    processing_time = time.time() - start_time
    
    # 如果成功，将结果加入缓存
    if result["success"]:
        cache.set(cache_key, result["answer"])
    
    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        success=result["success"],
        processing_time=processing_time,
        token_usage=result.get("token_usage")
    )

@app.post("/batch_query")
async def batch_query(questions: List[str]):
    """
    批量查询（异步非阻塞）
    
    Args:
        questions: 问题列表
    
    Returns:
        批量查询结果
    """
    if not workflow:
        raise HTTPException(status_code=503, detail="RAG服务未就绪")
    
    if len(questions) > 10:
        raise HTTPException(status_code=400, detail="批量查询最多支持10个问题")
    
    loop = asyncio.get_event_loop()
    
    async def run_query(question: str) -> dict:
        try:
            result = await loop.run_in_executor(
                executor,
                lambda: workflow.query(question)
            )
            return {
                "question": question,
                "answer": result["answer"],
                "success": result["success"]
            }
        except Exception as e:
            return {
                "question": question,
                "answer": f"查询失败：{str(e)}",
                "success": False
            }
    
    results = await asyncio.gather(*[run_query(q) for q in questions])
    
    return {"results": results}

@app.post("/cache/clear")
async def clear_cache():
    """清空缓存"""
    if cache:
        cache.clear()
        return {"message": "缓存已清空", "status": "success"}
    return {"message": "缓存未初始化", "status": "error"}

@app.get("/cache/stats")
async def cache_stats():
    """获取缓存统计"""
    if cache:
        return {
            "size": cache.size(),
            "ttl": cache.ttl,
            "status": "active"
        }
    return {"status": "inactive"}

@app.post("/reload")
async def reload_workflow():
    """重新加载工作流"""
    global workflow
    
    try:
        workflow = RAGWorkflow()
        return {"message": "工作流重新加载成功", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新加载失败: {str(e)}")

# ============== 错误处理 ==============
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理（生产环境不暴露详情）"""
    detail = str(exc) if Config.DEBUG_MODE else "服务器内部错误，请稍后重试"
    return JSONResponse(
        status_code=500,
        content={
            "error": detail,
            "type": type(exc).__name__ if Config.DEBUG_MODE else "InternalError"
        }
    )

# ============== 命令行启动 ==============
def main():
    """命令行启动"""
    print("="*50)
    print("LangChain RAG API Service")
    print("="*50)
    
    # 打印配置
    Config.print_config()
    
    print(f"\n🌐 启动服务: http://{Config.API_HOST}:{Config.API_PORT}")
    print(f"📚 API文档: http://{Config.API_HOST}:{Config.API_PORT}/docs")
    print(f"❤️ 健康检查: http://{Config.API_HOST}:{Config.API_PORT}/health")
    print("="*50)
    
    # 启动uvicorn服务器
    uvicorn.run(
        "api:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.DEBUG_MODE,
        workers=1 if Config.DEBUG_MODE else 2
    )

if __name__ == "__main__":
    main()