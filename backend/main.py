from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from models import R

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


# ==================== Global Exception Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=R.fail(code=exc.status_code, message=exc.detail),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=R.fail(code=500, message=str(exc)),
    )


# ==================== Request/Response Models 请求/响应模型 ====================

class ChatRequest(BaseModel):
    """Chat request model / 聊天请求模型"""
    agent_name: str
    message: str
    post_id: Optional[str] = None
    stream: Optional[bool] = False
    language: Optional[str] = None


class ChatReference(BaseModel):
    """Referenced article in chat response"""
    post_id: str
    title: str

class ChatResponse(BaseModel):
    """Chat response model / 聊天响应模型"""
    agent_name: str
    message: str
    response: str
    references: List[ChatReference] = []
    status: str


# ==================== API Endpoints API 端点 ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return R.ok({
        "message": "Welcome to Pool AI Knowledge API",
        "version": "0.2.0",
        "endpoints": {
            "agents": "/api/agents",
            "chat": "/api/chat",
            "examples": "/api/examples/{agent_name}",
            "admin": "/api/admin",
            "web": "/api/web",
            "docs": "/docs"
        }
    })


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
    return R.ok({"status": "healthy"})


@app.get("/api/agents")
async def get_available_agents():
    """Get list of available agents / 获取可用代理列表"""
    agents = list_agents()
    agent_info = {}

    for agent_name in agents:
        agent = get_agent(agent_name)
        if agent:
            agent_info[agent_name] = {
                "name": agent.name,
                "description": agent.description
            }

    return R.ok({"agents": agent_info, "total": len(agents)})


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


@app.post("/api/chat")
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
        
        # Build message with optional article context
        message_text = request.message
        if request.post_id:
            from database import SessionLocal, Post as DBPost
            db = SessionLocal()
            try:
                post = db.query(DBPost).filter(DBPost.id == request.post_id, DBPost.is_active == True).first()
                if post:
                    message_text = (
                        f"Based on this article:\n"
                        f"Title: {post.title}\n"
                        f"Content: {post.content}\n\n"
                        f"User question: {request.message}"
                    )
            finally:
                db.close()

        # Append language instruction if specified
        if request.language:
            lang_names = {"zh-CN": "Chinese (Simplified)", "en": "English"}
            lang_name = lang_names.get(request.language, request.language)
            message_text += f"\n\n[IMPORTANT: You MUST respond in {lang_name}.]"

        # Create Content object from message
        content = runner_types.Content(parts=[{"text": message_text}], role="user")
        
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
            result = _extract_response_from_events(events)
        except Exception as run_error:
            import traceback
            error_details = traceback.format_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Error running agent: {str(run_error)}\nDetails: {error_details[:500]}"
            )

        return R.ok(ChatResponse(
            agent_name=request.agent_name,
            message=request.message,
            response=result["text"],
            references=[ChatReference(**ref) for ref in result["references"]],
            status="success"
        ).model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running agent: {str(e)}"
        )


def _extract_response_from_events(events: List, debug: bool = False) -> dict:
    """
    Extract text response and references from agent events.

    Returns:
        dict with keys "text" and "references"
    """
    references = []
    response_text = ""

    if not events:
        return {"text": "No response generated", "references": []}

    # Pass 1: extract search_knowledge_base function_response results
    for event in events:
        if not (hasattr(event, 'content') and event.content and hasattr(event.content, 'parts')):
            continue
        for part in event.content.parts:
            if hasattr(part, 'function_response') and part.function_response:
                fr = part.function_response
                if getattr(fr, 'name', '') == 'search_knowledge_base':
                    try:
                        resp = fr.response if hasattr(fr, 'response') else {}
                        # ADK returns protobuf Struct, not plain dict; convert it
                        if not isinstance(resp, dict):
                            try:
                                resp = dict(resp)
                            except (TypeError, ValueError):
                                resp = {}
                        results = resp.get('results', [])
                        for r in results:
                            # Convert protobuf MapComposite to dict if needed
                            if not isinstance(r, dict):
                                try:
                                    r = dict(r)
                                except (TypeError, ValueError):
                                    continue
                            if r.get('post_id') and r.get('title'):
                                references.append({
                                    "post_id": str(r["post_id"]),
                                    "title": str(r["title"]),
                                })
                    except Exception:
                        pass

    # Pass 2: extract final text response
    for event in events:
        try:
            if hasattr(event, 'is_final_response') and event.is_final_response():
                if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text = part.text
                            break
                if response_text:
                    break
        except Exception:
            pass

    # Fallback: collect all text parts
    if not response_text:
        parts = []
        for event in events:
            if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        parts.append(part.text)
        response_text = '\n'.join(parts) if parts else "No text response found"

    # Deduplicate references by post_id
    seen = set()
    unique_refs = []
    for ref in references:
        if ref["post_id"] not in seen:
            seen.add(ref["post_id"])
            unique_refs.append(ref)

    return {"text": response_text, "references": unique_refs}


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
        result = await example_functions[agent_name]()
        return R.ok(result)
    else:
        return R.ok({
            "agent": agent_name,
            "description": agent.description,
            "note": "Use /api/chat endpoint to interact with this agent"
        })


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
    
    return R.ok({
        "name": agent.name,
        "description": agent.description,
        "model": agent.model,
        "tools_count": len(agent.tools) if hasattr(agent, 'tools') else 0,
        "tools": [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in agent.tools] if hasattr(agent, 'tools') else []
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
