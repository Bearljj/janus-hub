import asyncio
import os
import shutil
from .base import BaseSensor

class SystemSensor(BaseSensor):
    """
    系统状态传感器 (System State Sensor)
    周期性监测磁盘空间和负载，异常时触发反射。
    """
    def __init__(self, bus, interval: int = 10):
        super().__init__("SystemSensor", bus)
        self.interval = interval

    async def _run(self):
        while self.running:
            try:
                # 1. 监测磁盘
                usage = shutil.disk_usage("/")
                free_gb = usage.free / (1024**3)
                if free_gb < 10:
                    await self.bus.emit(source="system", data=f"磁盘空间告急", importance=0.8)

                # 2. 时间意识 - 午夜自省仪式 (Midnight Reflection Trigger)
                import datetime
                now = datetime.datetime.now()
                if now.hour == 2 and now.minute == 0:
                    await self.bus.emit(
                        source="chronos",
                        data=f"午夜钟声响起 ({now.strftime('%H:%M')})，系统进入沉思模式。",
                        importance=0.9
                    )

                # 3. 模拟 CPU 负载监测 (可在以后扩展)
                
            except Exception as e:
                pass
            
            await asyncio.sleep(self.interval)
