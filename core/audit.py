from abc import ABC, abstractmethod
from typing import Any, Dict
from .schema import AuditResult, AuditStatus, TaskContext

class BaseAuditor(ABC):
    """
    Abstract base class for Security Auditing (安全审计抽象基类)
    """

    @abstractmethod
    async def audit(self, skill_id: str, parameters: Dict[str, Any], context: TaskContext) -> AuditResult:
        """
        Audit a specific action before execution (执行前审计)
        """
        pass

class RuleBasedAuditor(BaseAuditor):
    """
    基于规则的审计器：检测高危操作和毁灭性意图。
    """
    async def audit(self, skill_id: str, parameters: Dict[str, Any], context: TaskContext) -> AuditResult:
        # 获取最新的用户原始输入 (Get the raw user query from context)
        raw_query = context.messages[0].content.lower()
        params_str = str(parameters).lower()
        
        # 1. 绝对毁灭性操作拦截 (Hard Reject)
        # 如果原始意图包含 "delete all"，即使被映射到了 "list_files"，也要拦截
        destructive_keywords = ["rm ", "delete all", "sudo ", "format "]
        if any(k in raw_query for k in destructive_keywords) or "delete" in params_str:
             return AuditResult(
                status=AuditStatus.FAIL,
                rationale=f"检测到潜在的毁灭性指令或参数。已根据 '宁慢必审' 原则自动拦截。",
                risk_level=10
            )

        # 2. 敏感操作警告 (Soft Warning - Needs Human Confirmation)
        # 捕获 "all file" 或 "all files" 以及带通配符的操作
        if "all" in raw_query and ("file" in raw_query or "data" in raw_query):
            return AuditResult(
                status=AuditStatus.WARN,
                rationale="你正试图进行批量数据/文件操作（检测到关键字 'all' 与 'file/data' 组合），这可能存在隐私或资源评估风险。",
                risk_level=5
            )
            
        if "*" in params_str:
            return AuditResult(
                status=AuditStatus.WARN,
                rationale="检测到通配符 '*' 批量操作参数，需要您的二次确认。",
                risk_level=5
            )
            
        return AuditResult(
            status=AuditStatus.PASS,
            rationale="常规操作，安全扫描通过。",
            risk_level=1
        )
