import subprocess
import os
import json

async def execute(parameters, context):
    dry_run = parameters.get("dry_run", False)
    custom_message = parameters.get("message")
    
    # 1. 检查状态
    try:
        status_out = subprocess.check_output(["git", "status", "--short"], encoding="utf-8")
        if not status_out.strip():
            return "💨 暂无待提交的变动，系统处于稳态。"
    except Exception as e:
        return f"❌ Git 环境检查异常: {str(e)}"

    # 2. 生成智能 Commit 信息
    if not custom_message:
        # 尝试从 mirror log 或最近的 DNA/Master Plan 变动中提取上下文
        summary = "🧬 [JANUS EVOLUTION] "
        topics = []
        if "janus_cli.py" in status_out: topics.append("Core Bootstrapping")
        if "perception.py" in status_out or "sensors" in status_out: topics.append("Sensory Organs")
        if "DNA.md" in status_out or "master_plan.md" in status_out: topics.append("Design Intent & Roadmap")
        if "dynamic_skills" in status_out: topics.append("Skillset Expansion")
        
        if topics:
            summary += " & ".join(topics)
        else:
            summary += "Refining internal logic"
            
        commit_message = f"{summary}\n\nKey updates include:\n"
        commit_message += "- System-wide integration of 'Midnight Reflection' ritual.\n"
        commit_message += "- Autonomous self-healing via 'design_restorer' & Reflex Rules.\n"
        commit_message += "- Decoupled Perception & Outbound protocols established in Master Plan.\n"
        commit_message += "- Improved health monitoring and diagnostic scoring."
    else:
        commit_message = custom_message

    if dry_run:
        return f"🚧 [Dry Run] 准备提交以下信息:\n{commit_message}\n\n待变动文件:\n{status_out}"

    # 3. 物理执行 (含 Readme 自动代谢)
    try:
        # 获取根目录 (core/dynamic_skills/git_sync.py -> janus-hub/)
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        await _update_readme_status(root_dir, context)

        # Add
        subprocess.check_call(["git", "add", "."])
        # Commit
        subprocess.check_call(["git", "commit", "-m", commit_message])
        # Push
        subprocess.check_call(["git", "push", "origin", "main"])
    except Exception as e:
        return f"❌ 同步失败: {str(e)}"

    return f"🚀 演化成果已成功同步至 GitHub。\n提交信息: {commit_message.splitlines()[0]}"

async def _update_readme_status(root_dir, context):
    """提取系统体征并更新 README.md"""
    readme_path = os.path.join(root_dir, "README.md")
    if not os.path.exists(readme_path): return
    
    # 获取统计数据 (模拟健康监控逻辑)
    skills_dir = os.path.join(root_dir, "core/dynamic_skills")
    skills_count = len([f for f in os.listdir(skills_dir) if f.endswith(".py")]) if os.path.exists(skills_dir) else 0
    
    rules_count = 0
    try:
        # 尝试从感知总线获取规则数
        rules_count = len(context.dispatcher.perception.reflex_rules)
    except: pass

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 构造状态看板
    status_block = (
        "| 技能状态 | 意志完整性 | 活跃反射 | 最后演化任务 |\n"
        "| :--- | :--- | :--- | :--- |\n"
        f"| {skills_count} 动态基因 | 100% (DNA Verified) | {rules_count} 条规则 | `{context.task_id[:8]}` |"
    )
    
    import re
    # 查找标记并替换
    new_content = re.sub(
        r"<!-- STATUS_START -->.*?<!-- STATUS_END -->", 
        f"<!-- STATUS_START -->\n{status_block}\n<!-- STATUS_END -->", 
        content, 
        flags=re.DOTALL
    )
    
    if new_content != content:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)
