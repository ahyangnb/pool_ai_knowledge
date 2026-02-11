# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pool AI Knowledge — a FastAPI backend providing a RAG-based knowledge base with Google ADK agent integration. Admins manage posts/documents via REST APIs; the system generates OpenAI embeddings stored in FAISS for semantic search. Users query via public search APIs or conversational AI agents (Gemini 2.0 Flash).

## Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Database init (creates tables + default admin)
python init_db.py

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Test knowledge base agent
python test_knowledge_agent.py
```

**Default admin:** `admin` / `admin123456`

## Architecture

### Unified Response Format

All endpoints use `R.ok(data)` / `R.fail(code, message)` from `models.py`:
```json
{"code": 0, "data": {...}, "message": "success"}
```
Global exception handlers in `main.py` ensure errors also follow this format.

### Request Flow

```
main.py          — FastAPI app, global handlers, chat/agent endpoints
├── admin_api.py — /api/admin/* (JWT protected) — post CRUD, API key mgmt, admin users
├── web_api.py   — /api/web/*  (public) — post listing, RAG search
├── auth.py      — JWT (HS256, 24h), bcrypt passwords, get_current_admin/require_super_admin deps
├── models.py    — Pydantic models (R wrapper, Post/APIKey/Admin/Search models)
└── database.py  — SQLAlchemy ORM models, MySQL connection, SQL file executor
```

### RAG Pipeline (knowledge_base_agent.py)

`KnowledgeBase` class loads posts from MySQL → generates OpenAI embeddings → stores in FAISS vector index. On query, FAISS similarity search returns top-k posts, which the Gemini agent uses to synthesize answers.

- Posts are embedded as `"{title}. {content}"`
- FAISS index lives in-memory, regenerated on startup and post updates
- `OPENAI_API_KEY` is mandatory for RAG to work

### Agent System (adk_agents.py)

Six agents registered in `AGENT_REGISTRY`: calculator, time, text, search, multi, knowledge. Each created via Google ADK `Agent()` with custom tool functions. The chat endpoint (`POST /api/chat`) creates a `Runner` per request with `InMemorySessionService`.

### Database

MySQL via SQLAlchemy. Schema managed by pure SQL files:
- `sql/schema.sql` — CREATE TABLE IF NOT EXISTS (idempotent)
- `sql/seed.sql` — INSERT ... WHERE NOT EXISTS (idempotent)

`database.py:init_db()` strips comments and executes these files via SQLAlchemy. Called on app startup and by `init_db.py`.

Four tables: `posts`, `api_keys`, `admin_users`, `system_config`.

### Key Conventions

- Admin endpoints require `Authorization: Bearer <jwt>` header
- Post tags stored as comma-separated strings in MySQL, exposed as `List[str]` in API
- API key values are masked (first 4 + last 4 chars) in all responses
- Post creation/update triggers RAG vector store regeneration
- `bcrypt==4.0.1` pinned for passlib compatibility (newer versions break)

## Environment Variables

Configured in `.env` (see `.env.example`):
- `DATABASE_URL` — MySQL connection string
- `GOOGLE_API_KEY` — For Google ADK agents
- `OPENAI_API_KEY` — Required for RAG embeddings
- `SECRET_KEY` — JWT signing key
