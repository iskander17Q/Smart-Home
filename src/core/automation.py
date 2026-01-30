"""Движок автоматизации (правила if-then)"""
from datetime import datetime
from typing import Dict, Any, Optional
from .models import AutomationRule, Device
from .event_bus import EventBus


class AutomationEngine:
    """Обработчик правил автоматизации"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.rules: Dict[str, AutomationRule] = {}
        self.devices: Dict[str, Device] = {}
        
        # Подписка на события датчиков
        self.event_bus.subscribe("sensor_update", self._on_sensor_update)
    
    def set_rules(self, rules: Dict[str, AutomationRule]):
        """Установить правила"""
        self.rules = rules
    
    def set_devices(self, devices: Dict[str, Device]):
        """Установить устройства"""
        self.devices = devices
    
    def _on_sensor_update(self, event: Dict[str, Any]):
        """Обработка обновления датчика"""
        data = event.get("data", {})
        device_id = data.get("device_id")
        value = data.get("value")
        
        if not device_id or value is None:
            return
        
        # Проверить все правила
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            if rule.if_sensor_id != device_id:
                continue
            
            # Проверить условие
            if self._check_condition(rule, value):
                # Проверить временное окно
                if self._check_time_window(rule):
                    # Выполнить действие
                    self._execute_action(rule)
    
    def _check_condition(self, rule: AutomationRule, sensor_value: Any) -> bool:
        """Проверить условие правила"""
        condition = rule.condition
        
        if condition == "triggered":
            return bool(sensor_value)
        elif condition == "opened":
            return bool(sensor_value)
        elif condition == ">":
            if rule.value is not None:
                try:
                    return float(sensor_value) > float(rule.value)
                except (ValueError, TypeError):
                    return False
        elif condition == "<":
            if rule.value is not None:
                try:
                    return float(sensor_value) < float(rule.value)
                except (ValueError, TypeError):
                    return False
        elif condition == "==":
            if rule.value is not None:
                try:
                    return float(sensor_value) == float(rule.value)
                except (ValueError, TypeError):
                    return str(sensor_value) == str(rule.value)
        
        return False
    
    def _check_time_window(self, rule: AutomationRule) -> bool:
        """Проверить временное окно"""
        if not rule.time_window:
            return True
        
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        start = rule.time_window.get("start", "00:00")
        end = rule.time_window.get("end", "23:59")
        
        # Простая проверка времени
        if start <= end:
            return start <= current_time <= end
        else:  # Переход через полночь
            return current_time >= start or current_time <= end
    
    def _execute_action(self, rule: AutomationRule):
        """Выполнить действие правила"""
        if not rule.then_device_id:
            return
        
        device = self.devices.get(rule.then_device_id)
        if not device or device.category != "actuator":
            return
        
        # Отправить событие для управления устройством
        self.event_bus.emit("rule_triggered", {
            "rule_id": rule.id,
            "rule_name": rule.name,
            "device_id": rule.then_device_id,
            "action": rule.action,
            "action_value": rule.action_value
        })
