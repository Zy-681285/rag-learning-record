# RAG学习记录 - 从零到部署

> **从零开始学习并构建完整的RAG系统，历时两个月的实战记录**
>
> 📅 学习时间：2026年3月20日 - 5月21日

---

## 📋 项目概览

这是一个**完整的RAG（检索增强生成）学习与实践项目**，记录了从环境搭建、代码实现、性能优化到生产部署的全过程。

### 🚀 核心成果
- **完整RAG系统**：基于LangChain + ChromaDB + 硅基流动API
- **电信套餐问答**：针对真实业务场景的智能客服系统
- **性能优化**：首次响应从120秒优化到4秒（30倍提升）
- **生产部署**：成功部署到云服务器并集成钉钉机器人

### 🎯 核心能力展示
- ✅ **完整RAG系统搭建**：从环境配置到代码实现
- ✅ **性能优化能力**：解决实际工程瓶颈（120秒→4秒）
- ✅ **生产环境部署**：集成钉钉机器人，7×24小时可用
- ✅ **实际业务处理**：电信套餐问答准确率80%+（基于100组人工标注测试集）
- ✅ **问题解决能力**：遇到编码、并发、部署等困难时主动排查解决

---

## 🏗️ 项目结构

```
rag-learning-record/
├── README.md                    # 本文件
├── chapters/                    # 学习日志（11个章节）
│   ├── 01-first-attempts.md    # 第一次尝试
│   ├── 02-langchain-success.md # LangChain成功
│   ├── 03-encoding-war.md      # 编码问题解决
│   ├── 04-platform-comparison.md # 平台对比
│   ├── 05-vllm-and-cloud.md    # VLLM探索
│   ├── 06-final-tuning.md      # 最终调优
│   ├── 07-performance-optimization.md # 性能优化（关键！）
│   ├── 08-dingtalk-deployment.md # 钉钉部署
│   ├── 09-model-switching.md   # 模型切换
│   ├── 10-langchain-third-attempt.md # 第三次搭建
│   └── 11-cloud-web-integration.md # 云服务集成
├── code/                        # 完整代码实现
│   ├── config.py               # 系统配置管理
│   ├── workflow_langchain.py   # 核心RAG工作流
│   ├── api.py                  # FastAPI服务接口
│   ├── build_vectors.py        # 向量库构建脚本
│   ├── test_system.py          # 系统测试脚本
│   ├── start.sh                # 快速启动脚本
│   ├── start-with-docker.sh    # Docker 一键启动脚本
│   ├── docker-compose.yml      # Docker编排配置
│   ├── Dockerfile              # 容器镜像构建文件
│   ├── requirements.txt        # Python依赖
│   ├── .env.example            # 环境变量示例
│   └── data/                   # 示例知识库数据
├── extras/                      # 实用资源
│   ├── configuration-snippets.md # 关键配置片段
│   ├── glossary.md             # RAG术语表
│   └── lessons-learned.md      # 避坑清单（重要！）
└── assets/                      # 资源文件
    └── screenshots/            # 截图和图表
```

### 🔧 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| **框架** | LangChain | 主流的LLM应用开发框架 |
| **向量数据库** | ChromaDB | 轻量级开源向量数据库 |
| **嵌入模型** | BAAI/bge-large-zh-v1.5 | 中文嵌入效果优秀 |
| **大语言模型** | DeepSeek-V4-Flash / GLM-4-9B | 多模型对比实验 |
| **API服务** | 硅基流动 | 国内稳定可用的AI API |
| **部署** | 云服务器 | 生产环境部署方案 |
| **容器化** | Docker | 可选部署方式 |

---

## 🚀 快速开始

> ⚠️ 本仓库代码正在整理中，git clone 链接将于近期开放。你也可以直接下载 code/ 目录使用。

### 1️⃣ 环境准备

```bash
# 克隆仓库（链接准备中）
git clone https://github.com/Zy-681285/rag-learning-record.git
cd rag-learning-record/code

# 创建虚拟环境
python -m venv rag-env
source rag-env/bin/activate  # Linux/Mac
# rag-env\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 配置API密钥

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
SILICONFLOW_API_KEY=sk-your-key-here
```

### 3️⃣ 运行系统

```bash
# 1. 构建向量数据库
python build_vectors.py

# 2. 启动API服务
python api.py

# 3. 测试系统
python test_system.py
```

### 4️⃣ 使用 Docker 部署（可选）

```bash
cd rag-learning-record/code
docker compose up -d
```

### 5️⃣ 访问服务

- **API文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health
- **问答接口**：http://localhost:8000/ask

---

## 📊 性能对比与优化成果

> 以下数据基于电信套餐问答场景测试，测试集为 100 组人工标注的问答对。

### 🎯 关键优化成果

| 优化项目 | 优化前 | 优化后 | 提升倍数 |
|----------|--------|--------|----------|
| **首次响应时间** | 120秒¹ | 4秒 | 30倍 |
| **检索召回率²** | 60% | 85% | 1.4倍 |
| **答案准确率³** | 70% | 80% | 1.1倍 |
| **部署方式** | 本地单机 | 云端+钉钉 | 生产级 |

> ¹ 优化前 120 秒包含首次加载模型 + 构建临时索引的冷启动时间，优化后通过预加载和缓存避免重复冷启动，纯问答响应稳定在 4 秒以内。
> ² 召回率 = 检索到的相关文档数 / 知识库中应召回的相关文档总数
> ³ 准确率：由人工逐条评判，回答是否准确回答用户问题（包含信息准确 + 意图匹配）

