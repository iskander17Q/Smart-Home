"""Экран логов"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ..core.models import LogEntry


class LogsWidget(QWidget):
    """Виджет логов"""
    
    def __init__(self, storage, event_bus):
        super().__init__()
        self.storage = storage
        self.event_bus = event_bus
        self._init_ui()
        self._connect_events()
    
    def _init_ui(self):
        """Инициализация UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Заголовок и поиск
        header = QHBoxLayout()
        title = QLabel("Логи событий")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        header.addWidget(title)
        header.addStretch()
        
        # Поиск
        search_label = QLabel("Поиск:")
        search_label.setStyleSheet("color: white;")
        header.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введите текст для поиска...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3a3a3a;
                padding: 5px;
                border-radius: 4px;
                min-width: 200px;
            }
        """)
        self.search_edit.textChanged.connect(self.refresh)
        header.addWidget(self.search_edit)
        
        # Кнопка экспорта
        btn_export = QPushButton("💾 Экспорт в TXT")
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        btn_export.clicked.connect(self._export_logs)
        header.addWidget(btn_export)
        
        layout.addLayout(header)
        
        # Таблица логов
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Время", "Тип", "Источник", "Сообщение"
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
        # Обновить логи при новом событии
        self.refresh()
    
    def refresh(self):
        """Обновить таблицу"""
        logs = self.storage.get_logs()
        search_text = self.search_edit.text().lower()
        
        # Фильтрация по поиску
        if search_text:
            logs = [
                log for log in logs
                if search_text in log.message.lower() or
                   search_text in log.source.lower() or
                   search_text in log.type.lower()
            ]
        
        # Обратный порядок (новые сверху)
        logs = list(reversed(logs))
        
        self.table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            # Время
            time_str = log.timestamp
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(log.timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
            self.table.setItem(row, 0, QTableWidgetItem(time_str))
            
            # Тип
            type_item = QTableWidgetItem(log.type)
            colors = {
                "sensor": Qt.cyan,
                "actuator": Qt.yellow,
                "rule": Qt.green,
                "system": Qt.white
            }
            type_item.setForeground(colors.get(log.type, Qt.white))
            self.table.setItem(row, 1, type_item)
            
            # Источник
            self.table.setItem(row, 2, QTableWidgetItem(log.source))
            
            # Сообщение
            self.table.setItem(row, 3, QTableWidgetItem(log.message))
    
    def _export_logs(self):
        """Экспортировать логи в файл"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт логов", "logs.txt", "Text Files (*.txt)"
        )
        if file_path:
            try:
                logs = self.storage.get_logs()
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("Логи событий SmartHome Dashboard\n")
                    f.write("=" * 50 + "\n\n")
                    for log in logs:
                        f.write(f"[{log.timestamp}] {log.type} | {log.source}\n")
                        f.write(f"  {log.message}\n\n")
                
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Успех", f"Логи экспортированы в {file_path}")
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать логи: {e}")
