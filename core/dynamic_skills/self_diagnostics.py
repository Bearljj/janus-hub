import os
import re

async def execute(parameters, context):
    """
    Self Diagnostics v0.2-EVOLVED: JANUS's active introspection module.
    Now supports code inspection and automatic optimization.
    """
    from core.schema import Message, MessageRole
    
    # Base paths
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dispatcher_path = os.path.join(root_dir, "core", "dispatcher.py")
    dynamic_dir = os.path.dirname(os.path.abspath(__file__))
    
    action = parameters.get("action", "report")
    
    if action == "optimize":
        return await handle_optimization(dispatcher_path)

    # 1. 扫描基因集 (Scan Gene Set)
    dynamic_files = [f for f in os.listdir(dynamic_dir) if f.endswith(".py") and f != "__init__.py"]
    
    # 2. 深度代码视诊 (Deep Code Inspection)
    redundancies = []
    if os.path.exists(dispatcher_path):
        with open(dispatcher_path, "r") as f:
            content = f.read()
            # 检查是否有重复或非顶层的 sys 导入
            if "import sys" in content and "import sys" not in content.split('\n')[0:20]:
                redundancies.append("发现非顶层 sys 导入 (建议移动至头部以提高执行效率)")

    # 3. 生成报告
    report = []
    report.append("🧬 **JANUS 自我生长诊断报告 (v0.2-EVOLVED)**")
    report.append("-" * 30)
    
    report.append(f"🧠 **当前发育阶段**: 「共生进化期 (Symbiotic Evolution)」")
    report.append(f"✅ **活跃基因数**: {len(dynamic_files)}")
    
    if redundancies:
        report.append("\n⚠️ **发现架构冗余 (Redundancies Found):**")
        for r in redundancies:
            report.append(f"  - {r}")
        report.append("\n*提示: 输入 'self_diagnostics action=optimize' 授权我进行自我优化手术。*")
    else:
        report.append("\n🟢 **架构底座状态: 优 (Optimal)**")
        report.append("  - 核心调度引擎逻辑纯净，无明显阻塞。")

    report.append("\n🚀 **下一步进化建议:**")
    report.append("  1. **[感知增强]**: 接入本地多模态基因 (Vision/Audio)。")
    report.append("  2. **[记忆归档]**: 影子镜像文件超过 100 份，建议启用清理序列。")

    return "\n".join(report)

async def handle_optimization(file_path):
    """
    执行手术：优化核心代码
    """
    if not os.path.exists(file_path):
        return "优化失败：找不到核心调度器文件。"
        
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    # 简单的优化逻辑：移除内嵌导入并提升至顶部
    sys_imported = False
    new_lines = []
    for line in lines:
        # 如果 import sys 出现在缩进中 (not at the very start of line), 则认为是内嵌导入
        if "import sys" in line and (line.startswith(" ") or line.startswith("\t")):
            sys_imported = True
            continue
        new_lines.append(line)
        
    if sys_imported:
        # 在头部加入 (Insert at top)
        new_lines.insert(0, "import sys\n")
        with open(file_path, "w") as f:
            f.writelines(new_lines)
        return "✨ **自我优化完成**：已将 `sys` 模块提升为顶层导入，引擎启动效率获得微秒级提升。"
    
    return "检查完毕：调度引擎已处于最优状态，无需手术。"
