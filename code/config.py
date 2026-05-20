"""
RAG系统配置管理
基于LangChain + SiliconFlow API
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """系统配置类"""
    
    # ============== API配置 ==============
    # SiliconFlow API配置
    SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
    SILICONFLOW_API_BASE = "https://api.siliconflow.cn/v1"
    
    # 钉钉配置（可选）
    DINGTALK_APP_KEY = os.getenv("DINGTALK_APP_KEY", "")
    DINGTALK_APP_SECRET = os.getenv("DINGTALK_APP_SECRET", "")
    
    # ============== 模型配置 ==============
    # LLM配置（推荐GLM-4-9B-0414，4秒响应）
    LLM_MODEL = os.getenv("LLM_MODEL", "THUDM/GLM-4-9B-0414")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "200"))
    
    # Embedding配置
    EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-large-zh-v1.5")
    # 嵌入方式：api（通过 SiliconFlow API）或 local（使用 HuggingFace 本地模型）
    # ⚠️ 如果使用 api 方式，确保该模型在 SiliconFlow 上可用：
    #    curl https://api.siliconflow.cn/v1/models -H "Authorization: Bearer $API_KEY"
    #    常见可用：BAAI/bge-large-zh-v1.5, BAAI/bge-m3
    # ⚠️ 如果使用 local 方式，需安装 sentence-transformers
    EMBED_MODE = os.getenv("EMBED_MODE", "api").lower()
    
    # Rerank配置（可选）
    RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
    USE_RERANK = os.getenv("USE_RERANK", "False").lower() == "true"
    
    # ============== 向量库配置 ==============
    # ChromaDB配置
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "langchain_collection")
    
    # 文档分割配置
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # 检索配置
    RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "3"))  # 返回最相似的3个文档
    
    # ============== 性能配置 ==============
    # 线程池配置（4核8GB服务器推荐）
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "2"))
    
    # 缓存配置
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5分钟缓存
    
    # 超时配置
    QUERY_TIMEOUT = int(os.getenv("QUERY_TIMEOUT", "60"))  # 60秒超时
    
    # ============== 服务配置 ==============
    # API服务配置
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # ============== 路径配置 ==============
    # 知识库文档路径
    DATA_DIR = os.getenv("DATA_DIR", "./data")
    
    # 日志路径
    LOG_DIR = os.getenv("LOG_DIR", "./logs")
    
    @classmethod
    def validate(cls):
        """验证必要配置"""
        if cls.EMBED_MODE == "api" and not cls.SILICONFLOW_API_KEY:
            raise ValueError("API 模式需要配置 SILICONFLOW_API_KEY 环境变量")
        
        if cls.EMBED_MODE not in ("api", "local"):
            raise ValueError(f"EMBED_MODE 必须是 'api' 或 'local'，当前值: {cls.EMBED_MODE}")
        
        # 确保目录存在
        os.makedirs(cls.VECTOR_DB_PATH, exist_ok=True)
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        
        return True
    
    @classmethod
    def print_config(cls):
        """打印当前配置（隐藏敏感信息）"""
        print("=== RAG系统配置 ===")
        print(f"LLM模型: {cls.LLM_MODEL}")
        print(f"嵌入模型: {cls.EMBED_MODEL}")
        print(f"向量库路径: {cls.VECTOR_DB_PATH}")
        print(f"API服务: {cls.API_HOST}:{cls.API_PORT}")
        print(f"最大工作线程: {cls.MAX_WORKERS}")
        print(f"缓存时间: {cls.CACHE_TTL}秒")
        print("=" * 30)

# 创建全局配置实例
config = Config()

if __name__ == "__main__":
    # 测试配置
    try:
        Config.validate()
        Config.print_config()
        print("✅ 配置验证通过")
    except Exception as e:
        print(f"❌ 配置错误: {e}")