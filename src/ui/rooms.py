"""Экран комнат"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import List
from ..core.models import Room, Device


class RoomsWidget(QWidget):
    """Виджет комнат"""
    
    def __init__(self, storage, event_bus, simulator_manager):
        super().__init__()
        self.storage = storage
        self.event_bus = event_bus
        self.simulator_manager = simulator_manager
        self._init_ui()
    
    def _init_ui(self):
        """Инициализация UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("Комнаты")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Контейнер комнат
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(15)
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll, 1)
        
        self.refresh()
    
    def refresh(self):
        """Обновить данные"""
        # Очистить старые карточки
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        rooms = self.storage.get_rooms()
        devices = self.storage.get_devices()
        
        # Группировать устройства по комнатам
        room_devices: dict = {}
        for device in devices:
            if device.room_id not in room_devices:
                room_devices[device.room_id] = []
            room_devices[device.room_id].append(device)
        
        # Создать карточки комнат
        for room in rooms:
            card = self._create_room_detail_card(room, room_devices.get(room.id, []))
            self.container_layout.addWidget(card)
        
        self.container_layout.addStretch()
    
    def _create_room_detail_card(self, room: Room, devices: List[Device]) -> QFrame:
        """Создать детальную карточку комнаты"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        # Название комнаты
        title = QLabel(room.name)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Устройства
        if devices:
            devices_label = QLabel("Устройства:")
            devices_label.setStyleSheet("color: #cccccc; font-size: 14px;")
            layout.addWidget(devices_label)
            
            devices_layout = QGridLayout()
            devices_layout.setSpacing(10)
            
            row = 0
            for device in devices:
                device_widget = self._create_device_widget(device)
                devices_layout.addWidget(device_widget, row // 2, row % 2)
                row += 1
            
            layout.addLayout(devices_layout)
        else:
            no_devices = QLabel("Нет устройств")
            no_devices.setStyleSheet("color: #888888; font-style: italic;")
            layout.addWidget(no_devices)
        
        return card
    
    def _create_device_widget(self, device: Device) -> QFrame:
        """Создать виджет устройства"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        # Название
        name = QLabel(device.name)
        name.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(name)
        
        # Тип
        type_label = QLabel(f"Тип: {device.type}")
        type_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        layout.addWidget(type_label)
        
        # Состояние
        if device.category == "sensor":
            value = device.state.get("value", "N/A")
            state_label = QLabel(f"Значение: {value}")
        else:
            powered = device.state.get("powered", False)
            state_label = QLabel(f"Состояние: {'ВКЛ' if powered else 'ВЫКЛ'}")
        
        state_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(state_label)
        
        # Кнопка управления (для актуаторов)
        if device.category == "actuator":
            btn = QPushButton("Переключить")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 6px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """)
            btn.clicked.connect(lambda checked, d=device: self._toggle_device(d))
            layout.addWidget(btn)
        
        return widget
    
    def _toggle_device(self, device: Device):
        """Переключить устройство"""
        current_state = device.state.get("powered", False)
        action = "off" if current_state else "on"
        self.simulator_manager.control_device(device.id, action)
        self.refresh()
