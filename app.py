"""Главный файл приложения SmartHome Dashboard"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.storage.storage import Storage
from src.core.event_bus import EventBus
from src.core.simulator import SimulatorManager
from src.core.automation import AutomationEngine
from src.utils.logger import Logger
from src.ui.main_window import MainWindow
from src.ui.dashboard import DashboardWidget
from src.ui.rooms import RoomsWidget
from src.ui.devices import DevicesWidget
from src.ui.automations import AutomationsWidget
from src.ui.logs import LogsWidget
from src.ui.settings import SettingsWidget


def main():
    """Главная функция"""
    # Создать приложение
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Тёмная тема
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
        }
        QWidget {
            background-color: #1e1e1e;
            color: white;
        }
        QDialog {
            background-color: #2b2b2b;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #1e1e1e;
            color: white;
            border: 1px solid #3a3a3a;
            padding: 5px;
            border-radius: 4px;
        }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border: 1px solid #0078d4;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
    """)
    
    # Инициализировать компоненты
    storage = Storage()
    event_bus = EventBus()
    simulator_manager = SimulatorManager(event_bus)
    automation_engine = AutomationEngine(event_bus)
    logger = Logger(storage, event_bus)
    
    # Загрузить устройства и создать симуляторы
    devices = storage.get_devices()
    for device in devices:
        simulator_manager.add_device(device)
    
    # Загрузить правила
    rules = {r.id: r for r in storage.get_rules()}
    devices_dict = {d.id: d for d in devices}
    automation_engine.set_rules(rules)
    automation_engine.set_devices(devices_dict)
    
    # Подключить управление устройствами из правил
    def on_rule_triggered(event: dict):
        data = event.get("data", {})
        device_id = data.get("device_id")
        action = data.get("action")
        action_value = data.get("action_value")
        simulator_manager.control_device(device_id, action, action_value)
    
    event_bus.subscribe("rule_triggered", on_rule_triggered)
    
    # Создать главное окно
    main_window = MainWindow()
    
    # Создать виджеты экранов
    dashboard = DashboardWidget(storage, event_bus, simulator_manager)
    rooms = RoomsWidget(storage, event_bus, simulator_manager)
    devices_widget = DevicesWidget(storage, event_bus, simulator_manager)
    automations = AutomationsWidget(storage, event_bus, automation_engine)
    logs = LogsWidget(storage, event_bus)
    settings = SettingsWidget(storage, event_bus)
    
    # Добавить виджеты в главное окно
    main_window.add_widget("dashboard", dashboard)
    main_window.add_widget("rooms", rooms)
    main_window.add_widget("devices", devices_widget)
    main_window.add_widget("automations", automations)
    main_window.add_widget("logs", logs)
    main_window.add_widget("settings", settings)
    
    # Подключить обновление дашборда
    dashboard.refresh_needed.connect(lambda: (
        dashboard.refresh(),
        rooms.refresh(),
        devices_widget.refresh()
    ))
    
    # Логировать запуск
    logger.log_system("Приложение запущено")
    
    # Показать окно
    main_window.show()
    
    # Запустить приложение
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
