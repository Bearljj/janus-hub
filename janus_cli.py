import asyncio
import os
import sys
from typing import List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.schema import AgentSkill, Intent, Message, TaskStatus
from core.provider import BaseProvider
from core.dispatcher import Dispatcher
from core.executor import MCPExecutor

class AssistantGuidedProvider(BaseProvider):
    """
    A provider that asks the human/assistant for intent resolution.
    (由人工/助手引导的供给侧，用于在没有 API Key 时调通流程)
    """
    async def chat(self, messages: List[Message]) -> str:
        # 在这个模式下，JANUS 会等待我在对话框中给出答案
        print("\n[需要大脑输入] JANUS 正在请求响应。请查看开发上下文。")
        return "助手正在处理..."

    async def resolve_intent(self, query: str, skills: List[AgentSkill]) -> Intent:
        """
        根据用户输入，手动模拟 AI 的解析逻辑。
        """
        print(f"\n[大脑逻辑] 输入查询: '{query}'")
        print("可用技能:")
        for s in skills:
            print(f" - {s.id}: {s.name}")

        # 这里我们预设一些自动化映射逻辑，模拟 AI 的判断
        q = query.lower()
        target = None
        params = {}
        thought = ""

        if "list" in q or "files" in q:
            target = "list_files"
            params = {"pattern": "*"}
            thought = "User wants to browse the directory."
        elif "search" in q or "find" in q:
            target = "search_in_file"
            # 简单模拟提取参数 (Simulate param extraction)
            thought = "Searching for patterns in a specific file."
            # 这里的参数逻辑在真实 AI 中会由 LLM 提取
            params = {"relative_path": "README.md", "query": "Project"} 
        elif "preview" in q or "schema" in q:
            target = "preview_data_schema"
            params = {"relative_path": "data/processed/insurance_data_cleaned.parquet"}
            thought = "User wants to see data structure."

        return Intent(
            raw_query=query,
            thought_process=thought,
            target_skill_id=target,
            parameters=params,
            confidence=1.0
        )

async def start_janus():
    print("=== Project JANUS 调度中心 (v0.1-alfa) ===")
    
    # 1. Setup Kernel
    provider = AssistantGuidedProvider()
    dispatcher = Dispatcher(provider=provider)

    # 2. Setup Executors
    server_script = os.path.abspath("mcp-servers/local_file_server.py")
    mcp_executor = MCPExecutor(command="python3", args=[server_script])

    # 3. Register Skills (Connecting Logic to Physical Tools)
    skills = [
        AgentSkill(id="list_files", name="List Files", description="List local files."),
        AgentSkill(id="search_in_file", name="Search Content", description="Search text in a file."),
        AgentSkill(id="preview_data_schema", name="Preview Data", description="Preview CSV/Parquet schema."),
    ]
    for s in skills:
        dispatcher.register_skill(s, mcp_executor)

    print("\nJANUS 已就绪。(系统当前运行在：助手引导模式)")
    
    # 4. Simple REPL
    while True:
        try:
            user_input = input("\n[用户] > ")
            if user_input.lower() in ['exit', 'quit', '退出']:
                break
                
            context = await dispatcher.handle_query(user_input)
            
            # Print Final Assistant Response
            for msg in context.messages:
                if msg.role == "assistant":
                    print(f"\n[Janus]:\n{msg.content}")
                elif msg.role == "system":
                    print(f"\n[系统错误]: {msg.content}")
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"执行出错: {e}")

if __name__ == "__main__":
    asyncio.run(start_janus())
