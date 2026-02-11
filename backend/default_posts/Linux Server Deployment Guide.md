---
tags: deployment,Linux,server,Nginx
language: en
---

## One-Click Linux Server Deployment

Pool AI Knowledge provides an automated deployment script supporting Ubuntu 20.04+, Debian 11+, CentOS 8+ / RHEL 8+.

### System Requirements

| Item | Minimum | Recommended |
|------|---------|-------------|
| CPU | 1 core | 2+ cores |
| RAM | 1 GB | 2+ GB |
| Disk | 10 GB | 20+ GB |
| OS | Ubuntu 20.04 / Debian 11 / CentOS 8 | Ubuntu 22.04 |
| Python | 3.10+ | 3.11+ |
| MySQL | 5.7+ | 8.0+ |

### One-Click Deploy

```bash
# 1. Upload the project to your server
scp -r pool_ai_knowledge/ user@your-server:/tmp/

# 2. SSH into the server
ssh user@your-server

# 3. Run the deployment script
cd /tmp/pool_ai_knowledge
chmod +x deploy.sh
sudo ./deploy.sh
```

The script automatically handles:

1. System dependencies (Python, Node.js, MySQL, Nginx)
2. Creates a dedicated system user (`poolai`)
3. Deploys the backend API (FastAPI + Uvicorn)
4. Builds and deploys the frontend (Vue 3)
5. Deploys the admin dashboard (pre-built Vue 2)
6. Configures Nginx reverse proxy
7. Creates a Systemd service (auto-start on boot)
8. Initializes the database with default data

### Deployment Modes

```bash
# Full deployment (recommended)
sudo ./deploy.sh

# App only — use an existing MySQL server
sudo ./deploy.sh --app-only

# Backend only — no frontend or Nginx
sudo ./deploy.sh --backend-only
```

### Directory Structure After Deployment

```
/opt/pool_ai_knowledge/
├── backend/          # Backend API
│   ├── .env          # Environment config (important!)
│   ├── main.py       # FastAPI application entry
│   ├── venv/         # Python virtual environment
│   └── ...
├── frontend/         # Frontend website (served by Nginx)
│   └── index.html
└── admin/            # Admin dashboard (served by Nginx)
    └── index.html
```

### Service Management

```bash
# Check backend service status
sudo systemctl status pool_ai_knowledge

# Restart backend (required after editing .env)
sudo systemctl restart pool_ai_knowledge

# Stop service
sudo systemctl stop pool_ai_knowledge

# View live logs
sudo journalctl -u pool_ai_knowledge -f

# Restart Nginx
sudo systemctl restart nginx
```

### Access URLs

After deployment, access the following:

| Service | URL |
|---------|-----|
| Frontend | `http://SERVER_IP/` |
| Admin Panel | `http://SERVER_IP/admin/` |
| API | `http://SERVER_IP:8000/` |
| API Docs | `http://SERVER_IP:8000/docs` |

### Custom Domain & HTTPS

Edit the Nginx configuration for a custom domain:

```bash
sudo nano /etc/nginx/sites-available/pool_ai_knowledge
```

Change `server_name _` to your domain:

```nginx
server_name example.com www.example.com;
```

Set up free HTTPS with Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

### Updating

When you have new code, simply re-run the deployment script:

```bash
cd /tmp/pool_ai_knowledge  # new version directory
sudo ./deploy.sh
```

The script preserves your existing `.env` configuration and will not overwrite your custom settings.
