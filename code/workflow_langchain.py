"""
LangChain RAG工作流核心实现
支持文档加载、分割、向量化、检索和生成
"""

import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

# LangChain核心组件
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain.schema import Document

# 本地配置
from config import Config

class RAGWorkflow:
    """RAG工作流类"""
    
    def __init__(self):
        """初始化RAG工作流"""
        print("🚀 初始化RAG工作流...")
        
        # 验证配置
        Config.validate()
        
        # 初始化组件
        self.embedding = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        
        # 初始化各个组件
        self._init_embedding()
        self._init_llm()
        self._init_vectorstore()
        self._init_qa_chain()
        
        print("✅ RAG工作流初始化完成")
    
    def _init_embedding(self):
        """初始化嵌入模型（支持 API 和本地两种模式）"""
        print(f"📊 初始化嵌入模型: {Config.EMBED_MODEL}（模式: {Config.EMBED_MODE}）")
        
        if Config.EMBED_MODE == "api":
            # 通过 SiliconFlow API 调用嵌入模型
            self.embedding = OpenAIEmbeddings(
                openai_api_key=Config.SILICONFLOW_API_KEY,
                openai_api_base=Config.SILICONFLOW_API_BASE,
                model=Config.EMBED_MODEL
            )
        else:
            # 本地加载 HuggingFace 嵌入模型
            from langchain_community.embeddings import HuggingFaceEmbeddings
            self.embedding = HuggingFaceEmbeddings(
                model_name=Config.EMBED_MODEL,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
    
    def _init_llm(self):
        """初始化LLM模型"""
        print(f"🤖 初始化LLM模型: {Config.LLM_MODEL}")
        
        self.llm = ChatOpenAI(
            openai_api_key=Config.SILICONFLOW_API_KEY,
            openai_api_base=Config.SILICONFLOW_API_BASE,
            model_name=Config.LLM_MODEL,
            temperature=Config.LLM_TEMPERATURE,
            max_tokens=Config.LLM_MAX_TOKENS
        )
    
    def _init_vectorstore(self):
        """初始化向量数据库"""
        print(f"🗄️ 初始化向量数据库: {Config.VECTOR_DB_PATH}")
        
        # 检查是否存在现有向量库
        if os.path.exists(Config.VECTOR_DB_PATH):
            print("📂 加载现有向量库...")
            self.vectorstore = Chroma(
                persist_directory=Config.VECTOR_DB_PATH,
                embedding_function=self.embedding,
                collection_name=Config.COLLECTION_NAME
            )
        else:
            print("📝 向量库不存在，请先运行 build_vectors.py 构建")
            self.vectorstore = None
    
    def _init_qa_chain(self):
        """初始化问答链"""
        if not self.vectorstore:
            print("⚠️ 向量库未初始化，跳过QA链初始化")
            return
        
        print("🔗 初始化检索问答链...")
        
        # 创建检索器
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": Config.RETRIEVAL_K}
        )
        
        # 自定义提示模板
        template = """你是一个专业的客服助手，请根据以下上下文信息回答用户问题。
要求回答简洁（100-200字），直接给出关键信息，使用中文回答。

上下文信息：
{context}

用户问题：{question}

回答："""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # 构建QA链
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        print("✅ QA链初始化完成")
    
    def load_documents(self, data_dir: str = None) -> int:
        """加载文档到向量库"""
        if data_dir is None:
            data_dir = Config.DATA_DIR
        
        print(f"📄 从 {data_dir} 加载文档...")
        
        # 检查数据目录是否存在
        if not os.path.exists(data_dir):
            print(f"⚠️ 数据目录不存在: {data_dir}")
            return 0
        
        # 加载txt文件
        loader = DirectoryLoader(
            data_dir,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        documents = loader.load()
        
        if not documents:
            print("⚠️ 未找到文档文件")
            return 0
        
        print(f"📚 找到 {len(documents)} 个文档")
        
        # 文档分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？", "；"]
        )
        
        texts = text_splitter.split_documents(documents)
        print(f"✂️ 分割为 {len(texts)} 个文本块")
        
        # 创建或更新向量库
        if self.vectorstore is None:
            print("🆕 创建新向量库...")
            self.vectorstore = Chroma.from_documents(
                documents=texts,
                embedding=self.embedding,
                persist_directory=Config.VECTOR_DB_PATH,
                collection_name=Config.COLLECTION_NAME
            )
        else:
            print("➕ 添加到现有向量库...")
            self.vectorstore.add_documents(texts)
        
        # 持久化
        self.vectorstore.persist()
        print(f"💾 向量库已保存到: {Config.VECTOR_DB_PATH}")
        
        # 重新初始化QA链
        self._init_qa_chain()
        
        return len(texts)
    
    def query(self, question: str) -> Dict[str, Any]:
        """查询RAG系统"""
        if not self.qa_chain:
            return {
                "answer": "向量库未初始化，请先运行 build_vectors.py 构建向量库",
                "sources": [],
                "success": False,
                "error": "vectorstore_not_initialized"
            }
        
        print(f"🔍 查询: {question}")
        
        try:
            with get_openai_callback() as cb:
                result = self.qa_chain({"query": question})
                
                # 提取答案和来源文档
                answer = result["result"]
                sources = [doc.page_content for doc in result["source_documents"]]
                
                # 记录性能信息
                print(f"📊 Token使用: {cb.total_tokens}")
                print(f"💰 预估费用: ${cb.total_cost:.6f}")
                
                return {
                    "answer": answer,
                    "sources": sources,
                    "token_usage": {
                        "total_tokens": cb.total_tokens,
                        "total_cost": cb.total_cost
                    },
                    "success": True
                }
                
        except Exception as e:
            print(f"❌ 查询失败: {str(e)}")
            return {
                "answer": f"查询失败：{str(e)}",
                "sources": [],
                "success": False,
                "error": str(e)
            }
    
    def batch_query(self, questions: List[str]) -> List[Dict[str, Any]]:
        """批量查询"""
        results = []
        for i, question in enumerate(questions):
            print(f"📝 处理 {i+1}/{len(questions)}: {question}")
            result = self.query(question)
            results.append(result)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        if not self.vectorstore:
            return {"status": "vectorstore_not_initialized"}
        
        try:
            # 使用 get() 替代私有属性 _collection
            all_docs = self.vectorstore.get()
            doc_ids = all_docs.get('ids', [])
            
            return {
                "status": "ready",
                "document_count": len(doc_ids),
                "vector_db_path": Config.VECTOR_DB_PATH,
                "llm_model": Config.LLM_MODEL,
                "embedding_model": Config.EMBED_MODEL,
                "chunk_size": Config.CHUNK_SIZE,
                "retrieval_k": Config.RETRIEVAL_K
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


def main():
    """命令行测试入口"""
    if len(sys.argv) < 2:
        print("用法: python workflow_langchain.py <查询问题>")
        print("示例: python workflow_langchain.py '有哪些手机套餐？'")
        return
    
    question = sys.argv[1]
    
    # 创建工作流
    workflow = RAGWorkflow()
    
    # 执行查询
    result = workflow.query(question)
    
    print("\n" + "="*50)
    print(f"❓ 问题: {question}")
    print(f"✅ 成功: {result['success']}")
    
    if result['success']:
        print(f"💡 回答: {result['answer']}")
        print(f"📚 来源文档数量: {len(result['sources'])}")
        if 'token_usage' in result:
            print(f"📊 Token使用: {result['token_usage']['total_tokens']}")
    else:
        print(f"❌ 错误: {result.get('error', '未知错误')}")
    
    print("="*50)


if __name__ == "__main__":
    main()