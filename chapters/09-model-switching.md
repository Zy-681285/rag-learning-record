# 模型切换实战：从DeepSeek到GLM-4-9B

> 响应时间从120秒到4秒的优化之路

---

## 📊 背景：为什么需要切换模型

### 初始配置（2026年5月）

- **LLM模型**：DeepSeek-V4-Flash
- **响应时间**：120-180秒（3次LLM调用）
- **用户反馈**："3分钟才生成结果，太慢了"
- **硬件限制**：4核8GB，无法并行化LLM调用

### 瓶颈分析

```
DeepSeek-V4-Flash 单次调用：25-33秒
完整工作流（3次调用）：75-99秒
加上其他开销：总时间120-180秒
```

---

## 🔍 模型调研与选择

### SiliconFlow API可用模型

通过API查询可用模型：

```bash
curl -s https://api.siliconflow.cn/v1/models \
  -H "Authorization: Bearer $API_KEY" | jq '.data[].id'
```

### 重点关注的模型

| 模型ID | 名称 | 响应时间 | 质量 | 适合场景 |
|--------|------|----------|------|----------|
| deepseek-ai/DeepSeek-V4-Flash | DeepSeek | 25-33秒 | ⭐⭐⭐⭐⭐ | 复杂分析 |
| **THUDM/GLM-4-9B-0414** | **GLM-4-9B** | **4秒** | **⭐⭐⭐⭐** | **客服场景** |
| Qwen/Qwen2.5-7B | Qwen2.5 | 10-15秒 | ⭐⭐⭐ | 通用对话 |
| THUDM/GLM-4-Flash | GLM-4 | 8-12秒 | ⭐⭐⭐ | 快速响应 |

### 最终选择：GLM-4-9B-0414

**优势：**
- 响应快（平均4秒），适合客服场景
- 中文能力优秀，能理解电信业务术语
- API兼容OpenAI格式，无需改代码

**不足：**
- 复杂推理能力不如DeepSeek
- 长文本处理能力有限

---

## 🔄 切换过程

### 1. 代码层面切换

```python
# 旧配置 - DeepSeek
llm = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V4-Flash",
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1",
    temperature=0.3
)

# 新配置 - GLM-4-9B
llm = ChatOpenAI(
    model="THUDM/GLM-4-9B-0414",
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1",
    temperature=0.1,  # 降低温度减少幻觉
    max_tokens=500
)
```

### 2. 配置对比

| 项 | DeepSeek-V4-Flash | GLM-4-9B-0414 |
|---|-------------------|---------------|
| temperature | 0.3 | 0.1 |
| max_tokens | 1000 | 500 |
| 单次调用时间 | 25-33秒 | 3-5秒 |
| 质量 | 优秀 | 良好 |

### 3. Prompt调整

```python
# DeepSeek Prompt（可以处理复杂指令）
SYSTEM_PROMPT_DEEPSEEK = """
你是一个专业的客服助手。
1. 分析用户问题
2. 从文档中提取相关信息
3. 生成简洁的回答
"""

# GLM-4-9B Prompt（需要更明确的指令）
SYSTEM_PROMPT_GLM = """
你是一个电信客服助手。
根据文档回答问题，不超过200字。
只使用文档内容，不要编造信息。
"""
```

---

## 📈 效果对比

### 响应时间

| 阶段 | 模型 | 响应时间 | 用户反馈 |
|------|------|---------|---------|
| 优化前 | DeepSeek-V4-Flash | 120-180秒 | ❌ "太慢了" |
| 减少LLM调用 | DeepSeek-V4-Flash | 25-33秒 | ❌ "还是慢" |
| 切换模型 | GLM-4-9B | 4-8秒 | ✅ "可以接受" |
| 最终调优 | GLM-4-9B | 3-5秒 | ✅ "还不错" |

### 质量评估

| 维度 | DeepSeek | GLM-4-9B | 说明 |
|------|----------|----------|------|
| 召回率 | 85% | 82% | 略有下降 |
| 准确率 | 90% | 85% | 略有下降 |
| 幻觉率 | 10% | 12% | 略有上升 |
| 响应时间 | 25-33秒 | 3-5秒 | ✅ 大幅提升 |

---

## 💡 经验总结

1. **场景决定模型**：客服场景不需要最强的模型，合适的才是最好的
2. **质量与速度的平衡**：GLM-4-9B牺牲约5%准确率，换来了85%的速度提升
3. **Prompt需要适配模型**：弱模型需要更简单明确的指令
4. **降temperature有用**：从0.3降到0.1，幻觉率明显降低
5. **客服场景GLM-4-9B够用**：简单问题准确率高，复杂问题可以fallback到DeepSeek
