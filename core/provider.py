from abc import ABC, abstractmethod
from typing import List
from .schema import Message, Intent, AgentSkill

class BaseProvider(ABC):
    """
    Abstract base class for LLM providers (LLM 供给侧抽象基类)
    Allows JANUS to switch between Cloud APIs, Local models, or Proxies.
    """
    
    @abstractmethod
    async def chat(self, messages: List[Message]) -> str:
        """Standard chat interface"""
        pass

    @abstractmethod
    async def resolve_intent(self, query: str, skills: List[AgentSkill], perception_snapshot: str = "") -> Intent:
        """
        Specialized method for intent resolution and skill mapping.
        Includes real-time perception context.
        """
        pass

