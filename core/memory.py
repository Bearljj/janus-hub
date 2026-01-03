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
            
            # 物理落盘保障 (Physical Disk Persistence)
            f.flush()
            os.fsync(f.fileno())
            print(f"[记忆层] 任务 {context.task_id[:8]} 已物理固化至镜像日志。")

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

# --- [AI-SAFEGUARD]: L4 记忆分层体系锁定 (DNA.md #2) ---
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
                data = json.load(f)
                # --- [AI-SAFEGUARD]: 数据分层逻辑锁定 (DNA.md #2) ---
                # 严禁将 L1-L4 层级合并。这种物理隔离保障了记忆的蒸馏路径。
                if "facts" in data:
                    print(f"[知识层] 识别到旧版扁平结构，正在执行物理分层迁移...")
                    new_struct = {
                        "episodic": [],   # L1/L2: 情境记忆 (短时)
                        "conceptual": [], # L3: 概念记忆 (架构, 规则)
                        "semantic": [],   # L4: 语义记忆 (永恒事实)
                        "preference": [], # L5: 偏好记忆 (用户习惯)
                        "last_updated": data.get("last_updated")
                    }
                    for fact in data["facts"]:
                        cat = fact.get("category", "")
                        # 启发式迁移逻辑
                        if "Preference" in cat: layer = "preference"
                        elif "Perception" in cat: layer = "episodic"
                        elif cat in ["SystemRoadmap", "Infrastructure", "Evolution"]: layer = "conceptual"
                        else: layer = "semantic"
                        new_struct[layer].append(fact)
                    return new_struct
                
                # 确保全层级存在 (Immutability Check)
                for k in ["episodic", "conceptual", "semantic", "preference"]:
                    if k not in data: data[k] = []
                return data
        
        return {
            "episodic": [], 
            "conceptual": [], 
            "semantic": [], 
            "preference": [],
            "last_updated": None
        }

    def _save(self):
        self.data["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
            # print(f"[知识层] 影子事实已同步至持久化存储。")

    def add_fact(self, category: str, content: str, source_task: str, layer: str = "episodic"):
        """
        记录一个新事实。
        layer: [episodic, conceptual, semantic, preference]
        """
        if layer not in self.data:
            layer = "episodic"

        # 1. 简单重构去重 (Deduplication)
        # 检查该层最后 50 条事实
        for fact in self.data[layer][-50:]:
            if fact["category"] == category and fact["content"] == content:
                try:
                    last_time = datetime.strptime(fact["timestamp"], '%Y-%m-%d %H:%M:%S')
                    # 对相同内容的事实，300秒内不重复记录（除非是关键状态变更）
                    if (datetime.now() - last_time).total_seconds() < 300:
                        return
                except:
                    return

        # 2. 插入新事实 (Insertion)
        self.data[layer].append({
            "category": category,
            "content": content,
            "source": source_task,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self._save()
        # 3. 自动维护 (Auto-Maintenance)
        self.prune_facts()

    def query_facts(self, keyword: str, layer: str = None) -> List[dict]:
        """
        跨层级事实查询。
        """
        results = []
        keywords = keyword.lower().split()
        
        # 确定搜索范围
        target_layers = [layer] if layer and layer in self.data else ["preference", "semantic", "conceptual", "episodic"]
        
        for lyr in target_layers:
            if lyr == "last_updated": continue
            for fact in self.data[lyr]:
                fact_str = f"{fact['category']} {fact['content']}".lower()
                if all(k in fact_str for k in keywords):
                    # 注入层级信息供前端展示
                    fact_with_layer = fact.copy()
                    fact_with_layer["_layer"] = lyr
                    results.append(fact_with_layer)
                
        return results

    def prune_facts(self):
        """
        [AI-SAFEGUARD]: 遗忘与修剪算法锁定。
        - Episodic: 时间代谢 (24h)
        - Conceptual/Semantic: 容量管理
        禁止将修剪逻辑通用化，不同层级的生命周期截然不同。
        """
        # 1. 情境决策：代谢超过 24 小时的记录 (Episodic Pruning)
        cutoff = 86400 # 24 小时
        now = datetime.now()
        
        original_len = len(self.data["episodic"])
        self.data["episodic"] = [
            f for f in self.data["episodic"]
            if (now - datetime.strptime(f["timestamp"], '%Y-%m-%d %H:%M:%S')).total_seconds() < cutoff
        ]
        
        # 2. 容量限制 (Capacity Pruning)
        for lyr in ["conceptual", "semantic", "preference"]:
            max_size = 500 if lyr == "conceptual" else 200
            if len(self.data[lyr]) > max_size:
                self.data[lyr] = self.data[lyr][-max_size:]

        if len(self.data["episodic"]) != original_len:
            self._save()

