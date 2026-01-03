import os

async def execute(parameters, context):
    """
    Gene Remover (基因移除器)
    安全地删除动态技能，防止系统污染。
    """
    skill_id = parameters.get("skill_id")
    confirm = parameters.get("confirm", False)
    
    if not skill_id:
        return "❌ 错误：未指定要移除的技能 ID。"
    
    # 安全检查：不允许删除核心系统技能
    protected_skills = ["gene_factory", "gene_remover", "self_diagnostics", "memory_synthesizer"]
    if skill_id in protected_skills:
        return f"🛡️ 拒绝操作：'{skill_id}' 是受保护的系统核心技能，无法移除。"
    
    # 构建文件路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dynamic_dir = os.path.join(project_root, "core", "dynamic_skills")
    
    json_file = os.path.join(dynamic_dir, f"{skill_id}.json")
    py_file = os.path.join(dynamic_dir, f"{skill_id}.py")
    
    # 检查文件是否存在
    if not os.path.exists(json_file) and not os.path.exists(py_file):
        return f"❌ 技能 '{skill_id}' 不存在。"
    
    # 二次确认机制
    if not confirm:
        return f"⚠️ 警告：即将删除技能 '{skill_id}'。\n如需确认，请使用参数 confirm=true 重新执行。"
    
    # 执行删除
    removed_files = []
    try:
        if os.path.exists(json_file):
            os.remove(json_file)
            removed_files.append(f"{skill_id}.json")
        
        if os.path.exists(py_file):
            os.remove(py_file)
            removed_files.append(f"{skill_id}.py")
        
        return f"✅ 基因移除成功：'{skill_id}'\n已删除文件：{', '.join(removed_files)}\n\n💡 提示：重启 JANUS 后该技能将从系统中完全卸载。"
    
    except Exception as e:
        return f"❌ 删除失败：{str(e)}"
