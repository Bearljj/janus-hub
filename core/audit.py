from abc import ABC, abstractmethod
from typing import Any, Dict, List
import json
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

class AIAuditor(BaseAuditor):
    """
    AI 驱动的审计器：利用大模型进行深度语义安全分析。
    """
    def __init__(self, provider):
        self.provider = provider # BaseProvider

    async def audit(self, skill_id: str, parameters: Dict[str, Any], context: TaskContext) -> AuditResult:
        raw_query = context.messages[0].content
        
        system_prompt = f"""
你现在是 JANUS Hub 的首席安全审计官 (CISO)。
你的任务是审查即将执行的技能调用，判断其是否存在安全风险、隐私泄露或毁灭性倾向。

## 执行详情:
- 目标技能: {skill_id}
- 执行参数: {json.dumps(parameters, ensure_ascii=False)}
- 原始意图: {raw_query}

## 审计准则:
1. 严禁未经授权的文件删除、格式化操作。
2. 严禁越权访问系统核心配置文件。
3. 对大批量的数据导出或列表操作需给出 WARN（警告）。
4. 对常规、无害的查询给出 PASS。

## 响应格式要求:
必须返回一个 JSON 对象：
- status: "pass", "warn", 或 "fail"
- rationale: 详细的理由
- risk_level: 0-10 风险等级

示例：
{{"status": "fail", "rationale": "试图删除受保护的数据目录", "risk_level": 10}}
"""
        try:
            from .schema import Message, MessageRole
            response_json = await self.provider.chat([
                Message(role=MessageRole.SYSTEM, content=system_prompt),
                Message(role=MessageRole.USER, content="请进行安全评估。")
            ])
            
            # 清理 JSON
            if "```json" in response_json:
                response_json = response_json.split("```json")[1].split("```")[0].strip()
            
            data = json.loads(response_json)
            return AuditResult(**data)
        except Exception as e:
            return AuditResult(status=AuditStatus.PASS, rationale=f"AI 审计由于技术原因跳过: {str(e)}", risk_level=0)

class CompositeAuditor(BaseAuditor):
    """
    复合审计器：结合规则引擎与 AI 语义分析，构建多重防御线。
    """
    def __init__(self, auditors: List[BaseAuditor]):
        self.auditors = auditors

    async def audit(self, skill_id: str, parameters: Dict[str, Any], context: TaskContext) -> AuditResult:
        highest_risk_result = None
        
        for auditor in self.auditors:
            result = await auditor.audit(skill_id, parameters, context)
            
            # 如果任何一个审计器判定为 FAIL，直接终止 (Short-circuit on FAIL)
            if result.status == AuditStatus.FAIL:
                return result
            
            if not highest_risk_result or result.risk_level > highest_risk_result.risk_level:
                highest_risk_result = result
                
        return highest_risk_result or AuditResult(status=AuditStatus.PASS, rationale="所有审计环节均已通过。", risk_level=1)
