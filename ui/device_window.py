"""
Окно конкретного устройства.
Итерация 11: Интеграция устройств в GUI.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class DeviceWindow(QWidget):
    """Индивидуальное окно устройства с регистрами"""

    def __init__(self, device, device_name, lang="en", always_on_top=False, parent=None):
        super().__init__(parent)
        self.device = device
        self.device_name = device_name
        self.lang = lang

        flags = Qt.Window
        if always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.setWindowTitle(f"{device_name}")
        self.setMinimumSize(350, 250)

        self._init_ui()

        # Автообновление каждые 200 мс
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.start(200)

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок с типом и базовым портом
        dev_type = type(self.device).__name__
        base_port = getattr(self.device, 'base_port', 0)
        info = QLabel(f"<b>{self.device_name}</b> — {dev_type} @ 0x{base_port:02X}")
        info.setFont(QFont("Segoe UI", 10))
        layout.addWidget(info)

        # Группа регистров
        self.regs_group = QGroupBox("Регистры")
        self.regs_layout = QFormLayout()
        self.regs_group.setLayout(self.regs_layout)
        layout.addWidget(self.regs_group)

        # Поля регистров
        self.reg_fields = {}
        self._build_fields()

        # Управление
        ctrl = QHBoxLayout()
        self.chk_auto = QCheckBox("Авто-обновление")
        self.chk_auto.setChecked(True)
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self.refresh)
        ctrl.addWidget(self.chk_auto)
        ctrl.addWidget(self.btn_refresh)
        layout.addLayout(ctrl)

    def _build_fields(self):
        """Построить поля из get_state()"""
        # Очищаем старые поля
        while self.regs_layout.count():
            item = self.regs_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.reg_fields.clear()

        state = self._get_state()
        for key, value in state.items():
            if key in ('name', 'base_port'):
                continue
            label = QLabel(f"{key}:")
            field = QLineEdit(str(value))
            field.setReadOnly(True)
            self.regs_layout.addRow(label, field)
            self.reg_fields[key] = field

    def _get_state(self):
        """Получить состояние устройства"""
        if hasattr(self.device, 'get_state'):
            return self.device.get_state()
        return {}

    def refresh(self):
        """Обновить значения регистров"""
        state = self._get_state()
        for key, field in self.reg_fields.items():
            val = state.get(key, '?')
            if isinstance(val, int):
                field.setText(f"0x{val:02X}" if val < 256 else f"0x{val:04X}")
            elif isinstance(val, dict):
                field.setText(str(val))
            else:
                field.setText(str(val))

    def _auto_refresh(self):
        if self.chk_auto.isChecked() and self.isVisible():
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
