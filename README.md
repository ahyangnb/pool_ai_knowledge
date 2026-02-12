<p align="center">
  <img src="git/logo.png" alt="Pool AI Knowledge Logo" width="120">
</p>

<p align="center">
  <img src="git/banner_english.png" alt="Pool AI Knowledge Banner">
</p>

<p align="center">
  <img src="git/banner_chinise.png" alt="Pool AI Knowledge 横幅">
</p>

# Pool AI Knowledge

An open-source AI knowledge base system with RAG (Retrieval-Augmented Generation) capabilities. It provides a full-stack solution including a Python backend, a Vue admin dashboard, and cross-platform clients for Web(Vue), Desktop (Flutter -> Windows/macOS/Linux), and Mobile (Flutter -> Android/iOS).

一个开源的 AI 知识库系统，具备 RAG（检索增强生成）能力。提供完整的全栈解决方案，包括 Python 后端、Vue 管理后台，以及支持 Web(Vue)、桌面端（Flutter -> Windows/macOS/Linux）和移动端（Flutter -> Android/iOS）的跨平台客户端。

> **Status / 状态:** Under active development / 积极开发中

## About author / 关于作者
微信（wechat）：q1666655
邮箱（email）：zonggeu@gmail.com

## Screenshots / 截图

### Admin Dashboard / 管理后台

<p align="center">
  <img src="screen_shots/admin_1.png" width="30%">&nbsp;
  <img src="screen_shots/admin_2.png" width="30%">&nbsp;
  <img src="screen_shots/admin_3.png" width="30%">
</p>

### Web - English

<p align="center">
  <img src="screen_shots/web_en_1.png" width="45%">&nbsp;
  <img src="screen_shots/web_en_2.png" width="45%">
</p>
<p align="center">
  <img src="screen_shots/web_en_3.png" width="45%">&nbsp;
  <img src="screen_shots/web_en_4.png" width="45%">
</p>

### Web - 中文

<p align="center">
  <img src="screen_shots/web_zh-cn_1.png" width="45%">&nbsp;
  <img src="screen_shots/web_zh-cn_2.png" width="45%">
</p>
<p align="center">
  <img src="screen_shots/web_zh-cn_3.png" width="45%">&nbsp;
  <img src="screen_shots/web_zh-cn_5.png" width="45%">
</p>
<p align="center">
  <img src="screen_shots/web_zh-cn_6.png" width="45%">
</p>

### Desktop (macOS) - English

<p align="center">
  <img src="screen_shots/pc_macos_en_1.png" width="45%">&nbsp;
  <img src="screen_shots/pc_macos_en_2.png" width="45%">
</p>
<p align="center">
  <img src="screen_shots/pc_macos_en_3.png" width="45%">&nbsp;
  <img src="screen_shots/pc_macos_en_4.png" width="45%">
</p>
<p align="center">
  <img src="screen_shots/pc_macos_en_5.png" width="45%">
</p>

### Desktop (macOS) - 中文

<p align="center">
  <img src="screen_shots/pc_macos_zh-cn_1.png" width="45%">&nbsp;
  <img src="screen_shots/pc_macos_zh-cn_2.png" width="45%">
</p>
<p align="center">
  <img src="screen_shots/pc_macos_zh-cn_3.png" width="45%">&nbsp;
  <img src="screen_shots/pc_macos_zh-cn_4.png" width="45%">
</p>
<p align="center">
  <img src="screen_shots/pc_macos_zh-cn_5.png" width="45%">
</p>

### Android - English

<p align="center">
  <img src="screen_shots/app_android_en_1.jpg" width="22%">&nbsp;
  <img src="screen_shots/app_android_en_2.jpg" width="22%">&nbsp;
  <img src="screen_shots/app_android_en_3.jpg" width="22%">&nbsp;
  <img src="screen_shots/app_android_en_4.jpg" width="22%">
</p>

### Android - 中文

<p align="center">
  <img src="screen_shots/app_android_zh-ch_1.jpg" width="18%">&nbsp;
  <img src="screen_shots/app_android_zh-ch_2.jpg" width="18%">&nbsp;
  <img src="screen_shots/app_android_zh-ch_3.jpg" width="18%">&nbsp;
  <img src="screen_shots/app_android_zh-ch_4.jpg" width="18%">&nbsp;
  <img src="screen_shots/app_android_zh-ch_5.jpg" width="18%">
</p>

## Architecture / 架构

