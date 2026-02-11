---
tags: 部署,Linux,服务器,Nginx
language: zh-CN
---

## Linux 服务器一键部署

Pool AI Knowledge 提供了自动化部署脚本，支持 Ubuntu 20.04+、Debian 11+、CentOS 8+ / RHEL 8+。

### 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 1 核 | 2 核+ |
| 内存 | 1 GB | 2 GB+ |
| 磁盘 | 10 GB | 20 GB+ |
| 系统 | Ubuntu 20.04 / Debian 11 / CentOS 8 | Ubuntu 22.04 |
| Python | 3.10+ | 3.11+ |
| MySQL | 5.7+ | 8.0+ |

### 一键部署

```bash
# 1. 将项目上传到服务器
scp -r pool_ai_knowledge/ user@your-server:/tmp/

# 2. 登录服务器
ssh user@your-server

# 3. 运行部署脚本
cd /tmp/pool_ai_knowledge
chmod +x deploy.sh
sudo ./deploy.sh
```

脚本会自动完成以下工作：

1. 安装系统依赖（Python、Node.js、MySQL、Nginx）
2. 创建专用系统用户 `poolai`
3. 部署后端 API 服务（FastAPI + Uvicorn）
4. 构建并部署前端网站（Vue 3）
5. 部署管理后台（Vue 2 预编译版本）
6. 配置 Nginx 反向代理
7. 创建 Systemd 服务（开机自启）
8. 初始化数据库和默认数据

### 部署模式

```bash
# 完整部署（推荐）
sudo ./deploy.sh

# 仅部署应用，使用已有的 MySQL（跳过 MySQL 安装）
sudo ./deploy.sh --app-only

# 仅部署后端 API（不安装 Nginx 和前端）
sudo ./deploy.sh --backend-only
```

### 部署后的目录结构

```
/opt/pool_ai_knowledge/
├── backend/          # 后端 API
│   ├── .env          # 环境配置（重要！）
│   ├── main.py       # FastAPI 应用入口
│   ├── venv/         # Python 虚拟环境
│   └── ...
├── frontend/         # 前端网站（Nginx 直接服务）
│   └── index.html
└── admin/            # 管理后台（Nginx 直接服务）
    └── index.html
```

### 服务管理

```bash
# 查看后端服务状态
sudo systemctl status pool_ai_knowledge

# 重启后端服务（修改 .env 后需要执行）
sudo systemctl restart pool_ai_knowledge

# 停止服务
sudo systemctl stop pool_ai_knowledge

# 查看实时日志
sudo journalctl -u pool_ai_knowledge -f

# 重启 Nginx
sudo systemctl restart nginx
```

### 访问地址

部署完成后，可以通过以下地址访问：

| 服务 | 地址 |
|------|------|
| 前端网站 | `http://服务器IP/` |
| 管理后台 | `http://服务器IP/admin/` |
| API 接口 | `http://服务器IP:8000/` |
| API 文档 | `http://服务器IP:8000/docs` |

### 配置域名和 HTTPS

如果需要使用域名访问，编辑 Nginx 配置：

```bash
sudo nano /etc/nginx/sites-available/pool_ai_knowledge
```

将 `server_name _` 修改为你的域名，例如：

```nginx
server_name example.com www.example.com;
```

使用 Let's Encrypt 免费配置 HTTPS：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

### 更新部署

当代码更新后，重新运行部署脚本即可：

```bash
cd /tmp/pool_ai_knowledge  # 新版本代码目录
sudo ./deploy.sh
```

脚本会保留已有的 `.env` 配置文件，不会覆盖你的自定义设置。
