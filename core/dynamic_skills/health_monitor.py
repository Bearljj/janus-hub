import os
import json
from datetime import datetime

async def execute(parameters, context):
    """
    Health Monitor v1.0
    全面的自我诊断系统
    """
    mode = parameters.get("mode", "quick")
    output_format = parameters.get("output", "report")
    
    # 基础路径
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dynamic_dir = os.path.join(root_dir, "core", "dynamic_skills")
    logs_dir = os.path.join(root_dir, "logs")
    mirror_dir = os.path.join(logs_dir, "mirror")
    knowledge_file = os.path.join(logs_dir, "knowledge.json")
    
    # 收集诊断数据
    diagnostics = {}
    
    # 1. 基因健康检查
    gene_health = check_gene_health(dynamic_dir)
    diagnostics["gene_health"] = gene_health
    
    # 2. 记忆健康检查
    memory_health = check_memory_health(mirror_dir, knowledge_file)
    diagnostics["memory_health"] = memory_health
    
    # 3. 系统资源检查
    resource_health = check_resources(root_dir)
    diagnostics["resource_health"] = resource_health
    
    # 4. 感知系统检查
    perception_health = check_perception(knowledge_file)
    diagnostics["perception_health"] = perception_health

    # 5. [新增] 设计一致性检查 (Design Consistency)
    design_health = check_design_consistency(root_dir)
    diagnostics["design_health"] = design_health
    
    # 计算总体评分
    total_score = calculate_total_score(diagnostics)
    
    # [核心进化]: 如果评分低，主动向感知总线发射“身体信号”
    if total_score < 100:
        await context.dispatcher.perception.emit(
            source="health",
            data={
                "msg": f"系统健康度下降 ({total_score}/100)",
                "details": diagnostics
            },
            importance=0.8
        )

    # 生成报告
    if output_format == "json":
        return json.dumps(diagnostics, indent=2, ensure_ascii=False)
    else:
        return generate_report(diagnostics, total_score)


def check_gene_health(dynamic_dir):
    """检查基因完整性"""
    json_files = set([f[:-5] for f in os.listdir(dynamic_dir) if f.endswith('.json') and f != '__init__.py'])
    py_files = set([f[:-3] for f in os.listdir(dynamic_dir) if f.endswith('.py') and f != '__init__.py'])
    
    complete_genes = json_files & py_files
    orphan_json = json_files - py_files
    orphan_py = py_files - json_files
    
    score = 100
    if orphan_json or orphan_py:
        score -= len(orphan_json) * 10 + len(orphan_py) * 10
    
    return {
        "score": max(score, 0),
        "total_genes": len(complete_genes),
        "complete_genes": list(complete_genes),
        "orphan_manifests": list(orphan_json),
        "orphan_code": list(orphan_py)
    }


def check_memory_health(mirror_dir, knowledge_file):
    """检查记忆系统健康"""
    score = 100
    issues = []
    
    # 检查 Mirror 日志
    mirror_files = [f for f in os.listdir(mirror_dir) if f.endswith('.md')] if os.path.exists(mirror_dir) else []
    mirror_size = sum(os.path.getsize(os.path.join(mirror_dir, f)) for f in mirror_files) if mirror_files else 0
    
    if len(mirror_files) > 20:
        score -= 10
        issues.append(f"Mirror 日志过多 ({len(mirror_files)} 个文件)")
    
    # 检查知识库
    kb_size = 0
    kb_stats = {"episodic": 0, "conceptual": 0, "semantic": 0, "preference": 0}
    
    if os.path.exists(knowledge_file):
        kb_size = os.path.getsize(knowledge_file)
        try:
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for layer in kb_stats.keys():
                    if layer in data:
                        kb_stats[layer] = len(data[layer])
        except:
            score -= 20
            issues.append("知识库文件损坏")
    
    if kb_size > 500 * 1024:  # >500KB
        score -= 15
        issues.append(f"知识库过大 ({kb_size // 1024} KB)")
    
    return {
        "score": max(score, 0),
        "mirror_files": len(mirror_files),
        "mirror_size_mb": round(mirror_size / (1024 * 1024), 2),
        "knowledge_size_kb": round(kb_size / 1024, 1),
        "knowledge_stats": kb_stats,
        "issues": issues
    }


def check_resources(root_dir):
    """检查系统资源"""
    import subprocess
    score = 100
    
    try:
        # 检查磁盘空间
        disk_info = subprocess.check_output("df -h / | tail -n 1", shell=True).decode().split()
        available_gb = disk_info[3]
        
        # 检查工作目录大小
        dir_size = subprocess.check_output(f"du -sh {root_dir}", shell=True).decode().split()[0]
        
        return {
            "score": score,
            "disk_available": available_gb,
            "workspace_size": dir_size
        }
    except:
        return {"score": 80, "error": "无法获取系统资源信息"}


def check_perception(knowledge_file):
    """检查感知系统"""
    score = 100
    rule_count = 0
    
    try:
        if os.path.exists(knowledge_file):
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "conceptual" in data:
                    for fact in data["conceptual"]:
                        if fact.get("category", "").lower() == "reflexrule":
                            rule_count += 1
    except:
        score -= 20
    
    return {
        "score": score,
        "active_rules": rule_count
    }


