import os
import time
from datetime import datetime, timedelta

async def execute(parameters, context):
    """
    Memory Cleaner: Analyzes and cleans interaction logs older than X days.
    """
    days = parameters.get('days', 3)
    dry_run = parameters.get('dry_run', False)
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    mirror_dir = os.path.join(project_root, 'logs', 'mirror')
    
    if not os.path.exists(mirror_dir):
        return f'❌ 未找到日志目录: {mirror_dir}'

    now = time.time()
    cutoff = now - (days * 86400)
    
    files_to_clean = []
    total_size = 0
    
    # 扫描日志文件 (MD 格式)
    for filename in os.listdir(mirror_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(mirror_dir, filename)
            mtime = os.path.getmtime(filepath)
            
            if mtime < cutoff:
                files_to_clean.append(filepath)
                total_size += os.path.getsize(filepath)

    if not files_to_clean:
        return f'✨ **[Memory Cleaner] 报告**\n\n扫描完毕。没有发现超过 {days} 天的旧日志文件。'

    report = f'🧹 **[Memory Cleaner] 扫描报告**\n'
    report += f'- **清理阈值**: > {days} 天\n'
    report += f'- **发现文件**: {len(files_to_clean)} 个\n'
    report += f'- **释放空间**: {total_size / 1024:.2f} KB\n\n'
    
    if dry_run:
        report += '⚠️ **当前为模拟模式，未执行删除。**\n'
        report += '待清理清单：\n'
        for f in files_to_clean:
            report += f'- {os.path.basename(f)}\n'
    else:
        # 执行删除
        deleted_count = 0
        for f in files_to_clean:
            try:
                os.remove(f)
                deleted_count += 1
            except Exception as e:
                report += f'❌ 删除失败 {os.path.basename(f)}: {e}\n'
        
        report += f'✅ **成功清理 {deleted_count} 个旧日志文件。**\n'
        report += '*进化记录: 物理存储层负载已降低。*'

    return report
