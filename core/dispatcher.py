import uuid
from typing import Dict, List, Optional
from .schema import AgentSkill, Intent, TaskContext, Message, MessageRole, TaskStatus
from .provider import BaseProvider
from .executor import BaseExecutor
from .audit import BaseAuditor, AuditStatus

class Dispatcher:
    """
    The Orchestration Engine of JANUS Hub (调度中枢)
    Responsible for Skill registration, Intent Resolution, and Task Routing.
    """

    def __init__(self, provider: BaseProvider, auditor: BaseAuditor):
        self.provider = provider
        self.auditor = auditor
        self.skills: Dict[str, AgentSkill] = {}
        self.skill_executors: Dict[str, BaseExecutor] = {}
        self.active_tasks: Dict[str, TaskContext] = {}

    def register_skill(self, skill: AgentSkill, executor: BaseExecutor):
        """Register a new capability and its executor (注册新技能及其执行器)"""
        self.skills[skill.id] = skill
        self.skill_executors[skill.id] = executor
        print(f"[调度器] 已注册技能: {skill.name} ({skill.id}) 通过 {executor.__class__.__name__}")

    async def handle_query(self, query: str) -> TaskContext:
        """
        Main entry point for user queries (用户查询主入口)
        """
        # 1. Resolve Intent (意图解析)
        intent = await self.provider.resolve_intent(query, list(self.skills.values()))
        
        # 2. Initialize Task Context
        task_id = str(uuid.uuid4())
        context = TaskContext(
            task_id=task_id,
            messages=[Message(role=MessageRole.USER, content=query)],
            metadata={"intent": intent.dict()} # Store intent for potential resume
        )
        self.active_tasks[task_id] = context
        
        print(f"[调度器] 任务 {task_id} 已创建。目标: {intent.target_skill_id or '通用(General)'}")
        
        # 3. Execution (执行)
        if intent.target_skill_id and intent.target_skill_id in self.skill_executors:
            context.status = TaskStatus.AUDITING
            
            # --- 强制审计环节 (Mandatory Audit) ---
            print(f"[审计中枢] 正在对技能 {intent.target_skill_id} 进行安全扫描...")
            audit_report = await self.auditor.audit(intent.target_skill_id, intent.parameters, context)
            
            # 将审计报告存入上下文消息中 (Persist audit report in context)
            context.messages.append(Message(
                role=MessageRole.SYSTEM, 
                content=f"审计报告: {audit_report.status.upper()} - {audit_report.rationale}",
                metadata={"audit_report": audit_report.dict()}
            ))

            if audit_report.status == AuditStatus.FAIL:
                print(f"[审计中枢] ❌ 审计未通过: {audit_report.rationale}")
                context.status = TaskStatus.REJECTED
                return context
            
            if audit_report.status == AuditStatus.WARN:
                print(f"[审计中枢] ⚠️ 审计警告: {audit_report.rationale}")
                # 让状态保持在 AUDITING，由 CLI 决定是否继续
                return context

            # 如果状态是 PASS，继续执行
            return await self.execute_task(context)
        
        return context

    async def execute_task(self, context: TaskContext) -> TaskContext:
        """
        真正的物理执行环节 (Actual physical execution)
        """
        intent_data = context.metadata.get("intent")
        if not intent_data:
            return context
            
        skill_id = intent_data["target_skill_id"]
        parameters = intent_data["parameters"]
        
        context.status = TaskStatus.RUNNING
        executor = self.skill_executors[skill_id]
        
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
            
        return context

    def get_skill_manifest(self) -> List[AgentSkill]:
        """Returns all registered skills (获取所有技能清单)"""
        return list(self.skills.values())