```
┌──────────────────────────────────────────────────────────┐
│                       Clients / 客户端                    │
├────────────────┬───────────────┬──────────────────────────┤
│  Vue 3 Web     │  Vue 2 Admin  │  Flutter App             │
│  Element Plus  │  Element UI   │  Android / iOS           │
│  Port 3000     │  Port 9527    │  Windows / macOS / Linux │
└───────┬────────┴───────┬───────┴────────┬────────────────┘
        │                │                │
        └────────────────┴────────────────┘
                         │  HTTP
                   ┌─────▼──────┐
                   │   Nginx    │  Production reverse proxy
                   └─────┬──────┘
                         │
            ┌────────────▼────────────┐
            │  FastAPI Backend        │  Port 8000
            │  /api/admin/* (JWT)     │
            │  /api/web/*             │
            │  /api/chat (ADK Agent)  │
            └─────┬──────────┬────────┘
                  │          │
          ┌───────▼───┐  ┌──▼──────────┐
          │   MySQL   │  │ FAISS Vector │
          └───────────┘  └──────────────┘
                  │
          ┌───────▼────────────┐
          │  External AI APIs  │
          │  OpenAI Embeddings │
          │  Google Gemini ADK │
          └────────────────────┘
```

## Tech Stack / 技术栈

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI, SQLAlchemy, LangChain, FAISS, Google ADK |
| **Database** | MySQL 8.0+ |
| **Admin** | Vue 2, Element UI, Vuex, vue-element-admin |
| **Web** | Vue 3, Vite, Element Plus, Pinia |
| **App** | Flutter, Riverpod, Dio, GoRouter |
| **Deployment** | Nginx, Systemd |

## Project Structure / 项目结构

```
pool_ai_knowledge/
├── backend/        # Python FastAPI backend / Python FastAPI 后端
├── admin/          # Vue 2 admin dashboard / Vue 2 管理后台
├── web/            # Vue 3 web frontend / Vue 3 Web 前端
├── app/            # Flutter cross-platform app / Flutter 跨平台应用
├── deploy.sh       # One-click deployment script / 一键部署脚本
└── README.md
```

## Backend / 后端

Built with **FastAPI** and provides RESTful APIs for all clients.

基于 **FastAPI** 构建，为所有客户端提供 RESTful API。

**Key features / 核心功能：**
- JWT authentication for admin APIs / 管理端 API 的 JWT 认证
- RAG pipeline: MySQL posts → OpenAI Embeddings → FAISS → Gemini synthesis / RAG 流水线：MySQL 文章 → OpenAI 向量化 → FAISS 检索 → Gemini 生成
- Google ADK agent integration (calculator, time, text, search, knowledge agents) / Google ADK 智能体集成
- Unified response format (`{"code": 0, "data": ..., "message": "success"}`) / 统一响应格式

**Setup / 启动：**

```bash
cd backend
cp .env.example .env   # Configure DATABASE_URL, OPENAI_API_KEY, GOOGLE_API_KEY
pip install -r requirements.txt
python init_db.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Admin Dashboard / 管理后台

Built with **Vue 2** + **Element UI** based on the vue-element-admin template.

基于 **Vue 2** + **Element UI** 构建，使用 vue-element-admin 模板。

**Key features / 核心功能：**
- Post CRUD with Markdown editor / 文章增删改查，支持 Markdown 编辑器
- API key management / API 密钥管理
- Role-based access control (admin / editor) / 基于角色的访问控制

**Setup / 启动：**

```bash
cd admin
npm install
npm run dev    # http://localhost:9527
```

## Web Frontend / Web 前端

Built with **Vue 3** + **Vite** + **Element Plus**.

基于 **Vue 3** + **Vite** + **Element Plus** 构建。

**Key features / 核心功能：**
- Post browsing and search / 文章浏览与搜索
- AI chat interface (knowledge-based Q&A) / AI 对话界面（基于知识库问答）
- Internationalization support / 国际化支持

**Setup / 启动：**

```bash
cd web
npm install
npm run dev    # http://localhost:3000
```

## Cross-Platform App / 跨平台应用

Built with **Flutter**, supporting Android, iOS, Windows, macOS, and Linux from a single codebase.

基于 **Flutter** 构建，通过单一代码库支持 Android、iOS、Windows、macOS 和 Linux。

**Key features / 核心功能：**
- Post browsing with Markdown rendering / 文章浏览，支持 Markdown 渲染
- AI chat / AI 对话
- Desktop window management (1200x800 default) / 桌面窗口管理
- Localization support / 本地化支持

**Setup / 启动：**

```bash
cd app
flutter pub get
flutter run    # Select target platform
```

## Deployment / 部署

A one-click deployment script is provided for Linux servers (Ubuntu/Debian/CentOS/RHEL).

提供一键部署脚本，支持 Linux 服务器（Ubuntu/Debian/CentOS/RHEL）。

```bash
chmod +x deploy.sh
./deploy.sh
```

The script automatically installs MySQL, Node.js, Python, and Nginx, then builds and deploys all services.

该脚本自动安装 MySQL、Node.js、Python 和 Nginx，然后构建并部署所有服务。

## License / 许可证

Open Source / 开源

## Contributing / 贡献

Contributions are welcome! Feel free to submit issues and pull requests.

欢迎贡献！请随时提交 Issue 和 Pull Request。
