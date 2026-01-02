from abc import ABC, abstractmethod
from typing import Any, Dict
from .schema import TaskContext

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import asynccontextmanager

class BaseExecutor(ABC):
    """
    Abstract base class for Skill execution (技能执行抽象基类)
    Implements the Adapter Pattern to decouple logic from transport.
    """

    @abstractmethod
    async def execute(self, skill_id: str, parameters: Dict[str, Any], context: TaskContext) -> Any:
        """
        Execute a specific skill (执行特定技能)
        """
        pass

class LocalPythonExecutor(BaseExecutor):
    """
    Directly executes local Python functions (直接执行本地 Python 函数)
    Used for core skills or as a fallback when MCP is not available.
    """
    async def execute(self, skill_id: str, parameters: Dict[str, Any], context: TaskContext) -> Any:
        # Placeholder for local execution logic
        return f"Locally executed {skill_id} with {parameters}"

class MCPExecutor(BaseExecutor):
    """
    Bridge to the Model Context Protocol (MCP 桥接执行器)
    Manages connections to MCP servers via stdio.
    """
    def __init__(self, command: str, args: list[str]):
        self.server_params = StdioServerParameters(
            command=command,
            args=args,
            env=None
        )

    async def execute(self, skill_id: str, parameters: Dict[str, Any], context: TaskContext) -> Any:
        # 建立连接并执行工具 (Establish connection and execute tool)
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # MCP 调用的核心 (Core of MCP call)
                result = await session.call_tool(skill_id, arguments=parameters)
                
                # 提取文本内容 (Extract text content)
                return "\n".join([c.text for c in result.content if hasattr(c, 'text')])
