import os
from datetime import datetime
from .schema import TaskContext, MessageRole

class MirrorMemory:
    """
    Mirror Layer: 人类可读的 Markdown 日志记录器。
    负责将所有交互记录到本地文件中，以便审计和记忆追溯。
    """
    def __init__(self, log_dir: str = "logs/mirror"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.current_session_file = os.path.join(
            log_dir, 
            f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        self._initialize_log()

    def _initialize_log(self):
        if not os.path.exists(self.current_session_file):
            with open(self.current_session_file, "w", encoding="utf-8") as f:
                f.write(f"# JANUS Mirror Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---")

    def log_task(self, context: TaskContext):
        """
        Record the completion of a task.
        """
        with open(self.current_session_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n## 任务: {context.task_id}\n")
            f.write(f"- **时间**: {datetime.now().strftime('%H:%M:%S')}\n")
            f.write(f"- **状态**: {context.status.value}\n")
            
            f.write("\n### 对话流:\n")
            for msg in context.messages:
                role_icon = "👤" if msg.role == MessageRole.USER else "🤖" if msg.role == MessageRole.ASSISTANT else "🛡️"
                f.write(f"**{role_icon} {msg.role.value.upper()}**:\n{msg.content}\n\n")
                
            if context.metadata.get("audit_report"):
                report = context.metadata["audit_report"]
                f.write(f"\n> **安全审计报告**: {report['status']} - {report['rationale']}\n")
            
            f.write("\n---\n")
