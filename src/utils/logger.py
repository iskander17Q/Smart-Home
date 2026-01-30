"""Утилита для логирования событий"""
from datetime import datetime
from ..core.models import LogEntry
from ..core.event_bus import EventBus


class Logger:
    """Логгер событий"""
    
    def __init__(self, storage, event_bus: EventBus):
        self.storage = storage
        self.event_bus = event_bus
        self._connect_events()
    
    def _connect_events(self):
        """Подключить события для логирования"""
        self.event_bus.subscribe("sensor_update", self._log_sensor)
        self.event_bus.subscribe("actuator_update", self._log_actuator)
        self.event_bus.subscribe("rule_triggered", self._log_rule)
    
    def _log_sensor(self, event: dict):
        """Логировать обновление датчика"""
        data = event.get("data", {})
        log = LogEntry(
            timestamp=datetime.now().isoformat(),
            type="sensor",
            source=data.get("device_name", "Unknown"),
            message=f"Датчик {data.get('type', 'unknown')}: {data.get('value', 'N/A')}"
        )
        self.storage.add_log(log)
    
    def _log_actuator(self, event: dict):
        """Логировать обновление актуатора"""
        data = event.get("data", {})
        log = LogEntry(
            timestamp=datetime.now().isoformat(),
            type="actuator",
            source=data.get("device_name", "Unknown"),
            message=f"Устройство {data.get('action', 'unknown')}: {data.get('state', {})}"
        )
        self.storage.add_log(log)
    
    def _log_rule(self, event: dict):
        """Логировать срабатывание правила"""
        data = event.get("data", {})
        log = LogEntry(
            timestamp=datetime.now().isoformat(),
            type="rule",
            source=data.get("rule_name", "Unknown Rule"),
            message=f"Правило сработало: {data.get('action', 'unknown')} на устройстве {data.get('device_id', 'unknown')}"
        )
        self.storage.add_log(log)
    
    def log_system(self, message: str):
        """Логировать системное сообщение"""
        log = LogEntry(
            timestamp=datetime.now().isoformat(),
            type="system",
            source="System",
            message=message
        )
        self.storage.add_log(log)
