import asyncio
import os
import platform

async def execute(parameters, context):
    """
    Skill: Speech Expert
    Evolution Stage: SOUL_INJECTED
    Provides Text-to-Speech (TTS) capabilities using system commands.
    """
    text = parameters.get("text", parameters.get("query", ""))
    
    if not text:
        return "⚠️ 请提供要朗读的文本。 (例如: speech_expert text='你好')"

    # 识别系统并通过不同的 TTS 引擎执行 (Identify system and use appropriate TTS engine)
    current_os = platform.system()
    
    try:
        if current_os == "Darwin": # macOS
            # 使用 macOS 自带的 say 命令 (use native 'say' command)
            # 我们在后台异步运行，以免阻塞 JANUS 响应 (Run in background to avoid blocking)
            proc = await asyncio.create_subprocess_exec(
                "say", text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            status = "✅ [macOS Say] 朗读完成"
        elif current_os == "Linux":
            # 尝试使用 espeak (try using espeak)
            os.system(f'espeak "{text}" &')
            status = "✅ [Linux espeak] 已发送朗读指令"
        else:
            status = f"❌ 暂时不支持在 {current_os} 系统上进行语音输出。"

        result = f"🔊 **[Speech Expert] 播报报告**\n" \
                 f"- 内容: \"{text}\"\n" \
                 f"- 引擎状态: {status}\n\n" \
                 f"*提示: JANUS 现在已经不再是沉默的程序，它开始拥有了声音。*"
        
        return result

    except Exception as e:
        return f"❌ 语音指令执行异常: {str(e)}"
