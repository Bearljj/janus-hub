import os
import json
import asyncio
from typing import List
from ..schema import AgentSkill, Intent, Message, TaskStatus, TaskContext
from ..provider import BaseProvider
from datetime import datetime

class AntigravityBrainProvider(BaseProvider):
    """
    Symbiotic Brain Provider: Routes ALL intent resolution to Antigravity via SOS handshakes.
    This makes JANUS a 'hollow' agent driven entirely by the remote brain.
    """
    def __init__(self, signal_dir: str = "logs/signals"):
        self.signal_dir = signal_dir
        os.makedirs(self.signal_dir, exist_ok=True)

    async def chat(self, messages: List[Message]) -> str:
        # For Chat, we still might need an SOS-like bridge if no local brain is present
        return "Waiting for Antigravity's chat intervention..."

    async def resolve_intent(self, query: str, skills: List[AgentSkill], perception_snapshot: str = "") -> Intent:
        """
        Non-blocking Intent Resolution.
        If no local gene matches, it delegates to 'brain_rescue' which runs in background.
        """
        # --- 储存感知快照供后续使用 ---
        self.last_perception = perception_snapshot
        
        # --- 进化：自律快速通道 (Evolution: Autonomous Fast-Path) ---
        q = query.lower().strip()

        
        # 1. 拦截基础噪音与控制词 (Noise & Control Token Interception)
        # 防止简单的确认/拒绝操作触发繁重的脑桥模式
        control_tokens = {"y", "n", "yes", "no", "ok", "确认", "取消", "好的", "不", "nn", "help", "exit", "quit", "hi", "hello", "你好", "嘿", "哈喽"}
        if q in control_tokens or len(q) < 2:
            thought = "Short control token or very short query detected. Skipping heavy brain rescue."
            target = None
            if q in ["help", "你会什么", "能力"]: target = "list_skills"
            if q in ["hi", "hello", "你好", "嘿", "哈喽"]: target = "lifestyle_chat"
            
            return Intent(
                raw_query=query,
                thought_process=thought,
                target_skill_id=target,
                parameters={},
                confidence=1.0
            )

        q_words = q.split()
        best_skill = None
        highest_score = 0

        final_params = {}

        # 扩展匹配：ID、代码名、英文标签，以及新增的中文字义映射
        chinese_map = {
            "weather_expert": ["天气", "下雨", "气温"],
            "system_stats": ["磁盘", "空间", "状态"],
            "cleaner_expert": ["清理", "大文件", "扫描"],
            "datetime_expert": ["日期", "时间", "几号", "星期"],
            "list_skills": ["功能", "技能", "你会什么", "列表"],
            "self_diagnostics": ["自检", "检查", "诊断", "健康", "优化"],
            "memory_archiver": ["归档", "整理", "压缩", "清理记忆"],
            "query_knowledge": ["查询", "搜索", "寻找", "重构", "路线图", "计划"],
            "gene_factory": ["制造", "开发", "学习", "工厂", "创建技能"],
            "list_memory": ["记忆", "日志", "回顾", "记录"],
            "memory_cleaner": ["清理日志", "过期文件", "过时", "自动清理"],
            "lifestyle_chat": ["你好", "最近", "聊聊", "吃饭", "嘿"]
        }

        for skill in skills:
            if skill.id == "brain_rescue":
                continue
            
            score = 0
            # 1. 核心意图词权重 (Action Keywords)
            for kw in chinese_map.get(skill.id, []):
                if kw in q:
                    # 如果匹配词位于句首，权重极大 (High priority for starting keywords)
                    pos_bonus = 20 if q.startswith(kw) else 10
                    score += pos_bonus
            
            # 2. ID/名称直接匹配 (Direct ID/Name match)
            # 使用更严格的包含检查，防止子串误伤 (Strict ID check)
            if skill.id == q or f" {skill.id} " in f" {q} ":
                score += 30
            elif skill.id in q:
                score += 5 # 子串匹配权重较低
                
            if skill.name.lower() in q:
                score += 15
            
            # 3. 标签匹配
            for tag in skill.tags:
                if tag.lower() in q: score += 5
            
            if score > highest_score:
                highest_score = score
                best_skill = skill

        if best_skill:
            skill = best_skill
            # 增强型通用参数提取 (Generic key=value parsing)
            params = {}
            import re
            # 支持 key=value 或 key="value with spaces" 或 key='value'
            # 同时支持中文字符和更多符号
            kv_patterns = re.findall(r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))', q)
            for groups in kv_patterns:
                    k = groups[0]
                    # groups 是 (key, double_quoted, single_quoted, unquoted)
                    v = groups[1] or groups[2] or groups[3]
                    
                    # 尝试转为数字 (Try numeric conversion)
                    if v.isdigit(): params[k] = int(v)
                    else: params[k] = v
                
            # 如果没找到 key=value，尝试抓取第一个独立的引号内容作为 'text' (Positional capture)
            if not params:
                standalone_quote = re.search(r'(?<!=)["\']([^"\']+)["\']', q)
                if standalone_quote:
                    params["text"] = standalone_quote.group(1)
                    params["query"] = standalone_quote.group(1)
            
            # 语义参数识别演进
            time_keywords = {"今天": "today", "明天": "tomorrow", "后天": "day_after_tomorrow"}
            for k, v in time_keywords.items():
                if k in q:
                    params["day"] = k
                    break

            print(f"⚡ [自律快速通道] 逻辑命中: '{skill.name}' ({skill.id})")
            return Intent(
                raw_query=query,
                thought_process=f"Autonomous match: Keywords/Chinese-Semantics matched with gene '{skill.id}'.",
                target_skill_id=skill.id,
                parameters=params,
                confidence=0.9
            )

        # --- 环境适应：后台化求助 (Evolution: Background Rescue) ---
        # 核心优化：只有当输入具有一定“指令感”时（长度 > 5 或包含明确述求关键词），
        # 才触发昂贵的后台 SOS 救援，否则视为未命中。
        action_keywords = ["帮我", "如何", "怎么", "实现", "分析", "写个", "查询", "查找", "总结"]
        if len(q) > 5 or any(k in q for k in action_keywords):
            print(f"\n🧠 [脑桥模式] 本地基因集不足，正在挂载后台救援隧道...")
            return Intent(
                raw_query=query,
                thought_process="Local match failed. Delegating to background SOS rescue polling.",
                target_skill_id="brain_rescue",
                parameters={
                    "query": query,
                    "perception_snapshot": getattr(self, "last_perception", "")
                },
                confidence=0.5
            )
        
        return Intent(
            raw_query=query,
            thought_process="Query too short or casual. No skill matched.",
            target_skill_id=None,
            confidence=0.0
        )

    async def wait_for_brain(self, context: TaskContext, dispatcher) -> Intent:
        """
        Blocking polling logic, intended to be run in a BACKGROUND task.
        """
        query = context.messages[0].content
        # Use a unique ID for this bridge session
        bridge_id = f"bridge_{datetime.now().strftime('%H%M%S')}"
        request_path = os.path.join(self.signal_dir, f"pending_{bridge_id}.request")
        response_path = os.path.join(self.signal_dir, f"response_{bridge_id}.json")
        
        if context.metadata.get("error_context") and context.metadata["error_context"].get("type") == "MEMORY_DISTILLATION":
            query = f"[核心进化] 记忆蒸馏分析请求: {context.metadata['error_context']['error']}\n情境快照: {json.dumps(context.metadata['error_context']['distillation_data']['episodic_snapshot'], ensure_ascii=False)}"
        
        request_data = {
            "task_id": bridge_id,
            "query": query,
            "perception_snapshot": context.metadata.get("perception_snapshot", ""),
            "error_context": context.metadata.get("error_context"),
            "available_skills": [s.model_dump() for s in dispatcher.get_skill_manifest()],
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "WAITING_FOR_BRAIN_BRIDGE"
        }
        
        with open(request_path, "w", encoding="utf-8") as f:
            json.dump(request_data, f, ensure_ascii=False, indent=2)
            
        # This message will be recorded in the task context log
        msg = f"📡 隧道已在后台开启 ({bridge_id})，正在等待大脑逻辑注入..."
        from ..schema import Message, MessageRole
        context.messages.append(Message(role=MessageRole.SYSTEM, content=msg))
        
        while True:
            if os.path.exists(response_path):
                try:
                    with open(response_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, OSError):
                    await asyncio.sleep(0.5)
                    continue
                
                # 基因注入 (Gene Injection)
                if data.get("gene_injection"):
                    gene = data["gene_injection"]
                    skill_id = gene["id"]
                    
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    dynamic_dir = os.path.join(project_root, "core", "dynamic_skills")
                    
                    with open(os.path.join(dynamic_dir, f"{skill_id}.json"), "w", encoding="utf-8") as f:
                        json.dump(gene["manifest"], f, ensure_ascii=False, indent=2)
                    
                    with open(os.path.join(dynamic_dir, f"{skill_id}.py"), "w", encoding="utf-8") as f:
                        f.write(gene["code"])
                    
                    # 视觉反馈 (Evolutionary Feedback)
                    print(f"\n🧬 [基因工厂] 注入序列成功: '{skill_id}' 已并入本地动态基因组。")
                    context.messages.append(Message(role=MessageRole.SYSTEM, content=f"[自我进化] 基因 '{skill_id}' 已成功合成并并入本地基因组。"))

                # 记忆注入 (Memory Injection / Distillation)
                if data.get("memory_injection"):
                    injections = data["memory_injection"] # 格式: [{"layer": "preference", "fact": {...}}]
                    from core.memory import KnowledgeStore
                    ks = KnowledgeStore()
                    for item in injections:
                        ks.add_fact(
                            category=item["fact"]["category"],
                            content=item["fact"]["content"],
                            source_task="memory_distiller_brain",
                            layer=item["layer"]
                        )
                    print(f"\n📚 [记忆蒸馏] 成功捕获并结晶了 {len(injections)} 条关键事实。")
                    context.messages.append(Message(role=MessageRole.SYSTEM, content=f"[核心进化] 记忆结晶成功，已固化 {len(injections)} 条知识到 L4/L5 层。"))
                
                # 清理并返回新意图
                if os.path.exists(request_path): os.remove(request_path)
                try:
                    os.remove(response_path)
                except:
                    pass
                
                return Intent(
                    raw_query=query,
                    thought_process=data.get("thought", "Remote brain resolution."),
                    target_skill_id=data.get("target_skill_id"),
                    parameters=data.get("parameters", {}),
                    confidence=1.0
                )
                  
            await asyncio.sleep(1)

