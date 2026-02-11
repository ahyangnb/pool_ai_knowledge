# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Vue 2 admin management system based on vue-element-admin template. Uses Element UI for components, Vuex for state, Vue Router for navigation. The backend API runs at `http://localhost:8000`.

## Commands

- **Dev server**: `npm run dev` (port 9527, auto-opens browser)
- **Build production**: `npm run build:prod`
- **Build staging**: `npm run build:stage`
- **Lint**: `npm run lint`
- **Test**: `npm run test:unit`
- **Lint + Test**: `npm run test:ci`

## Architecture

### Authentication Flow

1. Login via `/api/admin/login` → stores JWT token in cookie (`Admin-Token`)
2. Route guard (`src/permission.js`) checks token on every navigation
3. If authenticated but no roles loaded: calls `/api/admin/me` to get user info
4. `is_super_admin=true` → role `['admin']`, otherwise `['editor']`
5. Routes filtered by role via `store/modules/permission.js`, then added with `router.addRoutes()`

### API Conventions

- All API functions live in `src/api/*.js` and use the shared `request()` service (`src/utils/request.js`)
- Backend endpoints use prefix `/api/admin/` with `baseURL: ''` to bypass the mock base URL
- Response format: `{ code: 0, data: {...} }` — code 0 is success
- Token sent as `Authorization: Bearer <token>` header
- Codes 50008/50012/50014 trigger re-login flow

### Routing & Sidebar

- `constantRoutes`: visible to all users (dashboard, post management, settings)
- `asyncRoutes`: filtered by user roles, added dynamically
- Sidebar is auto-generated from routes. Key route properties:
  - `hidden: true` — hides from sidebar (used for create/edit pages)
  - `meta.title` — displayed menu text
  - `meta.icon` — sidebar icon (SVG name or `el-icon-*`)
  - `meta.activeMenu` — which menu item to highlight (for hidden routes)
  - `meta.roles` — restrict access by role
  - `meta.affix` — pin tab in TagsView
- Single visible child route renders as a flat menu item (no nesting)
- Multiple visible children render as expandable submenu

### State Management

Vuex store modules in `src/store/modules/`:
- `user.js` — token, roles, user profile
- `permission.js` — route generation and filtering
- `app.js` — sidebar state, device type
- `tagsView.js` — open tab tracking
- `settings.js` — UI preferences

### Environment Config

- Development: proxy `/api` → `http://localhost:8000`, base API `/dev-api`
- Production: uses MockXHR for demo, base API `/prod-api`
- Staging: base API `/stage-api`

## Key Patterns

- Page components go in `src/views/<feature>/`, with sub-components in a `components/` subfolder
- "Coming soon" placeholder pages use `src/views/coming-soon/index.vue`
- Post CRUD: list at `/post/list`, create at `/post/create`, edit at `/post/edit/:id`
- Form pages share a common form component (e.g., `PostForm.vue`) with `isEdit` prop
