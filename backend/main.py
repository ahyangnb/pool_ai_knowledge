from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from google.adk import Runner
from google.adk.runners import types as runner_types
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from adk_agents import (
    get_agent, 
    list_agents, 
    example_calculator_usage,
    example_search_usage,
    example_multi_tool_usage
)
from admin_api import router as admin_router
from web_api import router as web_router
from database import init_db

app = FastAPI(
    title="Pool AI Knowledge API",
    description="AI Knowledge Base API with Google ADK Agents, Admin Panel, and Web APIs",
    version="0.2.0"
)

# Include routers
app.include_router(admin_router)
app.include_router(web_router)

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
    """Root endpoint"""
    return {
        "message": "Welcome to Pool AI Knowledge API",
        "description": "AI Knowledge Base API with Google ADK Agents, Admin Panel, and Web APIs",
        "version": "0.2.0",
        "endpoints": {
            "agents": "/api/agents",
            "chat": "/api/chat",
            "examples": "/api/examples/{agent_name}",
            "admin": "/api/admin",
            "web": "/api/web",
            "docs": "/docs"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")


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


# Global runner instances for each agent / 每个代理的全局运行器实例
_agent_runners: dict = {}
_session_service = InMemorySessionService()


def get_runner(agent_name: str) -> Optional[Runner]:
    """
    Get or create a runner for an agent / 获取或创建代理的运行器
    
    Args:
        agent_name: Name of the agent / 代理名称
    
    Returns:
        Runner instance or None / 运行器实例或 None
    """
    if agent_name not in _agent_runners:
        agent = get_agent(agent_name)
        if not agent:
            return None
        # Use "agents" as app_name to match where agents are loaded from / 使用 "agents" 作为 app_name 以匹配代理加载位置
        _agent_runners[agent_name] = Runner(
            app_name="agents",
            agent=agent,
            session_service=_session_service
        )
    return _agent_runners[agent_name]


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
        # Get agent / 获取代理
        agent = get_agent(request.agent_name)
        if not agent:
            raise HTTPException(
                status_code=500,
                detail="Failed to get agent"
            )
        
        # Create a fresh runner for each request to ensure session service is properly linked / 为每个请求创建新的运行器以确保会话服务正确链接
        # This avoids potential threading issues with shared runners / 这避免了共享运行器的潜在线程问题
        runner = Runner(
            app_name="agents",
            agent=agent,
            session_service=_session_service
        )
        
        # Create Content object from message / 从消息创建 Content 对象
        content = runner_types.Content(parts=[{"text": request.message}])
        
        # Run the agent / 运行代理
        # Use a fixed session ID per agent for simplicity / 为简单起见，每个代理使用固定的会话 ID
        # In production, you might want to use user-specific sessions / 在生产环境中，您可能希望使用用户特定的会话
        session_id = f"api_{request.agent_name}"
        user_id = "api_user"
        
        # Always create session first to ensure it exists / 始终先创建会话以确保它存在
        # Directly create session (will not fail if already exists) / 直接创建会话（如果已存在则不会失败）
        try:
            _session_service.create_session_sync(
                user_id=user_id,
                session_id=session_id,
                app_name="agents"
            )
        except Exception as create_error:
            # If creation fails, try to get existing session / 如果创建失败，尝试获取现有会话
            try:
                _session_service.get_session_sync(
                    user_id=user_id,
                    session_id=session_id,
                    app_name="agents"
                )
            except Exception:
                # If both fail, raise error / 如果两者都失败，抛出错误
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create or get session: {str(create_error)}"
                )
        
        # Run the agent / 运行代理
        # Use asyncio.to_thread to run sync runner.run() in a separate thread / 使用 asyncio.to_thread 在单独线程中运行同步 runner.run()
        # This ensures the session service is accessible in the thread / 这确保会话服务在线程中可访问
        import asyncio
        
        def run_agent_sync():
            """Run agent synchronously in thread / 在线程中同步运行代理"""
            try:
                # Double-check session exists in thread / 在线程中再次检查会话是否存在
                _session_service.get_session_sync(
                    user_id=user_id,
                    session_id=session_id,
                    app_name="agents"
                )
            except Exception as e:
                raise RuntimeError(f"Session not accessible in thread: {e}")
            
            return list(runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ))
        
        try:
            # Run in thread to avoid blocking / 在线程中运行以避免阻塞
            events = await asyncio.to_thread(run_agent_sync)
            response_text = _extract_response_from_events(events, debug=not request.stream)
        except Exception as run_error:
            # If run fails, try to get more info / 如果运行失败，尝试获取更多信息
            import traceback
            error_details = traceback.format_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Error running agent: {str(run_error)}\nDetails: {error_details[:500]}"
            )
        
        return ChatResponse(
            agent_name=request.agent_name,
            message=request.message,
            response=response_text,
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running agent: {str(e)}"
        )