### 🔧 主要优化措施

1. **模型切换**：DeepSeek → GLM-4-9B-0414（响应速度提升6-8倍）
2. **检索策略**：单路检索 → 多路检索（召回率提升25%）
3. **缓存机制**：添加结果缓存（重复问题秒回）
4. **异步处理**：线程池优化（并发能力提升）

### 📈 性能对比图

```
响应时间对比（秒）
优化前: ████████████████████████████████ 120秒（含冷启动）
优化后: ██ 4秒（纯问答）

准确率对比（%）
优化前: ██████████████████████████████████████████████████████████ 70%
优化后: ████████████████████████████████████████████████████████████████████ 80%
```

---

## 🗺️ 给初学者的学习路线

### 第1周：环境搭建与基础概念

1. **理解RAG是什么**：检索增强生成的基本原理
2. **搭建开发环境**：Python + LangChain + 向量数据库
3. **运行第一个示例**：跑通最简单的RAG流程

### 第2周：代码理解与实践

1. **阅读核心代码**：理解 `workflow_langchain.py` 的工作流程
2. **修改配置参数**：尝试不同的分块大小、检索数量
3. **处理自己的数据**：准备一个领域的文档进行测试

### 第3周：调优与优化

1. **调整检索策略**：实验不同的相似度阈值
2. **优化性能**：解决响应慢、内存不足等问题
3. **对比不同模型**：测试多个LLM的效果

### 第4周：部署与展示

1. **创建API接口**：用FastAPI包装RAG功能
2. **部署到服务器**：使用Docker容器化部署
3. **制作作品集**：整理代码和文档，展示学习成果

### 🎓 学习资源推荐

- **官方文档**：[LangChain Documentation](https://docs.langchain.com/)
- **中文教程**：[硅基流动文档](https://docs.siliconflow.cn/)
- **开源项目**：[ChromaDB GitHub](https://github.com/chroma-core/chroma)

---

## 📖 详细学习日志

> 以下为原始学习记录，详细记录了每天的进展和问题。
> 对具体实现过程感兴趣的读者可以按顺序阅读。

### 📅 关键时间线

| 日期 | 里程碑 | 关键收获 |
|------|--------|----------|
| 3月20日 | 艰难起步 | 环境配置的各种坑 |
| 3月30日 | LangChain首次成功 | 基础RAG跑通 |
| 4月4日 | 编码问题解决 | UTF-8编码的重要性 |
| 4月15日 | Dify平台尝试 | 低代码平台的优缺点 |
| 5月4日 | 灵魂拷问 | RAG真的有效吗？ |
| 5月9日 | 调优突破 | 多路检索策略成功 |
| 5月20日 | 生产部署 | 云服务器+钉钉集成 |

### 📚 章节索引

详细的每日学习记录，请查看：
1. [第一次尝试](chapters/01-first-attempts.md) — Ollama、Dify部署困境
2. [LangChain成功](chapters/02-langchain-success.md) — 首次运行成功
3. [编码战争](chapters/03-encoding-war.md) — UTF-8编码问题解决
4. [平台对比](chapters/04-platform-comparison.md) — 多平台实验总结
5. [VLLM探索](chapters/05-vllm-and-cloud.md) — 本地模型部署尝试
6. [最终调优](chapters/06-final-tuning.md) — RAG本质思考
7. **[性能优化](chapters/07-performance-optimization.md)** ⭐ — 从120秒到4秒
8. [钉钉部署](chapters/08-dingtalk-deployment.md) — 生产环境集成
9. [模型切换](chapters/09-model-switching.md) — GLM-4-9B实战
10. [第三次搭建](chapters/10-langchain-third-attempt.md) — LangChain重写
11. [云服务集成](chapters/11-cloud-web-integration.md) — 最终部署

### 📝 经验总结

- **硬件配置**：8G内存可运行，16G更流畅
- **平台选择**：LangChain灵活，Dify易用，各有利弊
- **嵌入模型**：BGE-M3中英文通用，bge-large-zh中文优化
- **检索策略**：多路检索 > 单路检索，Reranker效果显著
- **数据处理**：编码转换很重要，分块策略影响效果

---

## 🙏 致谢与参考

### 感谢以下开源项目和API服务

- [LangChain](https://github.com/langchain-ai/langchain) — LLM应用开发框架
- [ChromaDB](https://github.com/chroma-core/chroma) — 向量数据库
- [硅基流动](https://siliconflow.cn/) — 国内AI API服务
- [BAAI/bge-large-zh-v1.5](https://huggingface.co/BAAI/bge-large-zh-v1.5) — 中文嵌入模型

### 学习资源

- [LangChain官方文档](https://docs.langchain.com/)
- [ChromaDB文档](https://docs.trychroma.com/)
- [硅基流动API文档](https://docs.siliconflow.cn/)

---

## 📞 联系我

**关彧** · RAG / LLM应用开发实践者
- GitHub: [Zy-681285](https://github.com/Zy-681285)
- 项目：[rag-learning-record](https://github.com/Zy-681285/rag-learning-record)
- 欢迎 Issue / PR 交流

---

## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

*最后更新：2026年5月21日*
*学习时长：2个月*
*项目状态：基础版本已完成，持续优化中*
```
