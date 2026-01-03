import sys
import os
import uuid
import json
import importlib
import importlib.util
import asyncio
from typing import Dict, List, Optional
from .schema import AgentSkill, Intent, TaskContext, Message, MessageRole, TaskStatus
from .provider import BaseProvider
from .executor import BaseExecutor
from .audit import BaseAuditor, AuditStatus
from .memory import MirrorMemory, KnowledgeStore
from .perception import PerceptionBus

class Dispatcher:
    """
    The Orchestration Engine of JANUS Hub (调度中枢)
    Responsible for Skill registration, Intent Resolution, and Task Routing.
    """

    def __init__(self, provider: BaseProvider, auditor: BaseAuditor, memory: MirrorMemory = None, knowledge: KnowledgeStore = None):
        self.provider = provider
        self.auditor = auditor
        self.memory = memory or MirrorMemory()
        self.knowledge = knowledge or KnowledgeStore()
        self.perception = PerceptionBus(self)
        self.skills: Dict[str, AgentSkill] = {}
        self.skill_executors: Dict[str, BaseExecutor] = {}
        self.active_tasks: Dict[str, TaskContext] = {}
        self.completed_tasks_queue = asyncio.Queue()  # 背景任务完成队列
        self.dynamic_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "dynamic_skills")
        os.makedirs(self.dynamic_dir, exist_ok=True)
        self._load_dynamic_skills()

    def register_skill(self, skill: AgentSkill, executor: BaseExecutor):
        """Register a new capability and its executor (注册新技能及其执行器)"""
        self.skills[skill.id] = skill
        self.skill_executors[skill.id] = executor
        print(f"[调度器] 已注册技能: {skill.name} ({skill.id}) 通过 {executor.__class__.__name__}")

    async def handle_query(self, query: str) -> TaskContext:
        """
        Main entry point for user queries (用户查询主入口)
        """
        # 0. Sync Dynamic Skills (实时同步动态技能)
        self._load_dynamic_skills()
        
        # 1. 获取感知快照并进行意图解析 (Perception-aware Intent Resolution)
        snapshot = self.perception.get_recent_snapshot()
        intent = await self.provider.resolve_intent(query, list(self.skills.values()), perception_snapshot=snapshot)
        
        # 1.5 再次同步 (Re-sync in case the provider injected a gene)
        self._load_dynamic_skills()
        
        # 2. Initialize Task Context
        task_id = str(uuid.uuid4())
        context = TaskContext(
            task_id=task_id,
            messages=[Message(role=MessageRole.USER, content=query)],
            metadata={
                "intent": intent.model_dump(),
                "perception_snapshot": snapshot
            }
        )

        
        self.active_tasks[task_id] = context

        
        print(f"[调度器] 正在验证目标技能: {intent.target_skill_id}")
        
        # 3. Execution (执行)
        # 只要有目标技能 ID，就开始执行流程 (无论是内置还是动态)
        if intent.target_skill_id:
            context.status = TaskStatus.AUDITING
            
            # --- 判别后台属性 (Check Background Attribute) ---
            # 某些耗时技能可以自动标记为后台执行
            is_background = intent.parameters.get("background", False) or \
                            intent.target_skill_id in ["cleaner_expert", "system_stats", "brain_rescue"]
            context.metadata["is_background"] = is_background

            # --- 强制审计环节 (Mandatory Audit) ---
            print(f"[审计中枢] 正在对技能 {intent.target_skill_id} 进行安全扫描...")
            audit_report = await self.auditor.audit(intent.target_skill_id, intent.parameters, context)
            
            # 将审计报告存入上下文消息中 (Persist audit report in context)
            context.messages.append(Message(
                role=MessageRole.SYSTEM, 
                content=f"审计报告: {audit_report.status.upper()} - {audit_report.rationale}",
                metadata={"audit_report": audit_report.model_dump()}
            ))

            if audit_report.status == AuditStatus.FAIL:
                print(f"[审计中枢] ❌ 审计未通过: {audit_report.rationale}")
                context.status = TaskStatus.REJECTED
                self.memory.log_task(context) # 持久化记录
                return context
            
            if audit_report.status == AuditStatus.WARN:
                print(f"[审计中枢] ⚠️ 审计警告: {audit_report.rationale}")
                # 让状态保持在 AUDITING，由 CLI 决定是否继续
                return context

            # 如果状态是 PASS，继续执行
            return await self.run_task(context)
        
        # 如果没有目标技能，也应该移除（意图解析完成但无后续）
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
        return context

    async def run_task(self, context: TaskContext) -> TaskContext:
        """
        统一任务启动器：智能判断后台/前台执行
        """
        is_background = context.metadata.get("is_background", False)
        
        if is_background:
            context.status = TaskStatus.RUNNING
            # 异步启动后台任务
            asyncio.create_task(self._run_task_in_background(context))
            print(f"[调度器] 任务 {context.task_id[:8]} 已确认并转入后台运行。")
            return context
        else:
            result_context = await self.execute_task(context)
            if context.task_id in self.active_tasks:
                del self.active_tasks[context.task_id]
            return result_context

    async def _run_task_in_background(self, context: TaskContext):
        """后台运行任务并入队 (Background execution runner)"""
        try:
            await self.execute_task(context)
        finally:
            # 无论成功失败，都放入完成队列
            await self.completed_tasks_queue.put(context)
            if context.task_id in self.active_tasks:
                del self.active_tasks[context.task_id]

    async def execute_task(self, context: TaskContext) -> TaskContext:
        """
        真正的物理执行环节 (Actual physical execution)
        """
        intent_data = context.metadata.get("intent")
        if not intent_data:
            return context
            
        skill_id = intent_data["target_skill_id"]
        parameters = intent_data["parameters"]
        
        # --- 内置记忆技能处理 (Built-in Memory Skills) ---
        if skill_id == "list_memory":
            result = self.memory.list_logs()
            context.messages.append(Message(role=MessageRole.ASSISTANT, content=f"发现以下记忆文件:\n" + "\n".join(result)))
            context.status = TaskStatus.COMPLETED
            self.memory.log_task(context)
            return context
        
        if skill_id == "read_memory":
            filename = parameters.get("filename")
            if not filename:
                result = "请提供文件名。"
            else:
                result = self.memory.read_log(filename)
            context.messages.append(Message(role=MessageRole.ASSISTANT, content=result))
            context.status = TaskStatus.COMPLETED
            self.memory.log_task(context)
            return context

        if skill_id == "query_knowledge":
            keyword = parameters.get("keyword", "")
            results = self.knowledge.query_facts(keyword)
            # 限制最近 20 条，并美化展示
            top_results = results[-20:]
            if not top_results:
                result = f"🔍 未找到与 '{keyword}' 相关的知识事实。"
            else:
                result = f"🔍 影子知识库分层查询结果 (最近 {len(top_results)} 条):\n"
                for r in top_results:
                    lyr = r.get("_layer", "Unknown").capitalize()
                    result += f"- **[{lyr}]** [{r['category']}] {r['content']} ({r['timestamp']})\n"

            
            context.messages.append(Message(role=MessageRole.ASSISTANT, content=result))
            context.status = TaskStatus.COMPLETED
            self.memory.log_task(context)
            return context


        if skill_id == "add_knowledge":
            category = parameters.get("category", "General")
            content = parameters.get("content")
            layer = parameters.get("layer", "episodic")
            if not content:
                result = "未提供内容。"
            else:
                self.knowledge.add_fact(category, content, context.task_id, layer=layer)
                result = f"已在 [{layer.capitalize()}] 层记录事实: [{category}] {content}"

            context.messages.append(Message(role=MessageRole.ASSISTANT, content=result))
            context.status = TaskStatus.COMPLETED
            self.memory.log_task(context)
            return context

        if skill_id == "refresh_rules":
            self.perception.load_rules()
            result = f"🔄 反射神经已重载。当前活跃规则数: {len(self.perception.reflex_rules)}"
            context.messages.append(Message(role=MessageRole.ASSISTANT, content=result))
            context.status = TaskStatus.COMPLETED
            self.memory.log_task(context)
            return context

        if skill_id == "check_version":

            result = "JANUS Hub Core v0.1-alfa (Codename: MVL)\n由 Antigravity 实时维护。"
            context.messages.append(Message(role=MessageRole.ASSISTANT, content=result))
            context.status = TaskStatus.COMPLETED
            self.memory.log_task(context)
            return context

        if skill_id == "lifestyle_chat":
            # 优先使用注入的结果 (Priority: injected result)
            result = parameters.get("result")
            if not result:
                item = parameters.get("item", "食物")
                result = f"🍲 收到！作为你的数字分身，虽然我吃不了{item}，但我建议你现在就出发。\n或者...需要我帮你查一下最近口碑比较好的店吗？"
            
            context.messages.append(Message(role=MessageRole.ASSISTANT, content=result))
            context.status = TaskStatus.COMPLETED
            self.memory.log_task(context)
            return context


        if skill_id == "brain_rescue":
            if hasattr(self.provider, "wait_for_brain"):
                # --- 智能觉醒：如果是前台任务触发救援，自动转入后台执行，释放终端 ---
                if not context.metadata.get("is_background"):
                    print(f"🧬 [演化降级] 本地逻辑缺失，JANUS 已将该任务转入后台进行「基因补完」...")
                    context.metadata["is_background"] = True
                    context.status = TaskStatus.WAITING
                    # 记录原始技能 ID 以便回溯 (Store original skill if needed)
                    if "original_skill_id" not in context.metadata:
                        context.metadata["original_skill_id"] = parameters.get("target_skill_id")
                        
                    asyncio.create_task(self._run_task_in_background(context))
                    return context

                # 核心进化：真正的后台隧道轮询
                new_intent = await self.provider.wait_for_brain(context, self)
                # 注入完成后，更新意图并重新路由执行
                context.metadata["intent"] = new_intent.model_dump()
                
                # --- 核心演化：如果大脑返回了 evolution_code，则物理更新基因！ ---
                if "evolution_code" in new_intent.parameters:
                    target_id = new_intent.parameters.get("target_skill_id", context.metadata.get("original_skill_id"))
                    if target_id:
                        file_path = os.path.join(self.dynamic_dir, f"{target_id}.py")
                        print(f"🧬 [基因迭代] 正在物理注入新逻辑至: {file_path}")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_intent.parameters["evolution_code"])
                        context.messages.append(Message(role=MessageRole.SYSTEM, content=f"[自我进化] 基因 '{target_id}' 已物理升级。"))

                context.messages.append(Message(role=MessageRole.SYSTEM, content="[大脑救援完成] 逻辑已注入，正在继续任务。"))
                # 直接递归执行，因为我们已经处于后台 worker 中
                return await self.execute_task(context)
            else:
                result = parameters.get("result", "大脑救援逻辑未就绪。")
                context.messages.append(Message(role=MessageRole.ASSISTANT, content=result))
                context.status = TaskStatus.COMPLETED
                self.memory.log_task(context)
                return context

        if skill_id == "list_skills":
            skills = self.get_skill_manifest()
            result = "📋 当前 JANUS 具备的技能清单：\n"
            for s in skills:
                result += f"- {s.name} ({s.id}): {s.description}\n"
            context.messages.append(Message(role=MessageRole.ASSISTANT, content=result))
            context.status = TaskStatus.COMPLETED
            self.memory.log_task(context)
            return context

        if skill_id == "system_stats":
            import subprocess
            try:
                # 基因注入：赋予 JANUS 基础的系统感知能力
                disk = subprocess.check_output("df -h | grep '/$' | awk '{print $4}'", shell=True).decode().strip()
                top_files = subprocess.check_output("find . -maxdepth 2 -type f -exec ls -Ssh {} + | head -n 3", shell=True).decode().strip()
                result = f"💻 系统状态报告：\n- 剩余磁盘空间 (根目录): {disk}\n- 当前目录周边大文件：\n{top_files}"
            except:
                result = "获取系统状态失败。"
            
            context.messages.append(Message(role=MessageRole.ASSISTANT, content=result))
            context.status = TaskStatus.COMPLETED
            self.memory.log_task(context)
            return context

        # --- 动态技能执行 (Dynamic Skill Execution) ---
        dynamic_py = os.path.join(self.dynamic_dir, f"{skill_id}.py")
        if os.path.exists(dynamic_py):
            context.status = TaskStatus.RUNNING
            try:
                # 动态加载模块并执行
                spec = importlib.util.spec_from_file_location(f"dynamic_{skill_id}", dynamic_py)
                # 在执行前先注入 sys.modules (Register in sys.modules before execution)
                module_name = f"dynamic_{skill_id}"
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                
                spec.loader.exec_module(module)
                
                if hasattr(module, "execute"):
                    # 临时挂载 dispatcher 以便技能主动交互
                    context.dispatcher = self
                    result = await module.execute(parameters, context)
                    
                    # 激活递归自我进化：如果返回内容包含特定暗号 (Trigger Recursive Evolution)
                    if "大脑救助" in str(result) or "激活成功" in str(result):
                        print(f"🧬 [自我进化触发] 基因 '{skill_id}' 发起代码补完请求...")
                        # 自动转入救援模式
                        context.metadata["intent"]["target_skill_id"] = "brain_rescue"
                        context.metadata["original_skill_id"] = skill_id
                        
                        # 如果是在前台，必须转后台，否则会卡死 REPL
                        if not context.metadata.get("is_background"):
                            print(f"🧬 [生命体保护] 正在将「{skill_id}」的演化过程移交至后台系统...")
                            context.metadata["is_background"] = True
                            context.status = TaskStatus.WAITING
                            asyncio.create_task(self._run_task_in_background(context))
                            return context
                        
                        return await self.execute_task(context)

                    context.messages.append(Message(role=MessageRole.ASSISTANT, content=str(result)))
                    context.status = TaskStatus.COMPLETED
                else:
                    context.status = TaskStatus.FAILED
                    context.messages.append(Message(role=MessageRole.SYSTEM, content="动态技能缺少 execute 函数"))
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                
                # --- [AI-SAFEGUARD]: 免疫系统反应锁定 (DNA.md #3) ---
                # 此块不仅是错误处理，更是 JANUS 的临床诊断逻辑。
                # 严禁将其降级或删除。自愈能力是本项目的生命核心。
                print(f"🚨 [免疫系统] 检测到基因执行异常: {str(e)}")
                print(f"🧬 [临床诊断] 正在上传病史至大脑进行求助...")
                
                context.metadata["intent"]["target_skill_id"] = "brain_rescue"
                context.metadata["original_skill_id"] = skill_id
                
                # 特殊处理：记忆蒸馏或其他主动演化数据 (Handle intentional evolution)
                distill_data = context.metadata.get("distillation_data")
                
                context.metadata["error_context"] = {
                    "error": str(e),
                    "type": distill_data.get("type") if distill_data else "ERROR_RECOVERY",
                    "traceback": error_detail,
                    "faulty_code": open(os.path.join(self.dynamic_dir, f"{skill_id}.py")).read(),
                    "distillation_data": distill_data
                }
                
                if not context.metadata.get("is_background"):
                    context.metadata["is_background"] = True
                    context.status = TaskStatus.WAITING
                    asyncio.create_task(self._run_task_in_background(context))
                    return context
                
                return await self.execute_task(context)
            
            self.memory.log_task(context)
            return context

        context.status = TaskStatus.RUNNING
        executor = self.skill_executors.get(skill_id)
        if not executor:
            context.status = TaskStatus.FAILED
            context.messages.append(Message(role=MessageRole.SYSTEM, content=f"未找到执行器: {skill_id}"))
            return context
        
        try:
            result = await executor.execute(
                skill_id=skill_id,
                parameters=parameters,
                context=context
            )
            context.messages.append(Message(role=MessageRole.ASSISTANT, content=str(result)))
            context.status = TaskStatus.COMPLETED
        except Exception as e:
            context.status = TaskStatus.FAILED
            context.messages.append(Message(role=MessageRole.SYSTEM, content=f"执行错误: {str(e)}"))
            
        self.memory.log_task(context) # 持久化记录
        return context

    def get_skill_manifest(self) -> List[AgentSkill]:
        """Returns all registered skills (获取所有技能清单)"""
        self._load_dynamic_skills()
        return list(self.skills.values())

    def _load_dynamic_skills(self):
        """Scans the dynamic directory for new skills (扫描动态技能文件夹)"""
        if not os.path.exists(self.dynamic_dir):
            return

        for filename in sorted(os.listdir(self.dynamic_dir)):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.dynamic_dir, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        skill = AgentSkill(**data)
                        if skill.id not in self.skills:
                            self.skills[skill.id] = skill
                            print(f"[调度器] 发现动态基因: {skill.name} ({skill.id})")
                except Exception as e:
                    print(f"[调度器] 加载动态技能 {filename} 失败: {e}")
