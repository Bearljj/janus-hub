from .system_sensor import SystemSensor
from .file_sensor import FileSensor

class SensorManager:
    """感知管理器 (Manager for all active sensors)"""
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.bus = dispatcher.perception
        self.sensors = []

    def setup_default_sensors(self, watch_path: str = "."):
        self.sensors.append(SystemSensor(self.bus))
        if watch_path:
            self.sensors.append(FileSensor(self.bus, watch_path))

    async def start_all(self):
        for s in self.sensors:
            await s.start()

    async def stop_all(self):
        for s in self.sensors:
            await s.stop()
