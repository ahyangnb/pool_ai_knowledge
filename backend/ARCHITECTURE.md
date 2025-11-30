# Backend Architecture

## Overview

This backend framework provides:
- **Admin APIs**: For managing API keys (OpenAI, Google) and posts
- **Web APIs**: Public endpoints for searching and viewing posts
- **MySQL Database**: Stores posts, API keys, admin users, and system config
- **RAG Integration**: Uses OpenAI embeddings for semantic search

## Database Schema

### Tables

1. **posts**: Stores knowledge base articles
   - id (String, PK)
   - title (String)
   - content (Text)
   - tags (Text, comma-separated)
   - created_at, updated_at (DateTime)
   - is_active (Boolean)

2. **api_keys**: Stores API key configurations
   - id (Integer, PK)
   - key_type (String: 'openai' or 'google')
   - key_name (String)
   - key_value (Text, encrypted in production)
   - is_active (Boolean)
   - created_by (String)
   - description (Text)

3. **admin_users**: Admin user accounts
   - id (Integer, PK)
   - username (String, unique)
   - email (String, unique)
   - password_hash (String)
   - is_active (Boolean)
   - is_super_admin (Boolean)

4. **system_config**: System configuration
   - id (Integer, PK)
   - config_key (String, unique)
   - config_value (Text)
   - description (Text)

## API Endpoints

### Admin APIs (`/api/admin`)

**Authentication:**
- `POST /api/admin/login` - Admin login (returns JWT token)

**API Key Management:**
- `GET /api/admin/api-keys` - List all API keys
- `POST /api/admin/api-keys` - Create new API key
- `GET /api/admin/api-keys/{key_id}` - Get API key by ID
- `PUT /api/admin/api-keys/{key_id}` - Update API key
- `DELETE /api/admin/api-keys/{key_id}` - Delete API key

**Post Management:**
- `GET /api/admin/posts` - List all posts
- `POST /api/admin/posts` - Create new post
- `GET /api/admin/posts/{post_id}` - Get post by ID
- `PUT /api/admin/posts/{post_id}` - Update post
- `DELETE /api/admin/posts/{post_id}` - Delete post

**Admin User Management (Super Admin only):**
- `POST /api/admin/users` - Create admin user

### Web APIs (`/api/web`)

**Public Access (No Authentication):**
- `GET /api/web/posts` - List active posts (paginated)
- `GET /api/web/posts/{post_id}` - Get post by ID
- `POST /api/web/search` - Search posts using RAG
- `GET /api/web/search?query=...&top_k=3` - Search posts (GET method)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

Create a MySQL database:

```sql
CREATE DATABASE pool_ai_knowledge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Update `.env` file:

```bash
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/pool_ai_knowledge?charset=utf8mb4
SECRET_KEY=your-secret-key-for-jwt-tokens
```

### 3. Initialize Database

```bash
python init_db.py
```

This will:
- Create all database tables
- Create a default admin user (username: `admin`, password: `admin123`)

**⚠️ IMPORTANT: Change the default admin password in production!**

### 4. Add API Keys

Login as admin and add API keys:

```bash
# Login
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Add OpenAI API key (use the token from login)
curl -X POST http://localhost:8000/api/admin/api-keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "key_type": "openai",
    "key_name": "OpenAI Production Key",
    "key_value": "sk-...",
    "description": "OpenAI API key for RAG"
  }'

# Add Google API key
curl -X POST http://localhost:8000/api/admin/api-keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "key_type": "google",
    "key_name": "Google API Key",
    "key_value": "your-google-api-key",
    "description": "Google API key for ADK agents"
  }'
```

### 5. Start Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Security Notes

1. **API Keys**: In production, encrypt API keys before storing in database
2. **JWT Secret**: Use a strong, random SECRET_KEY
3. **Password Hashing**: Passwords are hashed using bcrypt
4. **HTTPS**: Use HTTPS in production
5. **CORS**: Configure CORS properly for production

## Architecture Flow

1. **Admin configures API keys** → Stored in MySQL `api_keys` table
2. **Knowledge base loads API keys** → Gets OpenAI key from database for RAG
3. **Admin creates posts** → Stored in MySQL `posts` table
4. **RAG vector store updates** → Automatically when posts are added/updated
5. **Web users search** → Uses RAG to find relevant posts

## Migration from JSON to MySQL

The system automatically loads posts from MySQL. The JSON file (`knowledge_base.json`) is no longer used by default, but can be used as a fallback if `use_mysql=False` is set.

