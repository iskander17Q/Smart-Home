"""Экран устройств"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QComboBox, QLineEdit, QSpinBox, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import uuid
from ..core.models import Device


class DevicesWidget(QWidget):
    """Виджет устройств"""
    
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
        
        # Заголовок и кнопка добавления
        header = QHBoxLayout()
        title = QLabel("Устройства")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        header.addWidget(title)
        header.addStretch()
        
        btn_add = QPushButton("➕ Добавить устройство")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        btn_add.clicked.connect(self._add_device)
        header.addWidget(btn_add)
        
        layout.addLayout(header)
        
        # Фильтры
        filters = QHBoxLayout()
        filters.addWidget(QLabel("Фильтр по комнате:"))
        self.filter_room = QComboBox()
        self.filter_room.addItem("Все комнаты")
        self.filter_room.setStyleSheet("""
            QComboBox {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3a3a3a;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        self.filter_room.currentTextChanged.connect(self.refresh)
        filters.addWidget(self.filter_room)
        filters.addStretch()
        layout.addLayout(filters)
        
        # Таблица устройств
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Название", "Комната", "Категория", "Тип", "Состояние", "Последнее обновление", "Действия"
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: white;
                border: none;
                gridline-color: #3a3a3a;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)
        
        self.refresh()
    
    def _connect_events(self):
        """Подключить события"""
        self.event_bus.event_emitted.connect(self._on_event)
    
    def _on_event(self, event: dict):
        """Обработка события"""
        event_type = event.get("type")
        if event_type in ["sensor_update", "actuator_update"]:
            self.refresh()
    
    def refresh(self):
        """Обновить таблицу"""
        # Обновить фильтр комнат
        current_filter = self.filter_room.currentText()
        self.filter_room.clear()
        self.filter_room.addItem("Все комнаты")
        for room in self.storage.get_rooms():
            self.filter_room.addItem(room.name)
        if current_filter and current_filter != "Все комнаты":
            index = self.filter_room.findText(current_filter)
            if index >= 0:
                self.filter_room.setCurrentIndex(index)
        
        # Получить устройства
        devices = self.storage.get_devices()
        rooms = {r.id: r.name for r in self.storage.get_rooms()}
        
        # Применить фильтр
        filter_room_name = self.filter_room.currentText()
        if filter_room_name != "Все комнаты":
            room_id = next((r.id for r in self.storage.get_rooms() if r.name == filter_room_name), None)
            if room_id:
                devices = [d for d in devices if d.room_id == room_id]
        
        # Заполнить таблицу
        self.table.setRowCount(len(devices))
        for row, device in enumerate(devices):
            self.table.setItem(row, 0, QTableWidgetItem(device.name))
            self.table.setItem(row, 1, QTableWidgetItem(rooms.get(device.room_id, "N/A")))
            self.table.setItem(row, 2, QTableWidgetItem("Датчик" if device.category == "sensor" else "Актуатор"))
            self.table.setItem(row, 3, QTableWidgetItem(device.type))
            
            # Состояние
            if device.category == "sensor":
                value = device.state.get("value", "N/A")
                state_text = str(value)
            else:
                powered = device.state.get("powered", False)
                state_text = "ВКЛ" if powered else "ВЫКЛ"
            self.table.setItem(row, 4, QTableWidgetItem(state_text))
            
            # Последнее обновление
            last_seen = device.last_seen or "Никогда"
            if device.last_seen:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(device.last_seen)
                    last_seen = dt.strftime("%H:%M:%S")
                except:
                    pass
            self.table.setItem(row, 5, QTableWidgetItem(last_seen))
            
            # Действия
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
            """)
            btn_edit.clicked.connect(lambda checked, d=device: self._edit_device(d))
            actions_layout.addWidget(btn_edit)
            
            btn_delete = QPushButton("🗑️")
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #d32f2f;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
            """)
            btn_delete.clicked.connect(lambda checked, d=device: self._delete_device(d))
            actions_layout.addWidget(btn_delete)
            
            self.table.setCellWidget(row, 6, actions_widget)
    
    def _add_device(self):
        """Добавить устройство"""
        dialog = DeviceDialog(self.storage, self)
        if dialog.exec():
            device_data = dialog.get_device_data()
            device = Device(
                id=f"dev_{uuid.uuid4().hex[:8]}",
                name=device_data["name"],
                room_id=device_data["room_id"],
                category=device_data["category"],
                type=device_data["type"],
                state={},
                config=device_data.get("config", {}),
                last_seen=None
            )
            
            if device.category == "sensor":
                device.state = {"value": 0}
            else:
                device.state = {"powered": False}
            
            self.storage.add_device(device)
            self.simulator_manager.add_device(device)
            self.refresh()
    
    def _edit_device(self, device: Device):
        """Редактировать устройство"""
        dialog = DeviceDialog(self.storage, self, device)
        if dialog.exec():
            device_data = dialog.get_device_data()
            device.name = device_data["name"]
            device.room_id = device_data["room_id"]
            device.type = device_data["type"]
            if "config" in device_data:
                device.config.update(device_data["config"])
            
            self.storage.update_device(device)
            # Пересоздать симулятор
            self.simulator_manager.remove_device(device.id)
            self.simulator_manager.add_device(device)
            self.refresh()
    
    def _delete_device(self, device: Device):
        """Удалить устройство"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить устройство '{device.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.simulator_manager.remove_device(device.id)
            self.storage.delete_device(device.id)
            self.refresh()


class DeviceDialog(QDialog):
    """Диалог добавления/редактирования устройства"""
    
    def __init__(self, storage, parent=None, device=None):
        super().__init__(parent)
        self.storage = storage
        self.device = device
        self.setWindowTitle("Добавить устройство" if not device else "Редактировать устройство")
        self.setMinimumWidth(400)
        self._init_ui()
    
    def _init_ui(self):
        """Инициализация UI"""
        layout = QFormLayout(self)
        
        # Название
        self.name_edit = QLineEdit()
        if self.device:
            self.name_edit.setText(self.device.name)
        layout.addRow("Название:", self.name_edit)
        
        # Комната
        self.room_combo = QComboBox()
        for room in self.storage.get_rooms():
            self.room_combo.addItem(room.name, room.id)
        if self.device:
            index = self.room_combo.findData(self.device.room_id)
            if index >= 0:
                self.room_combo.setCurrentIndex(index)
        layout.addRow("Комната:", self.room_combo)
        
        # Категория
        self.category_combo = QComboBox()
        self.category_combo.addItems(["sensor", "actuator"])
        if self.device:
            index = self.category_combo.findText(self.device.category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        layout.addRow("Категория:", self.category_combo)
        
        # Тип
        self.type_combo = QComboBox()
        self._update_type_combo()
        if self.device:
            index = self.type_combo.findText(self.device.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        layout.addRow("Тип:", self.type_combo)
        
        # Конфигурация для датчиков
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(500, 10000)
        self.interval_spin.setValue(2000)
        self.interval_spin.setSuffix(" мс")
        if self.device and self.device.category == "sensor":
            self.interval_spin.setValue(self.device.config.get("update_interval", 2000))
        layout.addRow("Интервал обновления:", self.interval_spin)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["random", "smooth", "manual"])
        if self.device and self.device.category == "sensor":
            mode = self.device.config.get("mode", "random")
            index = self.mode_combo.findText(mode)
            if index >= 0:
                self.mode_combo.setCurrentIndex(index)
        layout.addRow("Режим генерации:", self.mode_combo)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self._on_category_changed()
    
    def _on_category_changed(self):
        """Обработка изменения категории"""
        self._update_type_combo()
        category = self.category_combo.currentText()
        self.interval_spin.setEnabled(category == "sensor")
        self.mode_combo.setEnabled(category == "sensor")
    
    def _update_type_combo(self):
        """Обновить список типов"""
        self.type_combo.clear()
        category = self.category_combo.currentText()
        if category == "sensor":
            self.type_combo.addItems(["temperature", "humidity", "motion", "light", "door"])
        else:
            self.type_combo.addItems(["light", "socket", "kettle", "fan", "heater"])
    
    def get_device_data(self):
        """Получить данные устройства"""
        return {
            "name": self.name_edit.text(),
            "room_id": self.room_combo.currentData(),
            "category": self.category_combo.currentText(),
            "type": self.type_combo.currentText(),
            "config": {
                "update_interval": self.interval_spin.value(),
                "mode": self.mode_combo.currentText()
            } if self.category_combo.currentText() == "sensor" else {}
        }
