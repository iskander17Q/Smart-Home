"""Главное окно приложения"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QListWidget, QListWidgetItem, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont
from .dashboard import DashboardWidget
from .rooms import RoomsWidget
from .devices import DevicesWidget
from .automations import AutomationsWidget
from .logs import LogsWidget
from .settings import SettingsWidget


class MainWindow(QMainWindow):
    """Главное окно с боковым меню"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartHome Dashboard")
        self.setMinimumSize(1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Боковое меню
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: none;
                color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #3a3a3a;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
        """)
        
        # Стек виджетов
        self.stacked_widget = QStackedWidget()
        
        # Добавить пункты меню
        menu_items = [
            ("📊 Dashboard", "dashboard"),
            ("🏠 Комнаты", "rooms"),
            ("🔌 Устройства", "devices"),
            ("⚙️ Автоматизация", "automations"),
            ("📋 Логи", "logs"),
            ("⚙️ Настройки", "settings")
        ]
        
        for text, key in menu_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, key)
            self.sidebar.addItem(item)
        
        self.sidebar.currentRowChanged.connect(self._on_menu_changed)
        self.sidebar.setCurrentRow(0)
        
        # Добавить в layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget, 1)
        
        # Виджеты экранов (будут добавлены извне)
        self.widgets = {}
    
    def add_widget(self, key: str, widget: QWidget):
        """Добавить виджет экрана"""
        self.widgets[key] = widget
        self.stacked_widget.addWidget(widget)
    
    def _on_menu_changed(self, index: int):
        """Обработка изменения пункта меню"""
        item = self.sidebar.item(index)
        if item:
            key = item.data(Qt.UserRole)
            if key in self.widgets:
                self.stacked_widget.setCurrentWidget(self.widgets[key])
                # Обновить виджет при переключении
                if hasattr(self.widgets[key], "refresh"):
                    self.widgets[key].refresh()
