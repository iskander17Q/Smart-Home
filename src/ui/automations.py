"""Экран автоматизации"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QComboBox, QLineEdit, QDoubleSpinBox, QTimeEdit, QCheckBox,
    QDialogButtonBox, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QFont
import uuid
from ..core.models import AutomationRule


class AutomationsWidget(QWidget):
    """Виджет автоматизации"""
    
    def __init__(self, storage, event_bus, automation_engine):
        super().__init__()
        self.storage = storage
        self.event_bus = event_bus
        self.automation_engine = automation_engine
        self._init_ui()
        self._connect_events()
    
    def _init_ui(self):
        """Инициализация UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Заголовок и кнопка добавления
        header = QHBoxLayout()
        title = QLabel("Автоматизация")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        header.addWidget(title)
        header.addStretch()
        
        btn_add = QPushButton("➕ Добавить правило")
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
        btn_add.clicked.connect(self._add_rule)
        header.addWidget(btn_add)
        
        layout.addLayout(header)
        
        # Таблица правил
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Название", "Условие", "Действие", "Временное окно", "Статус", "Действия"
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
        if event_type == "rule_triggered":
            self.refresh()
    
    def refresh(self):
        """Обновить таблицу"""
        rules = self.storage.get_rules()
        devices = {d.id: d for d in self.storage.get_devices()}
        
        self.table.setRowCount(len(rules))
        for row, rule in enumerate(rules):
            # Название
            name = rule.name or f"Правило {rule.id}"
            self.table.setItem(row, 0, QTableWidgetItem(name))
            
            # Условие
            sensor = devices.get(rule.if_sensor_id)
            sensor_name = sensor.name if sensor else "N/A"
            condition_text = f"IF {sensor_name} {rule.condition}"
            if rule.value is not None:
                condition_text += f" {rule.value}"
            self.table.setItem(row, 1, QTableWidgetItem(condition_text))
            
            # Действие
            device = devices.get(rule.then_device_id)
            device_name = device.name if device else "N/A"
            action_text = f"THEN {device_name} {rule.action}"
            if rule.action_value is not None:
                action_text += f" ({rule.action_value})"
            self.table.setItem(row, 2, QTableWidgetItem(action_text))
            
            # Временное окно
            if rule.time_window:
                tw = rule.time_window
                time_text = f"{tw.get('start', '')} - {tw.get('end', '')}"
            else:
                time_text = "Всегда"
            self.table.setItem(row, 3, QTableWidgetItem(time_text))
            
            # Статус
            status_item = QTableWidgetItem("Включено" if rule.enabled else "Выключено")
            status_item.setForeground(Qt.green if rule.enabled else Qt.red)
            self.table.setItem(row, 4, status_item)
            
            # Действия
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            btn_toggle = QPushButton("🔄" if rule.enabled else "▶️")
            btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
            """)
            btn_toggle.clicked.connect(lambda checked, r=rule: self._toggle_rule(r))
            actions_layout.addWidget(btn_toggle)
            
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
            btn_edit.clicked.connect(lambda checked, r=rule: self._edit_rule(r))
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
            btn_delete.clicked.connect(lambda checked, r=rule: self._delete_rule(r))
            actions_layout.addWidget(btn_delete)
            
            self.table.setCellWidget(row, 5, actions_widget)
    
    def _add_rule(self):
        """Добавить правило"""
        dialog = RuleDialog(self.storage, self)
        if dialog.exec():
            rule_data = dialog.get_rule_data()
            rule = AutomationRule(
                id=f"rule_{uuid.uuid4().hex[:8]}",
                enabled=True,
                name=rule_data["name"],
                if_sensor_id=rule_data["if_sensor_id"],
                condition=rule_data["condition"],
                value=rule_data.get("value"),
                time_window=rule_data.get("time_window"),
                then_device_id=rule_data["then_device_id"],
                action=rule_data["action"],
                action_value=rule_data.get("action_value")
            )
            
            self.storage.add_rule(rule)
            self._update_automation_engine()
            self.refresh()
    
    def _edit_rule(self, rule: AutomationRule):
        """Редактировать правило"""
        dialog = RuleDialog(self.storage, self, rule)
        if dialog.exec():
            rule_data = dialog.get_rule_data()
            rule.name = rule_data["name"]
            rule.enabled = rule_data.get("enabled", rule.enabled)
            rule.if_sensor_id = rule_data["if_sensor_id"]
            rule.condition = rule_data["condition"]
            rule.value = rule_data.get("value")
            rule.time_window = rule_data.get("time_window")
            rule.then_device_id = rule_data["then_device_id"]
            rule.action = rule_data["action"]
            rule.action_value = rule_data.get("action_value")
            
            self.storage.update_rule(rule)
            self._update_automation_engine()
            self.refresh()
    
    def _toggle_rule(self, rule: AutomationRule):
        """Переключить правило"""
        rule.enabled = not rule.enabled
        self.storage.update_rule(rule)
        self._update_automation_engine()
        self.refresh()
    
    def _delete_rule(self, rule: AutomationRule):
        """Удалить правило"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить правило '{rule.name or rule.id}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.storage.delete_rule(rule.id)
            self._update_automation_engine()
            self.refresh()
    
    def _update_automation_engine(self):
        """Обновить движок автоматизации"""
        rules = {r.id: r for r in self.storage.get_rules()}
        devices = {d.id: d for d in self.storage.get_devices()}
        self.automation_engine.set_rules(rules)
        self.automation_engine.set_devices(devices)


