# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Vue 3 frontend for the Pool AI Knowledge Base. Provides a public-facing interface for browsing knowledge base articles and chatting with an AI agent (RAG-powered). The backend is a FastAPI server at `http://localhost:8000`.

## Commands

```bash
npm run dev       # Dev server on http://localhost:3000 (proxies /api → localhost:8000)
npm run build     # Production build to dist/
npm run preview   # Preview production build
```

No linting, testing, or formatting tools are configured yet.

## Architecture

### Tech Stack

Vue 3 (Composition API, `<script setup>`) + Vite + Element Plus + Vue Router 4 + Axios. Pinia is installed but not actively used — components use local `ref()` state.

### API Layer

All HTTP requests go through `src/api/request.js` — an Axios instance with a response interceptor that:
- Unwraps the backend's `{ code: 0, data: T, message: string }` envelope, returning only `data`
- Rejects when `code !== 0`

API modules in `src/api/` export plain functions (not classes). The `/api` prefix is proxied to the backend via `vite.config.js`.

### Routing

`src/router/index.js` — four lazy-loaded routes using `createWebHistory`:
- `/` → Home (recent posts + hero)
- `/posts` → Paginated post list
- `/posts/:id` → Post detail
- `/chat` → AI chat (calls `POST /api/chat` with `agent_name: "knowledge"`)

### Component Conventions

- Views live in `src/views/<feature>/index.vue` (or `detail.vue` for sub-pages)
- All components use `<script setup>` with Composition API
- All Element Plus icons are globally registered in `main.js`
- Scoped CSS with Element Plus theme variables (`--el-color-primary`, etc.)
- Loading states use Element Plus `v-loading` directive

### Backend API Endpoints Used

- `GET /api/web/posts?skip=0&limit=20` — public post list
- `GET /api/web/posts/:id` — single post
- `POST /api/web/search` — RAG search `{ query, top_k }`
- `POST /api/chat` — AI agent chat `{ agent_name, message }`
