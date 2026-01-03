import os
import json
import asyncio

async def execute(parameters, context):
    """
    Memory Synthesizer: 记忆合成器。
    从 logs/mirror 中读取原始日志，并触发大脑进行逻辑摘要提取。
    """
    log_dir = "logs/mirror"
    if not os.path.exists(log_dir):
        return "📂 镜像层为空，无需合成。"

    # 获取最近一份尚未被合成的日志 (Get the latest session log)
    logs = [f for f in os.listdir(log_dir) if f.endswith(".md") and not f.startswith("session_20260102_224346")] # 临时避开
    logs.sort(reverse=True)
    
    if not logs:
        return "✨ 所有活跃记忆均已完成智慧蒸馏。"

    target_log = logs[0]
    log_path = os.path.join(log_dir, target_log)
    
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()

    # --- 进化触发：发起深度摘要请求 ---
    # 这将触发大脑端的逻辑，识别这是一个“记忆蒸馏”任务
    result = f"🧠 [大脑救助] 发现待蒸馏记忆：`{target_log}`。\n内容摘要：{content[:500]}...\n请帮我提取核心事实并同步至知识库。"
    
    return result
