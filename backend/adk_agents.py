"""
ADK Agent Functions and Examples
使用 Google ADK (Agent Development Kit) 创建的 AI 代理函数和示例
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from google.adk.agents import Agent
from google.adk.tools import google_search
from knowledge_base_agent import create_knowledge_base_agent


# ==================== Custom Tools 自定义工具 ====================

def calculate(expression: str) -> Dict[str, str]:
    """
    Calculate a mathematical expression / 计算数学表达式
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")
    
    Returns:
        Dictionary with calculation result / 包含计算结果的字典
    """
    try:
        # Safe evaluation of mathematical expressions / 安全地评估数学表达式
        result = eval(expression, {"__builtins__": {}}, {})
        return {
            "status": "success",
            "expression": expression,
            "result": str(result)
        }
    except Exception as e:
        return {
            "status": "error",
            "expression": expression,
            "error": str(e)
        }


def get_current_time(timezone: str = "UTC") -> Dict[str, str]:
    """
    Get current time in specified timezone / 获取指定时区的当前时间
    
    Args:
        timezone: Timezone name (e.g., "UTC", "Asia/Shanghai", "America/New_York")
    
    Returns:
        Dictionary with current time information / 包含当前时间信息的字典
    """
    now = datetime.now()
    return {
        "status": "success",
        "timezone": timezone,
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": str(now.timestamp())
    }


def format_text(text: str, format_type: str = "uppercase") -> Dict[str, str]:
    """
    Format text in different ways / 以不同方式格式化文本
    
    Args:
        text: Text to format / 要格式化的文本
        format_type: Format type - "uppercase", "lowercase", "title", "reverse"
    
    Returns:
        Dictionary with formatted text / 包含格式化文本的字典
    """
    formats = {
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "title": text.title(),
        "reverse": text[::-1]
    }
    
    result = formats.get(format_type.lower(), text)
    return {
        "status": "success",
        "original": text,
        "format_type": format_type,
        "formatted": result
    }


def word_count(text: str) -> Dict[str, int]:
    """
    Count words and characters in text / 统计文本中的单词和字符数
    
    Args:
        text: Text to analyze / 要分析的文本
    
    Returns:
        Dictionary with word and character counts / 包含单词和字符数的字典
    """
    words = text.split()
    return {
        "status": "success",
        "character_count": len(text),
        "word_count": len(words),
        "sentence_count": text.count('.') + text.count('!') + text.count('?')
    }


# ==================== Agent Definitions 代理定义 ====================

def create_calculator_agent() -> Agent:
    """
    Create a calculator agent with math tools / 创建带有数学工具的计算器代理
    
    Returns:
        Agent instance configured for calculations / 配置用于计算的代理实例
    """
    return Agent(
        model='gemini-2.0-flash',
        name='calculator_agent',
        description="A helpful calculator agent that can perform mathematical calculations. / 一个可以进行数学计算的有用计算器代理",
        instruction="""
        You are a helpful calculator assistant. When users ask for calculations, 
        use the calculate tool to solve mathematical expressions.
        Always show your work and explain the result clearly.
        
        你是一个有用的计算器助手。当用户要求计算时，使用 calculate 工具来解决数学表达式。
        始终展示你的工作过程并清楚地解释结果。
        """,
        tools=[calculate]
    )


def create_time_agent() -> Agent:
    """
    Create a time agent that provides current time information / 创建提供当前时间信息的时间代理
    
    Returns:
        Agent instance configured for time queries / 配置用于时间查询的代理实例
    """
    return Agent(
        model='gemini-2.0-flash',
        name='time_agent',
        description="Provides current time information in various timezones. / 提供各种时区的当前时间信息",
        instruction="""
        You are a time assistant. When users ask about the current time, 
        use the get_current_time tool to provide accurate time information.
        Be helpful and friendly in your responses.
        
        你是一个时间助手。当用户询问当前时间时，使用 get_current_time 工具提供准确的时间信息。
        在你的回复中要友好和乐于助人。
        """,
        tools=[get_current_time]
    )


def create_text_processing_agent() -> Agent:
    """
    Create a text processing agent with formatting tools / 创建带有格式化工具的文本处理代理
    
    Returns:
        Agent instance configured for text processing / 配置用于文本处理的代理实例
    """
    return Agent(
        model='gemini-2.0-flash',
        name='text_processing_agent',
        description="Processes and formats text in various ways. / 以各种方式处理和格式化文本",
        instruction="""
        You are a text processing assistant. You can format text, count words, 
        and perform various text operations. Use the available tools to help users.
        
        你是一个文本处理助手。你可以格式化文本、统计单词并执行各种文本操作。
        使用可用工具帮助用户。
        """,
        tools=[format_text, word_count]
    )


def create_search_agent() -> Agent:
    """
    Create a search agent using Google Search tool / 使用 Google 搜索工具创建搜索代理
    
    Returns:
        Agent instance configured for web searches / 配置用于网络搜索的代理实例
    """
    return Agent(
        model='gemini-2.0-flash',
        name='search_agent',
        description="An assistant that can search the web using Google Search. / 可以使用 Google 搜索搜索网络的助手",
        instruction="""
        You are a helpful search assistant. When users ask questions that require 
        current information or web search, use the google_search tool to find 
        relevant information. Summarize the results clearly and cite sources.
        
        你是一个有用的搜索助手。当用户提出需要最新信息或网络搜索的问题时，
        使用 google_search 工具查找相关信息。清楚地总结结果并引用来源。
        """,
        tools=[google_search]
    )


def create_multi_tool_agent() -> Agent:
    """
    Create a comprehensive agent with multiple tools / 创建具有多个工具的综合代理
    
    Returns:
        Agent instance with all available tools / 具有所有可用工具的代理实例
    """
    return Agent(
        model='gemini-2.0-flash',
        name='multi_tool_agent',
        description="A versatile assistant with multiple capabilities including calculation, time, text processing, and web search. / 具有多种功能的多功能助手，包括计算、时间、文本处理和网络搜索",
        instruction="""
        You are a versatile assistant with access to multiple tools:
        - calculate: For mathematical calculations
        - get_current_time: For time information
        - format_text: For text formatting
        - word_count: For text analysis
        - google_search: For web searches
        
        Choose the appropriate tool(s) based on the user's request. Be helpful and clear.
        
        你是一个多功能助手，可以使用多种工具：
        - calculate: 用于数学计算
        - get_current_time: 用于时间信息
        - format_text: 用于文本格式化
        - word_count: 用于文本分析
        - google_search: 用于网络搜索
        
        根据用户的请求选择适当的工具。要友好和清晰。
        """,
        tools=[calculate, get_current_time, format_text, word_count, google_search]
    )


# ==================== Agent Registry 代理注册表 ====================

AGENT_REGISTRY: Dict[str, Agent] = {
    "calculator": create_calculator_agent(),
    "time": create_time_agent(),
    "text": create_text_processing_agent(),
    "search": create_search_agent(),
    "multi": create_multi_tool_agent(),
    "knowledge": create_knowledge_base_agent(),  # Knowledge base agent / 知识库代理
}


def get_agent(agent_name: str) -> Optional[Agent]:
    """
    Get an agent by name / 通过名称获取代理
    
    Args:
        agent_name: Name of the agent / 代理名称
    
    Returns:
        Agent instance or None if not found / 代理实例，如果未找到则返回 None
    """
    return AGENT_REGISTRY.get(agent_name.lower())


def list_agents() -> List[str]:
    """
    List all available agent names / 列出所有可用的代理名称
    
    Returns:
        List of agent names / 代理名称列表
    """
    return list(AGENT_REGISTRY.keys())


# ==================== Example Usage Functions 示例使用函数 ====================

async def example_calculator_usage():
    """
    Example of using the calculator agent / 使用计算器代理的示例
    """
    agent = get_agent("calculator")
    if agent:
        # Example queries / 示例查询
        examples = [
            "What is 25 * 4?",
            "Calculate 100 divided by 5",
            "What's the result of 2 to the power of 8?"
        ]
        return {
            "agent": "calculator",
            "examples": examples,
            "note": "Use agent.run() or agent.stream() to interact with the agent"
        }
    return {"error": "Calculator agent not found"}


async def example_search_usage():
    """
    Example of using the search agent / 使用搜索代理的示例
    """
    agent = get_agent("search")
    if agent:
        examples = [
            "What's the latest news about AI?",
            "Find information about Python programming",
            "Search for weather in New York"
        ]
        return {
            "agent": "search",
            "examples": examples,
            "note": "This agent uses Google Search to find current information"
        }
    return {"error": "Search agent not found"}


async def example_multi_tool_usage():
    """
    Example of using the multi-tool agent / 使用多工具代理的示例
    """
    agent = get_agent("multi")
    if agent:
        examples = [
            "Calculate 15 * 23 and format the result in uppercase",
            "What time is it now? Also count the words in this sentence.",
            "Search for Python tutorials and calculate how many hours are in a week"
        ]
        return {
            "agent": "multi",
            "examples": examples,
            "note": "This agent can use multiple tools in a single conversation"
        }
    return {"error": "Multi-tool agent not found"}

