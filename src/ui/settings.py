"""Экран настроек"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QSpinBox, QGroupBox, QFormLayout,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SettingsWidget(QWidget):
    """Виджет настроек"""
    
    def __init__(self, storage, event_bus):
        super().__init__()
        self.storage = storage
        self.event_bus = event_bus
        self._init_ui()
    
    def _init_ui(self):
        """Инициализация UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("Настройки")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Режим работы
        mode_group = QGroupBox("Режим работы")
        mode_group.setStyleSheet("""
            QGroupBox {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                color: white;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        mode_layout = QFormLayout(mode_group)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["local", "mqtt"])
        self.mode_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #3a3a3a;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        mode_layout.addRow("Режим:", self.mode_combo)
        
        layout.addWidget(mode_group)
        
        # MQTT настройки
        mqtt_group = QGroupBox("Настройки MQTT")
        mqtt_group.setStyleSheet("""
            QGroupBox {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                color: white;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        mqtt_layout = QFormLayout(mqtt_group)
        
        self.mqtt_host = QLineEdit()
        self.mqtt_host.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #3a3a3a;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        mqtt_layout.addRow("Host:", self.mqtt_host)
        
        self.mqtt_port = QSpinBox()
        self.mqtt_port.setRange(1, 65535)
        self.mqtt_port.setValue(1883)
        self.mqtt_port.setStyleSheet("""
            QSpinBox {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #3a3a3a;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        mqtt_layout.addRow("Port:", self.mqtt_port)
        
        self.mqtt_topic = QLineEdit()
        self.mqtt_topic.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #3a3a3a;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        mqtt_layout.addRow("Base Topic:", self.mqtt_topic)
        
        btn_test = QPushButton("Тест подключения")
        btn_test.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        btn_test.clicked.connect(self._test_mqtt)
        mqtt_layout.addRow("", btn_test)
        
        layout.addWidget(mqtt_group)
        
        # Действия
        actions_group = QGroupBox("Действия")
        actions_group.setStyleSheet("""
            QGroupBox {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                color: white;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        actions_layout = QVBoxLayout(actions_group)
        
        btn_reset = QPushButton("🔄 Сбросить демо-данные")
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        btn_reset.clicked.connect(self._reset_demo_data)
        actions_layout.addWidget(btn_reset)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        # Кнопка сохранения
        btn_save = QPushButton("💾 Сохранить настройки")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        btn_save.clicked.connect(self._save_settings)
        layout.addWidget(btn_save)
        
        self.refresh()
    
    def refresh(self):
        """Обновить настройки"""
        settings = self.storage.get_settings()
        
        # Режим
        mode = settings.get("mode", "local")
        index = self.mode_combo.findText(mode)
        if index >= 0:
            self.mode_combo.setCurrentIndex(index)
        
        # MQTT
        mqtt = settings.get("mqtt", {})
        self.mqtt_host.setText(mqtt.get("host", "localhost"))
        self.mqtt_port.setValue(mqtt.get("port", 1883))
        self.mqtt_topic.setText(mqtt.get("base_topic", "smarthome"))
    
    def _save_settings(self):
        """Сохранить настройки"""
        settings = {
            "mode": self.mode_combo.currentText(),
            "mqtt": {
                "host": self.mqtt_host.text(),
                "port": self.mqtt_port.value(),
                "base_topic": self.mqtt_topic.text()
            }
        }
        
        self.storage.update_settings(settings)
        QMessageBox.information(self, "Успех", "Настройки сохранены")
        
        # Уведомить о необходимости перезапуска для MQTT
        if settings["mode"] == "mqtt":
            QMessageBox.warning(
                self, "Внимание",
                "Для применения MQTT режима требуется перезапуск приложения.\n"
                "MQTT режим пока не реализован полностью."
            )
    
    def _test_mqtt(self):
        """Тест подключения MQTT"""
        QMessageBox.information(
            self, "Информация",
            "MQTT режим пока не реализован.\n"
            "В текущей версии используется только Local Simulation Mode."
        )
    
    def _reset_demo_data(self):
        """Сбросить демо-данные"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите сбросить все данные к демо-версии?\n"
            "Все текущие данные будут потеряны!",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.storage.reset_demo_data()
            QMessageBox.information(self, "Успех", "Данные сброшены. Перезапустите приложение.")
            self.event_bus.emit("data_reset", {})
