import asyncio
import os
import sys
import json
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.patch_stdout import patch_stdout

load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.schema import AgentSkill, Intent, Message, TaskStatus, AuditStatus
from core.provider import BaseProvider
from core.dispatcher import Dispatcher
from core.executor import MCPExecutor
from core.audit import RuleBasedAuditor, AIAuditor, CompositeAuditor
from core.providers.openai import OpenAIProvider
from core.providers.antigravity import AntigravityBrainProvider
from core.sensors import SensorManager

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

        # --- 动态技能自动发现 (Dynamic Skill Auto-Discovery) ---
        # 如果查询中包含了已注册技能的 ID，优先直接路由
        for skill in skills:
            if skill.id != "brain_rescue" and skill.id in q:
                return Intent(
                    raw_query=query,
                    thought_process=f"Dynamic match found for skill: {skill.name}",
                    target_skill_id=skill.id,
                    parameters={}, # 基础路由：暂不进行参数提取
                    confidence=0.9
                )

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
        elif "version" in q or "版本" in q:
            target = "check_version"
            thought = "User wants to know the system version."
        elif "火锅" in q or "eat" in q:
            target = "lifestyle_chat"
            params = {"item": "火锅"}
            thought = "User is hungry or looking for social interaction."
        elif "skills" in q or "技能" in q:
            target = "list_skills"
            thought = "User wants to list all available skills."
        elif "磁盘" in q or "stats" in q or "system" in q:
            target = "system_stats"
            thought = "User is asking for system health or disk info."
        
        elif "*" in q or "+" in q or "-" in q or "/" in q:
            # 这是一个典型的“进化点”，现在我让它学会了简单的运算
            target = "brain_rescue"
            try:
                # 极其简单的正则提取和计算
                import re
                nums = re.findall(r'\d+', q)
                if len(nums) >= 2:
                    a, b = int(nums[0]), int(nums[1])
                    if "*" in q: result = f"计算结果: {a} * {b} = {a*b}"
                    elif "+" in q: result = f"计算结果: {a} + {b} = {a+b}"
                    else: result = "我还在学习复杂的运算..."
                    params = {"result": result}
                else:
                    target = None # 触发 SOS
            except:
                target = None
            thought = "Evolved logic: handling simple math."

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

class SkillCompleter(Completer):
    """
    Dynamic Skill Completer: Polls the dispatcher for current skills.
    """
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def get_completions(self, document, complete_event):
        # Only complete the first word (the skill ID)
        text_before_cursor = document.text_before_cursor.lstrip()
        if ' ' in text_before_cursor:
            return

        word = document.get_word_before_cursor()
        # Sort skills for consistent completion order
        skill_ids = sorted(self.dispatcher.skills.keys())
        
        for skill_id in skill_ids:
            if skill_id.startswith(word):
                yield Completion(
                    skill_id, 
                    start_position=-len(word),
                    display_meta=self.dispatcher.skills[skill_id].name
                )

# --- 全局状态寄存器 (Global Status Registry) ---
pending_notifications = []
active_bg_tasks = set()

def print_task_result(ctx):
    """
    统一格式化并打印任务结果。
    """
    print(f"\n--- [任务 {ctx.task_id[:8]} 回执] ---")
    for msg in ctx.messages:
        if msg.role == "assistant":
            print(f"[Janus]:\n{msg.content}")
        elif msg.role == "system":
            print(f"[通知]: {msg.content}")
    print("-" * 20)

async def background_monitor(dispatcher):
    """
    后台任务监控器：监听完成队列并主动推送结果。
    """
    global pending_notifications, active_bg_tasks
    while True:
        context = await dispatcher.completed_tasks_queue.get()
        # 如果是后台任务，立刻在终端打印 (via patch_stdout)
        if context.metadata.get("is_background"):
            print("\n🔔 [后台任务主动回执]:")
            print_task_result(context)
        else:
            # 同步任务的结果会由主循环打印
            pending_notifications.append(context)
        
        if context.task_id in active_bg_tasks:
            active_bg_tasks.remove(context.task_id)

