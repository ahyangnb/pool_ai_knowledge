#!/usr/bin/env bash
# ============================================================
# Pool AI Knowledge - Full Stack Deployment Script
# Deploys: Backend (FastAPI) + Frontend (Vue 3) + Admin (Vue 2) + Nginx
# Supports: Ubuntu 20.04+, Debian 11+, CentOS 8+ / RHEL 8+
#
# Usage:
#   chmod +x deploy.sh
#   sudo ./deploy.sh                # Full install (MySQL + Node + Nginx + app)
#   sudo ./deploy.sh --app-only     # Skip MySQL install (use existing DB)
#   sudo ./deploy.sh --backend-only # Backend only, no frontend/nginx
# ============================================================

set -euo pipefail

# -------------------- Configuration --------------------
APP_NAME="pool_ai_knowledge"
APP_DIR="/opt/${APP_NAME}"
APP_USER="poolai"
PYTHON_MIN="3.10"
VENV_DIR="${APP_DIR}/backend/venv"
SERVICE_NAME="${APP_NAME}"
API_PORT=8000
FRONTEND_DIR="${APP_DIR}/frontend"
ADMIN_DIR="${APP_DIR}/admin"
NGINX_CONF="/etc/nginx/sites-available/${APP_NAME}"
DOMAIN="_"  # Default: listen on all server names

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; }
step() { echo -e "\n${CYAN}========== $* ==========${NC}"; }

# -------------------- Pre-checks --------------------

if [[ $EUID -ne 0 ]]; then
    err "This script must be run as root (use sudo)"
    exit 1
fi

APP_ONLY=false
BACKEND_ONLY=false
for arg in "$@"; do
    case "$arg" in
        --app-only)     APP_ONLY=true ;;
        --backend-only) BACKEND_ONLY=true ;;
    esac
done

if [[ "$APP_ONLY" == true ]]; then
    log "Running in app-only mode (skipping MySQL installation)"
fi
if [[ "$BACKEND_ONLY" == true ]]; then
    log "Running in backend-only mode (skipping frontend & Nginx)"
fi

# Detect package manager
if command -v apt-get &>/dev/null; then
    PKG_MGR="apt"
elif command -v dnf &>/dev/null; then
    PKG_MGR="dnf"
elif command -v yum &>/dev/null; then
    PKG_MGR="yum"
else
    err "Unsupported package manager. Please use Ubuntu/Debian or CentOS/RHEL."
    exit 1
fi

log "Detected package manager: ${PKG_MGR}"

# Locate project root (where this script lives)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ==================== 1. System Dependencies ====================
step "1/9 Installing system dependencies"

if [[ "$PKG_MGR" == "apt" ]]; then
    apt-get update -qq
    apt-get install -y -qq python3 python3-venv python3-pip python3-dev \
        build-essential libffi-dev libssl-dev curl git rsync
elif [[ "$PKG_MGR" == "dnf" || "$PKG_MGR" == "yum" ]]; then
    $PKG_MGR install -y python3 python3-devel python3-pip \
        gcc gcc-c++ libffi-devel openssl-devel curl git rsync
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    log "Python ${PYTHON_VERSION} OK (>= ${PYTHON_MIN})"
else
    err "Python >= ${PYTHON_MIN} is required, found ${PYTHON_VERSION}"
    exit 1
fi

# ==================== 2. MySQL (optional) ====================
step "2/9 MySQL database"

DB_URL=""
DB_PASSWORD=""

if [[ "$APP_ONLY" == false ]]; then
    if command -v mysql &>/dev/null; then
        warn "MySQL is already installed, skipping installation"
    else
        log "Installing MySQL Server..."
        if [[ "$PKG_MGR" == "apt" ]]; then
            apt-get install -y -qq mysql-server mysql-client
            systemctl enable mysql
            systemctl start mysql
        elif [[ "$PKG_MGR" == "dnf" || "$PKG_MGR" == "yum" ]]; then
            $PKG_MGR install -y mysql-server
            systemctl enable mysqld
            systemctl start mysqld
        fi
        log "MySQL installed and started"
    fi

    log "Setting up MySQL database..."
    DB_PASSWORD=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 16)

    mysql -u root <<EOF || warn "Database may already exist, continuing..."
