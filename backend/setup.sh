#!/usr/bin/env bash
# ============================================================
# Pool AI Knowledge - One-click Linux Setup Script
# Supports: Ubuntu 20.04+, Debian 11+, CentOS 8+ / RHEL 8+
#
# Usage:
#   chmod +x setup.sh
#   sudo ./setup.sh            # Full install (MySQL + Python + app)
#   sudo ./setup.sh --app-only # Skip MySQL install (use existing DB)
# ============================================================

set -euo pipefail

# -------------------- Configuration --------------------
APP_NAME="pool_ai_knowledge"
APP_DIR="/opt/${APP_NAME}"
APP_USER="poolai"
PYTHON_MIN="3.10"
VENV_DIR="${APP_DIR}/venv"
SERVICE_NAME="${APP_NAME}"
APP_PORT=8000

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# -------------------- Pre-checks --------------------

if [[ $EUID -ne 0 ]]; then
    err "This script must be run as root (use sudo)"
    exit 1
fi

APP_ONLY=false
if [[ "${1:-}" == "--app-only" ]]; then
    APP_ONLY=true
    log "Running in app-only mode (skipping MySQL installation)"
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

# -------------------- 1. System Dependencies --------------------

log "Installing system dependencies..."

if [[ "$PKG_MGR" == "apt" ]]; then
    apt-get update -qq
    apt-get install -y -qq python3 python3-venv python3-pip python3-dev \
        build-essential libffi-dev libssl-dev curl git
elif [[ "$PKG_MGR" == "dnf" || "$PKG_MGR" == "yum" ]]; then
    $PKG_MGR install -y python3 python3-devel python3-pip \
        gcc gcc-c++ libffi-devel openssl-devel curl git
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
log "Python version: ${PYTHON_VERSION}"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    log "Python version OK (>= ${PYTHON_MIN})"
else
    err "Python >= ${PYTHON_MIN} is required, found ${PYTHON_VERSION}"
    exit 1
fi

# -------------------- 2. MySQL (optional) --------------------

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

    # Create database and user
    log "Setting up MySQL database..."
    DB_PASSWORD=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 16)

    mysql -u root <<EOF || warn "Database may already exist, continuing..."
CREATE DATABASE IF NOT EXISTS ${APP_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${APP_NAME}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${APP_NAME}.* TO '${APP_NAME}'@'localhost';
FLUSH PRIVILEGES;
EOF

    DB_URL="mysql+pymysql://${APP_NAME}:${DB_PASSWORD}@localhost:3306/${APP_NAME}?charset=utf8mb4"
    log "Database created: ${APP_NAME}"
else
    DB_URL=""
    DB_PASSWORD=""
fi

# -------------------- 3. Application User --------------------

if id "${APP_USER}" &>/dev/null; then
    log "User ${APP_USER} already exists"
else
    useradd -r -m -d /home/${APP_USER} -s /bin/bash ${APP_USER}
    log "Created system user: ${APP_USER}"
fi

# -------------------- 4. Deploy Application --------------------

log "Deploying application to ${APP_DIR}..."

mkdir -p "${APP_DIR}"

# Copy project files (excluding venv, __pycache__, .env)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${SCRIPT_DIR}" != "${APP_DIR}" ]]; then
    rsync -a --exclude='venv' --exclude='__pycache__' --exclude='.env' \
        --exclude='*.pyc' --exclude='.git' --exclude='.cursor' --exclude='.claude' \
        "${SCRIPT_DIR}/" "${APP_DIR}/"
    log "Files copied to ${APP_DIR}"
else
    log "Already running from ${APP_DIR}, skipping copy"
fi

# -------------------- 5. Python Virtual Environment --------------------

log "Setting up Python virtual environment..."

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

pip install --upgrade pip -q
pip install -r "${APP_DIR}/requirements.txt" -q
# bcrypt pinned for passlib compatibility
pip install 'bcrypt==4.0.1' -q

log "Python dependencies installed"

# -------------------- 6. Environment Configuration --------------------

ENV_FILE="${APP_DIR}/.env"

if [[ -f "${ENV_FILE}" ]]; then
    warn ".env file already exists, skipping generation"
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
# Generated by setup.sh on $(date -Iseconds)

# Database
DATABASE_URL=${DATABASE_URL}

# API Keys (configure via admin panel or here)
GOOGLE_API_KEY=
OPENAI_API_KEY=

# JWT Secret
SECRET_KEY=${SECRET_KEY}

# Server
API_HOST=0.0.0.0
API_PORT=${APP_PORT}
DEBUG=False
ENVEOF

    chmod 600 "${ENV_FILE}"
    log ".env file created at ${ENV_FILE}"
fi

# -------------------- 7. Initialize Database --------------------

log "Initializing database tables..."

cd "${APP_DIR}"
"${VENV_DIR}/bin/python" init_db.py

log "Database initialized"

# -------------------- 8. Systemd Service --------------------

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
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin:/usr/bin:/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/uvicorn main:app --host 0.0.0.0 --port ${APP_PORT} --workers 2
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

# Fix ownership
chown -R ${APP_USER}:${APP_USER} "${APP_DIR}"

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}

log "Systemd service created and started"

# -------------------- 9. Summary --------------------

echo ""
echo "=========================================="
echo -e "${GREEN}  Pool AI Knowledge - Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "  Application directory : ${APP_DIR}"
echo "  Service name          : ${SERVICE_NAME}"
echo "  API URL               : http://$(hostname -I | awk '{print $1}'):${APP_PORT}"
echo "  API Docs              : http://$(hostname -I | awk '{print $1}'):${APP_PORT}/docs"
echo ""
echo "  Default admin account:"
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
echo "  Manage service:"
echo "    sudo systemctl status  ${SERVICE_NAME}"
echo "    sudo systemctl restart ${SERVICE_NAME}"
echo "    sudo journalctl -u ${SERVICE_NAME} -f"
echo ""
echo "  Configure API keys:"
echo "    Option 1: Edit ${APP_DIR}/.env"
echo "    Option 2: Use admin panel API POST /api/admin/api-keys"
echo ""
echo -e "${YELLOW}  IMPORTANT: Change the default admin password!${NC}"
echo ""
