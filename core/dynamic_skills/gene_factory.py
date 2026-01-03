import os
import json
import textwrap

async def execute(parameters, context):
    """
    Gene Factory: The self-replication incubator of JANUS.
    Generates new .json manifests and .py execution logic on demand.
    """
    skill_id = parameters.get("target_skill_id")
    description = parameters.get("description", "A new dynamic skill created by Gene Factory.")
    code_hint = parameters.get("code_template", "")
    
    dynamic_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(dynamic_dir, f"{skill_id}.json")
    py_path = os.path.join(dynamic_dir, f"{skill_id}.py")
    
    if os.path.exists(json_path) or os.path.exists(py_path):
        return f"🚨 [基因抑制]: ID '{skill_id}' 已存在，请使用其他 ID 以免发生逻辑冲突。"

    # 1. 生成 Manifest (Build Manifest)
    manifest = {
        "id": skill_id,
        "name": skill_id.replace("_", " ").title(),
        "description": description,
        "tags": ["dynamic", "generated"],
        "input_schema": {"type": "object", "properties": {}}
    }
    
    # 2. 生成 Scaffold 代码 (Build Scaffold Code)
    scaffold = textwrap.dedent(f'''\
        import asyncio
        import os
        
        async def execute(parameters, context):
            """
            Skill: {manifest["name"]}
            Automatically incubated by Gene Factory.
            """
            # TODO: Implement the following logic:
            # {description}
            
            result = f"⚡ **[{manifest["name"]}] 激活成功**\\n" \\
                     f"这是为你自动生成的预览逻辑。\\n" \\
                     f"输入指令详情以触发进一步的大脑救助。"
            
            return result
    ''')

    # 3. 物理落盘 (Physical Writing)
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(scaffold)
            
        return f"✨ **新的基因已孵化！**\n" \
               f"- **ID**: {skill_id}\n" \
               f"- **位置**: `{py_path}`\n" \
               f"你可以现在尝试在 CLI 中直接调用 `{skill_id}`。调度器会自动完成剩余的突触连接。"
               
    except Exception as e:
        return f"❌ 基因孵化失败: {str(e)}"