class RuleDialog(QDialog):
    """Диалог добавления/редактирования правила"""
    
    def __init__(self, storage, parent=None, rule=None):
        super().__init__(parent)
        self.storage = storage
        self.rule = rule
        self.setWindowTitle("Добавить правило" if not rule else "Редактировать правило")
        self.setMinimumWidth(500)
        self._init_ui()
    
    def _init_ui(self):
        """Инициализация UI"""
        layout = QVBoxLayout(self)
        
        # Название
        form = QFormLayout()
        self.name_edit = QLineEdit()
        if self.rule:
            self.name_edit.setText(self.rule.name)
        form.addRow("Название правила:", self.name_edit)
        
        # Условие IF
        if_group = QGroupBox("Условие (IF)")
        if_layout = QFormLayout(if_group)
        
        self.sensor_combo = QComboBox()
        sensors = [d for d in self.storage.get_devices() if d.category == "sensor"]
        for sensor in sensors:
            self.sensor_combo.addItem(sensor.name, sensor.id)
        if self.rule:
            index = self.sensor_combo.findData(self.rule.if_sensor_id)
            if index >= 0:
                self.sensor_combo.setCurrentIndex(index)
        self.sensor_combo.currentIndexChanged.connect(self._on_sensor_changed)
        if_layout.addRow("Датчик:", self.sensor_combo)
        
        self.condition_combo = QComboBox()
        self.condition_combo.addItems([">", "<", "==", "triggered", "opened"])
        if self.rule:
            index = self.condition_combo.findText(self.rule.condition)
            if index >= 0:
                self.condition_combo.setCurrentIndex(index)
        self.condition_combo.currentTextChanged.connect(self._on_condition_changed)
        if_layout.addRow("Условие:", self.condition_combo)
        
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(-100, 100)
        self.value_spin.setDecimals(1)
        if self.rule and self.rule.value is not None:
            self.value_spin.setValue(self.rule.value)
        if_layout.addRow("Значение:", self.value_spin)
        
        layout.addLayout(form)
        layout.addWidget(if_group)
        
        # Временное окно
        time_group = QGroupBox("Временное окно (опционально)")
        time_layout = QFormLayout(time_group)
        
        self.time_enabled = QCheckBox("Ограничить по времени")
        if self.rule and self.rule.time_window:
            self.time_enabled.setChecked(True)
        time_layout.addRow(self.time_enabled)
        
        self.time_start = QTimeEdit()
        self.time_start.setDisplayFormat("HH:mm")
        if self.rule and self.rule.time_window:
            start = self.rule.time_window.get("start", "22:00")
            try:
                hour, minute = map(int, start.split(":"))
                self.time_start.setTime(QTime(hour, minute))
            except:
                pass
        else:
            self.time_start.setTime(QTime(22, 0))
        time_layout.addRow("Начало:", self.time_start)
        
        self.time_end = QTimeEdit()
        self.time_end.setDisplayFormat("HH:mm")
        if self.rule and self.rule.time_window:
            end = self.rule.time_window.get("end", "06:00")
            try:
                hour, minute = map(int, end.split(":"))
                self.time_end.setTime(QTime(hour, minute))
            except:
                pass
        else:
            self.time_end.setTime(QTime(6, 0))
        time_layout.addRow("Конец:", self.time_end)
        
        layout.addWidget(time_group)
        
        # Действие THEN
        then_group = QGroupBox("Действие (THEN)")
        then_layout = QFormLayout(then_group)
        
        self.device_combo = QComboBox()
        actuators = [d for d in self.storage.get_devices() if d.category == "actuator"]
        for actuator in actuators:
            self.device_combo.addItem(actuator.name, actuator.id)
        if self.rule:
            index = self.device_combo.findData(self.rule.then_device_id)
            if index >= 0:
                self.device_combo.setCurrentIndex(index)
        then_layout.addRow("Устройство:", self.device_combo)
        
        self.action_combo = QComboBox()
        self.action_combo.addItems(["on", "off", "set_level"])
        if self.rule:
            index = self.action_combo.findText(self.rule.action)
            if index >= 0:
                self.action_combo.setCurrentIndex(index)
        self.action_combo.currentTextChanged.connect(self._on_action_changed)
        then_layout.addRow("Действие:", self.action_combo)
        
        self.action_value_spin = QDoubleSpinBox()
        self.action_value_spin.setRange(0, 100)
        self.action_value_spin.setDecimals(1)
        if self.rule and self.rule.action_value is not None:
            self.action_value_spin.setValue(self.rule.action_value)
        then_layout.addRow("Значение:", self.action_value_spin)
        
        layout.addWidget(then_group)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self._on_sensor_changed()
        self._on_condition_changed()
        self._on_action_changed()
    
    def _on_sensor_changed(self):
        """Обработка изменения датчика"""
        # Можно добавить логику для определения типа датчика
        pass
    
    def _on_condition_changed(self):
        """Обработка изменения условия"""
        condition = self.condition_combo.currentText()
        self.value_spin.setEnabled(condition in [">", "<", "=="])
    
    def _on_action_changed(self):
        """Обработка изменения действия"""
        action = self.action_combo.currentText()
        self.action_value_spin.setEnabled(action == "set_level")
    
    def get_rule_data(self):
        """Получить данные правила"""
        time_window = None
        if self.time_enabled.isChecked():
            time_window = {
                "start": self.time_start.time().toString("HH:mm"),
                "end": self.time_end.time().toString("HH:mm")
            }
        
        return {
            "name": self.name_edit.text(),
            "if_sensor_id": self.sensor_combo.currentData(),
            "condition": self.condition_combo.currentText(),
            "value": self.value_spin.value() if self.value_spin.isEnabled() else None,
            "time_window": time_window,
            "then_device_id": self.device_combo.currentData(),
            "action": self.action_combo.currentText(),
            "action_value": self.action_value_spin.value() if self.action_value_spin.isEnabled() else None
        }
