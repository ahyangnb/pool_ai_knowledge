# Pool AI Knowledge - 智能知识库后端

[English](README.md) | 中文

基于 FastAPI 的 RAG 智能知识库系统，集成 Google ADK Agent，支持语义搜索和多语言内容管理。

## 功能特性

- **RAG 语义搜索** — OpenAI Embeddings + FAISS 向量索引，智能匹配文章内容
- **AI Agent 对话** — 基于 Google ADK + Gemini 模型，支持知识库问答、计算、搜索等多种 Agent
- **后台管理** — JWT 认证，文章 / API Key / 模型 全部可通过 API 管理
- **多语言支持** — 文章支持语言标签（zh-CN / en / ja 等），搜索和列表可按语言过滤
- **一键部署** — 提供 Linux 安装脚本 + systemd 服务

## 快速开始

### 环境要求

- Python >= 3.10
- MySQL >= 5.7
- OpenAI API Key（RAG 必需）
- Google API Key（Agent 对话必需）

### 本地开发

```bash
# 1. 创建虚拟环境
python -m venv venv && source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入数据库连接和 API Key

# 4. 初始化数据库
python init_db.py

# 5. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Linux 服务器部署

```bash
# 一键安装（包含 MySQL）
sudo chmod +x setup.sh
sudo ./setup.sh

# 如已有 MySQL，跳过数据库安装
sudo ./setup.sh --app-only
```

安装完成后：
- API 地址: `http://<服务器IP>:8000`
- 接口文档: `http://<服务器IP>:8000/docs`
- 默认管理员: `admin` / `admin123456`

## 环境变量

| 变量 | 说明 | 必填 |
|------|------|------|
| `DATABASE_URL` | MySQL 连接串 | 是 |
| `OPENAI_API_KEY` | OpenAI API Key（用于 RAG 向量化） | 是 |
| `GOOGLE_API_KEY` | Google API Key（用于 Gemini Agent） | 是 |
| `SECRET_KEY` | JWT 签名密钥 | 是 |

> API Key 也可通过后台管理 API 设置，数据库中的配置优先于 .env 文件。

## API 概览

### 认证

所有 `/api/admin/*` 端点需要 JWT Token：

```bash
# 登录获取 Token
curl -X POST /api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123456"}'
```

### 文章管理

```bash
# 创建文章（指定语言）
POST /api/admin/posts
{"title": "标题", "content": "内容", "tags": ["标签"], "language": "zh-CN"}

# 列表（按语言过滤）
GET /api/admin/posts?language=zh-CN&skip=0&limit=20

# 更新
PUT /api/admin/posts/{id}

# 删除
DELETE /api/admin/posts/{id}
```

### 公共 API

```bash
# 文章列表（按语言过滤）
GET /api/web/posts?language=en

# 语义搜索（按语言过滤）
GET /api/web/search?query=Python教程&language=zh-CN
POST /api/web/search
{"query": "Python tutorial", "top_k": 5, "language": "en"}
```

### AI 对话

```bash
# 与知识库 Agent 对话
POST /api/chat
{
  "agent_name": "knowledge",
  "message": "Python虚拟环境怎么用？",
  "language": "zh-CN"
}
```

### API Key 管理

```bash
# 查看当前生效的 Key（脱敏）
GET /api/admin/api-keys/effective

# 创建 Key
POST /api/admin/api-keys
{"key_type": "openai", "key_name": "OpenAI Key", "key_value": "sk-xxx"}

# 列表 / 更新 / 删除
GET    /api/admin/api-keys
PUT    /api/admin/api-keys/{id}
DELETE /api/admin/api-keys/{id}
```

### 模型管理

```bash
# 获取可用模型列表 + 当前模型
GET /api/admin/models

# 切换模型
PUT /api/admin/models/current
{"model": "gemini-2.5-flash-preview-04-17"}
```

### 可用 Agent

| Agent | 说明 |
|-------|------|
| `knowledge` | 知识库问答（RAG 语义搜索） |
| `calculator` | 数学计算 |
| `time` | 时间查询 |
| `text` | 文本处理 |
| `search` | 网络搜索 |
| `multi` | 多功能综合 |

## 项目结构

```
backend/
├── main.py                  # FastAPI 入口，全局异常处理，聊天端点
├── admin_api.py             # 后台管理 API（JWT 保护）
├── web_api.py               # 公共 API
├── auth.py                  # JWT 认证 + bcrypt 密码
├── models.py                # Pydantic 请求/响应模型
├── database.py              # SQLAlchemy ORM + 工具函数
├── adk_agents.py            # Google ADK Agent 定义
├── knowledge_base_agent.py  # RAG 知识库 Agent
├── init_db.py               # 数据库初始化脚本
├── setup.sh                 # Linux 一键部署脚本
├── requirements.txt         # Python 依赖
├── sql/
│   ├── schema.sql           # 建表语句
│   └── seed.sql             # 初始数据
└── .env.example             # 环境变量模板
```

## 服务管理

```bash
# 查看状态
sudo systemctl status pool_ai_knowledge

# 重启
sudo systemctl restart pool_ai_knowledge

# 查看日志
sudo journalctl -u pool_ai_knowledge -f

# 停止
sudo systemctl stop pool_ai_knowledge
```

## 许可证

MIT
