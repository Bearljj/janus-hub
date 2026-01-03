import asyncio

async def execute(parameters, context):
    day = parameters.get("day", "今天")
    # Mocking weather service
    result = f"🌤️ **Weather Expert 报告**

关于 '{day}' 的天气预报：
- 状态：晴朗转多云
- 温度：15°C ~ 22°C
- 建议：早晚温差较大，建议多带一件外套。"
    return result