CREATE DATABASE IF NOT EXISTS ${APP_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${APP_NAME}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${APP_NAME}.* TO '${APP_NAME}'@'localhost';
FLUSH PRIVILEGES;
EOF

    DB_URL="mysql+pymysql://${APP_NAME}:${DB_PASSWORD}@localhost:3306/${APP_NAME}?charset=utf8mb4"
    log "Database ready: ${APP_NAME}"
else
    log "Skipping MySQL installation (--app-only)"
fi

# ==================== 3. Application User ====================
step "3/9 Application user"

if id "${APP_USER}" &>/dev/null; then
    log "User ${APP_USER} already exists"
else
    useradd -r -m -d /home/${APP_USER} -s /bin/bash ${APP_USER}
    log "Created system user: ${APP_USER}"
fi

# ==================== 4. Deploy Files ====================
step "4/9 Deploying application files"

mkdir -p "${APP_DIR}/backend" "${FRONTEND_DIR}" "${ADMIN_DIR}"

if [[ "${PROJECT_ROOT}" != "${APP_DIR}" ]]; then
    # Copy backend
    rsync -a --exclude='venv' --exclude='__pycache__' --exclude='.env' \
        --exclude='*.pyc' --exclude='.git' --exclude='.cursor' --exclude='.claude' \
        "${PROJECT_ROOT}/backend/" "${APP_DIR}/backend/"
    log "Backend files copied"

    # Copy frontend source (for building)
    if [[ "$BACKEND_ONLY" == false && -d "${PROJECT_ROOT}/front_end" ]]; then
        rsync -a --exclude='node_modules' --exclude='dist' \
            "${PROJECT_ROOT}/front_end/" "${APP_DIR}/front_end_src/"
        log "Frontend source copied"
    fi

    # Copy admin dist (pre-built)
    if [[ "$BACKEND_ONLY" == false && -d "${PROJECT_ROOT}/admin/dist" ]]; then
        rsync -a "${PROJECT_ROOT}/admin/dist/" "${ADMIN_DIR}/"
        log "Admin dashboard copied (pre-built)"
    fi
else
    log "Already running from ${APP_DIR}, skipping copy"
fi

# ==================== 5. Python Backend ====================
step "5/9 Python backend setup"

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

pip install --upgrade pip -q
pip install -r "${APP_DIR}/backend/requirements.txt" -q
pip install 'bcrypt==4.0.1' -q

log "Python dependencies installed"

# ==================== 6. Frontend Build ====================
if [[ "$BACKEND_ONLY" == false ]]; then
    step "6/9 Building frontend"

    # Install Node.js if not present
    if ! command -v node &>/dev/null; then
        log "Installing Node.js 18..."
        if [[ "$PKG_MGR" == "apt" ]]; then
            curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
            apt-get install -y -qq nodejs
        elif [[ "$PKG_MGR" == "dnf" || "$PKG_MGR" == "yum" ]]; then
            curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
            $PKG_MGR install -y nodejs
        fi
        log "Node.js $(node -v) installed"
    else
        log "Node.js $(node -v) already installed"
    fi

    # Build frontend
    if [[ -d "${APP_DIR}/front_end_src" ]]; then
        cd "${APP_DIR}/front_end_src"
        npm install --silent 2>/dev/null || npm install
        npm run build
        # Copy build output to serve directory
        if [[ -d "dist" ]]; then
            cp -r dist/* "${FRONTEND_DIR}/"
            log "Frontend built and deployed"
        else
            warn "Frontend build did not produce dist/, skipping"
        fi
        cd "${APP_DIR}"
    else
        warn "No frontend source found, skipping build"
    fi
else
    step "6/9 Skipping frontend (--backend-only)"
fi

# ==================== 7. Environment Configuration ====================
step "7/9 Environment configuration"

ENV_FILE="${APP_DIR}/backend/.env"

if [[ -f "${ENV_FILE}" ]]; then
    warn ".env file already exists at ${ENV_FILE}, skipping generation"
else
    SECRET_KEY=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)

    if [[ -n "${DB_URL}" ]]; then
        DATABASE_URL="${DB_URL}"
    else
        DATABASE_URL="mysql+pymysql://root:password@localhost:3306/${APP_NAME}?charset=utf8mb4"
        warn "Using placeholder DATABASE_URL — please edit ${ENV_FILE}"
    fi

    cat > "${ENV_FILE}" <<ENVEOF
# Pool AI Knowledge - Environment Configuration
# Generated by deploy.sh on $(date -Iseconds)

# Database
DATABASE_URL=${DATABASE_URL}

# API Keys — configure here or via admin panel
# Get your OpenAI key:  https://platform.openai.com/api-keys
# Get your Google key:  https://aistudio.google.com/apikey
GOOGLE_API_KEY=
OPENAI_API_KEY=

# JWT Secret
SECRET_KEY=${SECRET_KEY}

# Server
API_HOST=0.0.0.0
API_PORT=${API_PORT}
DEBUG=False
ENVEOF

    chmod 600 "${ENV_FILE}"
    log ".env created at ${ENV_FILE}"
fi

# ==================== 8. Initialize Database ====================
step "8/9 Database initialization"

cd "${APP_DIR}/backend"
"${VENV_DIR}/bin/python" init_db.py
log "Database tables and seed data initialized"

# ==================== 9. Systemd + Nginx ====================
step "9/9 Services setup"

# --- Systemd service for backend ---
log "Creating systemd service..."

cat > /etc/systemd/system/${SERVICE_NAME}.service <<SVCEOF
[Unit]
Description=Pool AI Knowledge API Server
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}/backend
Environment="PATH=${VENV_DIR}/bin:/usr/bin:/bin"
EnvironmentFile=${APP_DIR}/backend/.env
ExecStart=${VENV_DIR}/bin/uvicorn main:app --host 127.0.0.1 --port ${API_PORT} --workers 2
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

# --- Nginx reverse proxy + static files ---
if [[ "$BACKEND_ONLY" == false ]]; then
    # Install Nginx if not present
    if ! command -v nginx &>/dev/null; then
        log "Installing Nginx..."
        if [[ "$PKG_MGR" == "apt" ]]; then
            apt-get install -y -qq nginx
        elif [[ "$PKG_MGR" == "dnf" || "$PKG_MGR" == "yum" ]]; then
            $PKG_MGR install -y nginx
        fi
    fi

    log "Configuring Nginx..."

    cat > "${NGINX_CONF}" <<NGXEOF
server {
    listen 80;
    server_name ${DOMAIN};

    # Frontend (Vue 3)
    root ${FRONTEND_DIR};
    index index.html;

    # API — reverse proxy to FastAPI backend
    location /api/ {
        proxy_pass http://127.0.0.1:${API_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    # Swagger docs
    location /docs {
        proxy_pass http://127.0.0.1:${API_PORT};
        proxy_set_header Host \$host;
    }
    location /openapi.json {
        proxy_pass http://127.0.0.1:${API_PORT};
    }
    location /redoc {
        proxy_pass http://127.0.0.1:${API_PORT};
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:${API_PORT};
    }

    # Admin dashboard
    location /admin/ {
        alias ${ADMIN_DIR}/;
        index index.html;
        try_files \$uri \$uri/ /admin/index.html;
    }

    # Frontend SPA fallback
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Static file caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
NGXEOF

    # Enable site
    if [[ -d /etc/nginx/sites-enabled ]]; then
        ln -sf "${NGINX_CONF}" /etc/nginx/sites-enabled/${APP_NAME}
        # Remove default site if it conflicts
        rm -f /etc/nginx/sites-enabled/default
    elif [[ -d /etc/nginx/conf.d ]]; then
        # CentOS/RHEL style
        cp "${NGINX_CONF}" /etc/nginx/conf.d/${APP_NAME}.conf
    fi

    nginx -t && log "Nginx configuration OK" || err "Nginx config test failed!"
    systemctl enable nginx
    systemctl reload nginx || systemctl start nginx
    log "Nginx configured and running"
fi

# Fix ownership & start backend
chown -R ${APP_USER}:${APP_USER} "${APP_DIR}"
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}
log "Backend service started"

# ==================== Summary ====================
SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "=============================================="
echo -e "${GREEN}  Pool AI Knowledge - Deployment Complete!${NC}"
echo "=============================================="
echo ""
if [[ "$BACKEND_ONLY" == false ]]; then
echo "  Website          : http://${SERVER_IP}"
echo "  Admin panel      : http://${SERVER_IP}/admin/"
fi
echo "  API              : http://${SERVER_IP}:${API_PORT}"
echo "  API Docs         : http://${SERVER_IP}:${API_PORT}/docs"
echo ""
echo "  Default admin credentials:"
echo "    Username : admin"
echo "    Password : admin123456"
echo ""
if [[ -n "${DB_PASSWORD}" ]]; then
echo "  MySQL credentials:"
echo "    Database : ${APP_NAME}"
echo "    User     : ${APP_NAME}"
echo "    Password : ${DB_PASSWORD}"
echo ""
fi
echo "  Key directories:"
echo "    Backend  : ${APP_DIR}/backend/"
echo "    Frontend : ${FRONTEND_DIR}/"
echo "    Admin    : ${ADMIN_DIR}/"
echo "    Env file : ${APP_DIR}/backend/.env"
echo ""
echo "  Manage services:"
echo "    sudo systemctl status|restart|stop ${SERVICE_NAME}"
echo "    sudo systemctl status|restart|stop nginx"
echo "    sudo journalctl -u ${SERVICE_NAME} -f"
echo ""
echo "  Next steps:"
echo "    1. Configure API keys (see below)"
echo "    2. Change the default admin password"
echo "    3. Add your knowledge base content"
echo ""
echo "  Configure API keys (choose one method):"
echo "    Method A: Edit ${APP_DIR}/backend/.env"
echo "      OPENAI_API_KEY=sk-xxxx"
echo "      GOOGLE_API_KEY=AIzaSy-xxxx"
echo "      Then: sudo systemctl restart ${SERVICE_NAME}"
echo ""
echo "    Method B: Use admin panel"
echo "      Login -> API Key Management -> Add keys"
echo ""
echo -e "${YELLOW}  IMPORTANT: Change the default admin password!${NC}"
echo ""
