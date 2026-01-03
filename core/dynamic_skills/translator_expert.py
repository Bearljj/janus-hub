import asyncio
import json

async def execute(parameters, context):
    """
    Translator Expert: Real-time translation gene.
    Evolved to bridge to the Brain if local OpenAI is not configured.
    """
    text = parameters.get("text", parameters.get("query", ""))
    
    # 获取原始查询，判断是否是仅仅为了测试或对话 (Handling casual queries)
    if not text:
        return "❌ 请提供需要翻译的内容。用法：`translator_expert text=\"Hello\"`"

    # --- 核心进化逻辑：由于本地没有 API Key，发起“大脑救助”暗号 ---
    # 这里的字符串包含“大脑救助”，将触发 Dispatcher 的递归 SOS 机制
    result = f"🧠 [大脑救助] 正在通过共生中枢请求真实翻译...\n目标内容: {text}"
    
    return result