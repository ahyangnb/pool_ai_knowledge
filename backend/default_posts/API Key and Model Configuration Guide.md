---
tags: API-key,model-config,OpenAI,Google,tutorial
language: en
---

## API Key & Model Configuration

Pool AI Knowledge relies on two external APIs for its core AI capabilities. This guide walks you through obtaining and configuring these keys.

### Which API Keys Do You Need?

| Key | Purpose | Required |
|-----|---------|----------|
| **OpenAI API Key** | Text embedding generation (RAG semantic search) | Yes |
| **Google API Key** | AI chat generation (Gemini models) | Yes |

### Getting an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an OpenAI account
3. Click **"Create new secret key"**
4. Copy the generated key (starts with `sk-`)

> **Note**: OpenAI API is a paid service, but new users typically get free credits. Text embeddings (text-embedding-ada-002) are very affordable at ~$0.1 per million tokens.

### Getting a Google API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Select a GCP project (or create a new one)
5. Copy the generated key (starts with `AIzaSy`)

> **Note**: The Gemini API offers a generous free tier that is usually sufficient for personal and small-scale projects.

### Method 1: Admin Panel (Recommended)

This is the easiest method and requires no server restart.

1. Log in to the admin panel
2. Go to **API Key Management**
3. Click **Add Key**
4. Fill in the details:

**Adding an OpenAI key:**
- Key Type: `openai`
- Key Name: `OpenAI Production` (custom name)
- Key Value: `sk-xxxxxxxxxxxxxxxx`

**Adding a Google key:**
- Key Type: `google`
- Key Name: `Google Gemini` (custom name)
- Key Value: `AIzaSy-xxxxxxxxxxxxxxxx`

5. Keys take effect immediately — **no restart required**

### Method 2: Environment Variables

Edit the `.env` file:

```bash
# Development
nano backend/.env

# Production (after deployment)
sudo nano /opt/pool_ai_knowledge/backend/.env
```

Add or update these lines:

```env
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=AIzaSy-your-google-key-here
```

Then restart the service:

```bash
# Development — just restart uvicorn

# Production
sudo systemctl restart pool_ai_knowledge
```

### Switching AI Models

The default model is `gemini-2.0-flash`. You can change it in the admin panel:

1. Log in to the admin panel
2. Go to **Model Settings**
3. Choose from the available models:

| Model | Characteristics |
|-------|----------------|
| `gemini-2.0-flash` | Fast and efficient, recommended for daily use |
| `gemini-2.0-flash-lite` | Lightweight, faster responses |
| `gemini-2.5-flash-preview` | Latest preview with deep thinking |
| `gemini-2.5-pro-preview` | Most capable, best for complex tasks |

4. Changes take effect immediately

### Verifying Your Configuration

After configuration, verify everything works:

**Test Semantic Search (OpenAI):**
- Enter a question on the frontend search page
- If relevant articles are returned, the OpenAI key is working

**Test AI Chat (Google):**
- Send a message on the frontend chat page
- If you receive an AI response, the Google key is working

**Via API:**

```bash
# Health check
curl http://localhost:8000/health

# Test AI chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "knowledge", "message": "hello"}'
```

### Security Best Practices

1. **Never commit keys to Git** — `.env` is already in `.gitignore`
2. **Rotate keys regularly** — update every 90 days
3. **Use least privilege** — restrict key permissions in OpenAI/Google dashboards
4. **Monitor usage** — check API usage regularly to avoid unexpected charges
5. **Production** — set `.env` file permissions to 600 (owner read/write only)
