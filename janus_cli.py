import asyncio
import os
import sys
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.schema import AgentSkill, Intent, Message, TaskStatus, AuditStatus
from core.provider import BaseProvider
from core.dispatcher import Dispatcher
from core.executor import MCPExecutor
from core.audit import RuleBasedAuditor, AIAuditor, CompositeAuditor
from core.providers import OpenAIProvider

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
        elif "summary" in q or "stats" in q or "分析" in q:
            target = "data_summary_stats"
            params = {"relative_path": "data/processed/insurance_data_cleaned.parquet"}
            thought = "User wants a statistical overview of the dataset."
        elif "memory" in q or "记忆" in q or "回顾" in q:
            target = "list_memory"
            thought = "User wants to see session history."
        elif "read log" in q or "读日志" in q:
            target = "read_memory"
            params = {"filename": "session_latest.md"} # 真实 AI 会提取具体文件名
            thought = "User wants to read a specific log."
        elif "knowledge" in q or "事实" in q or "知识" in q:
            target = "query_knowledge"
            params = {"keyword": ""}
            thought = "User wants to query the structured knowledge store."
        elif "remember" in q or "记住" in q:
            target = "add_knowledge"
            params = {"category": "UserPreference", "content": "Owner likes transposed views."}
            thought = "User wants to manually record a fact."

        else:
            # --- 触发 SOS 信号 (Trigger SOS Signal) ---
            print(f"\n[SOS] JANUS 无法理解意图: '{query}'")
            return Intent(
                raw_query=query,
                thought_process="Mock logic failed. Emitting SOS to Antigravity.",
                target_skill_id=None,
                parameters={},
                confidence=0.0
            )

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
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        provider = OpenAIProvider(
            model=os.getenv("JANUS_MODEL", "gpt-4-turbo-preview"),
            api_key=api_key,
            base_url=os.getenv("OPENAI_API_BASE")
        )
        mode_text = "智能大脑模式 (Connected to Cloud LLM)"
        # 为智能模式启用复合审计 (Rule + AI)
        auditor = CompositeAuditor([
            RuleBasedAuditor(),
            AIAuditor(provider=provider)
        ])
    else:
        provider = AssistantGuidedProvider()
        mode_text = "助手引导模式 (Mock Brain)"
        auditor = RuleBasedAuditor()
        
    dispatcher = Dispatcher(provider=provider, auditor=auditor)

    # 2. Setup Executors
    server_script = os.path.abspath("mcp-servers/local_file_server.py")
    mcp_executor = MCPExecutor(command="python3", args=[server_script])

    # 3. Register Skills (Connecting Logic to Physical Tools)
    skills = [
        AgentSkill(id="list_files", name="List Files", description="List local files."),
        AgentSkill(id="search_in_file", name="Search Content", description="Search text in a file."),
        AgentSkill(id="preview_data_schema", name="Preview Data", description="Preview CSV/Parquet schema."),
        AgentSkill(id="data_summary_stats", name="Data Stats", description="Get statistical summary of a data file."),
        AgentSkill(id="list_memory", name="List Memory", description="List all interaction logs."),
        AgentSkill(id="read_memory", name="Read Memory", description="Read a specific log file."),
        AgentSkill(id="query_knowledge", name="Query Knowledge", description="Query factual information."),
        AgentSkill(id="add_knowledge", name="Add Knowledge", description="Manually record a fact."),
    ]
    for s in skills:
        dispatcher.register_skill(s, mcp_executor)

    print(f"\nJANUS 已就绪。(系统当前运行在：{mode_text})")
    
    # 4. Simple REPL
    while True:
        try:
            user_input = input("\n[用户] > ")
            if user_input.lower() in ['exit', 'quit', '退出']:
                break
                
            context = await dispatcher.handle_query(user_input)
            
            # --- SOS 协同环节 ---
            if context.status == TaskStatus.PENDING and not context.metadata.get("intent", {}).get("target_skill_id"):
                 print(f"\n🚨 [系统信号] JANUS 陷入逻辑困境。")
                 print(f"信号已发送至 Antigravity (大脑中心)。请等待逻辑补全...")
                 context.status = TaskStatus.WAITING
                 # 实际上，这会触发我这边的响应，逻辑在此时挂起
            
            # --- 人机协同环节 (Human-in-the-loop) ---
            if context.status == TaskStatus.AUDITING:
                confirm = input("\n[注意] 检测到安全警告。是否允许继续执行？(y/n/查看理由): ").lower()
                if confirm == 'y':
                    context = await dispatcher.execute_task(context)
                elif '理由' in confirm or 'reason' in confirm:
                    # 获取审计报告理由 (Extract reason from metadata)
                    for msg in context.messages:
                        if "metadata" in msg.__dict__ and "audit_report" in msg.metadata:
                            print(f"\n[审计详情]: {msg.metadata['audit_report']['rationale']}")
                    confirm_again = input("\n读完理由后，是否允许继续执行？(y/n): ").lower()
                    if confirm_again == 'y':
                        context = await dispatcher.execute_task(context)
                    else:
                        print("[系统] 任务已被用户取消。")
                else:
                    print("[系统] 任务已被用户取消。")

            # --- 结果展示 (Final Result Display) ---
            for msg in context.messages:
                if msg.role == "assistant":
                    print(f"\n[Janus]:\n{msg.content}")
                elif msg.role == "system":
                    print(f"\n[通知]: {msg.content}")
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"执行出错: {e}")

if __name__ == "__main__":
    asyncio.run(start_janus())
