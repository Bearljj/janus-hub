import asyncio
import os

async def execute(parameters, context):
    """
    Git Stats: Evolution Stage SOUL_INJECTED
    Provides repository statistics.
    """
    try:
        # 统计提交数 (Count commits)
        proc = await asyncio.create_subprocess_exec(
            'git', 'rev-list', '--count', 'HEAD',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        commits = stdout.decode().strip() if stdout else '0'

        # 统计未提交文件 (Count uncommitted files)
        proc = await asyncio.create_subprocess_exec(
            'git', 'status', '--short',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        uncommitted = stdout.decode().strip()
        file_count = len(uncommitted.split('\n')) if uncommitted else 0

        result = (f"📊 **[Git Stats] 仓库状态报告**\n"
                 f"- **总提交数 (Commits)**: {commits}\n"
                 f"- **待处理文件 (Changes)**: {file_count} 个\n\n"
                 f"```\n{uncommitted or 'Clean Working Tree'}\n```\n\n"
                 f"*进化记录: 该基因此刻已由骨架演化为全功能实战基因。*")
        
        return result
    except Exception as e:
        return f"❌ Git 执行失败 (该目录可能不是 Git 仓库): {str(e)}"
