"""
Knowledge Base Agent Usage Examples
知识库代理使用示例

This file demonstrates how to use the knowledge base agent.
此文件演示如何使用知识库代理。
"""

import asyncio
from knowledge_base_agent import (
    create_knowledge_base_agent,
    add_post_to_knowledge_base,
    _knowledge_base
)
from google.adk import Runner
from google.adk.runners import types
from google.adk.sessions.in_memory_session_service import InMemorySessionService


async def example_add_posts():
    """Example: Add posts to knowledge base / 示例：向知识库添加文章"""
    print("=" * 60)
    print("Example: Adding Posts to Knowledge Base")
    print("示例：向知识库添加文章")
    print("=" * 60)
    
    # Add some posts / 添加一些文章
    posts = [
        {
            "title": "Python 虚拟环境最佳实践",
            "content": "使用虚拟环境可以隔离项目依赖。推荐使用 python -m venv venv 创建，使用 source venv/bin/activate 激活。这样可以避免不同项目之间的包冲突。",
            "tags": ["Python", "虚拟环境", "开发"]
        },
        {
            "title": "FastAPI 路由和中间件",
            "content": "FastAPI 使用装饰器定义路由，支持路径参数和查询参数。可以使用中间件处理请求和响应。异步路由使用 async def 定义。",
            "tags": ["FastAPI", "Web开发", "Python"]
        },
        {
            "title": "Google ADK 工具开发",
            "content": "在 Google ADK 中，可以创建自定义工具函数。工具函数会被自动转换为代理可用的工具。使用 @tool 装饰器或直接定义函数即可。",
            "tags": ["Google ADK", "AI", "工具开发"]
        }
    ]
    
    for post in posts:
        result = add_post_to_knowledge_base(
            title=post["title"],
            content=post["content"],
            tags=post["tags"]
        )
        print(f"\n✅ Added post: {result['title']} (ID: {result['post_id']})")
    
    print(f"\nTotal posts in knowledge base: {len(_knowledge_base.posts)}")
    print("\n" + "=" * 60 + "\n")


async def example_query_knowledge_base():
    """Example: Query knowledge base with agent / 示例：使用代理查询知识库"""
    print("=" * 60)
    print("Example: Querying Knowledge Base")
    print("示例：查询知识库")
    print("=" * 60)
    
    # Create agent / 创建代理
    agent = create_knowledge_base_agent()
    
    # Create runner / 创建运行器
    session_service = InMemorySessionService()
    runner = Runner(app_name="knowledge", agent=agent, session_service=session_service)
    
    # Create session before running queries / 在运行查询之前创建会话
    session_id = "test_session"
    user_id = "test_user"
    
    # Create session / 创建会话
    try:
        session_service.create_session_sync(
            user_id=user_id,
            session_id=session_id,
            app_name="knowledge"
        )
    except Exception:
        # Session might already exist, try to get it / 会话可能已存在，尝试获取它
        try:
            session_service.get_session_sync(
                user_id=user_id,
                session_id=session_id,
                app_name="knowledge"
            )
        except Exception:
            pass  # If both fail, continue anyway / 如果两者都失败，继续执行
    
    # Test queries / 测试查询
    queries = [
        "如何使用 Python 虚拟环境？",
        "FastAPI 如何定义路由？",
        "如何创建 Google ADK 工具？",
        "如何学习机器学习？"  # This should return "not found" / 这应该返回"未找到"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query / 查询: {query}")
        print(f"{'='*60}")
        
        try:
            content = types.Content(parts=[{"text": query}])
            events = list(runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ))
            
            # Extract response / 提取响应
            response_parts = []
            for event in events:
                try:
                    if hasattr(event, 'is_final_response') and event.is_final_response():
                        if hasattr(event, 'content') and event.content:
                            if hasattr(event.content, 'parts') and event.content.parts:
                                for part in event.content.parts:
                                    if isinstance(part, dict) and 'text' in part:
                                        response_parts.append(part['text'])
                                    elif hasattr(part, 'text') and part.text:
                                        response_parts.append(part.text)
                except:
                    pass
                
                # Fallback: extract from any content / 后备：从任何内容提取
                if hasattr(event, 'content') and event.content:
                    content_obj = event.content
                    if hasattr(content_obj, 'parts') and content_obj.parts:
                        for part in content_obj.parts:
                            if isinstance(part, dict) and 'text' in part:
                                response_parts.append(part['text'])
                            elif hasattr(part, 'text') and part.text:
                                response_parts.append(part.text)
            
            response = ' '.join(response_parts) if response_parts else "No response"
            print(f"\nResponse / 响应:\n{response}\n")
            
        except Exception as e:
            print(f"Error / 错误: {e}")
            import traceback
            traceback.print_exc()
            print(f"\nResponse / 响应:\nNo response\n")
    
    print("\n" + "=" * 60 + "\n")


async def example_direct_search():
    """Example: Direct search without agent / 示例：不使用代理直接搜索"""
    print("=" * 60)
    print("Example: Direct Knowledge Base Search")
    print("示例：直接知识库搜索")
    print("=" * 60)
    
    from knowledge_base_agent import search_knowledge_base
    
    query = "我想了解有关FastApi中间件的内容"
    result = search_knowledge_base(query, top_k=2)
    
    print(f"\nQuery / 查询: {query}")
    print(f"Status / 状态: {result['status']}")
    print(f"Results Count / 结果数量: {result.get('results_count', 0)}")
    
    if result['status'] == 'found':
        print("\nResults / 结果:")
        for i, r in enumerate(result['results'], 1):
            print(f"\n{i}. {r['title']} (ID: {r['post_id']})")
            print(f"   Relevance Score / 相关性分数: {r['relevance_score']}")
            print(f"   Reason / 原因: {r['reason']}")
            print(f"   Matched Content / 匹配内容: {r['matched_content'][:100]}...")
    
    print("\n" + "=" * 60 + "\n")


async def run_all_examples():
    """Run all examples / 运行所有示例"""
    print("\n" + "=" * 60)
    print("Knowledge Base Agent Examples")
    print("知识库代理示例")
    print("=" * 60 + "\n")
    
    # Example 1: Add posts / 示例 1：添加文章
    # await example_add_posts()
    
    # Example 2: Direct search / 示例 2：直接搜索
    await example_direct_search()
    
    # Example 3: Query with agent / 示例 3：使用代理查询
    # await example_query_knowledge_base()
    
    print("\n" + "=" * 60)
    print("All examples completed! / 所有示例完成！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_examples())

