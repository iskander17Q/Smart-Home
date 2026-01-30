"""Хранилище данных в JSON"""
import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from ..core.models import Room, Device, AutomationRule, LogEntry


class Storage:
    """JSON хранилище данных"""
    
    def __init__(self, data_file: str = "data/state.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._data = {
            "rooms": [],
            "devices": [],
            "rules": [],
            "logs": [],
            "settings": {
                "mode": "local",  # local или mqtt
                "mqtt": {
                    "host": "localhost",
                    "port": 1883,
                    "base_topic": "smarthome"
                }
            }
        }
        self._load()
    
    def _load(self):
        """Загрузить данные из файла"""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
                self._data = self._get_default_data()
        else:
            self._data = self._get_default_data()
            self._save()
    
    def _save(self):
        """Сохранить данные в файл"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def _get_default_data(self) -> dict:
        """Получить данные по умолчанию (демо)"""
        return {
            "rooms": [
                {"id": "room_1", "name": "Кухня"},
                {"id": "room_2", "name": "Спальня"},
                {"id": "room_3", "name": "Коридор"}
            ],
            "devices": [
                {
                    "id": "dev_1",
                    "name": "Датчик температуры",
                    "room_id": "room_2",
                    "category": "sensor",
                    "type": "temperature",
                    "state": {"value": 22.0},
                    "config": {"update_interval": 2000, "mode": "smooth"},
                    "last_seen": None
                },
                {
                    "id": "dev_2",
                    "name": "Датчик влажности",
                    "room_id": "room_2",
                    "category": "sensor",
                    "type": "humidity",
                    "state": {"value": 50.0},
                    "config": {"update_interval": 2000, "mode": "smooth"},
                    "last_seen": None
                },
                {
                    "id": "dev_3",
                    "name": "Датчик движения",
                    "room_id": "room_3",
                    "category": "sensor",
                    "type": "motion",
                    "state": {"value": False},
                    "config": {"update_interval": 1000, "mode": "random"},
                    "last_seen": None
                },
                {
                    "id": "dev_4",
                    "name": "Датчик освещенности",
                    "room_id": "room_1",
                    "category": "sensor",
                    "type": "light",
                    "state": {"value": 500.0},
                    "config": {"update_interval": 2000, "mode": "smooth"},
                    "last_seen": None
                },
                {
                    "id": "dev_5",
                    "name": "Свет в коридоре",
                    "room_id": "room_3",
                    "category": "actuator",
                    "type": "light",
                    "state": {"powered": False},
                    "config": {},
                    "last_seen": None
                },
                {
                    "id": "dev_6",
                    "name": "Свет на кухне",
                    "room_id": "room_1",
                    "category": "actuator",
                    "type": "light",
                    "state": {"powered": False},
                    "config": {},
                    "last_seen": None
                },
                {
                    "id": "dev_7",
                    "name": "Чайник",
                    "room_id": "room_1",
                    "category": "actuator",
                    "type": "kettle",
                    "state": {"powered": False},
                    "config": {},
                    "last_seen": None
                },
                {
                    "id": "dev_8",
                    "name": "Вентилятор",
                    "room_id": "room_2",
                    "category": "actuator",
                    "type": "fan",
                    "state": {"powered": False},
                    "config": {},
                    "last_seen": None
                },
                {
                    "id": "dev_9",
                    "name": "Обогреватель",
                    "room_id": "room_2",
                    "category": "actuator",
                    "type": "heater",
                    "state": {"powered": False},
                    "config": {},
                    "last_seen": None
                }
            ],
            "rules": [
                {
                    "id": "rule_1",
                    "enabled": True,
                    "name": "Включить вентилятор при высокой температуре",
                    "if_sensor_id": "dev_1",
                    "condition": ">",
                    "value": 26.0,
                    "time_window": None,
                    "then_device_id": "dev_8",
                    "action": "on",
                    "action_value": None
                },
                {
                    "id": "rule_2",
                    "enabled": True,
                    "name": "Включить свет при движении ночью",
                    "if_sensor_id": "dev_3",
                    "condition": "triggered",
                    "value": None,
                    "time_window": {"start": "22:00", "end": "06:00"},
                    "then_device_id": "dev_5",
                    "action": "on",
                    "action_value": None
                }
            ],
            "logs": [],
            "settings": {
                "mode": "local",
                "mqtt": {
                    "host": "localhost",
                    "port": 1883,
                    "base_topic": "smarthome"
                }
            }
        }
    
    # Rooms
    def get_rooms(self) -> List[Room]:
        """Получить все комнаты"""
        return [Room.from_dict(r) for r in self._data["rooms"]]
    
    def add_room(self, room: Room):
        """Добавить комнату"""
        self._data["rooms"].append(room.to_dict())
        self._save()
    
    def update_room(self, room: Room):
        """Обновить комнату"""
        for i, r in enumerate(self._data["rooms"]):
            if r["id"] == room.id:
                self._data["rooms"][i] = room.to_dict()
                self._save()
                return
    
    def delete_room(self, room_id: str):
        """Удалить комнату"""
        self._data["rooms"] = [r for r in self._data["rooms"] if r["id"] != room_id]
        self._save()
    
    # Devices
    def get_devices(self) -> List[Device]:
        """Получить все устройства"""
        return [Device.from_dict(d) for d in self._data["devices"]]
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Получить устройство по ID"""
        for d in self._data["devices"]:
            if d["id"] == device_id:
                return Device.from_dict(d)
        return None
    
    def add_device(self, device: Device):
        """Добавить устройство"""
        self._data["devices"].append(device.to_dict())
        self._save()
    
    def update_device(self, device: Device):
        """Обновить устройство"""
        for i, d in enumerate(self._data["devices"]):
            if d["id"] == device.id:
                self._data["devices"][i] = device.to_dict()
                self._save()
                return
    
    def delete_device(self, device_id: str):
        """Удалить устройство"""
        self._data["devices"] = [d for d in self._data["devices"] if d["id"] != device_id]
        self._save()
    
    # Rules
    def get_rules(self) -> List[AutomationRule]:
        """Получить все правила"""
        return [AutomationRule.from_dict(r) for r in self._data["rules"]]
    
    def add_rule(self, rule: AutomationRule):
        """Добавить правило"""
        self._data["rules"].append(rule.to_dict())
        self._save()
    
    def update_rule(self, rule: AutomationRule):
        """Обновить правило"""
        for i, r in enumerate(self._data["rules"]):
            if r["id"] == rule.id:
                self._data["rules"][i] = rule.to_dict()
                self._save()
                return
    
    def delete_rule(self, rule_id: str):
        """Удалить правило"""
        self._data["rules"] = [r for r in self._data["rules"] if r["id"] != rule_id]
        self._save()
    
    # Logs
    def add_log(self, log: LogEntry):
        """Добавить лог"""
        self._data["logs"].append(log.to_dict())
        # Ограничить количество логов
        if len(self._data["logs"]) > 1000:
            self._data["logs"] = self._data["logs"][-1000:]
        self._save()
    
    def get_logs(self, limit: Optional[int] = None) -> List[LogEntry]:
        """Получить логи"""
        logs = [LogEntry.from_dict(l) for l in self._data["logs"]]
        if limit:
            logs = logs[-limit:]
        return logs
    
    def clear_logs(self):
        """Очистить логи"""
        self._data["logs"] = []
        self._save()
    
    # Settings
    def get_settings(self) -> dict:
        """Получить настройки"""
        return self._data["settings"].copy()
    
    def update_settings(self, settings: dict):
        """Обновить настройки"""
        self._data["settings"].update(settings)
        self._save()
    
    def reset_demo_data(self):
        """Сбросить данные к демо"""
        self._data = self._get_default_data()
        self._save()
