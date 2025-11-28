"""
ADK Agent Usage Examples
ADK 代理使用示例

This file contains example code showing how to use the ADK agents.
此文件包含展示如何使用 ADK 代理的示例代码。
"""

import asyncio
from adk_agents import (
    get_agent,
    list_agents,
    create_calculator_agent,
    create_search_agent,
    create_multi_tool_agent
)


async def example_1_calculator_agent():
    """
    Example 1: Using the calculator agent / 示例 1：使用计算器代理
    """
    print("=" * 60)
    print("Example 1: Calculator Agent / 示例 1：计算器代理")
    print("=" * 60)
    
    agent = get_agent("calculator")
    
    queries = [
        "What is 25 multiplied by 4?",
        "Calculate 100 divided by 5",
        "What's 2 to the power of 8?"
    ]
    
    for query in queries:
        print(f"\nQuery / 查询: {query}")
        try:
            response = await agent.run(query)
            print(f"Response / 响应: {response}")
        except Exception as e:
            print(f"Error / 错误: {e}")
    
    print("\n" + "=" * 60 + "\n")


async def example_2_time_agent():
    """
    Example 2: Using the time agent / 示例 2：使用时间代理
    """
    print("=" * 60)
    print("Example 2: Time Agent / 示例 2：时间代理")
    print("=" * 60)
    
    agent = get_agent("time")
    
    queries = [
        "What time is it now?",
        "Get the current time in UTC",
        "Tell me the current timestamp"
    ]
    
    for query in queries:
        print(f"\nQuery / 查询: {query}")
        try:
            response = await agent.run(query)
            print(f"Response / 响应: {response}")
        except Exception as e:
            print(f"Error / 错误: {e}")
    
    print("\n" + "=" * 60 + "\n")


async def example_3_text_processing_agent():
    """
    Example 3: Using the text processing agent / 示例 3：使用文本处理代理
    """
    print("=" * 60)
    print("Example 3: Text Processing Agent / 示例 3：文本处理代理")
    print("=" * 60)
    
    agent = get_agent("text")
    
    queries = [
        "Format 'hello world' in uppercase",
        "Count the words in: 'The quick brown fox jumps over the lazy dog'",
        "Reverse this text: 'Python Programming'"
    ]
    
    for query in queries:
        print(f"\nQuery / 查询: {query}")
        try:
            response = await agent.run(query)
            print(f"Response / 响应: {response}")
        except Exception as e:
            print(f"Error / 错误: {e}")
    
    print("\n" + "=" * 60 + "\n")


async def example_4_search_agent():
    """
    Example 4: Using the search agent / 示例 4：使用搜索代理
    Note: Requires GOOGLE_API_KEY in environment / 注意：需要在环境中设置 GOOGLE_API_KEY
    """
    print("=" * 60)
    print("Example 4: Search Agent / 示例 4：搜索代理")
    print("=" * 60)
    
    agent = get_agent("search")
    
    queries = [
        "What is Python programming?",
        "Find information about FastAPI",
        "Search for latest AI news"
    ]
    
    for query in queries:
        print(f"\nQuery / 查询: {query}")
        try:
            response = await agent.run(query)
            print(f"Response / 响应: {response}")
        except Exception as e:
            print(f"Error / 错误: {e}")
    
    print("\n" + "=" * 60 + "\n")


async def example_5_multi_tool_agent():
    """
    Example 5: Using the multi-tool agent / 示例 5：使用多工具代理
    """
    print("=" * 60)
    print("Example 5: Multi-Tool Agent / 示例 5：多工具代理")
    print("=" * 60)
    
    agent = get_agent("multi")
    
    queries = [
        "Calculate 15 * 23 and format the result in uppercase",
        "What time is it now? Also count the words in this sentence.",
        "Calculate how many hours are in a week"
    ]
    
    for query in queries:
        print(f"\nQuery / 查询: {query}")
        try:
            response = await agent.run(query)
            print(f"Response / 响应: {response}")
        except Exception as e:
            print(f"Error / 错误: {e}")
    
    print("\n" + "=" * 60 + "\n")


async def example_6_list_all_agents():
    """
    Example 6: List all available agents / 示例 6：列出所有可用代理
    """
    print("=" * 60)
    print("Example 6: List All Agents / 示例 6：列出所有代理")
    print("=" * 60)
    
    agents = list_agents()
    print(f"\nAvailable agents / 可用代理: {agents}\n")
    
    for agent_name in agents:
        agent = get_agent(agent_name)
        if agent:
            print(f"Agent / 代理: {agent.name}")
            print(f"Description / 描述: {agent.description}")
            print(f"Model / 模型: {agent.model}")
            print("-" * 60)
    
    print("\n" + "=" * 60 + "\n")


async def example_7_streaming_agent():
    """
    Example 7: Using streaming with an agent / 示例 7：使用代理的流式传输
    """
    print("=" * 60)
    print("Example 7: Streaming Agent / 示例 7：流式代理")
    print("=" * 60)
    
    agent = get_agent("calculator")
    
    query = "Calculate 123 * 456 and explain the steps"
    
    print(f"\nQuery / 查询: {query}")
    print("Streaming response / 流式响应:\n")
    
    try:
        async for chunk in agent.stream(query):
            print(chunk, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"Error / 错误: {e}")
    
    print("\n" + "=" * 60 + "\n")


async def run_all_examples():
    """
    Run all examples / 运行所有示例
    """
    print("\n" + "=" * 60)
    print("ADK Agent Examples / ADK 代理示例")
    print("=" * 60 + "\n")
    
    # Run examples / 运行示例
    await example_6_list_all_agents()
    await example_1_calculator_agent()
    await example_2_time_agent()
    await example_3_text_processing_agent()
    # Uncomment to test search agent (requires API key) / 取消注释以测试搜索代理（需要 API 密钥）
    # await example_4_search_agent()
    await example_5_multi_tool_agent()
    await example_7_streaming_agent()
    
    print("\n" + "=" * 60)
    print("All examples completed! / 所有示例完成！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Run all examples / 运行所有示例
    asyncio.run(run_all_examples())

