---
tags: FAQ,常见问题,故障排查
language: zh-CN
---

## 常见问题（FAQ）

### 部署与安装

**Q: 部署脚本支持哪些操作系统？**

A: 支持以下 Linux 发行版：
- Ubuntu 20.04+
- Debian 11+
- CentOS 8+ / RHEL 8+

暂不支持 Windows 服务器直接部署，但可以在 Windows 上通过 WSL2 运行开发环境。

---

**Q: 可以使用 Docker 部署吗？**

A: 目前项目没有提供 Docker 镜像，建议使用提供的 `deploy.sh` 脚本直接部署。后续版本计划支持 Docker 部署。

---

**Q: 部署后无法访问网站？**

A: 请按以下步骤排查：

1. 检查后端服务是否运行：
```bash
sudo systemctl status pool_ai_knowledge
```

2. 检查 Nginx 是否运行：
```bash
sudo systemctl status nginx
```

3. 检查防火墙是否放行 80 和 8000 端口：
```bash
# Ubuntu/Debian
sudo ufw allow 80
sudo ufw allow 8000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

4. 检查后端日志：
```bash
sudo journalctl -u pool_ai_knowledge -n 50
```

---

### 搜索与 RAG

**Q: 搜索结果不相关或为空？**

A: 可能的原因：

1. **OpenAI API Key 未配置**：语义搜索依赖 OpenAI 嵌入向量，必须正确配置密钥
2. **知识库为空**：确保已添加文章内容
3. **文章内容太少**：内容越详细、结构化越好，搜索效果越佳
4. **向量索引未更新**：重启服务会自动重建索引
```bash
sudo systemctl restart pool_ai_knowledge
```

---

**Q: 搜索速度很慢？**

A: FAISS 向量检索通常在毫秒级完成，如果很慢，可能是：

1. OpenAI API 网络延迟 — 检查服务器到 OpenAI 的网络连通性
2. 文章数量过多（>10,000）— 考虑优化 FAISS 索引类型
3. 服务器内存不足 — 检查可用内存

---

### AI 对话

**Q: AI 对话没有响应或报错？**

A: 请检查：

1. **Google API Key 是否有效**：在 [Google AI Studio](https://aistudio.google.com/) 验证密钥
2. **网络连通性**：服务器能否访问 Google API
```bash
curl -s https://generativelanguage.googleapis.com/ -o /dev/null -w "%{http_code}"
```
3. **查看错误日志**：
```bash
sudo journalctl -u pool_ai_knowledge -n 100 | grep -i error
```

---

**Q: AI 回答与知识库内容无关？**

A: 确保使用的是 `knowledge` Agent（知识库 Agent）。这个 Agent 会先从知识库检索相关内容再回答。如果使用其他 Agent，则不会检索知识库。

---

**Q: 如何切换 AI 模型？**

A: 在管理后台的「模型设置」页面选择新模型即可。可选模型包括：
- `gemini-2.0-flash` — 快速高效（默认）
- `gemini-2.0-flash-lite` — 更轻量
- `gemini-2.5-flash-preview` — 最新预览版
- `gemini-2.5-pro-preview` — 最强能力

---

### 管理后台

**Q: 忘记管理员密码怎么办？**

A: 可以通过数据库直接重置：

```bash
# 连接 MySQL
mysql -u root pool_ai_knowledge

# 重置为 admin123456（bcrypt hash）
UPDATE admin_users
SET password_hash = '$2b$12$NsHUq2/S42CBqax/GHGUQOFSq3V6a9/KYbsItoKkcUFFDlhttAv2W'
WHERE username = 'admin';
```

---

**Q: 如何添加更多管理员？**

A: 使用超级管理员账号登录后，在管理后台的「管理员管理」页面添加新管理员。

---

**Q: API 密钥在管理后台如何显示？**

A: 出于安全考虑，密钥值会被遮蔽显示，只展示前 4 位和后 4 位字符，例如：`sk-7x...B2mQ`。

---

### 数据与文章

**Q: 文章支持什么格式？**

A: 文章内容完全支持 **Markdown** 格式，包括：
- 标题、段落、列表
- 代码块（支持语法高亮）
- 表格
- 引用
- 链接和图片
- 粗体、斜体等内联样式

---

**Q: 如何批量导入文章？**

A: 目前有两种方式：

1. **通过 API 批量创建**：
```bash
curl -X POST http://localhost:8000/api/admin/posts \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "文章标题",
    "content": "Markdown 内容",
    "tags": ["标签1", "标签2"],
    "language": "zh-CN"
  }'
```

2. **通过默认文章目录**：将 `.md` 文件放入 `backend/default_posts/` 目录，重启服务后自动导入。

---

**Q: 删除文章后搜索还能找到？**

A: 删除文章会触发 RAG 向量索引更新。如果仍然能搜索到，尝试重启服务强制重建索引：
```bash
sudo systemctl restart pool_ai_knowledge
```

---

### 性能与维护

**Q: 服务突然变慢或崩溃？**

A: 排查步骤：

1. 检查服务器资源：
```bash
free -h     # 内存
df -h       # 磁盘
top         # CPU
```

2. 检查 MySQL 连接：
```bash
sudo systemctl status mysql
```

3. 查看应用日志：
```bash
sudo journalctl -u pool_ai_knowledge -n 200
```

---

**Q: 如何备份数据？**

A: 定期备份 MySQL 数据库：

```bash
# 备份数据库
mysqldump -u root pool_ai_knowledge > backup_$(date +%Y%m%d).sql

# 恢复数据库
mysql -u root pool_ai_knowledge < backup_20240101.sql
```

同时建议备份 `.env` 配置文件。
