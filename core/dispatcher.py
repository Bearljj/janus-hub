import uuid
from typing import Dict, List, Optional
from .schema import AgentSkill, Intent, TaskContext, Message, MessageRole, TaskStatus
from .provider import BaseProvider
from .executor import BaseExecutor

class Dispatcher:
    """
    The Orchestration Engine of JANUS Hub (调度中枢)
    Responsible for Skill registration, Intent Resolution, and Task Routing.
    """

    def __init__(self, provider: BaseProvider):
        self.provider = provider
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
            messages=[Message(role=MessageRole.USER, content=query)]
        )
        self.active_tasks[task_id] = context
        
        print(f"[调度器] 任务 {task_id} 已创建。目标: {intent.target_skill_id or '通用(General)'}")
        
        # 3. Execution (执行)
        if intent.target_skill_id and intent.target_skill_id in self.skill_executors:
            context.status = TaskStatus.RUNNING
            executor = self.skill_executors[intent.target_skill_id]
            
            # TODO: Add Audit Layer here in Phase 2
            
            try:
                result = await executor.execute(
                    skill_id=intent.target_skill_id,
                    parameters=intent.parameters,
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
