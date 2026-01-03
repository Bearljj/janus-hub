import os
import json

class DistillationRequired(Exception):
    """自定义异常，用于触发自愈系统进行记忆蒸馏"""
    def __init__(self, context_data):
        self.context_data = context_data

async def execute(parameters, context):
    # 1. 准备数据
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    knowledge_path = os.path.join(project_root, "logs", "knowledge.json")
    
    with open(knowledge_path, "r", encoding="utf-8") as f:
        knowledge = json.load(f)
    
    episodic_data = knowledge.get("episodic", [])[-50:]
    
    # 2. 故意引发一个“需求缺失”异常，触发自愈系统
    print(f"🔮 [记忆蒸馏] 正在打包 {len(episodic_data)} 条情境记忆，准备发起结晶请求...")
    
    # 注入数据到 context，方便 Dispatcher 提取
    context.metadata["distillation_data"] = {
        "type": "MEMORY_DISTILLATION",
        "episodic_snapshot": episodic_data,
        "current_preferences": knowledge.get("preference", [])
    }
    
    raise DistillationRequired("触发自愈演化：需要对当前情境记忆进行结晶蒸馏。")
