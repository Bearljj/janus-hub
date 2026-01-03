from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Enums (状态与类型) ---

class MessageRole(str, Enum):
    """
    Message roles in a conversation (会话中的角色)
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class TaskStatus(str, Enum):
    """
    Status of a task execution (任务执行状态)
    """
    PENDING = "pending"
    AUDITING = "auditing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected" # 审计拒绝
    WAITING = "waiting"   # 等待大脑协同 (SOS)

class AuditStatus(str, Enum):
    """
    Status of a security audit (安全审计状态)
    """
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"

# --- Core Models (核心模型) ---

class AuditResult(BaseModel):
    """
    Detailed report of a security audit (安全审计报告)
    """
    status: AuditStatus
    rationale: str = Field(..., description="审计理由")
    suggested_changes: Optional[str] = None
    risk_level: int = Field(0, ge=0, le=10) # 0-10 风险等级

class AgentSkill(BaseModel):
    """
    Definition of an Agent's capability (智能体技能定义)
    Follows the ADK-inspired AgentCard schema.
    """
    id: str = Field(..., description="Unique ID of the skill")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Detailed description for the orchestrator")
    tags: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list, description="Usage examples for AI reasoning")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for inputs")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for outputs")

class Message(BaseModel):
    """
    A single exchange in a conversation (单个会话消息)
    """
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Intent(BaseModel):
    """
    Resolved user intent (解析后的用户意图)
    Produced by the Dispatcher.
    """
    raw_query: str
    thought_process: str = Field(..., description="The logic behind the dispatch decision")
    target_skill_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(0.0, ge=0.0, le=1.0)

class TaskContext(BaseModel):
    """
    The context carried throughout a task lifecycle (任务生命周期中的上下文)
    """
    task_id: str
    messages: List[Message] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    artifacts: List[str] = Field(default_factory=list, description="Paths to generated files/data")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    dispatcher: Any = None # 核心进化：允许动态技能回调调度器
