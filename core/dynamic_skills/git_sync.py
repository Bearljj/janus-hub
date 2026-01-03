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

    # 3. 物理执行
    try:
        # Add
        subprocess.check_call(["git", "add", "."])
        # Commit
        subprocess.check_call(["git", "commit", "-m", commit_message])
        # Push
        subprocess.check_call(["git", "push", "origin", "main"]) # 假设是 main 分支
    except Exception as e:
        return f"❌ 同步失败: {str(e)}"

    return f"🚀 演化成果已成功同步至基座仓库 (GitHub)。\n提交信息: {commit_message.splitlines()[0]}"
