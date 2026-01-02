import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.schema import AgentSkill, Intent, Message, TaskStatus
from core.provider import BaseProvider
from core.dispatcher import Dispatcher
from core.executor import MCPExecutor

class IntegrationMockProvider(BaseProvider):
    async def chat(self, messages: list[Message]) -> str:
        return "Integration Mode"

    async def resolve_intent(self, query: str, skills: list[AgentSkill]) -> Intent:
        # 简单模拟：如果包含 "list" 就调用 list_files
        if "list" in query.lower():
            return Intent(
                raw_query=query,
                thought_process="User wants to see files.",
                target_skill_id="list_files",
                parameters={"pattern": "*"},
                confidence=1.0
            )
        return Intent(raw_query=query, thought_process="No matching skill", confidence=0.0)

async def main():
    # 1. Initialize Dispatcher
    provider = IntegrationMockProvider()
    dispatcher = Dispatcher(provider=provider)

    # 2. Define the MCP Executor for our local file server
    # 使用 absolute path 确保可靠性
    server_script = os.path.abspath("mcp-servers/local_file_server.py")
    executor = MCPExecutor(command="python3", args=[server_script])

    # 3. Register the skill (Mapped to MCP tool)
    list_skill = AgentSkill(
        id="list_files", # ID must match tool name for this simple executor
        name="List Local Files",
        description="Lists files in the secure directory.",
        input_schema={"pattern": "string"}
    )
    dispatcher.register_skill(list_skill, executor)

    # 4. Run Query
    print("\n--- Running MCP Integration Test ---")
    query = "Please list all files in my directory."
    context = await dispatcher.handle_query(query)
    
    print(f"\nTask Status: {context.status}")
    if context.status == TaskStatus.COMPLETED:
        print("Final Result Content:")
        for msg in context.messages:
            if msg.role == "assistant":
                print(msg.content)
    else:
        for msg in context.messages:
            if msg.role == "system":
                print(f"Error: {msg.content}")

if __name__ == "__main__":
    asyncio.run(main())
