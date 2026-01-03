import asyncio
from abc import ABC, abstractmethod

class BaseSensor(ABC):
    """感知传感器基类 (Base class for all sensors)"""
    def __init__(self, name: str, bus):
        self.name = name
        self.bus = bus
        self.running = False
        self._task = None

    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self._run())
        # print(f"[感知器] {self.name} 已启动。") # 保持后台静默


    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print(f"[感知器] {self.name} 已停止。")

    @abstractmethod
    async def _run(self):
        """主循环：采集数据并 emit 到总线"""
        pass
