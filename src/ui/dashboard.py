"""Dashboard экран"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Dict, List
from ..core.models import Room, Device, LogEntry


class DashboardWidget(QWidget):
    """Виджет дашборда"""
    
    refresh_needed = Signal()
    
    def __init__(self, storage, event_bus, simulator_manager):
        super().__init__()
        self.storage = storage
        self.event_bus = event_bus
        self.simulator_manager = simulator_manager
        self._init_ui()
        self._connect_events()
    
    def _init_ui(self):
        """Инициализация UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Быстрые кнопки
        quick_actions = QHBoxLayout()
        quick_actions.setSpacing(10)
        
        btn_all_off = QPushButton("🔌 Выключить весь свет")
        btn_night = QPushButton("🌙 Режим Ночь")
        btn_away = QPushButton("🚪 Я ушёл")
        
        for btn in [btn_all_off, btn_night, btn_away]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """)
        
        btn_all_off.clicked.connect(self._all_lights_off)
        btn_night.clicked.connect(self._night_mode)
        btn_away.clicked.connect(self._away_mode)
        
        quick_actions.addWidget(btn_all_off)
        quick_actions.addWidget(btn_night)
        quick_actions.addWidget(btn_away)
        quick_actions.addStretch()
        
        layout.addLayout(quick_actions)
        
        # Карточки комнат
        self.rooms_scroll = QScrollArea()
        self.rooms_scroll.setWidgetResizable(True)
        self.rooms_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.rooms_container = QWidget()
        self.rooms_layout = QGridLayout(self.rooms_container)
        self.rooms_layout.setSpacing(15)
        self.rooms_scroll.setWidget(self.rooms_container)
        
        layout.addWidget(self.rooms_scroll, 1)
        
        # Лог событий
        logs_label = QLabel("Последние события")
        logs_label.setFont(QFont("Arial", 14, QFont.Bold))
        logs_label.setStyleSheet("color: white;")
        layout.addWidget(logs_label)
        
        self.logs_area = QFrame()
        self.logs_area.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.logs_layout = QVBoxLayout(self.logs_area)
        self.logs_layout.setSpacing(5)
        
        layout.addWidget(self.logs_area)
        
        self.refresh()
    
    def _connect_events(self):
        """Подключить события"""
        self.event_bus.event_emitted.connect(self._on_event)
    
    def _on_event(self, event: dict):
        """Обработка события"""
        event_type = event.get("type")
        if event_type in ["sensor_update", "actuator_update", "rule_triggered"]:
            self.refresh()
    
    def _all_lights_off(self):
        """Выключить весь свет"""
        devices = self.storage.get_devices()
        for device in devices:
            if device.category == "actuator" and device.type == "light":
                self.simulator_manager.control_device(device.id, "off")
        self.refresh_needed.emit()
    
    def _night_mode(self):
        """Режим ночь"""
        devices = self.storage.get_devices()
        for device in devices:
            if device.category == "actuator":
                if device.type == "light":
                    self.simulator_manager.control_device(device.id, "off")
                elif device.type in ["fan", "heater"]:
                    self.simulator_manager.control_device(device.id, "off")
        self.refresh_needed.emit()
    
    def _away_mode(self):
        """Режим 'Я ушёл'"""
        devices = self.storage.get_devices()
        for device in devices:
            if device.category == "actuator":
                self.simulator_manager.control_device(device.id, "off")
        self.refresh_needed.emit()
    
    def refresh(self):
        """Обновить данные"""
        self._update_rooms()
        self._update_logs()
    
    def _update_rooms(self):
        """Обновить карточки комнат"""
        # Очистить старые карточки
        while self.rooms_layout.count():
            item = self.rooms_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        rooms = self.storage.get_rooms()
        devices = self.storage.get_devices()
        
        # Группировать устройства по комнатам
        room_devices: Dict[str, List[Device]] = {}
        for device in devices:
            if device.room_id not in room_devices:
                room_devices[device.room_id] = []
            room_devices[device.room_id].append(device)
        
        # Создать карточки
        row = 0
        col = 0
        for room in rooms:
            card = self._create_room_card(room, room_devices.get(room.id, []))
            self.rooms_layout.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    def _create_room_card(self, room: Room, devices: List[Device]) -> QFrame:
        """Создать карточку комнаты"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        card.setMinimumHeight(200)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Название комнаты
        title = QLabel(room.name)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Показатели
        sensors = [d for d in devices if d.category == "sensor"]
        for sensor in sensors:
            value = sensor.state.get("value", "N/A")
            unit = self._get_unit(sensor.type)
            label = QLabel(f"{self._get_sensor_name(sensor.type)}: {value} {unit}")
            label.setStyleSheet("color: #cccccc; font-size: 12px;")
            layout.addWidget(label)
        
        layout.addStretch()
        
        return card
    
    def _get_sensor_name(self, sensor_type: str) -> str:
        """Получить название датчика"""
        names = {
            "temperature": "🌡️ Температура",
            "humidity": "💧 Влажность",
            "motion": "👁️ Движение",
            "light": "💡 Освещенность",
            "door": "🚪 Дверь"
        }
        return names.get(sensor_type, sensor_type)
    
    def _get_unit(self, sensor_type: str) -> str:
        """Получить единицу измерения"""
        units = {
            "temperature": "°C",
            "humidity": "%",
            "light": "lx",
            "motion": "",
            "door": ""
        }
        return units.get(sensor_type, "")
    
    def _update_logs(self):
        """Обновить логи"""
        # Очистить старые логи
        while self.logs_layout.count():
            item = self.logs_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        logs = self.storage.get_logs(limit=10)
        for log in reversed(logs):  # Последние сверху
            label = QLabel(f"[{log.timestamp}] {log.source}: {log.message}")
            label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
            self.logs_layout.addWidget(label)
        
        self.logs_layout.addStretch()
