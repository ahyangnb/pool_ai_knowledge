# Backend API

FastAPI backend for Pool AI Knowledge Base with Google ADK (Agent Development Kit) integration.
带有 Google ADK（代理开发工具包）集成的 Pool AI 知识库 FastAPI 后端。

## Setup / 设置

1. Install dependencies / 安装依赖:
```bash
pip install -r requirements.txt
```

2. Set up environment variables / 设置环境变量:
Create a `.env` file in the project root / 在项目根目录创建 `.env` 文件:
```bash
GOOGLE_API_KEY=your_api_key_here
```

You can get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey).
您可以从 [Google AI Studio](https://makersuite.google.com/app/apikey) 获取 API 密钥。

3. Run the server / 运行服务器:
```bash
python main.py
```

Or with uvicorn directly / 或直接使用 uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation / API 文档

Once running, visit / 运行后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ADK Agents / ADK 代理

This project includes several pre-configured ADK agents with different capabilities:
此项目包含多个具有不同功能的预配置 ADK 代理：

### Available Agents / 可用代理

1. **calculator** - Performs mathematical calculations / 执行数学计算
2. **time** - Provides current time information / 提供当前时间信息
3. **text** - Processes and formats text / 处理和格式化文本
4. **search** - Searches the web using Google Search / 使用 Google 搜索搜索网络
5. **multi** - Multi-tool agent with all capabilities / 具有所有功能的多工具代理

### API Endpoints / API 端点

#### List Available Agents / 列出可用代理
```bash
GET /api/agents
```

#### Chat with an Agent / 与代理聊天
```bash
POST /api/chat
Content-Type: application/json

{
  "agent_name": "calculator",
  "message": "What is 25 * 4?",
  "stream": false
}
```

#### Get Agent Examples / 获取代理示例
```bash
GET /api/examples/{agent_name}
```

#### Get Agent Info / 获取代理信息
```bash
GET /api/agents/{agent_name}/info
```

### Example Usage / 使用示例

#### Using Python / 使用 Python

```python
from adk_agents import get_agent

# Get an agent / 获取代理
agent = get_agent("calculator")

# Run a query / 运行查询
response = await agent.run("What is 25 * 4?")
print(response)

# Stream responses / 流式响应
async for chunk in agent.stream("Calculate 100 / 5"):
    print(chunk, end="")
```

#### Using the API / 使用 API

```bash
# List all agents / 列出所有代理
curl http://localhost:8000/api/agents

# Chat with calculator agent / 与计算器代理聊天
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "calculator",
    "message": "What is 25 * 4?"
  }'

# Get examples / 获取示例
curl http://localhost:8000/api/examples/calculator
```

### Running Examples / 运行示例

Run the example script to see all agents in action:
运行示例脚本以查看所有代理的运行情况：

```bash
python examples.py
```

This will demonstrate:
这将演示：
- Calculator agent usage / 计算器代理用法
- Time agent usage / 时间代理用法
- Text processing agent usage / 文本处理代理用法
- Search agent usage / 搜索代理用法
- Multi-tool agent usage / 多工具代理用法
- Streaming responses / 流式响应

## Custom Tools / 自定义工具

The project includes several custom tools:
项目包含多个自定义工具：

- `calculate(expression)` - Evaluates mathematical expressions / 评估数学表达式
- `get_current_time(timezone)` - Gets current time / 获取当前时间
- `format_text(text, format_type)` - Formats text / 格式化文本
- `word_count(text)` - Counts words and characters / 统计单词和字符

You can create your own agents with these tools or add new custom tools.
您可以使用这些工具创建自己的代理或添加新的自定义工具。

## Project Structure / 项目结构

```
backend/
├── main.py              # FastAPI application / FastAPI 应用程序
├── adk_agents.py        # ADK agent definitions / ADK 代理定义
├── examples.py          # Usage examples / 使用示例
├── requirements.txt     # Dependencies / 依赖项
└── README.md           # This file / 本文件
```
