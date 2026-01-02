import asyncio
import sys
import os

# Add parent directory to path to allow importing core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.schema import AgentSkill, Intent, Message
from core.provider import BaseProvider
from core.dispatcher import Dispatcher
from core.executor import LocalPythonExecutor

class MockAIProvider(BaseProvider):
    """
    Temporary provider for Phase 1 verification.
    (Phase 1 校验用的临时供给侧)
    """
    async def chat(self, messages: list[Message]) -> str:
        return "Thinking... (Proxy Mode)"

    async def resolve_intent(self, query: str, skills: list[AgentSkill]) -> Intent:
        # 模拟解析逻辑 (Simulate resolution logic)
        if "data" in query.lower() or "csv" in query.lower():
            target = "data_analyzer"
        else:
            target = None
            
        return Intent(
            raw_query=query,
            thought_process="User mentioned data related terms, routing to analyzer.",
            target_skill_id=target,
            confidence=0.9
        )

async def main():
    # 1. Initialize Dispatcher with Mock AI and Local Executor
    # 这里演示了即便没有 MCP，系统也能通过本地适配器跑通 (Adapter Pattern)
    provider = MockAIProvider()
    executor = LocalPythonExecutor()
    dispatcher = Dispatcher(provider=provider, executor=executor)

    # 2. Register a Sample Skill
    analyzer_skill = AgentSkill(
        id="data_analyzer",
        name="Data Analyzer",
        description="Expert at processing local CSV and Excel files.",
        tags=["data", "analytics"],
        examples=["Analyze the sales.csv file", "Give me a summary of historical data"]
    )
    dispatcher.register_skill(analyzer_skill)

    # 3. Handle a Query
    print("\n--- Testing Dispatcher ---")
    query = "Please look at my sales data in the working directory."
    context = await dispatcher.handle_query(query)
    
    print(f"Final Task Status: {context.status}")

if __name__ == "__main__":
    asyncio.run(main())
