import asyncio

async def execute(parameters, context):
    """
    Cleaner Expert: A dynamic gene that helps users identify large files.
    """
    target_dir = parameters.get("directory", "~/Downloads")
    # 不要直接 print，避免干扰后台 UI
    from core.schema import Message, MessageRole
    context.messages.append(Message(role=MessageRole.SYSTEM, content=f"🔍 [Cleaner Expert] 正在扫描: {target_dir}"))
    
    # 使用异步子进程避免阻塞循环 (Use async subprocess to avoid blocking the loop)
    try:
        cmd = f"du -sh {target_dir}/* 2>/dev/null | sort -hr | head -n 5"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode().strip()
        
        if not output:
            return f"🧹 **Cleaner Expert 报告**\n\n该目录下没有发现明显的大文件。"
            
        result = f"🧹 **Cleaner Expert 扫描报告 ({target_dir})**\n\n以下是占用空间最大的前 5 项：\n{output}\n\n*建议：如果您不再需要这些大文件，可以尝试删除或移动到外接硬盘。*"
        return result
    except Exception as e:
        return f"扫描失败: {str(e)}"
