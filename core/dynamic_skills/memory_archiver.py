import os
import json
from datetime import datetime
import shutil

async def execute(parameters, context):
    """
    Memory Archiver: JANUS's data lifecycle manager.
    Moves old markdown logs to an archive and extracts facts to the knowledge store.
    """
    threshold = parameters.get("threshold", 5)
    log_dir = "logs/mirror"
    archive_dir = os.path.join(log_dir, "archived")
    os.makedirs(archive_dir, exist_ok=True)
    
    # 1. 获取所有日志并按时间排序 (Get all logs and sort by time)
    logs = [f for f in os.listdir(log_dir) if f.endswith(".md")]
    logs.sort() # Oldest first
    
    if len(logs) <= threshold:
        return f"🟢 记忆层存储状态健康：当前共有 {len(logs)} 份日志，未达到归档阈值 ({threshold})。"

    to_archive = logs[:-threshold]
    archived_count = 0
    facts_extracted = 0
    
    # 这里模拟从日志中提取“客观事实”并存入 KnowledgeStore
    # 在真实场景中，这里会调用 LLM 进行摘要提取
    from core.memory import KnowledgeStore
    ks = KnowledgeStore()
    
    for log_name in to_archive:
        log_path = os.path.join(log_dir, log_name)
        
        # 模拟提取逻辑：每份日志提取一条“历史足迹”
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
            # 简单的正则或文本搜索，寻找任务成功记录
            if "## 任务:" in content:
                tasks = content.split("## 任务:")[1:]
                for task in tasks:
                    task_id = task.split("\n")[0].strip()
                    ks.add_fact(
                        category="HistoricalSession",
                        content=f"归档记录：会话 {log_name} 中完成了任务 {task_id[:8]}",
                        source_task=context.task_id
                    )
                    facts_extracted += 1

        # 移动到归档文件夹
        shutil.move(log_path, os.path.join(archive_dir, log_name))
        archived_count += 1
        
    result = f"🧹 **记忆层归档完成**\n" \
             f"- 已将 {archived_count} 份旧日志移至 `{archive_dir}`\n" \
             f"- 从中提取了 {facts_extracted} 条历史事实并同步至影子知识库。\n" \
             f"- 当前活跃日志数: {threshold}"
             
    return result
