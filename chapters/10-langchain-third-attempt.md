
# 第三次RAG搭建：LangChain实战



> 从Cherry Studio到LangChain的进化之路



---



## 📊 三次RAG搭建回顾



### 第一次尝试：Cherry Studio（2026年3月20日）

- **工具**：Cherry Studio + Ollama + DeepSeek R1

- **特点**：可视化操作，入门友好

- **局限**：定制化程度低，功能受限

- **成果**：初步理解RAG基本概念



### 第二次尝试：langchain仅打通流程（2026年3月31日）

- **工具**：自定义Python脚本 + 各种API

- **特点**：更灵活，但维护复杂

- **问题**：代码结构混乱，难以扩展

- **教训**：需要更好的框架支持



### 第三次尝试：LangChain完整搭建（2026年5月15日）

- **框架**：LangChain + ChromaDB+workflow

- **API**：SiliconFlow（embedding + rerank + LLM）

- **目标**：构建可生产部署的RAG系统

- **优势**：模块化，易维护，社区支持好



---



## 🎯 为什么选择LangChain？



### 1. 模块化设计

```python



# 清晰的组件划分

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.embeddings import OpenAIEmbeddings

from langchain.vectorstores import Chroma

from langchain.chat_models import ChatOpenAI

from langchain.chains import RetrievalQA



```



### 2. 丰富的集成

- 支持多种LLM（OpenAI, Anthropic, 本地模型）

- 多种向量数据库（Chroma, Pinecone, Weaviate）

- 多种文档加载器（PDF, Word, 网页）



### 3. 生产就绪

- 内置缓存机制

- 异步支持

- 监控和调试工具

- 社区活跃，文档完善

```



（完整文件有427行，包含详细代码示例、性能对比、经验教训等）








