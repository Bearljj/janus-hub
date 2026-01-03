import asyncio
import collections
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from .schema import Message, MessageRole, TaskStatus

class PerceptionEvent:
    """单个感知事件 (A single perception unit)"""
    def __init__(self, source: str, content: Any, importance: float = 0.1):
        self.timestamp = datetime.now()
        self.source = source
        self.content = content
        self.importance = importance # 0.0 - 1.0

class PerceptionBus:
    """
    JANUS 感知总线 (Real-time Perception Bus)
    负责汇聚来自耳朵、眼睛、系统的实时流，并进行初步语义压缩。
    """
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        # 瞬时环形缓冲区 (Transient Buffer): 只保留最近 50 条原始感知记录
        self.transient_log = collections.deque(maxlen=50)
        self.suggestion_cooldown = {} # {(rule_id, msg): last_time}
        self.running = False
        
        # --- 聚合机制 (Aggregation State) ---
        self._visual_buffer = []
        self._visual_flush_task = None
        self._visual_lock = asyncio.Lock()
        
        # --- 动态反射逻辑 (Dynamic Reflexes) ---
        self.reflex_rules = []
        self.load_rules()

    def load_rules(self):
        """从 L4 知识库中弹性加载反射规则"""
        import json
        # 1. 系统核心基因 (Baseline Genes)
        self.reflex_rules = [
            {
                "id": "sys_disk_panic",
                "source": "system",
                "pattern": "磁盘空间告急",
                "target_skill": "memory_cleaner",
                "template": "检测到磁盘空间紧缺 ({data})，建议启动自动清理流程。",
                "params": {"days": 7}
            },
            {
                "id": "code_refactor_suggest",
                "source": "visual",
                "pattern": ".py",
                "target_skill": "git_stats",
                "template": "检测到核心代码变更 ({data})，是否需要记录 Git 状态？",
                "params": {}
            },
            {
                "id": "code_refactor_js",
                "source": "visual",
                "pattern": ".js",
                "target_skill": "git_stats",
                "template": "检测到 JS 活动 ({data})，建议同步 Git 状态。",
                "params": {}
            }
        ]
        
        # 2. 尝试合并来自脑桥进化的规则 (Merge evolved rules)
        try:
            evolved = self.dispatcher.knowledge.query_facts("ReflexRule", layer="conceptual")
            for r in evolved:
                try:
                    rule_data = json.loads(r["content"])
                    self.reflex_rules.append(rule_data)
                except: continue
        except: pass

    async def emit(self, source: str, data: Any, importance: float = 0.5):
        """向总头发射感知信号"""
        if source == "visual":
            async with self._visual_lock:
                self._visual_buffer.append({"data": data, "importance": importance, "time": datetime.now()})
                if self._visual_flush_task:
                    self._visual_flush_task.cancel()
                self._visual_flush_task = asyncio.create_task(self._deferred_flush_visuals())
            return

        event = PerceptionEvent(source, data, importance)
        print(f"📡 [总线调试] 收到来自 {source} 的信号: {str(data)[:50]}...")
        await self._process_event(event)

    async def _deferred_flush_visuals(self):
        """语义聚合：将碎片的信号合并为宏观认知"""
        try:
            await asyncio.sleep(1.0)
            async with self._visual_lock:
                if not self._visual_buffer: return
                
                count = len(self._visual_buffer)
                avg_imp = sum(e["importance"] for e in self._visual_buffer) / count
                
                # 聚合路径信息
                paths = []
                for e in self._visual_buffer:
                    if ":" in str(e["data"]):
                        paths.append(str(e["data"]).split(":")[-1].strip())
                
                distinct = list(set(paths))
                if count > 1:
                    summary = f"检测到批量活动 ({count} 项变更): {', '.join(distinct[:2])}"
                    if len(distinct) > 2: summary += " 等"
                else:
                    summary = str(self._visual_buffer[0]["data"])
                
                self._visual_buffer = []
                self._visual_flush_task = None
                
            event = PerceptionEvent("visual", summary, avg_imp)
            await self._process_event(event)
        except asyncio.CancelledError:
            pass

    async def _process_event(self, event: PerceptionEvent):
        """核心处理链路"""
        self.transient_log.append(event)
        
        # 1. 记忆固化
        if event.importance > 0.7:
            self.dispatcher.knowledge.add_fact(
                "Perception", 
                f"[{event.source.upper()}] {str(event.content)}", 
                "PerceptionBus", 
                layer="episodic"
            )

        # 2. 规则映射
        await self._check_reflexes(event)

    async def _check_reflexes(self, event: PerceptionEvent):
        """遍历反射逻辑组"""
        trigger_msg = str(event.content)
        import time, uuid
        from .schema import TaskContext, Message, MessageRole, TaskStatus
        from prompt_toolkit import print_formatted_text, HTML
        import sys

        for rule in self.reflex_rules:
            print(f"🔍 [匹配中] RuleSource: {rule['source']} == {event.source}?, Pattern: {rule['pattern']} in {trigger_msg[:50]}?")
            if event.source != rule["source"]: continue
            if rule["pattern"].lower() not in trigger_msg.lower(): continue

            # 冷却与防抖
            cooldown_key = f"reflex_{rule['id']}"
            if time.time() - self.suggestion_cooldown.get(cooldown_key, 0) < 5: continue
            
            # 避免多重建议 (自律通道拥有完全并发权)
            if not rule.get("is_auto_run"):
                if any(tid.startswith("reflex_") for tid in self.dispatcher.active_tasks): return

            self.suggestion_cooldown[cooldown_key] = time.time()
            suggestion_msg = rule["template"].format(data=trigger_msg)
            
            context = TaskContext(
                task_id=f"reflex_{uuid.uuid4().hex[:6]}",
                status=TaskStatus.AUDITING,
                messages=[Message(role=MessageRole.SYSTEM, content=suggestion_msg)],
                metadata={
                    "is_suggestion": not rule.get("is_auto_run", False),
                    "is_background": rule.get("is_auto_run", False),
                    "trigger_event": event.__dict__,
                    "intent": { "target_skill_id": rule["target_skill"], "parameters": rule.get("params", {}) }
                }
            )

            if rule.get("is_auto_run"):
                print_formatted_text(HTML(f"\n<ansigreen>⚡ [自律快速通道] 逻辑命中: '{rule['id']}' 正在自动执行...</ansigreen>"))
                self.dispatcher.active_tasks[context.task_id] = context
                asyncio.create_task(self.dispatcher.execute_task(context))
            else:
                self.dispatcher.active_tasks[context.task_id] = context
                print_formatted_text(HTML(f"\n<ansiyellow>⚡ [反射中枢]: {suggestion_msg} [y/n]</ansiyellow>"))
            
            sys.stdout.flush()
            break

    def get_recent_snapshot(self) -> str:
        """获取深度感知快照 (Deep Context Snapshot)"""
        if not self.transient_log:
            return "当前感知环境：静默。"
        
        summary = "📋 [近期感知上下文缓存]:\n"
        # 提取最近 10 条，并进行语义截断
        for e in list(self.transient_log)[-10:]:
            summary += f"- {e.timestamp.strftime('%H:%M:%S')} [{e.source}] {str(e.content)[:60]}\n"
        return summary
