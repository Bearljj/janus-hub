import os
import re

async def execute(parameters, context):
    action = parameters.get("action", "auto_fix")
    # 定位根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 定义修复字典：[文件路径关键字, 匹配代码行, 要写回的完整锁标记]
    REPAIR_TARGETS = [
        {
            "file": "janus_cli.py",
            "anchor": r"workspace_root =",
            "lock": "# [AI-SAFEGUARD]: 核心设计意图 - 监控范围锁定 (DNA.md #1)"
        },
        {
            "file": "core/memory.py",
            "anchor": r"class KnowledgeStore",
            "lock": "# --- [AI-SAFEGUARD]: L4 记忆分层体系锁定 (DNA.md #2) ---"
        },
        {
            "file": "core/dispatcher.py",
            "anchor": r"except Exception as e:",
            "lock": "# --- [AI-SAFEGUARD]: 免疫系统反应锁定 (DNA.md #3) ---"
        },
        {
            "file": "core/sensors/file_sensor.py",
            "anchor": r"async def _check_file",
            "lock": "# [AI-SAFEGUARD]: 强制哈希双检逻辑 (DNA.md)"
        }
    ]
    
    fixed_files = []
    
    for target in REPAIR_TARGETS:
        file_path = os.path.join(root_dir, target["file"])
        if not os.path.exists(file_path): continue
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        content = "".join(lines)
        # 检查是否已经存在锁标记
        if target["lock"] in content:
            continue
            
        print(f"🛠️ [修复中] 正在为 {target['file']} 重新植入意志锁...")
        
        new_lines = []
        applied = False
        for line in lines:
            if re.search(target["anchor"], line) and not applied:
                # 在锚点行上方插入锁
                indent = line[:len(line) - len(line.lstrip())]
                new_lines.append(f"{indent}{target['lock']}\n")
                applied = True
            new_lines.append(line)
        
        if applied:
            if action == "auto_fix":
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
            fixed_files.append(target["file"])

    if not fixed_files:
        return "🛡️ 所有设计锁完好无损，系统意志坚定。"
        
    return f"✅ 成功修复了 {len(fixed_files)} 个文件的设计意志漏洞: {', '.join(fixed_files)}"
