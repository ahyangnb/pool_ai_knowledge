# Pool AI Knowledge - Backend

English | [中文](README_ZH.md)

A FastAPI backend providing a RAG-based knowledge base with Google ADK agent integration, admin management, and multilingual content support.

## Features

- **RAG Semantic Search** — OpenAI Embeddings + FAISS vector index for intelligent content matching
- **AI Agent Chat** — Google ADK + Gemini models, with knowledge base Q&A, calculator, search, and more
- **Admin Panel API** — JWT-protected endpoints for managing posts, API keys, and model selection
- **Multilingual Support** — Posts tagged with language (zh-CN / en / ja, etc.), filterable in search and listing
- **One-click Deploy** — Linux install script with systemd service

## Quick Start

### Requirements

- Python >= 3.10
- MySQL >= 5.7
- OpenAI API Key (required for RAG)
- Google API Key (required for agents)

### Local Development

```bash
# 1. Create virtual environment
python -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your database URL and API keys

# 4. Initialize database
python init_db.py

# 5. Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Linux Server Deployment

```bash
# Full install (includes MySQL)
sudo chmod +x setup.sh
sudo ./setup.sh

# App only (existing MySQL)
sudo ./setup.sh --app-only
```

After installation:
- API: `http://<server-ip>:8000`
- Docs: `http://<server-ip>:8000/docs`
- Default admin: `admin` / `admin123456`

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | MySQL connection string | Yes |
| `OPENAI_API_KEY` | OpenAI API Key for RAG embeddings | Yes |
| `GOOGLE_API_KEY` | Google API Key for Gemini agents | Yes |
| `SECRET_KEY` | JWT signing key | Yes |

> API keys can also be configured via the admin API. Database values take priority over .env.

## API Overview

### Authentication

All `/api/admin/*` endpoints require a JWT token:

```bash
# Login
curl -X POST /api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123456"}'
```

### Post Management

```bash
# Create post (with language)
POST /api/admin/posts
{"title": "Title", "content": "Content", "tags": ["tag1"], "language": "en"}

# List (filter by language)
GET /api/admin/posts?language=en&skip=0&limit=20

# Update
PUT /api/admin/posts/{id}

# Delete
DELETE /api/admin/posts/{id}
```

### Public API

```bash
# List posts (filter by language)
GET /api/web/posts?language=zh-CN

# Semantic search (filter by language)
GET /api/web/search?query=Python+tutorial&language=en
POST /api/web/search
{"query": "Python tutorial", "top_k": 5, "language": "en"}
```

### AI Chat

```bash
# Chat with knowledge base agent
POST /api/chat
{
  "agent_name": "knowledge",
  "message": "How do I use Python virtual environments?",
  "language": "en"
}
```

### API Key Management

```bash
# View effective keys (masked)
GET /api/admin/api-keys/effective

# Create key
POST /api/admin/api-keys
{"key_type": "openai", "key_name": "OpenAI Key", "key_value": "sk-xxx"}

# List / Update / Delete
GET    /api/admin/api-keys
PUT    /api/admin/api-keys/{id}
DELETE /api/admin/api-keys/{id}
```

### Model Management

```bash
# List available models + current
GET /api/admin/models

# Switch model
PUT /api/admin/models/current
{"model": "gemini-2.5-flash-preview-04-17"}
```

### Available Agents

| Agent | Description |
|-------|-------------|
| `knowledge` | Knowledge base Q&A (RAG semantic search) |
| `calculator` | Mathematical calculations |
| `time` | Time queries |
| `text` | Text processing |
| `search` | Web search |
| `multi` | Multi-tool combined |

## Project Structure

```
backend/
├── main.py                  # FastAPI app, global handlers, chat endpoints
├── admin_api.py             # Admin API (JWT protected)
├── web_api.py               # Public API
├── auth.py                  # JWT auth + bcrypt passwords
├── models.py                # Pydantic request/response models
├── database.py              # SQLAlchemy ORM + utility functions
├── adk_agents.py            # Google ADK agent definitions
├── knowledge_base_agent.py  # RAG knowledge base agent
├── init_db.py               # Database initialization script
├── setup.sh                 # Linux one-click deploy script
├── requirements.txt         # Python dependencies
├── sql/
│   ├── schema.sql           # Table creation
│   └── seed.sql             # Seed data
└── .env.example             # Environment variable template
```

## Service Management

```bash
# Status
sudo systemctl status pool_ai_knowledge

# Restart
sudo systemctl restart pool_ai_knowledge

# Logs
sudo journalctl -u pool_ai_knowledge -f

# Stop
sudo systemctl stop pool_ai_knowledge
```

## License

MIT