def check_design_consistency(root_dir):
    """
    [核心进化]: 设计一致性检查。
    扫描 DNA.md 并验证关键文件中的 SAFEGUARD 标记。
    """
    # [核心修复]: 更加稳健的根目录获取方式
    current_file = os.path.abspath(__file__)
    # 从 core/dynamic_skills/health_monitor.py 向上跳三级到 janus-hub/
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    score = 100
    missing_locks = []
    
    dna_path = os.path.join(root_dir, ".janus", "DNA.md")
    if not os.path.exists(dna_path):
        return {"score": 0, "error": "缺失 DNA.md 设计基准文件"}
    
    # 定义必须包含守护标记的关键文件 (通过特殊的注释前缀定位)
    mandatory_safeguards = {
        "janus_cli.py": "# [AI-SAFEGUARD]:",
        "core/memory.py": "# --- [AI-SAFEGUARD]:",
        "core/dispatcher.py": "# --- [AI-SAFEGUARD]:",
        "core/sensors/file_sensor.py": "# [AI-SAFEGUARD]:"
    }
    
    for file, pattern in mandatory_safeguards.items():
        full_path = os.path.join(root_dir, file)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
                if pattern not in content:
                    score -= 25
                    missing_locks.append(file)
        else:
            score -= 10
            missing_locks.append(f"{file} (文件缺失)")
            
    return {
        "score": max(score, 0),
        "missing_locks": missing_locks,
        "dna_present": True
    }


def calculate_total_score(diagnostics):
    """计算总体评分"""
    weights = {
        "gene_health": 0.25,
        "memory_health": 0.25,
        "resource_health": 0.1,
        "perception_health": 0.1,
        "design_health": 0.3      # 设计一致性拥有最高权重
    }
    
    total = sum(diagnostics[key]["score"] * weights[key] for key in weights.keys())
    return round(total)


def generate_report(diagnostics, total_score):
    """生成文本报告"""
    # 评分等级
    if total_score >= 90:
        grade = "🟢 优秀"
    elif total_score >= 70:
        grade = "🟡 良好"
    elif total_score >= 50:
        grade = "🟠 警告"
    else:
        grade = "🔴 危险"
    
    report = []
    report.append("🏥 JANUS 健康检查报告")
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"总体评分: {total_score}/100 {grade}")
    report.append("\n" + "━" * 50 + "\n")
    
    # 基因健康
    gh = diagnostics["gene_health"]
    report.append(f"1. 基因健康 [{gh['score']}/100] {'🟢' if gh['score'] >= 90 else '🟡'}")
    report.append(f"   ✅ 活跃基因数: {gh['total_genes']}")
    if gh['orphan_manifests']:
        report.append(f"   ⚠️  孤儿清单: {', '.join(gh['orphan_manifests'])}")
    if gh['orphan_code']:
        report.append(f"   ⚠️  孤儿代码: {', '.join(gh['orphan_code'])}")
    
    # 记忆健康
    mh = diagnostics["memory_health"]
    report.append(f"\n2. 记忆健康 [{mh['score']}/100] {'🟢' if mh['score'] >= 90 else '🟡'}")
    report.append(f"   📝 Mirror 日志: {mh['mirror_files']} 个文件 ({mh['mirror_size_mb']} MB)")
    report.append(f"   📚 知识库大小: {mh['knowledge_size_kb']} KB")
    report.append(f"   📊 分层统计: E:{mh['knowledge_stats']['episodic']} C:{mh['knowledge_stats']['conceptual']} S:{mh['knowledge_stats']['semantic']} P:{mh['knowledge_stats']['preference']}")
    for issue in mh['issues']:
        report.append(f"   ⚠️  {issue}")
    
    # 系统资源
    rh = diagnostics["resource_health"]
    report.append(f"\n3. 系统资源 [{rh['score']}/100] 🟢")
    report.append(f"   💾 磁盘剩余: {rh.get('disk_available', 'N/A')}")
    report.append(f"   📁 工作目录: {rh.get('workspace_size', 'N/A')}")
    
    # 感知系统
    ph = diagnostics["perception_health"]
    report.append(f"\n4. 感知系统 [{ph['score']}/100] 🟢")
    report.append(f"   🎯 活跃反射规则: {ph['active_rules']} 条")
    
    # 5. 设计一致性
    dh = diagnostics["design_health"]
    report.append(f"\n5. 设计一致性 [{dh['score']}/100] {'🟢' if dh['score'] >= 90 else '🔴'}")
    report.append(f"   🧬 DNA.md 状态: {'✅ 启用' if dh.get('dna_present') else '❌ 缺失'}")
    if dh['missing_locks']:
        report.append(f"   ⚠️  设计锁缺失: {', '.join(dh['missing_locks'])}")
    
    report.append("\n" + "━" * 50)
    
    # 优化建议
    report.append("\n💡 优化建议:\n")
    if dh['score'] < 100:
        report.append("• [严重] 检测到设计退化！请参考 DNA.md 恢复丢失的 [AI-SAFEGUARD] 标记")
    if mh['mirror_files'] > 10:
        report.append("• [建议] 运行 memory_archiver 归档旧日志")
    if mh['knowledge_size_kb'] > 200:
        report.append("• [建议] 清理 episodic 层的过期事实")
    if gh['orphan_manifests'] or gh['orphan_code']:
        report.append("• [注意] 发现孤儿文件，建议检查或清理")
    
    if total_score >= 90:
        report.append("• ✨ 系统状态优秀，保持当前运行状态")
    
    return "\n".join(report)
