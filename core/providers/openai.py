import json
import os
from typing import List
from openai import AsyncOpenAI
from ..schema import Message, Intent, AgentSkill
from ..provider import BaseProvider

class OpenAIProvider(BaseProvider):
    """
    OpenAI 兼容的云端 AI 供给侧实现。
    支持 OpenAI, DeepSeek, Azure 等标准 API。
    """
    
    def __init__(self, model: str = "gpt-4-turbo-preview", base_url: str = None, api_key: str = None):
        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or os.getenv("OPENAI_API_BASE")
        )
        self.model = model

    async def chat(self, messages: List[Message]) -> str:
        formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages
        )
        return response.choices[0].message.content

    async def resolve_intent(self, query: str, skills: List[AgentSkill]) -> Intent:
        """
        利用 LLM 进行意图识别和参数提取。
        """
        skill_manifest = [s.dict() for s in skills]
        
        system_prompt = f"""
你现在是 JANUS Hub 的中枢调度员。
你的任务是根据用户的输入，判断是否需要调用特定的技能库，并提取参数。

## 可用技能清单:
{json.dumps(skill_manifest, ensure_ascii=False, indent=2)}

## 响应格式要求:
你必须仅返回一个有效的 JSON 对象，包含以下字段：
- raw_query: 原始查询
- thought_process: 简短的调度逻辑思考
- target_skill_id: 匹配的技能 ID，如果不匹配任何技能则为 null
- parameters: 提取出的技能参数字典
- confidence: 信心评分 (0.0 - 1.0)

示例：
{{
  "raw_query": "列出数据目录下的文件",
  "thought_process": "用户希望浏览文件，匹配 list_files 技能。",
  "target_skill_id": "list_files",
  "parameters": {{"pattern": "*分享*"}},
  "confidence": 0.95
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                response_format={ "type": "json_object" } if "gpt-4" in self.model or "gpt-3.5" in self.model else None
            )
            
            content = response.choices[0].message.content
            # 处理可能的 Markdown 包裹
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            
            data = json.loads(content)
            return Intent(**data)
            
        except Exception as e:
            # 降级处理：如果没有成功解析，返回通用意图
            return Intent(
                raw_query=query,
                thought_process=f"LLM 意图解析失败: {str(e)}",
                target_skill_id=None,
                parameters={},
                confidence=0.0
            )