def _extract_response_from_events(events: List, debug: bool = False) -> str:
    """
    Extract text response from agent events / 从代理事件中提取文本响应
    
    Args:
        events: List of events from agent / 来自代理的事件列表
        debug: Enable debug output / 启用调试输出
    
    Returns:
        Extracted text response / 提取的文本响应
    """
    if not events:
        return "No response generated - no events received from agent"
    
    if debug:
        print(f"[DEBUG] Processing {len(events)} events")
    
    # Method 1: Look for final response event / 方法 1：查找最终响应事件
    for i, event in enumerate(events):
        try:
            if hasattr(event, 'is_final_response') and event.is_final_response():
                if debug:
                    print(f"[DEBUG] Found final response in event {i}")
                
                # Extract text from final response / 从最终响应提取文本
                if hasattr(event, 'content') and event.content:
                    content = event.content
                    if hasattr(content, 'parts') and content.parts:
                        for part in content.parts:
                            if hasattr(part, 'text') and part.text:
                                if debug:
                                    print(f"[DEBUG] Extracted text from final response: {len(part.text)} chars")
                                return part.text
        except Exception as e:
            if debug:
                print(f"[DEBUG] Error checking is_final_response: {e}")
    
    # Method 2: Extract text from all events / 方法 2：从所有事件提取文本
    response_parts = []
    
    for i, event in enumerate(events):
        if debug:
            print(f"[DEBUG] Event {i}: {type(event).__name__}")
        
        # Check for content with text parts / 检查包含文本部分的 content
        if hasattr(event, 'content') and event.content:
            content = event.content
            
            # Check if content has parts / 检查 content 是否有 parts
            if hasattr(content, 'parts') and content.parts:
                for part in content.parts:
                    # Extract text from part / 从 part 提取文本
                    if hasattr(part, 'text') and part.text:
                        response_parts.append(part.text)
                        if debug:
                            print(f"[DEBUG] Found text in part: {part.text[:50]}...")
                    # Skip function calls and responses / 跳过函数调用和响应
                    elif hasattr(part, 'function_call') or hasattr(part, 'function_response'):
                        if debug:
                            print(f"[DEBUG] Skipping function call/response part")
                        continue
            
            # Check if content has text directly / 检查 content 是否直接有 text
            elif hasattr(content, 'text') and content.text:
                response_parts.append(content.text)
                if debug:
                    print(f"[DEBUG] Found text in content: {content.text[:50]}...")
        
        # Check for text attribute directly / 直接检查 text 属性
        elif hasattr(event, 'text') and event.text:
            response_parts.append(event.text)
            if debug:
                print(f"[DEBUG] Found text attribute: {event.text[:50]}...")
    
    # Combine all text parts / 组合所有文本部分
    if response_parts:
        response = '\n'.join(response_parts)
        if debug:
            print(f"[DEBUG] Extracted response length: {len(response)}")
        return response
    
    # Method 3: Return last event as fallback / 方法 3：返回最后一个事件作为后备
    last_event = events[-1]
    if debug:
        print(f"[DEBUG] No text found, checking last event: {type(last_event).__name__}")
    
    # Try to get any text from last event / 尝试从最后一个事件获取任何文本
    if hasattr(last_event, 'content') and last_event.content:
        if hasattr(last_event.content, 'parts') and last_event.content.parts:
            for part in last_event.content.parts:
                if hasattr(part, 'text') and part.text:
                    return part.text
    
    # Final fallback / 最终后备
    return f"No text response found in {len(events)} events. Last event type: {type(last_event).__name__}"


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
