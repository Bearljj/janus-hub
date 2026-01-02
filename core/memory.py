import os
import json
from datetime import datetime
from typing import List
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

    def list_logs(self) -> List[str]:
        """列出所有日志文件 (List all log files)"""
        import glob
        logs = glob.glob(os.path.join(self.log_dir, "*.md"))
        return sorted([os.path.basename(l) for l in logs], reverse=True)

    def read_log(self, log_filename: str) -> str:
        """读取指定日志内容 (Read specific log content)"""
        path = os.path.join(self.log_dir, log_filename)
        if not os.path.exists(path):
            return "日志文件不存在。"
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

class KnowledgeStore:
    """
    Shadow Layer: 影子知识层。
    负责存储从分析中提取的结构化事实 (Facts)。
    """
    def __init__(self, filename: str = "logs/knowledge.json"):
        self.filename = filename
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"facts": [], "last_updated": None}

    def _save(self):
        self.data["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_fact(self, category: str, content: str, source_task: str):
        """记录一个新事实"""
        self.data["facts"].append({
            "category": category,
            "content": content,
            "source": source_task,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self._save()

    def query_facts(self, keyword: str) -> List[dict]:
        """查询事实"""
        return [f for f in self.data["facts"] if keyword.lower() in str(f).lower()]
