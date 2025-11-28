from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from adk_agents import (
    get_agent, 
    list_agents, 
    example_calculator_usage,
    example_search_usage,
    example_multi_tool_usage
)

app = FastAPI(
    title="Pool AI Knowledge API",
    description="AI Knowledge Base API with Google ADK Agents / 带有 Google ADK 代理的 AI 知识库 API",
    version="0.1.0"
)

# CORS middleware for Flutter frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Request/Response Models 请求/响应模型 ====================

class ChatRequest(BaseModel):
    """Chat request model / 聊天请求模型"""
    agent_name: str
    message: str
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    """Chat response model / 聊天响应模型"""
    agent_name: str
    message: str
    response: str
    status: str


# ==================== API Endpoints API 端点 ====================

@app.get("/")
async def root():
    """Root endpoint / 根端点"""
    return {
        "message": "Welcome to Pool AI Knowledge API",
        "description": "AI Knowledge Base API with Google ADK Agents",
        "endpoints": {
            "agents": "/api/agents",
            "chat": "/api/chat",
            "examples": "/api/examples/{agent_name}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint / 健康检查端点"""
    return {"status": "healthy"}


@app.get("/api/agents")
async def get_available_agents():
    """
    Get list of available agents / 获取可用代理列表
    
    Returns:
        List of agent names and descriptions / 代理名称和描述列表
    """
    agents = list_agents()
    agent_info = {}
    
    for agent_name in agents:
        agent = get_agent(agent_name)
        if agent:
            agent_info[agent_name] = {
                "name": agent.name,
                "description": agent.description
            }
    
    return {
        "status": "success",
        "agents": agent_info,
        "total": len(agents)
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Chat with an ADK agent / 与 ADK 代理聊天
    
    Args:
        request: Chat request with agent name and message / 包含代理名称和消息的聊天请求
    
    Returns:
        Agent response / 代理响应
    """
    agent = get_agent(request.agent_name)
    
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{request.agent_name}' not found. Available agents: {', '.join(list_agents())}"
        )
    
    try:
        # Run the agent with the user's message / 使用用户消息运行代理
        if request.stream:
            # For streaming, we would need to handle SSE / 对于流式传输，我们需要处理 SSE
            # For now, we'll use regular run / 目前，我们使用常规运行
            response = await agent.run(request.message)
        else:
            response = await agent.run(request.message)
        
        return ChatResponse(
            agent_name=request.agent_name,
            message=request.message,
            response=str(response),
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running agent: {str(e)}"
        )


@app.get("/api/examples/{agent_name}")
async def get_agent_examples(agent_name: str):
    """
    Get example usage for a specific agent / 获取特定代理的示例用法
    
    Args:
        agent_name: Name of the agent / 代理名称
    
    Returns:
        Example usage information / 示例用法信息
    """
    agent = get_agent(agent_name)
    
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found. Available agents: {', '.join(list_agents())}"
        )
    
    # Get examples based on agent type / 根据代理类型获取示例
    example_functions = {
        "calculator": example_calculator_usage,
        "search": example_search_usage,
        "multi": example_multi_tool_usage
    }
    
    if agent_name in example_functions:
        return await example_functions[agent_name]()
    else:
        return {
            "agent": agent_name,
            "description": agent.description,
            "note": "Use /api/chat endpoint to interact with this agent"
        }


@app.get("/api/agents/{agent_name}/info")
async def get_agent_info(agent_name: str):
    """
    Get detailed information about a specific agent / 获取特定代理的详细信息
    
    Args:
        agent_name: Name of the agent / 代理名称
    
    Returns:
        Agent information / 代理信息
    """
    agent = get_agent(agent_name)
    
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found. Available agents: {', '.join(list_agents())}"
        )
    
    return {
        "name": agent.name,
        "description": agent.description,
        "model": agent.model,
        "tools_count": len(agent.tools) if hasattr(agent, 'tools') else 0,
        "tools": [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in agent.tools] if hasattr(agent, 'tools') else []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
