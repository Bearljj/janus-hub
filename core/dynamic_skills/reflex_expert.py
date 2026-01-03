import os
import json

async def execute(parameters, context):
    """
    Reflex Expert (感知反射专家)
    分析 logs/mirror 中的会话记录，提取潜在的自动化需求。
    """
    mode = parameters.get("mode", "analyze")
    
    log_dir = "logs/mirror"
    if not os.path.exists(log_dir):
        return "📂 待分析记忆为空。"

    # 读取最近的 3 份交互日志
    logs = sorted([f for f in os.listdir(log_dir) if f.endswith(".md")], reverse=True)[:3]
    content_sample = ""
    for log in logs:
        with open(os.path.join(log_dir, log), "r", encoding="utf-8") as f:
            content_sample += f"\n--- {log} ---\n" + f.read()[-2000:] # 取末尾核心交互

    if mode == "analyze":
        # 发起“进化请求”到共生大脑
        return f"🧠 [大脑救助] 启动“反射神经进化”分析。\n环境感知：检测到近期活跃文件及系统状态。\n需求提取：请根据以下对话样本，识别用户是否对某些重复性建议有明确的偏好（y/n），并构造对应的 ReflexRule JSON。\n样本内容：{content_sample[:1500]}..."
    
    return "✅ 正在切换至自主决策模式..."