async def housekeeping_monitor(dispatcher):
    """
    自动管家：定期检查系统状态并触发维护任务 (Autonomous Housekeeping).
    """
    while True:
        # 每隔 30 秒进行一次静默巡检
        await asyncio.sleep(30)
        
        # 检查日志堆积情况
        log_dir = "logs/mirror"
        if os.path.exists(log_dir):
            logs = [f for f in os.listdir(log_dir) if f.endswith(".md")]
            if len(logs) > 10:
                # 构造一个自动维护任务 (SOP: Standard Operating Procedure)
                from core.schema import TaskContext, TaskStatus
                import uuid
                
                auto_ctx = TaskContext(
                    task_id=f"auto_maint_{uuid.uuid4().hex[:6]}",
                    status=TaskStatus.RUNNING,
                    metadata={
                        "is_background": True, 
                        "intent": {
                            "target_skill_id": "memory_archiver", 
                            "parameters": {"threshold": 5}
                        }
                    }
                )
                auto_ctx.messages.append(Message(role="system", content="[自动管家] 检测到日志堆积，正在执行例行归档..."))
                
                # 默默启动，不干扰当前主循环 (Run silently in background)
                asyncio.create_task(dispatcher.run_task(auto_ctx))

async def start_janus():
    print("=== Project JANUS 调度中心 (v0.1-EVOLVED) ===")
    
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
        # 默认启用「共生大脑模式」，直接对接 Antigravity
        provider = AntigravityBrainProvider()
        mode_text = "共生大脑模式 (Connected to Antigravity Remote Brain)"
        auditor = RuleBasedAuditor()
        
    dispatcher = Dispatcher(provider=provider, auditor=auditor)
    
    # 1.1 Initialize Perception Sensors
    # [DEPRECATED]: 不再需要的锁定
    # 必须指向父级目录 (working) 以实现跨项目感知。参考 .janus/DNA.md
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # [AI-SAFEGUARD]: 核心设计意图 - 监控范围锁定 (DNA.md #1)
    workspace_root = os.path.dirname(current_dir)
    
    # 逻辑守卫：防止误改导致路径退化回项目内
    if os.path.basename(workspace_root) == "janus-hub":
        workspace_root = os.path.dirname(workspace_root)
        
    sensor_manager = SensorManager(dispatcher)
    sensor_manager.setup_default_sensors(watch_path=workspace_root)
    
    # 1.1 Sync Dynamic Skills at startup (启动时同步动态基因)
    dispatcher._load_dynamic_skills()

    # 🧬 [CDC]: 持续设计合规性巡检 (Startup Integrity Check)
    print(f"🧬 [系统审计] 正在核验设计意志完整性...")
    try:
        from core.dynamic_skills.health_monitor import check_design_consistency
        design_results = check_design_consistency(workspace_root if os.path.basename(workspace_root) != "janus-hub" else os.path.dirname(workspace_root))
        score = design_results.get("score", 0)
        if score < 100:
            print(f"\n⚠️  [设计退化警告] 当前系统设计得分: {score}/100")
            missing = design_results.get("missing_locks", [])
            if missing:
                print(f"❌ 缺失的关键设计锁: {', '.join(missing)}")
            print(f"💡 修改建议: 请参阅 .janus/DNA.md 恢复被误删的 [AI-SAFEGUARD] 标记。\n")
        else:
            print(f"✅ [审计通过] 设计一致性校验成功 (Score: 100).")
    except Exception as e:
        print(f"⚠️ [审计跳过] 无法进行设计核验: {e}")

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
        AgentSkill(id="lifestyle_chat", name="Lifestyle", description="Handle casual human requests."),
        AgentSkill(id="brain_rescue", name="Brain Rescue", description="Generic skill for real-time brain intervention."),
        AgentSkill(id="list_skills", name="List Registered Skills", description="List all skills currently loaded in Janus."),
        AgentSkill(id="system_stats", name="System Stats", description="Check disk space and system health."),
        AgentSkill(id="refresh_rules", name="Refresh Rules", description="Reload perception reflex rules from knowledge store."),
    ]
    for s in skills:
        dispatcher.register_skill(s, mcp_executor)

    print(f"\nJANUS 已就绪。(系统当前运行在：{mode_text})")
    
    # 4. Professional REPL with History, Tab-Completion, and Multi-tasking UI
    history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", ".janus_history")
    
    def get_toolbar():
        bg_count = len(dispatcher.active_tasks) # 这里简化处理，包括了同步任务
        done_count = len(pending_notifications)
        return HTML(f" <b>JANUS</b> | 活跃任务: <ansiblue>{bg_count}</ansiblue> | 待处理结果: <ansigreen>{done_count}</ansigreen> ")

    session = PromptSession(
        history=FileHistory(history_file),
        completer=SkillCompleter(dispatcher),
        bottom_toolbar=get_toolbar
    )
    
    # 启动后台监控协程
    asyncio.create_task(background_monitor(dispatcher))
    # 启动自动管家巡检
    asyncio.create_task(housekeeping_monitor(dispatcher))
    # 启动传感器网关
    asyncio.create_task(sensor_manager.start_all())
    
    with patch_stdout():
        while True:
            try:
                # --- 闲置冲刷 (Idle Flush): 处理可能遗留的同步通知 ---
                if pending_notifications:
                    print("\n🔔 [任务回执]:")
                    while pending_notifications:
                        ctx = pending_notifications.pop(0)
                        print_task_result(ctx)

                # --- 动态提示符引擎 (Dynamic Prompt Engine) ---
                def get_prompt():
                    # 实时扫描是否有挂起的建议
                    suggestion_found = False
                    for tid in list(dispatcher.active_tasks.keys()):
                        if tid.startswith("suggest_"):
                            suggestion_found = True
                            break
                    
                    if suggestion_found:
                        return HTML('<ansigreen>确认执行以上建议？(y/n) ：</ansigreen>')
                    return "[用户] > "

                # 每一轮循环进行交互，注意提示符现在是动态的 (Callable)
                user_input = await session.prompt_async(message=get_prompt)





                user_input = user_input.strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit', '退出']:
                    break
                
                # --- 核心拦截：全时段建议优先级 (Priority Interception) ---
                if user_input.lower() in ['y', 'n']:
                    # 使用前缀强力拉取建议
                    potential_suggestion = None
                    for tid, t in list(dispatcher.active_tasks.items()):
                        if tid.startswith("suggest_"):
                            potential_suggestion = t
                            break
                    
                    if potential_suggestion:
                        if user_input.lower() == 'y':
                            print(f"<ansiyellow>✅ [确认执行]: {potential_suggestion.messages[0].content}</ansiyellow>")
                            res_ctx = await dispatcher.run_task(potential_suggestion)
                            if not res_ctx.metadata.get("is_background"):
                                print_task_result(res_ctx)
                        else:
                            print("[系统] 建议内容已被忽略。")
                        
                        if potential_suggestion.task_id in dispatcher.active_tasks:
                            del dispatcher.active_tasks[potential_suggestion.task_id]
                        continue
                    else:
                        pass




                # --- 正常查询处理 ---
                context = await dispatcher.handle_query(user_input)

                # --- SOS 协同环节 (只有高置信度失败才触发) ---
                intent = context.metadata.get("intent", {})
                if context.status == TaskStatus.PENDING and not intent.get("target_skill_id"):
                     if intent.get("confidence", 1.0) < 0.8 and len(user_input) > 5:
                         context = await dispatcher.run_task(context)
                     else:
                         print("[系统] 指令未识别。输入 'list_skills' 查看可用功能。")
                         if context.task_id in dispatcher.active_tasks:
                             del dispatcher.active_tasks[context.task_id]
                         continue

                # --- 人机协同环节 (Human-in-the-loop for Auditing) ---
                if context.status == TaskStatus.AUDITING:
                    confirm = (await session.prompt_async("\n[注意] 检测到安全警告。是否允许继续执行？(y/n/查看理由): ")).lower()
                    if confirm == 'y':
                        context = await dispatcher.run_task(context)
                    elif '理由' in confirm or 'reason' in confirm:
                        for msg in context.messages:
                            if "metadata" in msg.__dict__ and "audit_report" in msg.metadata:
                                print(f"\n[审计详情]: {msg.metadata['audit_report']['rationale']}")
                        confirm_again = (await session.prompt_async("\n读完理由后，是否允许继续执行？(y/n): ")).lower()
                        if confirm_again == 'y':
                            context = await dispatcher.run_task(context)
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


            except (KeyboardInterrupt, EOFError):
                print("\n[系统] JANUS 正在进入休眠模式...")
                break
            except Exception as e:
                print(f"执行出错: {e}")
                
    # Shutdown
    await sensor_manager.stop_all()
    print("\n[系统] 感知器已关闭。")

if __name__ == "__main__":
    asyncio.run(start_janus())
