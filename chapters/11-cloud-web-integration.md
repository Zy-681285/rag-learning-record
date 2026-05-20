# 云服务迁移与网页集成实战

> 从本地开发到云端部署的关键转折点

---

## 🎯 迁移动机：为什么要上云？

### 本地开发的局限性

1. **访问限制**：只能本地访问，无法远程使用
2. **性能瓶颈**：本地资源有限（4核8GB）
3. **稳定性差**：电脑关机/网络断开服务就停止
4. **协作困难**：无法多人同时使用

### 云端部署的优势

1. **24/7可用**：云服务器稳定运行
2. **弹性扩展**：可按需升级配置
3. **全球访问**：通过公网IP随时访问
4. **易于维护**：SSH远程管理，自动化部署

---

## 📋 迁移前的准备工作

### 1. 代码重构

```python
# 之前：硬编码配置
PERSIST_DIR = '/home/user/rag_db'
API_KEY = 'sk-hardcoded-key'

# 之后：环境变量配置
PERSIST_DIR = os.getenv('VECTOR_DB_PATH', './vector_db')
API_KEY = os.getenv('SILICONFLOW_API_KEY')
```

### 2. 项目结构优化

```
rag-cloud/
├── src/                    # 源代码
│   ├── workflow.py        # RAG工作流
│   ├── api.py            # API服务
│   └── config.py         # 配置管理
├── data/                  # 知识库数据
├── scripts/               # 部署脚本
│   ├── deploy.sh         # 部署脚本
│   ├── build_vectors.py  # 构建向量库
│   └── health_check.py   # 健康检查
├── tests/                 # 测试
├── requirements.txt       # 依赖
└── .env.example          # 环境变量模板
```

---

## 🚀 部署方案

### 方案A：FastAPI + 进程管理

```python
# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.workflow import RAGWorkflow

app = FastAPI()
rag = RAGWorkflow()

class Query(BaseModel):
    question: str
    user_id: str = "anonymous"

@app.post("/api/query")
async def query(request: Query):
    try:
        result = rag.run(request.question)
        return {
            "answer": result['answer'],
            "sources": result['sources'],
            "time": result['time']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "ok", "model": rag.current_model}
```

### 方案B：Gunicorn + Uvicorn

```bash
# 安装
pip install gunicorn uvicorn

# 启动（4 workers）
gunicorn api:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

---

## 🌐 网页集成

### 简易Web界面

```html
<!DOCTYPE html>
<html>
<head>
    <title>客服助手</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: auto; padding: 20px; }
        #chat { height: 400px; overflow: auto; border: 1px solid #ccc; padding: 10px; }
        #input { width: 80%; padding: 8px; }
    </style>
</head>
<body>
    <h2>📞 电信客服助手</h2>
    <div id="chat"></div>
    <input id="input" placeholder="请输入您的问题..." />
    <button onclick="send()">发送</button>
    
    <script>
        async function send() {
            const question = document.getElementById('input').value;
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question})
            });
            const data = await response.json();
            // 显示结果
            document.getElementById('chat').innerHTML += 
                `<p><b>用户：</b>${question}</p>
                 <p><b>助手：</b>${data.answer}</p>`;
        }
    </script>
</body>
</html>
```

---

## 🔧 部署与运维

### 一键部署脚本

```bash
#!/bin/bash
# deploy.sh
set -e

echo "🚀 开始部署 RAG 系统..."

# 1. 更新代码
git pull origin main

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 更新依赖
pip install -r requirements.txt

# 4. 重启服务
sudo systemctl restart rag-api

echo "✅ 部署完成！"

# 5. 健康检查
sleep 3
curl http://localhost:8000/api/health
```

### 日志监控

```python
# 使用logging记录
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag.log'),
        logging.StreamHandler()
    ]
)
```

---

## 📊 运行效果

| 指标 | 本地环境 | 云服务器 | 提升 |
|------|---------|---------|------|
| 可用时间 | 工作时间 | 24/7 | ✅ |
| 响应时间 | 4-8秒 | 3-6秒 | ✅ |
| 并发处理 | 1个 | 4个并发 | ✅ |
| 维护方式 | 手动 | 自动化 | ✅ |
| 访问方式 | 本地 | 公网+钉钉 | ✅ |

---

## 💡 经验总结

1. **环境变量管理密钥**：永不硬编码API密钥
2. **使用Systemd管理进程**：自动重启保证稳定性
3. **健康检查接口**：便于监控和调试
4. **日志记录**：排查问题的基础
5. **分步部署**：先内部测试再对外开放
