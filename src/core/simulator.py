"""Симулятор устройств ESP32/ESP8266"""
import random
import math
from datetime import datetime
from typing import Dict, Any, Optional
from PySide6.QtCore import QTimer, QObject, Signal
from .models import Device
from .event_bus import EventBus


class DeviceSimulator(QObject):
    """Симулятор одного устройства"""
    
    value_changed = Signal(str, dict)  # device_id, new_state
    
    def __init__(self, device: Device, event_bus: EventBus):
        super().__init__()
        self.device = device
        self.event_bus = event_bus
        self.timer = QTimer()
        self.timer.timeout.connect(self._update)
        
        # Состояние для генерации данных
        self._sensor_state = {
            "temperature": 22.0,
            "humidity": 50.0,
            "light": 500.0,
            "motion": False,
            "door": False,
        }
        self._last_motion_time = 0
        self._update_counter = 0
        
        # Интервал обновления (мс)
        interval = device.config.get("update_interval", 2000)
        self.timer.start(interval)
    
    def _update(self):
        """Обновить значение датчика"""
        if self.device.category != "sensor":
            return
        
        mode = self.device.config.get("mode", "random")
        new_value = None
        
        if self.device.type == "temperature":
            if mode == "smooth":
                # Плавное изменение
                change = random.uniform(-0.5, 0.5)
                self._sensor_state["temperature"] += change
                self._sensor_state["temperature"] = max(18, min(28, self._sensor_state["temperature"]))
                new_value = round(self._sensor_state["temperature"], 1)
            else:
                new_value = round(random.uniform(18, 28), 1)
        
        elif self.device.type == "humidity":
            if mode == "smooth":
                change = random.uniform(-2, 2)
                self._sensor_state["humidity"] += change
                self._sensor_state["humidity"] = max(30, min(80, self._sensor_state["humidity"]))
                new_value = round(self._sensor_state["humidity"], 1)
            else:
                new_value = round(random.uniform(30, 80), 1)
        
        elif self.device.type == "motion":
            # Движение - случайные события
            if random.random() < 0.1:  # 10% шанс
                self._sensor_state["motion"] = True
                new_value = True
            else:
                self._sensor_state["motion"] = False
                new_value = False
        
        elif self.device.type == "light":
            # Освещенность - синусоида + шум
            hour = datetime.now().hour
            base = 100 + 400 * (1 - abs(hour - 12) / 12)
            noise = random.uniform(-50, 50)
            new_value = max(0, round(base + noise))
        
        elif self.device.type == "door":
            # Дверь - редкие события
            if random.random() < 0.05:  # 5% шанс
                self._sensor_state["door"] = not self._sensor_state["door"]
                new_value = self._sensor_state["door"]
        
        if new_value is not None:
            old_value = self.device.state.get("value")
            self.device.state["value"] = new_value
            self.device.last_seen = datetime.now().isoformat()
            
            # Отправить событие только если значение изменилось
            if old_value != new_value:
                self.value_changed.emit(self.device.id, {"value": new_value})
                self.event_bus.emit("sensor_update", {
                    "device_id": self.device.id,
                    "device_name": self.device.name,
                    "type": self.device.type,
                    "value": new_value,
                    "room_id": self.device.room_id
                })
    
    def control(self, action: str, value: Optional[Any] = None):
        """Управление актуатором"""
        if self.device.category != "actuator":
            return
        
        if action == "on":
            self.device.state["powered"] = True
        elif action == "off":
            self.device.state["powered"] = False
        elif action == "set_level" and value is not None:
            self.device.state["level"] = value
        
        self.device.last_seen = datetime.now().isoformat()
        
        self.event_bus.emit("actuator_update", {
            "device_id": self.device.id,
            "device_name": self.device.name,
            "type": self.device.type,
            "action": action,
            "value": value,
            "state": self.device.state.copy(),
            "room_id": self.device.room_id
        })
    
    def stop(self):
        """Остановить симулятор"""
        self.timer.stop()


class SimulatorManager(QObject):
    """Менеджер всех симуляторов"""
    
    def __init__(self, event_bus: EventBus):
        super().__init__()
        self.event_bus = event_bus
        self.simulators: Dict[str, DeviceSimulator] = {}
    
    def add_device(self, device: Device):
        """Добавить устройство для симуляции"""
        if device.id in self.simulators:
            self.remove_device(device.id)
        
        simulator = DeviceSimulator(device, self.event_bus)
        self.simulators[device.id] = simulator
    
    def remove_device(self, device_id: str):
        """Удалить устройство из симуляции"""
        if device_id in self.simulators:
            self.simulators[device_id].stop()
            del self.simulators[device_id]
    
    def control_device(self, device_id: str, action: str, value: Optional[Any] = None):
        """Управление устройством"""
        if device_id in self.simulators:
            self.simulators[device_id].control(action, value)
    
    def stop_all(self):
        """Остановить все симуляторы"""
        for simulator in self.simulators.values():
            simulator.stop()
        self.simulators.clear()
