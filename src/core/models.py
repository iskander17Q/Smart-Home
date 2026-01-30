"""Модели данных для умного дома"""
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, Literal
from datetime import datetime
import uuid


@dataclass
class Room:
    id: str
    name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Room':
        return cls(**data)


@dataclass
class Device:
    id: str
    name: str
    room_id: str
    category: Literal["sensor", "actuator"]
    type: str  # temperature, humidity, motion, light, door, socket, kettle, fan, heater
    state: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    last_seen: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Device':
        return cls(**data)


@dataclass
class AutomationRule:
    id: str
    enabled: bool
    if_sensor_id: str
    condition: str  # >, <, ==, triggered, opened
    value: Optional[float] = None
    time_window: Optional[Dict[str, str]] = None  # {"start": "22:00", "end": "06:00"}
    then_device_id: str = ""
    action: str = ""  # on, off, set_level
    action_value: Optional[float] = None
    name: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationRule':
        return cls(**data)


@dataclass
class LogEntry:
    timestamp: str
    type: str  # sensor, actuator, rule, system
    source: str
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        return cls(**data)
