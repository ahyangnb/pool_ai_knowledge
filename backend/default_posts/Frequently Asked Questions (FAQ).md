---
tags: FAQ,troubleshooting,help
language: en
---

## Frequently Asked Questions (FAQ)

### Deployment & Installation

**Q: Which operating systems are supported?**

A: The deployment script supports:
- Ubuntu 20.04+
- Debian 11+
- CentOS 8+ / RHEL 8+

Windows Server is not directly supported, but you can run a development environment on Windows via WSL2.

---

**Q: Can I deploy with Docker?**

A: Docker images are not yet provided. We recommend using the `deploy.sh` script for direct deployment. Docker support is planned for a future release.

---

**Q: The website is not accessible after deployment?**

A: Follow these troubleshooting steps:

1. Check if the backend service is running:
```bash
sudo systemctl status pool_ai_knowledge
```

2. Check if Nginx is running:
```bash
sudo systemctl status nginx
```

3. Ensure the firewall allows ports 80 and 8000:
```bash
# Ubuntu/Debian
sudo ufw allow 80
sudo ufw allow 8000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

4. Check backend logs:
```bash
sudo journalctl -u pool_ai_knowledge -n 50
```

---

### Search & RAG

**Q: Search results are irrelevant or empty?**

A: Possible causes:

1. **OpenAI API Key not configured**: Semantic search requires OpenAI embeddings
2. **Knowledge base is empty**: Make sure you have added articles
3. **Articles are too brief**: More detailed, well-structured content yields better results
4. **Vector index not updated**: Restart the service to rebuild the index
```bash
sudo systemctl restart pool_ai_knowledge
```

---

**Q: Search is very slow?**

A: FAISS vector search typically completes in milliseconds. If it's slow:

1. High latency to OpenAI API — check network connectivity
2. Too many articles (>10,000) — consider optimizing the FAISS index type
3. Insufficient server memory — check available RAM

---

### AI Chat

**Q: AI chat is not responding or returns errors?**

A: Please check:

1. **Is the Google API Key valid?** Verify at [Google AI Studio](https://aistudio.google.com/)
2. **Network connectivity**: Can the server reach Google API?
```bash
curl -s https://generativelanguage.googleapis.com/ -o /dev/null -w "%{http_code}"
```
3. **Check error logs**:
```bash
sudo journalctl -u pool_ai_knowledge -n 100 | grep -i error
```

---

**Q: AI responses are unrelated to my knowledge base?**

A: Make sure you are using the `knowledge` agent. This agent retrieves content from the knowledge base before answering. Other agents (calculator, time, etc.) do not query the knowledge base.

---

**Q: How do I switch AI models?**

A: Go to the "Model Settings" page in the admin panel and select a new model:
- `gemini-2.0-flash` — Fast and efficient (default)
- `gemini-2.0-flash-lite` — Lightweight
- `gemini-2.5-flash-preview` — Latest preview version
- `gemini-2.5-pro-preview` — Most capable

---

### Admin Panel

**Q: I forgot my admin password?**

A: Reset it directly in the database:

```bash
# Connect to MySQL
mysql -u root pool_ai_knowledge

# Reset to admin123456 (bcrypt hash)
UPDATE admin_users
SET password_hash = '$2b$12$NsHUq2/S42CBqax/GHGUQOFSq3V6a9/KYbsItoKkcUFFDlhttAv2W'
WHERE username = 'admin';
```

---

**Q: How do I add more admin users?**

A: Log in as a super admin, then go to "Admin Management" in the admin panel to add new administrators.

---

**Q: Why are API keys masked in the admin panel?**

A: For security, API key values are masked and only display the first 4 and last 4 characters, e.g., `sk-7x...B2mQ`.

---

### Content & Articles

**Q: What format do articles support?**

A: Article content fully supports **Markdown**, including:
- Headings, paragraphs, lists
- Code blocks (with syntax highlighting)
- Tables
- Blockquotes
- Links and images
- Bold, italic, and other inline styles

---

**Q: How do I bulk import articles?**

A: Two methods are available:

1. **Via API**:
```bash
curl -X POST http://localhost:8000/api/admin/posts \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Article Title",
    "content": "Markdown content here",
    "tags": ["tag1", "tag2"],
    "language": "en"
  }'
```

2. **Via default posts directory**: Place `.md` files in `backend/default_posts/` and restart the service — they will be imported automatically.

---

**Q: Deleted articles still appear in search?**

A: Deleting an article triggers a RAG vector index update. If it still appears, restart the service to force a full rebuild:
```bash
sudo systemctl restart pool_ai_knowledge
```

---

### Performance & Maintenance

**Q: The service suddenly becomes slow or crashes?**

A: Troubleshooting steps:

1. Check server resources:
```bash
free -h     # Memory
df -h       # Disk
top         # CPU
```

2. Check MySQL:
```bash
sudo systemctl status mysql
```

3. Check application logs:
```bash
sudo journalctl -u pool_ai_knowledge -n 200
```

---

**Q: How do I back up my data?**

A: Regularly back up the MySQL database:

```bash
# Backup
mysqldump -u root pool_ai_knowledge > backup_$(date +%Y%m%d).sql

# Restore
mysql -u root pool_ai_knowledge < backup_20240101.sql
```

Also back up the `.env` configuration file.
