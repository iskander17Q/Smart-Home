"""Event Bus для публикации и подписки на события"""
from typing import Callable, Dict, List, Any
from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    """Централизованная система событий"""
    
    # Сигнал для всех событий
    event_emitted = Signal(dict)
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers: Dict[str, List[Callable]] = {}
        return cls._instance
    
    def subscribe(self, event_type: str, callback: Callable):
        """Подписаться на событие"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Отписаться от события"""
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
    
    def emit(self, event_type: str, data: Dict[str, Any]):
        """Опубликовать событие"""
        event = {
            "type": event_type,
            "data": data
        }
        
        # Уведомить через сигнал Qt
        self.event_emitted.emit(event)
        
        # Уведомить подписчиков напрямую
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")
