---
tags: API密钥,模型配置,OpenAI,Google,教程
language: zh-CN
---

## API 密钥与模型配置

Pool AI Knowledge 依赖两个外部 API 来提供核心 AI 能力。本文将指导你获取和配置这些密钥。

### 需要哪些 API 密钥？

| 密钥 | 用途 | 是否必须 |
|------|------|----------|
| **OpenAI API Key** | 生成文本嵌入向量（RAG 语义搜索） | 是 |
| **Google API Key** | AI 对话生成（Gemini 模型） | 是 |

### 获取 OpenAI API Key

1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录或注册 OpenAI 账号
3. 点击 **"Create new secret key"**
4. 复制生成的密钥（以 `sk-` 开头）

> **注意**：OpenAI API 是付费服务，新用户通常有免费额度。文本嵌入（text-embedding-ada-002）的费用非常低，每百万 token 约 $0.1。

### 获取 Google API Key

1. 访问 [Google AI Studio](https://aistudio.google.com/apikey)
2. 使用 Google 账号登录
3. 点击 **"Create API Key"**
4. 选择一个 GCP 项目（或创建新项目）
5. 复制生成的密钥（以 `AIzaSy` 开头）

> **注意**：Gemini API 提供免费使用额度，对于个人和小型项目来说通常足够。

### 配置方式一：通过管理后台（推荐）

这是最便捷的方式，无需重启服务。

1. 登录管理后台
2. 进入 **API 密钥管理** 页面
3. 点击 **添加密钥**
4. 填写信息：

**添加 OpenAI 密钥：**
- 密钥类型：`openai`
- 密钥名称：`OpenAI Production`（自定义名称）
- 密钥值：`sk-xxxxxxxxxxxxxxxx`

**添加 Google 密钥：**
- 密钥类型：`google`
- 密钥名称：`Google Gemini`（自定义名称）
- 密钥值：`AIzaSy-xxxxxxxxxxxxxxxx`

5. 保存后密钥立即生效，**无需重启服务**

### 配置方式二：通过环境变量文件

编辑服务器上的 `.env` 文件：

```bash
# 开发环境
nano backend/.env

# 生产环境（部署后）
sudo nano /opt/pool_ai_knowledge/backend/.env
```

添加或修改以下行：

```env
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=AIzaSy-your-google-key-here
```

保存后重启服务：

```bash
# 开发环境
# 重新运行 uvicorn 即可

# 生产环境
sudo systemctl restart pool_ai_knowledge
```

### 切换 AI 模型

系统默认使用 `gemini-2.0-flash` 模型，你可以在管理后台切换：

1. 登录管理后台
2. 进入 **模型设置** 页面
3. 从可用模型列表中选择：

| 模型 | 特点 |
|------|------|
| `gemini-2.0-flash` | 快速高效，推荐日常使用 |
| `gemini-2.0-flash-lite` | 更轻量，响应更快 |
| `gemini-2.5-flash-preview` | 最新预览版，支持深度思考 |
| `gemini-2.5-pro-preview` | 最强能力，适合复杂任务 |

4. 选择后立即生效

### 验证配置

配置完成后，可以通过以下方式验证：

**验证语义搜索（OpenAI）：**
- 在前端搜索页面输入一个问题
- 如果返回相关文章结果，说明 OpenAI 密钥工作正常

**验证 AI 对话（Google）：**
- 在前端聊天页面发送一条消息
- 如果收到 AI 回复，说明 Google 密钥工作正常

**通过 API 验证：**

```bash
# 健康检查
curl http://localhost:8000/health

# 测试 AI 对话
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "knowledge", "message": "你好"}'
```

### 密钥安全建议

1. **不要将密钥提交到 Git 仓库** — `.env` 文件已在 `.gitignore` 中
2. **定期轮换密钥** — 建议每 90 天更新一次
3. **使用最小权限** — 在 OpenAI/Google 后台限制密钥权限
4. **监控用量** — 定期检查 API 用量，避免意外费用
5. **生产环境** — 密钥文件权限设为 600（仅所有者可读写）
