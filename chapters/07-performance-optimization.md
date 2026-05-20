# RAG性能优化实战

> 基于4核8GB服务器的优化心得，响应时间从120秒到4秒

---

## 📊 性能瓶颈分析

### 初始状态（优化前）

| 指标 | 数值 | 备注 |
|------|------|------|
| LLM调用时间 | 25-33秒 | DeepSeek-V4-Flash模型 |
| 总响应时间 | 120-180秒 | 3次LLM调用的完整工作流 |
| 并发能力 | 1-2个 | 4核8GB限制 |
| 内存使用 | ~150MB/工作流 | ChromaDB + LangChain |

### 瓶颈定位

1. **LLM API调用**：占总时间80%以上
2. **向量检索**：相对快速，<2秒
3. **Python进程启动**：每次调用约2-3秒开销

---

## 🔧 优化策略与实施

### 策略1：减少LLM调用次数

**原始工作流（3次调用）：**

```python
# 调用1：意图识别
intent = llm_call("分析用户意图...")
# 调用2：信息提取
info = llm_call("从文档提取关键信息...")
# 调用3：生成回复
answer = llm_call("根据信息生成回答...")
```

**优化后（1次调用）：**

```python
# 合并为1次调用
answer = llm_call("""
根据以下文档回答问题，要求简洁（200字内）。
文档：{context}
问题：{question}
""")
```

**性能提升：** 75-99秒 → 25-33秒

### 策略2：使用GLM-4-9B替代DeepSeek-V4-Flash

将LLM模型从DeepSeek-V4-Flash切换到GLM-4-9B-0414。

**效果对比：**

| 模型 | 单次调用时间 | 质量评分 |
|------|-------------|---------|
| DeepSeek-V4-Flash | 25-33秒 | ⭐⭐⭐⭐⭐ |
| GLM-4-9B-0414 | 3-5秒 | ⭐⭐⭐⭐ |

**实际收益：**
- 单次调用从25-33秒降至3-5秒
- 完整工作流从75-99秒降至9-15秒
- 质量略微下降但客服场景完全可以接受

### 策略3：增加Reranker提升检索质量

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker

# 加载Reranker模型（BAAI/bge-reranker-v2-m3）
reranker = CrossEncoderReranker(model_name="BAAI/bge-reranker-v2-m3")

# 构建压缩检索器
compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=vector_store.as_retriever(search_kwargs={"k": 10})
)
```

**效果：**
- 召回率提升20-30%
- 准确率提升15-25%
- 检索时间增加<1秒（可忽略）

### 策略4：调整向量检索参数

```python
# 优化前
retriever = vector_store.as_retriever(search_kwargs={"k": 4})

# 优化后
retriever = vector_store.as_retriever(
    search_kwargs={
        "k": 6,              # 增加检索数量
        "score_threshold": 0.7  # 设置相似度阈值
    }
)
```

### 策略5：优化提示词（Prompt Engineering）

**优化前（导致重复检索）：**

```
你是一个客服助手，请根据以下文档回答问题。
如果文档中没有相关信息，请说"不知道"。
```

**优化后（减少幻觉）：**

```
你是一个电信客服助手。请严格根据以下文档回答问题。

规则：
1. 回答不超过200字
2. 只使用文档中的信息
3. 如果文档信息不足，请说："根据现有资料，我无法确定这个问题的答案"
4. 不要编造信息
5. 输出格式：直接回答，不要加前缀

文档：{context}
问题：{question}
```

---

## 📈 优化效果汇总

| 优化步骤 | 优化前 | 优化后 | 提升比例 |
|---------|--------|--------|---------|
| 减少LLM调用 | 75-99秒 | 25-33秒 | ~70% |
| 切换模型(GLM-4-9B) | 25-33秒 | 3-5秒 | ~85% |
| 增加Reranker | 召回率50% | 召回率80% | ~60% |
| 优化Prompt | 幻觉率30% | 幻觉率10% | ~67% |

### 最终效果

- **响应时间**：3-8秒（平均5秒）
- **召回率**：85%+
- **准确率**：85%+
- **幻觉率**：<10%
- **用户满意度**：从"太慢了"到"还不错"

---

## 💡 经验总结

1. **先优化架构，再优化代码**：减少LLM调用次数带来的收益远大于代码级优化
2. **选择合适的模型**：客服场景不需要最强的模型，合适的模型更重要
3. **Reranker是性价比最高的优化**：少量时间成本带来显著质量提升
4. **Prompt Engineering不能忽视**：好的提示词可以减少一半以上的幻觉
5. **监控是关键**：没有数据就没有优化方向
