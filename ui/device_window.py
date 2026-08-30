"""
Окно конкретного устройства.
Итерация 11: Интеграция устройств в GUI.

Отображает состояние устройства (регистры, флаги, параметры)
через метод get_state(). Автообновление каждые 200 мс.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QCheckBox,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from .display_widgets import create_display_widget

from .serial_terminal import create_terminal_widget

class DeviceWindow(QWidget):
    """Индивидуальное окно устройства с автообновлением состояния"""

    def __init__(self, device, device_name, lang="en", always_on_top=False, parent=None):
        super().__init__(parent)
        self.device = device
        self.device_name = device_name
        self.lang = lang

        flags = Qt.Window
        if always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.setWindowTitle(device_name)
        self.setMinimumSize(380, 300)
        self.resize(420, 400)

        self._fields = {}  # {key: QLineEdit}

        self._init_ui()

        # Автообновление каждые 200 мс
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.start(200)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок: имя + тип + базовый порт
        dev_type = type(self.device).__name__
        base_port = getattr(self.device, 'base_port', 0)
        info = QLabel(f"<b>{self.device_name}</b> — {dev_type} @ 0x{base_port:02X}")
        info.setFont(QFont("Segoe UI", 10))
        layout.addWidget(info)

        # Разделитель
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        # === Виджет дисплея (если устройство — дисплей) ===
        self.display_widget = create_display_widget(self.device)
        if self.display_widget is not None:
            layout.addWidget(self.display_widget)
            
        # === Виджет терминала (если устройство — USART/UART) ===
        self.terminal_widget = create_terminal_widget(self.device)
        if self.terminal_widget is not None:
            layout.addWidget(self.terminal_widget, 1)
        
        # Прокручиваемая область с регистрами
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.regs_layout = QFormLayout(scroll_widget)
        self.regs_layout.setContentsMargins(4, 4, 4, 4)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)

        # Панель управления
        ctrl = QHBoxLayout()
        self.chk_auto = QCheckBox("Авто")
        self.chk_auto.setChecked(True)
        self.chk_auto.setToolTip("Автообновление каждые 200 мс")
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self.refresh)
        ctrl.addWidget(self.chk_auto)
        ctrl.addWidget(self.btn_refresh)
        layout.addLayout(ctrl)

        # Первое обновление
        self.refresh()

    def _get_state(self):
        """Получить состояние устройства"""
        if hasattr(self.device, 'get_state'):
            return self.device.get_state()
        return {}

    def _format_value(self, val):
        """Форматировать значение для отображения"""
        if isinstance(val, bool):
            return "Да" if val else "Нет"
        if isinstance(val, int):
            if val < 0:
                return str(val)
            if val <= 0xFF:
                return f"0x{val:02X} ({val})"
            if val <= 0xFFFF:
                return f"0x{val:04X} ({val})"
            return f"0x{val:08X} ({val})"
        if isinstance(val, dict):
            return str(val)
        if isinstance(val, list):
            return ", ".join(str(v) for v in val)
        return str(val)

    def refresh(self):
        """Обновить значения регистров"""
        state = self._get_state()

        # Если ключей стало больше/меньше — перестраиваем форму
        new_keys = set(state.keys())
        old_keys = set(self._fields.keys())

        if new_keys != old_keys:
            # Перестраиваем форму
            while self.regs_layout.count():
                item = self.regs_layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()
            self._fields.clear()

            for key, value in state.items():
                if key in ('name', 'base_port'):
                    continue
                label = QLabel(f"{key}:")
                field = QLineEdit(self._format_value(value))
                field.setReadOnly(True)
                field.setFont(QFont("Consolas", 9))
                self.regs_layout.addRow(label, field)
                self._fields[key] = field
        else:
            # Просто обновляем значения
            for key, value in state.items():
                if key in self._fields:
                    self._fields[key].setText(self._format_value(value))

    def _auto_refresh(self):
        if self.chk_auto.isChecked() and self.isVisible():
            if self.display_widget is not None:
                self.display_widget.refresh()
            self.refresh()

    def set_always_on_top(self, enabled):
        """Установить/снять флаг поверх всех окон"""
        flags = self.windowFlags()
        if enabled:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
        self.show()  # Нужно после setWindowFlags

    def closeEvent(self, event):
        self.refresh_timer.stop()
        event.accept()
