# 钉钉机器人部署实战

> 从本地RAG到钉钉在线客服的完整过程

---

## 🎯 目标：让RAG系统在钉钉中可用

### 最终效果

- 用户在钉钉中发送问题
- 机器人调用RAG工作流
- 返回简洁的客服回答（200字内）
- 响应时间：4-30秒（根据问题复杂度）

---

## 📋 前期准备

### 1. 创建钉钉企业内部应用

1. 登录[钉钉开放平台](https://open.dingtalk.com)
2. 创建企业内部应用
3. 获取 `AppKey` 和 `AppSecret`
4. 启用"机器人"能力
5. 配置事件订阅（接收消息）

### 2. 服务器配置

- **系统**：Ubuntu 20.04 LTS
- **配置**：4核8GB（阿里云ECS）
- **Python**：3.9+
- **依赖**：langchain, chromadb, dingtalk-stream

---

## 🔧 部署步骤

### 步骤1：环境准备

```bash
# 克隆代码
git clone https://github.com/your-repo/rag-project.git
cd rag-project

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤2：配置环境变量

```bash
export DINGTALK_APP_KEY="your_app_key"
export DINGTALK_APP_SECRET="your_app_secret"
export SILICONFLOW_API_KEY="your_siliconflow_key"
export VECTOR_DB_PATH="/path/to/vector_db"
```

### 步骤3：启动机器人服务

```python
# dingtalk_bot.py
import os
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from dingtalk_stream import AckMessage
import dingtalk_stream

# 初始化向量库
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3"
)
vector_store = Chroma(
    persist_directory=os.getenv('VECTOR_DB_PATH'),
    embedding_function=embeddings
)

# 处理消息的回调
def on_message(message):
    # 1. 接收钉钉消息
    user_question = message.text.content
    
    # 2. 调用RAG工作流
    result = rag_workflow(user_question)
    
    # 3. 返回结果
    return result['answer']

# 启动钉钉Stream模式
def start_bot():
    client = dingtalk_stream.DingTalkStreamClient(
        app_key=os.getenv('DINGTALK_APP_KEY'),
        app_secret=os.getenv('DINGTALK_APP_SECRET')
    )
    
    @client.msg_callback_filter('sample_callback')
    def callback(message):
        reply = on_message(message)
        client.sync_reply_message(reply, message)
        return AckMessage.STATUS_OK, 'OK'
    
    client.start()
```

### 步骤4：部署为系统服务

```ini
# /etc/systemd/system/dingtalk-bot.service
[Unit]
Description=DingTalk RAG Bot
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/rag-project
EnvironmentFile=/home/admin/rag-project/.env
ExecStart=/home/admin/rag-project/venv/bin/python dingtalk_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable dingtalk-bot
sudo systemctl start dingtalk-bot
```

---

## ⚠️ 踩过的坑

### 坑1：响应超时

问题：钉钉要求5秒内返回消息，但RAG工作流需要25-30秒。

解决：改为异步模式，先返回"正在查询中..."，再发送结果。

### 坑2：消息去重

问题：钉钉偶发重复推送消息，导致重复查询。

解决：实现消息ID去重缓存。

```python
from cachetools import TTLCache

message_cache = TTLCache(maxsize=100, ttl=300)  # 5分钟过期

def on_message(message):
    msg_id = message.message_id
    if msg_id in message_cache:
        return  # 已处理过，跳过
    message_cache[msg_id] = True
    # 处理消息...
```

### 坑3：环境变量配置

问题：直接在代码中硬编码API密钥，导致Git泄露。

解决：使用 `.env` 文件 + `python-dotenv` 管理，`.env` 加入 `.gitignore`。

---

## 📊 运行效果

| 指标 | 数值 |
|------|------|
| 平均响应时间 | 4-8秒 |
| 日处理消息数 | 50-200条 |
| 系统CPU使用率 | 60-80% |
| 内存使用 | 2-3GB |
| 运行稳定性 | 99%+ uptime |
