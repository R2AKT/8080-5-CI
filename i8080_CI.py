import sys
import time
import serial
import serial.tools.list_ports
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QPushButton, QComboBox, QLabel, 
                               QLineEdit, QTextEdit, QGroupBox, QMessageBox,
                               QTabWidget, QTableView, QHeaderView, QFileDialog,
                               QProgressBar, QSpinBox, QCheckBox, QScrollArea, QInputDialog,
                               QToolTip, QStyle, QStatusBar)
from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal, QAbstractTableModel, QModelIndex, QEvent, QLocale, QSettings
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush


# ==================== ЛОКАЛИЗАЦИЯ И ТЕМЫ ====================
LANGS = {
    "en": {
        "app_title": "i8080-5 Master Controller",
        "port": "Port:", "baud": "Baud:", "connect": "Connect", "disconnect": "Disconnect",
        "refresh": "Refresh", "tab_control": "Control", "tab_data": "Data", "tab_hex": "Hex Editor",
        "tab_disasm": "Disassembler", "tab_test": "Memory Test", "tab_io_seq": "IO Sequencer",
        "log": "Log:", "bus_control": "Bus Control", "hold": "Hold Bus (HOLD)", "unhold": "Release Bus (UNHOLD)",
        "files": "Files (Intel HEX / BIN)", "save_dump": "Save Dump (.hex)", "load_fw": "Load Firmware (.hex/.bin)",
        "memory": "Memory (RAM/ROM) — read/write values", "io_port": "IO Port — read/write values",
        "addr_hex": "Address (HEX):", "port_hex": "Port (HEX):", "bits": "Bit width:",
        "value_hex": "Value (HEX):", "endian": "Byte order:", "read": "Read", "write": "Write",
        "range": "Range:", "read_block": "Read Block...", "start": "Start:", "len": "Len:",
        "disasm": "Disassemble", "auto_disasm": "Auto on read/load",
        "pattern": "Pattern:", "start_test": "Start Memory Test",
        "single_io": "Single IO Operations", "read_in": "Read (IN)", "write_out": "Write (OUT)",
        "io_seq": "IO Sequencer (command sequence)", "load_file": "Load File...", "run_seq": "Run Sequence",
        "connected": "Connected", "disconnected": "Disconnected", "test_conn": "Connection test (NOP)...",
        "err_port": "Select a COM port!", "err_connect": "Connection Error", "err_open": "Failed to open port",
        "err_addr": "Invalid address!", "err_addr_val": "Invalid address or value!",
        "err_port_addr": "Invalid port address!", "err_empty": "Empty", "err_no_data": "No data to save.",
        "save_as": "Save Dump As", "load_fw_title": "Load Firmware", "base_addr": "Base Address",
        "base_addr_hint": "Enter base address for BIN (HEX):", "err_hex": "Invalid HEX address!",
        "flash_q": "Flash", "flash_msg": "Write this data to device memory?", "loaded": "Loaded",
        "bytes_from_file": "bytes from file.", "thread_done": "Thread finished.",
        "err_not_open": "Port not open!", "err_send": "Send error:", "err_read_port": "Port read error:",
        "err_write_port": "Port write error:", "err_seq_fmt": "Invalid line format:",
        "io_seq_start": "Starting IO sequencer...", "io_seq_done": "IO sequencer finished.",
        "delay": "DELAY", "ok": "OK", "error": "ERROR", "write_io": "IO Write", "read_io": "IO Read",
        "conn_est": "Connection established (NOP).", "err_ack": "AckError from device.",
        "theme": "Theme:", "language": "Language:", "light": "Light", "dark": "Dark",
        "mem_test": "Memory test", "errors": "errors", "write_block": "Writing block to",
        "read_block_msg": "Reading block:", "read_ok": "Successfully read", "bytes": "bytes.",
        "read_err": "Block read error!", "write_done": "Write complete", "write_err": "Write error at address",
        "io_read_block": "Reading IO block:", "io_read_ok": "Successfully read", "io_bytes": "IO bytes.",
        "io_read_err": "IO block read error!", "io_write_block": "Writing IO block to",
        "io_write_done": "IO write complete", "io_write_err": "IO write error at address",
        "test_mem": "Memory test", "pattern": "pattern", "test_done": "Test complete.",
        "write_fail": "Write failure at", "read_fail": "Read failure at",
        "expected": "Expected", "got": "Got", "export": "Export",
    },
    "ru": {
        "app_title": "i8080-5 Мастер Контроллер",
        "port": "Порт:", "baud": "Скорость:", "connect": "Подключиться", "disconnect": "Отключиться",
        "refresh": "Обновить", "tab_control": "Управление", "tab_data": "Данные", "tab_hex": "Hex Редактор",
        "tab_disasm": "Дизассемблер", "tab_test": "Тест Памяти", "tab_io_seq": "IO Секвенсор",
        "log": "Журнал:", "bus_control": "Управление шиной", "hold": "Захватить шину (HOLD)", "unhold": "Освободить шину (UNHOLD)",
        "files": "Файлы (Intel HEX / BIN)", "save_dump": "Сохранить дамп (.hex)", "load_fw": "Загрузить прошивку (.hex/.bin)",
        "memory": "Память (RAM/ROM) — чтение/запись значений", "io_port": "Порт ввода-вывода (IO) — чтение/запись значений",
        "addr_hex": "Адрес (HEX):", "port_hex": "Порт (HEX):", "bits": "Разрядность (бит):",
        "value_hex": "Значение (HEX):", "endian": "Порядок байтов:", "read": "Прочитать", "write": "Записать",
        "range": "Диапазон:", "read_block": "Читать блок...", "start": "Start:", "len": "Len:",
        "disasm": "Дизассемблировать", "auto_disasm": "Авто при чтении/загрузке",
        "pattern": "Паттерн:", "start_test": "Запустить тест памяти",
        "single_io": "Одиночные операции IO", "read_in": "Читать (IN)", "write_out": "Записать (OUT)",
        "io_seq": "IO Секвенсор (последовательность команд)", "load_file": "Загрузить файл...", "run_seq": "Выполнить последовательность",
        "connected": "Подключено", "disconnected": "Отключено", "test_conn": "Тест соединения (NOP)...",
        "err_port": "Выберите COM-порт!", "err_connect": "Ошибка подключения", "err_open": "Не удалось открыть порт",
        "err_addr": "Неверный адрес!", "err_addr_val": "Неверный адрес или значение!",
        "err_port_addr": "Неверный адрес порта!", "err_empty": "Пусто", "err_no_data": "Нет данных для сохранения.",
        "save_as": "Сохранить дамп", "load_fw_title": "Загрузить прошивку", "base_addr": "Базовый адрес",
        "base_addr_hint": "Укажите базовый адрес для BIN (HEX):", "err_hex": "Неверный HEX адрес!",
        "flash_q": "Прошивка", "flash_msg": "Записать эти данные в память устройства?", "loaded": "Загружено",
        "bytes_from_file": "байт из файла.", "thread_done": "Поток завершен.",
        "err_not_open": "Порт не открыт!", "err_send": "Ошибка отправки:", "err_read_port": "Ошибка чтения порта:",
        "err_write_port": "Ошибка записи в порт:", "err_seq_fmt": "Неверный формат строки:",
        "io_seq_start": "Запуск IO секвенсора...", "io_seq_done": "IO секвенсор завершен.",
        "delay": "ЗАДЕРЖКА", "ok": "OK", "error": "ОШИБКА", "write_io": "Запись IO", "read_io": "Чтение IO",
        "conn_est": "Соединение установлено (NOP).", "err_ack": "AckError от устройства.",
        "theme": "Тема:", "language": "Язык:", "light": "Светлая", "dark": "Тёмная",
        "mem_test": "Тест памяти", "errors": "ошибок", "write_block": "Запись блока в",
        "read_block_msg": "Чтение блока:", "read_ok": "Успешно прочитано", "bytes": "байт.",
        "read_err": "Ошибка чтения блока!", "write_done": "Запись завершена", "write_err": "Ошибка записи на адресе",
        "io_read_block": "Чтение IO блока:", "io_read_ok": "Успешно прочитано", "io_bytes": "IO байт.",
        "io_read_err": "Ошибка чтения IO блока!", "io_write_block": "Запись IO блока в",
        "io_write_done": "Запись IO завершена", "io_write_err": "Ошибка записи IO на адресе",
        "test_mem": "Тест памяти", "pattern": "паттерном", "test_done": "Тест завершен.",
        "write_fail": "Сбой записи на", "read_fail": "Сбой чтения на",
        "expected": "Ожидалось", "got": "Получено", "export": "Экспорт",
    }
}

THEMES = {
    "Light": "",
    "Dark": """
        QMainWindow, QWidget { background-color: #2b2b2b; color: #d4d4d4; }
        QTabWidget::pane { border: 1px solid #555; }
        QTabBar::tab { background: #3c3c3c; padding: 5px 10px; }
        QTabBar::tab:selected { background: #0078d4; color: white; }
        QPushButton { background-color: #3c3c3c; border: 1px solid #555; padding: 5px; border-radius: 3px; }
        QPushButton:hover { background-color: #505050; }
        QLineEdit, QComboBox, QSpinBox { background-color: #3c3c3c; border: 1px solid #555; padding: 3px; border-radius: 3px; }
        QTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #555; }
        QTableView { background-color: #1e1e1e; color: #d4d4d4; gridline-color: #555; border: 1px solid #555; }
        QGroupBox { border: 1px solid #555; border-radius: 5px; margin-top: 10px; padding-top: 10px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QProgressBar { border: 1px solid #555; border-radius: 3px; text-align: center; }
        QProgressBar::chunk { background-color: #0078d4; }
    """
}

def get_system_language():
    """Определяет системный язык. Возвращает 'ru', 'en' или 'en' по умолчанию."""
    try:
        lang = QLocale.system().name()  # Например: 'ru_RU', 'en_US', 'de_DE'
        if lang.startswith('ru'):
            return "ru"
        elif lang.startswith('en'):
            return "en"
        # Можно добавить другие языки здесь
    except Exception:
        pass
    return "en"  # По умолчанию английский

# --- Константы SLIP и Команд ---
_FEND = 0xC0; _FESC = 0xDB; _TFEND = 0xDC; _TFESC = 0xDD
CMD_NOP = 0x00
CMD_HOLD = 0x01; CMD_UNHOLD = 0x02
CMD_MEM_READ_BYTE = 0x10; CMD_MEM_READ_BLOCK = 0x11
CMD_MEM_WRITE_BYTE = 0x12; CMD_MEM_WRITE_BLOCK = 0x13
CMD_IO_READ_BYTE = 0x20; CMD_IO_READ_BLOCK = 0x21
CMD_IO_WRITE_BYTE = 0x22; CMD_IO_WRITE_BLOCK = 0x23
ACK_NOP = 0x00
ACK_MEM_READ_BYTE = 0x10; ACK_MEM_READ_BLOCK = 0x11
ACK_MEM_WRITE_BYTE = 0x12; ACK_MEM_WRITE_BLOCK = 0x13
ACK_IO_READ_BYTE = 0x20; ACK_IO_READ_BLOCK = 0x21
ACK_IO_WRITE_BYTE = 0x22; ACK_IO_WRITE_BLOCK = 0x23
ACK_ERROR = 0xFF

# ==================== ПРОТОКОЛ SLIP ====================
class SlipProtocol:
    @staticmethod
    def encode(data: bytes) -> bytes:
        encoded = bytearray([_FEND])
        for b in data:
            if b == _FEND: encoded.extend([_FESC, _TFEND])
            elif b == _FESC: encoded.extend([_FESC, _TFESC])
            else: encoded.append(b)
        encoded.append(_FEND)
        return bytes(encoded)

    @staticmethod
    def decode(data: bytes) -> bytes:
        decoded = bytearray()
        i = 0
        while i < len(data):
            if data[i] == _FESC:
                if i + 1 < len(data):
                    if data[i+1] == _TFEND: decoded.append(_FEND)
                    elif data[i+1] == _TFESC: decoded.append(_FESC)
                    i += 2
                else: break
            else:
                decoded.append(data[i])
                i += 1
        return bytes(decoded)

# ==================== INTEL HEX PARSER ====================
class IntelHex:
    @staticmethod
    def parse(text):
        mem = {}
        base_addr = 0
        for line in text.strip().split('\n'):
            line = line.strip()
            if not line.startswith(':') or len(line) < 11: continue
            try:
                length = int(line[1:3], 16)
                addr = int(line[3:7], 16)
                rec_type = int(line[7:9], 16)
                data = bytes.fromhex(line[9:-2])
                if rec_type == 0x00:
                    for i in range(length):
                        mem[base_addr + addr + i] = data[i]
                elif rec_type == 0x02:
                    base_addr = int.from_bytes(data, 'big') << 4
                elif rec_type == 0x04:
                    base_addr = int.from_bytes(data, 'big') << 16
                elif rec_type == 0x01: break
            except ValueError: continue
        return mem

    @staticmethod
    def generate(mem_dict):
        lines = []
        sorted_addrs = sorted(mem_dict.keys())
        i = 0
        while i < len(sorted_addrs):
            addr = sorted_addrs[i]
            chunk_len = min(16, len(sorted_addrs) - i)
            actual_len = 0
            for j in range(chunk_len):
                if i + j < len(sorted_addrs) and sorted_addrs[i+j] == addr + j:
                    actual_len += 1
                else: break
            
            data = [mem_dict[addr + k] for k in range(actual_len)]
            hex_data = "".join(f"{b:02X}" for b in data)
            checksum = (actual_len + (addr >> 8) + (addr & 0xFF) + 0x00 + sum(data)) & 0xFF
            checksum = (~checksum + 1) & 0xFF
            lines.append(f":{actual_len:02X}{addr:04X}00{hex_data}{checksum:02X}")
            i += actual_len
        lines.append(":00000001FF")
        return "\n".join(lines)

# ==================== I8080 DISASSEMBLER ====================
class I8080Disassembler:
    REGS = ['B', 'C', 'D', 'E', 'H', 'L', 'M', 'A']
    ALUS = ['ADD', 'ADC', 'SUB', 'SBB', 'ANA', 'XRA', 'ORA', 'CMP']
    RP = ['B', 'D', 'H', 'SP']
    RP_PUSH = ['B', 'D', 'H', 'PSW']
    CC = ['NZ', 'Z', 'NC', 'C', 'PO', 'PE', 'P', 'M']

    def __init__(self):
        self.table = self._generate_table()

    def _generate_table(self):
        t = {}
        for op in [0x08, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38, 0xDD, 0xED, 0xFD]:
            t[op] = (1, "NOP*")
        t[0xD9] = (1, "RET*")
        t[0xCB] = (1, "CALL*")
        
        t[0x00] = (1, "NOP"); t[0x76] = (1, "HLT")
        for i in range(4): t[0x01 + i*16] = (3, f"LXI {self.RP[i]},{{1:02X}}{{0:02X}}h")
        for i in range(4): t[0x03 + i*16] = (1, f"INX {self.RP[i]}")
        for i in range(4): t[0x0B + i*16] = (1, f"DCX {self.RP[i]}")
        for i in range(8): t[0x04 + i*8] = (1, f"INR {self.REGS[i]}")
        for i in range(8): t[0x05 + i*8] = (1, f"DCR {self.REGS[i]}")
        for i in range(8): t[0x06 + i*8] = (2, f"MVI {self.REGS[i]},{{0:02X}}h")
        
        t[0x02] = (1, "STAX B"); t[0x12] = (1, "STAX D")
        t[0x0A] = (1, "LDAX B"); t[0x1A] = (1, "LDAX D")
        t[0x22] = (3, "SHLD {1:02X}{0:02X}h"); t[0x2A] = (3, "LHLD {1:02X}{0:02X}h")
        t[0x32] = (3, "STA {1:02X}{0:02X}h"); t[0x3A] = (3, "LDA {1:02X}{0:02X}h")
        t[0x07] = (1, "RLC"); t[0x0F] = (1, "RRC"); t[0x17] = (1, "RAL"); t[0x1F] = (1, "RAR")
        t[0x27] = (1, "DAA"); t[0x2F] = (1, "CMA"); t[0x37] = (1, "STC"); t[0x3F] = (1, "CMC")
        t[0xE3] = (1, "XTHL"); t[0xE9] = (1, "PCHL"); t[0xF9] = (1, "SPHL")
        t[0xEB] = (1, "XCHG"); t[0xF3] = (1, "DI"); t[0xFB] = (1, "EI")
        t[0xDB] = (2, "IN {0:02X}h"); t[0xD3] = (2, "OUT {0:02X}h")
        
        for i in range(0x40, 0x80):
            if i not in t:
                dst = (i >> 3) & 7; src = i & 7
                t[i] = (1, f"MOV {self.REGS[dst]},{self.REGS[src]}")
                
        for i in range(0x80, 0xC0):
            alu = (i >> 3) & 7; src = i & 7
            t[i] = (1, f"{self.ALUS[alu]} {self.REGS[src]}")
            
        for i in range(8):
            t[0xC0 + i*8] = (1, f"R{self.CC[i]}")
            t[0xC2 + i*8] = (3, f"J{self.CC[i]} {{1:02X}}{{0:02X}}h")
            t[0xC4 + i*8] = (3, f"C{self.CC[i]} {{1:02X}}{{0:02X}}h")
            
        t[0xC3] = (3, "JMP {1:02X}{0:02X}h")
        t[0xCD] = (3, "CALL {1:02X}{0:02X}h")
        t[0xC9] = (1, "RET")
        
        for i in range(4):
            t[0xC1 + i*16] = (1, f"POP {self.RP_PUSH[i]}")
            t[0xC5 + i*16] = (1, f"PUSH {self.RP_PUSH[i]}")
            
        for i in range(8):
            t[0xC6 + i*8] = (2, f"{self.ALUS[i]} {{0:02X}}h")
            
        t[0xC7] = (1, "RST 0"); t[0xCF] = (1, "RST 1"); t[0xD7] = (1, "RST 2")
        t[0xDF] = (1, "RST 3"); t[0xE7] = (1, "RST 4"); t[0xEF] = (1, "RST 5")
        t[0xF7] = (1, "RST 6"); t[0xFF] = (1, "RST 7")
        return t

    def get_target(self, op, args):
        if op in [0xC3, 0xCD] or \
           op in [0xC2, 0xCA, 0xD2, 0xDA, 0xE2, 0xEA, 0xF2, 0xFA] or \
           op in [0xC4, 0xCC, 0xD4, 0xDC, 0xE4, 0xEC, 0xF4, 0xFC]:
            if len(args) >= 2:
                return (args[1] << 8) | args[0]
        elif op in [0xC7, 0xCF, 0xD7, 0xDF, 0xE7, 0xEF, 0xF7, 0xFF]:
            return ((op - 0xC7) // 8) * 8
        return None

    def get_mnemonic(self, byte_val):
        """Возвращает мнемонику для одного байта (для подсказок)"""
        if byte_val in self.table:
            size, fmt = self.table[byte_val]
            # Извлекаем мнемонику из формата (первое слово)
            parts = fmt.split()
            if parts:
                mnemonic = parts[0]
                # Для команд с аргументами показываем только мнемонику
                if "{" in fmt:
                    return f"{mnemonic} ..."
                return mnemonic
        return f"DB {byte_val:02X}h"

    def disassemble(self, mem_dict, start_addr, length):
        lines = []
        i = 0
        while i < length:
            addr = start_addr + i
            if addr not in mem_dict:
                i += 1; continue
            op = mem_dict[addr]
            if op not in self.table:
                lines.append((addr, 1, f"DB {op:02X}h", "*", None))
                i += 1; continue
            
            size, fmt = self.table[op]
            args = [mem_dict.get(addr+1+k, 0) for k in range(size-1)]
            try:
                asm = fmt.format(*args) if args else fmt
            except:
                asm = fmt
                
            undoc = "*" if "NOP*" in asm or "RET*" in asm or "CALL*" in asm else ""
            target = self.get_target(op, args)
            
            lines.append((addr, size, asm, undoc, target))
            i += size
        return lines

# ==================== КАСТОМНЫЙ ВИДЖЕТ ДИЗАССЕМБЛЕРА СО СТРЕЛКАМИ ====================
class DisasmView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lines = []
        self.line_height = 22
        self.addr_to_index = {}
        self.setFont(QFont("Consolas", 10))
        self.setMinimumWidth(700)
        self.arrow_margin = 30
        
    def set_lines(self, lines):
        self.lines = lines
        self.addr_to_index = {line[0]: i for i, line in enumerate(lines)}
        self.setFixedHeight(len(lines) * self.line_height + 10)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self.font())
        
        # Используем стандартный фон виджета вместо чёрного
        painter.fillRect(self.rect(), self.palette().window())
        
        for i, (addr, size, asm, undoc, target) in enumerate(self.lines):
            y = i * self.line_height + self.line_height // 2 + 5
            
            painter.setPen(self.palette().windowText().color())
            painter.drawText(self.arrow_margin + 10, y, f"{addr:04X}")
            
            asm_text = f"{asm} {undoc}".strip()
            painter.drawText(self.arrow_margin + 70, y, asm_text)
            
            if target is not None:
                painter.setPen(QColor("#569cd6"))
                painter.drawText(self.arrow_margin + 250, y, f"; -> {target:04X}h")
                
        self.draw_arrows(painter)
        
    def draw_arrows(self, painter):
        arrow_x_start = 5
        arrow_colors = [QColor("#ff6b6b"), QColor("#4ecdc4"), QColor("#ffe66d"), 
                        QColor("#a8e6cf"), QColor("#ffd93d"), QColor("#6bcf7f")]
        color_idx = 0
        
        for i, (addr, size, asm, undoc, target) in enumerate(self.lines):
            if target is not None and target in self.addr_to_index:
                target_idx = self.addr_to_index[target]
                y1 = i * self.line_height + self.line_height // 2 + 5
                y2 = target_idx * self.line_height + self.line_height // 2 + 5
                
                color = arrow_colors[color_idx % len(arrow_colors)]
                color_idx += 1
                
                pen = QPen(color, 2)
                painter.setPen(pen)
                
                x_offset = arrow_x_start + (color_idx % 5) * 4
                
                painter.drawLine(x_offset, y1, x_offset, y2)
                painter.drawLine(x_offset, y2, self.arrow_margin + 5, y2)
                
                if y2 > y1:
                    painter.drawLine(self.arrow_margin + 5, y2, self.arrow_margin, y2 - 4)
                    painter.drawLine(self.arrow_margin + 5, y2, self.arrow_margin, y2 + 4)
                else:
                    painter.drawLine(self.arrow_margin + 5, y2, self.arrow_margin, y2 - 4)
                    painter.drawLine(self.arrow_margin + 5, y2, self.arrow_margin, y2 + 4)
                    
                painter.setBrush(color)
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(x_offset - 2, y1 - 2, 4, 4)
                painter.setPen(pen)

# ==================== МОДЕЛЬ ДАННЫХ HEX-РЕДАКТОРА ====================
class HexModel(QAbstractTableModel):
    dataEdited = Signal()  # Новый сигнал для уведомления об изменении
    
    def __init__(self, mem_dict=None):
        super().__init__()
        self.mem = mem_dict if mem_dict is not None else {}
        self.min_addr = 0
        self.max_addr = 0
        self.update_range()

    def update_data(self, new_mem):
        self.mem.update(new_mem)
        self.update_range()
        self.layoutChanged.emit()

    def update_range(self):
        if self.mem:
            self.min_addr = min(self.mem.keys())
            self.max_addr = max(self.mem.keys())
            self.min_addr &= ~0x0F
        else:
            self.min_addr = 0; self.max_addr = 0

    def rowCount(self, parent=QModelIndex()):
        if not self.mem: return 0
        return ((self.max_addr - self.min_addr) >> 4) + 1

    def columnCount(self, parent=QModelIndex()):
        return 18

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        row = index.row(); col = index.column()
        addr = self.min_addr + (row * 16)
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if col == 0: return f"{addr:04X}"
            elif 1 <= col <= 16:
                byte_addr = addr + col - 1
                if byte_addr in self.mem: return f"{self.mem[byte_addr]:02X}"
            elif col == 17:
                ascii_str = ""
                for c in range(16):
                    b = self.mem.get(addr + c, -1)
                    if 32 <= b <= 126: ascii_str += chr(b)
                    else: ascii_str += "."
                return ascii_str
        elif role == Qt.FontRole:
            return QFont("Consolas", 10)
        return None

    def flags(self, index):
        flags = super().flags(index)
        if 1 <= index.column() <= 16:
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and 1 <= index.column() <= 16:
            try:
                val = int(value, 16)
                if 0 <= val <= 255:
                    addr = self.min_addr + (index.row() * 16) + index.column() - 1
                    self.mem[addr] = val
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                    self.dataEdited.emit()  # Излучаем новый сигнал
                    return True
            except ValueError: pass
        return False

# ==================== КАСТОМНАЯ ТАБЛИЦА HEX-РЕДАКТОРА С ПОДСКАЗКАМИ ====================
class HexTableView(QTableView):
    statusUpdate = Signal(str, str, str)  # addr, data, mnemonic
    
    def __init__(self, disassembler, mem_data, parent=None):
        super().__init__(parent)
        self.disassembler = disassembler
        self.mem_data = mem_data
        self.setMouseTracking(True)
        
    def event(self, event):
        if event.type() == QEvent.ToolTip:
            viewport_pos = self.viewport().mapFrom(self, event.pos())
            index = self.indexAt(viewport_pos)
            if index.isValid() and 1 <= index.column() <= 16:
                row = index.row()
                col = index.column()
                model = self.model()
                if model and hasattr(model, 'min_addr'):
                    addr = model.min_addr + (row * 16) + col - 1
                    if addr in self.mem_data:
                        byte_val = self.mem_data[addr]
                        mnemonic = self.disassembler.get_mnemonic(byte_val)
                        QToolTip.showText(event.globalPos(), f"0x{byte_val:02X}: {mnemonic}", self)
                        return True
                        
        elif event.type() == QEvent.HoverMove:
            viewport_pos = self.viewport().mapFrom(self, event.pos())
            index = self.indexAt(viewport_pos)
            if index.isValid() and 1 <= index.column() <= 16:
                row = index.row()
                col = index.column()
                model = self.model()
                if model and hasattr(model, 'min_addr'):
                    addr = model.min_addr + (row * 16) + col - 1
                    if addr in self.mem_data:
                        byte_val = self.mem_data[addr]
                        mnemonic = self.disassembler.get_mnemonic(byte_val)
                        self.statusUpdate.emit(f"0x{addr:04X}", f"0x{byte_val:02X}", mnemonic)
                        
        return super().event(event)

# ==================== РАБОЧИЙ ПОТОК ====================
class BusWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal(dict)
    
    def __init__(self, serial_port, task, params, lang="en"):
        super().__init__()
        self.ser = serial_port
        self.task = task
        self.params = params
        self.is_running = True
        self.lang = lang

    def stop(self):
        self.is_running = False

    def tr(self, key):
        return LANGS.get(self.lang, LANGS["en"]).get(key, key)

    def run(self):
        if self.task == "read_block":
            self.do_read_block()
        elif self.task == "test_mem":
            self.do_test_mem()
        elif self.task == "write_block":
            self.do_write_block()
        elif self.task == "run_io_sequence":
            self.do_run_io_sequence()
        elif self.task == "read_io_block":
            self.do_read_io_block()
        elif self.task == "write_io_block":
            self.do_write_io_block()

    def send_and_recv(self, payload, timeout=2.0):
        try:
            self.ser.write(SlipProtocol.encode(payload))
            self.ser.flush()
        except serial.SerialException as e:
            self.log.emit(f"{self.tr('err_write_port')} {e}")
            return None
            
        buffer = bytearray()
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_running: return None
            try:
                if self.ser.in_waiting:
                    buffer.extend(self.ser.read(self.ser.in_waiting))
                    if _FEND in buffer:
                        end_idx = buffer.index(_FEND)
                        if end_idx > 0:
                            raw = buffer[:end_idx]
                            self.ser.reset_input_buffer()
                            return SlipProtocol.decode(raw)
            except serial.SerialException as e:
                self.log.emit(f"{self.tr('err_read_port')} {e}")
                return None
            time.sleep(0.01)
        return None

    def do_read_block(self):
        addr, size = self.params
        self.log.emit(f"{self.tr('read_block_msg')} 0x{addr:04X} ({size})")
        cmd = bytes([CMD_MEM_READ_BLOCK, size & 0xFF, (addr >> 8) & 0xFF, addr & 0xFF])
        resp = self.send_and_recv(cmd)
        mem = {}
        if resp and resp[0] == ACK_MEM_READ_BLOCK:
            for i in range(resp[1]):
                if 3 + i < len(resp):
                    mem[addr + i] = resp[3 + i]
            self.log.emit(f"{self.tr('read_ok')} {len(mem)} {self.tr('bytes')}")
        else:
            self.log.emit(self.tr('read_err'))
        self.finished.emit(mem)

    def do_write_block(self):
        mem_dict, start_addr = self.params
        self.log.emit(f"{self.tr('write_block')} 0x{start_addr:04X}...")
        addrs = sorted(mem_dict.keys())
        written = 0
        for i in range(0, len(addrs), 128):
            if not self.is_running: break
            chunk_addrs = addrs[i:i+128]
            chunk_data = [mem_dict[a] for a in chunk_addrs]
            c_addr = chunk_addrs[0]
            c_size = len(chunk_data)
            
            cmd = bytearray([CMD_MEM_WRITE_BLOCK, c_size, (c_addr >> 8) & 0xFF, c_addr & 0xFF])
            cmd.extend(chunk_data)
            resp = self.send_and_recv(bytes(cmd))
            if not resp or resp[0] != ACK_MEM_WRITE_BLOCK:
                self.log.emit(f"{self.tr('write_err')} 0x{c_addr:04X}")
                break
            written += c_size
            self.progress.emit(int((i + c_size) * 100 / len(addrs)))
        self.log.emit(f"{self.tr('write_done')} ({written} {self.tr('bytes')}).")
        self.finished.emit({})

    def do_read_io_block(self):
        addr, size = self.params
        self.log.emit(f"{self.tr('io_read_block')} 0x{addr:04X} ({size})")
        cmd = bytes([CMD_IO_READ_BLOCK, size & 0xFF, (addr >> 8) & 0xFF, addr & 0xFF])
        resp = self.send_and_recv(cmd)
        mem = {}
        if resp and resp[0] == ACK_IO_READ_BLOCK:
            for i in range(resp[1]):
                if 3 + i < len(resp):
                    mem[addr + i] = resp[3 + i]
            self.log.emit(f"{self.tr('io_read_ok')} {len(mem)} {self.tr('io_bytes')}")
        else:
            self.log.emit(self.tr('io_read_err'))
        self.finished.emit(mem)

    def do_write_io_block(self):
        mem_dict, start_addr = self.params
        self.log.emit(f"{self.tr('io_write_block')} 0x{start_addr:04X}...")
        addrs = sorted(mem_dict.keys())
        written = 0
        for i in range(0, len(addrs), 128):
            if not self.is_running: break
            chunk_addrs = addrs[i:i+128]
            chunk_data = [mem_dict[a] for a in chunk_addrs]
            c_addr = chunk_addrs[0]
            c_size = len(chunk_data)
            
            cmd = bytearray([CMD_IO_WRITE_BLOCK, c_size, (c_addr >> 8) & 0xFF, c_addr & 0xFF])
            cmd.extend(chunk_data)
            resp = self.send_and_recv(bytes(cmd))
            if not resp or resp[0] != ACK_IO_WRITE_BLOCK:
                self.log.emit(f"{self.tr('io_write_err')} 0x{c_addr:04X}")
                break
            written += c_size
            self.progress.emit(int((i + c_size) * 100 / len(addrs)))
        self.log.emit(f"{self.tr('io_write_done')} ({written} {self.tr('bytes')}).")
        self.finished.emit({})

    def do_test_mem(self):
        start, end, pattern_name = self.params
        size = end - start + 1
        self.log.emit(f"{self.tr('test_mem')} 0x{start:04X}-0x{end:04X} {self.tr('pattern')} '{pattern_name}'")
        
        errors = 0
        chunk_size = 128
        
        def get_pattern(offset, length):
            if pattern_name == "Zero": return [0x00] * length
            elif pattern_name == "One": return [0xFF] * length
            elif pattern_name == "Checker": return [0x55 if (offset + i) % 2 == 0 else 0xAA for i in range(length)]
            elif pattern_name == "Addr": return [(start + offset + i) & 0xFF for i in range(length)]
            return [0x00] * length

        for i in range(0, size, chunk_size):
            if not self.is_running: break
            c_size = min(chunk_size, size - i)
            c_addr = start + i
            data = get_pattern(i, c_size)
            
            cmd = bytearray([CMD_MEM_WRITE_BLOCK, c_size, (c_addr >> 8) & 0xFF, c_addr & 0xFF])
            cmd.extend(data)
            resp = self.send_and_recv(bytes(cmd))
            if not resp or resp[0] != ACK_MEM_WRITE_BLOCK:
                self.log.emit(f"{self.tr('write_fail')} 0x{c_addr:04X}")
                break
                
            cmd_r = bytes([CMD_MEM_READ_BLOCK, c_size, (c_addr >> 8) & 0xFF, c_addr & 0xFF])
            resp_r = self.send_and_recv(cmd_r)
            if resp_r and resp_r[0] == ACK_MEM_READ_BLOCK:
                for j in range(c_size):
                    if 3 + j < len(resp_r) and resp_r[3+j] != data[j]:
                        errors += 1
                        self.log.emit(f"{self.tr('error')}: Addr 0x{c_addr+j:04X} {self.tr('expected')} 0x{data[j]:02X}, {self.tr('got')} 0x{resp_r[3+j]:02X}")
            else:
                self.log.emit(f"{self.tr('read_fail')} 0x{c_addr:04X}")
                break
                
            self.progress.emit(int((i + c_size) * 100 / size))
            
        self.log.emit(f"{self.tr('test_done')} {self.tr('errors')}: {errors}")
        self.finished.emit({"errors": errors})

    def do_run_io_sequence(self):
        sequence = self.params['sequence']
        self.log.emit(self.tr('io_seq_start'))
        for line in sequence:
            if not self.is_running: break
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('#'):
                continue
                
            parts = line.split()
            cmd = parts[0].upper()
            
            try:
                if cmd == 'W' and len(parts) == 3:
                    port = int(parts[1], 16)
                    data = int(parts[2], 16)
                    payload = bytes([CMD_IO_WRITE_BYTE, (port >> 8) & 0xFF, port & 0xFF, data])
                    resp = self.send_and_recv(payload, timeout=1.0)
                    if not resp or resp[0] != ACK_IO_WRITE_BYTE:
                        self.log.emit(f"  [{self.tr('error')}] {self.tr('write_io')} 0x{port:02X}")
                    else:
                        self.log.emit(f"  [{self.tr('ok')}] W IO 0x{port:02X} = 0x{data:02X}")
                        
                elif cmd == 'R' and len(parts) == 2:
                    port = int(parts[1], 16)
                    payload = bytes([CMD_IO_READ_BYTE, (port >> 8) & 0xFF, port & 0xFF])
                    resp = self.send_and_recv(payload, timeout=1.0)
                    if resp and resp[0] == ACK_IO_READ_BYTE:
                        val = resp[3]
                        self.log.emit(f"  [{self.tr('ok')}] R IO 0x{port:02X} = 0x{val:02X}")
                    else:
                        self.log.emit(f"  [{self.tr('error')}] {self.tr('read_io')} 0x{port:02X}")
                        
                elif cmd == 'D' and len(parts) == 2:
                    ms = int(parts[1])
                    time.sleep(ms / 1000.0)
                    self.log.emit(f"  [{self.tr('delay')}] {ms} ms")
            except ValueError:
                self.log.emit(f"  [{self.tr('error')}] {self.tr('err_seq_fmt')} {line}")
                
        self.log.emit(self.tr('io_seq_done'))
        self.finished.emit({})

# ==================== ГЛАВНОЕ ОКНО ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # === Загрузка настроек ===
        self.settings = QSettings("8080-5 CI", "8080-5 CI application")
        saved_lang = self.settings.value("language", None)
        saved_theme = self.settings.value("theme", None)
        
        # === Статусная строка ===
        self.statusBar = self.statusBar()  # Создаёт статусную строку
        self.status_label_addr = QLabel("Адрес: -")
        self.status_label_data = QLabel("Данные: -")
        self.status_label_mnem = QLabel("Мнемоника: -")
        self.status_label_size = QLabel("Размер: 0 байт")
        self.status_label_conn = QLabel("Отключено")
        
        self.statusBar.addWidget(self.status_label_conn)
        self.statusBar.addPermanentWidget(self.status_label_size)
        self.statusBar.addPermanentWidget(self.status_label_addr)
        self.statusBar.addPermanentWidget(self.status_label_data)
        self.statusBar.addPermanentWidget(self.status_label_mnem)
        
        # Определение языка: сохранённый -> системный -> английский
        if saved_lang in LANGS:
            self.current_lang = saved_lang
        else:
            self.current_lang = get_system_language()
            
        # Определение темы: сохранённая -> светлая
        if saved_theme in THEMES:
            self.current_theme = saved_theme
        else:
            self.current_theme = "Light"
        
        # === Инициализация данных ===
        self.serial_port = None
        self.rx_buffer = bytearray()
        self.mem_data = {}
        self.disassembler = I8080Disassembler()
        self.hex_model = HexModel(self.mem_data)
        
        self.worker = None
        self.worker_thread = None
        self.pending_read = None
        
        self.init_ui()
        self.retranslate_ui()
        
        # Применяем тему при запуске
        QApplication.instance().setStyleSheet(THEMES[self.current_theme])
        
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.read_serial)
        
        # === Инициализация данных ===
        self.serial_port = None
        self.rx_buffer = bytearray()
        self.mem_data = {}
        self.disassembler = I8080Disassembler()
        self.hex_model = HexModel(self.mem_data)
        
        self.worker = None
        self.worker_thread = None
        self.pending_read = None
        
        self.init_ui()
        self.retranslate_ui()
        
        # Применяем тему при запуске
        QApplication.instance().setStyleSheet(THEMES[self.current_theme])
        
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.read_serial)
        
        self.serial_port = None
        self.rx_buffer = bytearray()
        self.mem_data = {}
        self.disassembler = I8080Disassembler()
        self.hex_model = HexModel(self.mem_data)
        
        self.worker = None
        self.worker_thread = None
        self.pending_read = None
        self.disasm_timer = QTimer()
        self.disasm_timer.setSingleShot(True)
        self.disasm_timer.timeout.connect(self.auto_disasm)
        
        self.init_ui()
        self.retranslate_ui()
        
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.read_serial)
        
    def tr(self, key):
        return LANGS.get(self.current_lang, LANGS["en"]).get(key, key)
        
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # --- Верхняя панель: Подключение, Язык, Тема ---
        conn_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()
        self.btn_refresh = QPushButton()
        self.btn_refresh.clicked.connect(self.refresh_ports)
        
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "57600", "115200", "230400"])
        self.baud_combo.setCurrentText("115200")
        
        self.btn_connect = QPushButton()
        self.btn_connect.clicked.connect(self.toggle_connection)
        
        self.lbl_lang = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Русский", "English"])
        # Устанавливаем сохранённый язык
        self.lang_combo.setCurrentIndex(0 if self.current_lang == "ru" else 1)
        self.lang_combo.currentIndexChanged.connect(self.on_lang_changed)
        
        self.lbl_theme = QLabel()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        # Устанавливаем сохранённую тему
        self.theme_combo.setCurrentIndex(0 if self.current_theme == "Light" else 1)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        
        conn_layout.addWidget(QLabel("Port:"))  # Будет обновлено в retranslate_ui
        self.lbl_port = conn_layout.itemAt(0).widget()
        conn_layout.addWidget(self.port_combo)
        conn_layout.addWidget(self.btn_refresh)
        conn_layout.addWidget(QLabel("Baud:"))  # Будет обновлено в retranslate_ui
        self.lbl_baud = conn_layout.itemAt(3).widget()
        conn_layout.addWidget(self.baud_combo)
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addStretch()
        conn_layout.addWidget(self.lbl_lang)
        conn_layout.addWidget(self.lang_combo)
        conn_layout.addWidget(self.lbl_theme)
        conn_layout.addWidget(self.theme_combo)
        main_layout.addLayout(conn_layout)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.create_tab_control()
        self.create_tab_data()
        self.create_tab_hex()
        self.create_tab_disasm()
        self.create_tab_test()
        self.create_tab_io_seq()
        
        self.lbl_log = QLabel()
        main_layout.addWidget(self.lbl_log)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("font-family: Consolas, Courier New, monospace;")
        main_layout.addWidget(self.log_text)
        
        # Подключаем сигнал изменения данных в hex-редакторе
        self.hex_model.dataEdited.connect(self.on_hex_data_changed)

    def create_tab_control(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.bus_group = QGroupBox()
        bus_layout = QHBoxLayout()
        self.btn_hold = QPushButton()
        self.btn_unhold = QPushButton()
        self.btn_hold.clicked.connect(lambda: self.send_command(bytes([CMD_HOLD])))
        self.btn_unhold.clicked.connect(lambda: self.send_command(bytes([CMD_UNHOLD])))
        bus_layout.addWidget(self.btn_hold)
        bus_layout.addWidget(self.btn_unhold)
        self.bus_group.setLayout(bus_layout)
        layout.addWidget(self.bus_group)
        
        self.file_group = QGroupBox()
        file_layout = QHBoxLayout()
        self.btn_save = QPushButton()
        self.btn_save.clicked.connect(self.save_dump)
        self.btn_load = QPushButton()
        self.btn_load.clicked.connect(self.load_and_flash)
        file_layout.addWidget(self.btn_save)
        file_layout.addWidget(self.btn_load)
        self.file_group.setLayout(file_layout)
        layout.addWidget(self.file_group)
        
        layout.addStretch()
        self.tabs.addTab(tab, "")
        self.tab_control = tab

    def create_tab_data(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.mem_group = QGroupBox()
        mem_layout = QGridLayout()
        
        self.mem_data_addr = QLineEdit("0000")
        self.mem_data_bits = QComboBox()
        self.mem_data_bits.addItems(["8", "16", "24", "32"])
        self.mem_data_bits.setCurrentText("8")
        self.mem_data_value = QLineEdit("00")
        self.mem_data_endian = QComboBox()
        self.mem_data_endian.addItems(["Little", "Big"])
        self.mem_data_endian.setCurrentText("Little")
        
        self.btn_mem_read = QPushButton()
        self.btn_mem_write = QPushButton()
        self.btn_mem_read.clicked.connect(self.read_memory_data)
        self.btn_mem_write.clicked.connect(self.write_memory_data)
        
        self.lbl_mem_addr = QLabel()
        self.lbl_mem_bits = QLabel()
        self.lbl_mem_value = QLabel()
        self.lbl_mem_endian = QLabel()
        
        mem_layout.addWidget(self.lbl_mem_addr, 0, 0)
        mem_layout.addWidget(self.mem_data_addr, 0, 1)
        mem_layout.addWidget(self.lbl_mem_bits, 1, 0)
        mem_layout.addWidget(self.mem_data_bits, 1, 1)
        mem_layout.addWidget(self.lbl_mem_value, 2, 0)
        mem_layout.addWidget(self.mem_data_value, 2, 1)
        mem_layout.addWidget(self.lbl_mem_endian, 3, 0)
        mem_layout.addWidget(self.mem_data_endian, 3, 1)
        mem_layout.addWidget(self.btn_mem_read, 4, 0)
        mem_layout.addWidget(self.btn_mem_write, 4, 1)
        
        self.mem_group.setLayout(mem_layout)
        layout.addWidget(self.mem_group)
        
        self.io_group = QGroupBox()
        io_layout = QGridLayout()
        
        self.io_data_addr = QLineEdit("00")
        self.io_data_bits = QComboBox()
        self.io_data_bits.addItems(["8", "16", "24", "32"])
        self.io_data_bits.setCurrentText("8")
        self.io_data_value = QLineEdit("00")
        self.io_data_endian = QComboBox()
        self.io_data_endian.addItems(["Little", "Big"])
        self.io_data_endian.setCurrentText("Little")
        
        self.btn_io_read = QPushButton()
        self.btn_io_write = QPushButton()
        self.btn_io_read.clicked.connect(self.read_io_data)
        self.btn_io_write.clicked.connect(self.write_io_data)
        
        self.lbl_io_addr = QLabel()
        self.lbl_io_bits = QLabel()
        self.lbl_io_value = QLabel()
        self.lbl_io_endian = QLabel()
        
        io_layout.addWidget(self.lbl_io_addr, 0, 0)
        io_layout.addWidget(self.io_data_addr, 0, 1)
        io_layout.addWidget(self.lbl_io_bits, 1, 0)
        io_layout.addWidget(self.io_data_bits, 1, 1)
        io_layout.addWidget(self.lbl_io_value, 2, 0)
        io_layout.addWidget(self.io_data_value, 2, 1)
        io_layout.addWidget(self.lbl_io_endian, 3, 0)
        io_layout.addWidget(self.io_data_endian, 3, 1)
        io_layout.addWidget(self.btn_io_read, 4, 0)
        io_layout.addWidget(self.btn_io_write, 4, 1)
        
        self.io_group.setLayout(io_layout)
        layout.addWidget(self.io_group)
        
        layout.addStretch()
        self.tabs.addTab(tab, "")
        self.tab_data = tab

    def create_tab_hex(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        ctrl_layout = QHBoxLayout()
        self.lbl_range = QLabel()
        self.btn_read_block = QPushButton()
        self.btn_read_block.clicked.connect(self.show_read_block_dialog)
        ctrl_layout.addWidget(self.lbl_range)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(self.btn_read_block)
        layout.addLayout(ctrl_layout)
        
        self.table = HexTableView(self.disassembler, self.mem_data)
        self.table.setModel(self.hex_model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setFont(QFont("Consolas", 10))
        layout.addWidget(self.table)
		
        # Подключаем сигнал обновления статусной строки
        self.table.statusUpdate.connect(self.on_status_update)
        
        self.tabs.addTab(tab, "")
        self.tab_hex = tab

    def create_tab_disasm(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        ctrl_layout = QHBoxLayout()
        self.lbl_disasm_start = QLabel()
        self.disasm_start = QLineEdit("0000")
        self.lbl_disasm_len = QLabel()
        self.disasm_len = QLineEdit("100")
        self.btn_disasm = QPushButton()
        self.btn_disasm.clicked.connect(self.run_disasm)
        self.auto_disasm_check = QCheckBox()
        self.auto_disasm_check.setChecked(True)
        ctrl_layout.addWidget(self.lbl_disasm_start)
        ctrl_layout.addWidget(self.disasm_start)
        ctrl_layout.addWidget(self.lbl_disasm_len)
        ctrl_layout.addWidget(self.disasm_len)
        ctrl_layout.addWidget(self.btn_disasm)
        ctrl_layout.addWidget(self.auto_disasm_check)
        self.btn_export_disasm = QPushButton("Export")  # Будет переведено в retranslate_ui
        self.btn_export_disasm.clicked.connect(self.export_disasm)
        ctrl_layout.addWidget(self.btn_export_disasm)
        layout.addLayout(ctrl_layout)
        
        self.disasm_view = DisasmView()
        self.disasm_scroll = QScrollArea()
        self.disasm_scroll.setWidget(self.disasm_view)
        self.disasm_scroll.setWidgetResizable(True)
        layout.addWidget(self.disasm_scroll)
        
        self.tabs.addTab(tab, "")
        self.tab_disasm = tab

    def create_tab_test(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        form_layout = QHBoxLayout()
        self.lbl_test_start = QLabel()
        self.test_start = QLineEdit("0000")
        self.lbl_test_end = QLabel()
        self.test_end = QLineEdit("00FF")
        self.lbl_test_pattern = QLabel()
        self.test_pattern = QComboBox()
        self.test_pattern.addItems(["Checker", "Zero", "One", "Addr"])
        
        form_layout.addWidget(self.lbl_test_start)
        form_layout.addWidget(self.test_start)
        form_layout.addWidget(self.lbl_test_end)
        form_layout.addWidget(self.test_end)
        form_layout.addWidget(self.lbl_test_pattern)
        form_layout.addWidget(self.test_pattern)
        layout.addLayout(form_layout)
        
        self.btn_test = QPushButton()
        self.btn_test.clicked.connect(self.start_mem_test)
        layout.addWidget(self.btn_test)
        
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.tabs.addTab(tab, "")
        self.tab_test = tab

    def create_tab_io_seq(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.single_io_group = QGroupBox()
        single_layout = QHBoxLayout()
        self.io_addr = QLineEdit("00")
        self.io_data = QLineEdit("00")
        self.btn_io_read_single = QPushButton()
        self.btn_io_write_single = QPushButton()
        self.btn_io_read_single.clicked.connect(self.io_read_single)
        self.btn_io_write_single.clicked.connect(self.io_write_single)
        self.lbl_io_seq_port = QLabel()
        self.lbl_io_seq_data = QLabel()
        single_layout.addWidget(self.lbl_io_seq_port)
        single_layout.addWidget(self.io_addr)
        single_layout.addWidget(self.lbl_io_seq_data)
        single_layout.addWidget(self.io_data)
        single_layout.addWidget(self.btn_io_read_single)
        single_layout.addWidget(self.btn_io_write_single)
        self.single_io_group.setLayout(single_layout)
        layout.addWidget(self.single_io_group)
        
        self.seq_group = QGroupBox()
        seq_layout = QVBoxLayout()
        
        seq_ctrl_layout = QHBoxLayout()
        self.btn_seq_load = QPushButton()
        self.btn_seq_load.clicked.connect(self.load_sequence_file)
        self.btn_seq_run = QPushButton()
        self.btn_seq_run.clicked.connect(self.run_io_sequence)
        seq_ctrl_layout.addWidget(self.btn_seq_load)
        seq_ctrl_layout.addWidget(self.btn_seq_run)
        seq_layout.addLayout(seq_ctrl_layout)
        
        self.seq_text = QTextEdit()
        self.seq_text.setPlaceholderText("Формат:\nW 01 FF ; Запись в порт 01h значения FFh\nR 02    ; Чтение из порта 02h\nD 10    ; Задержка 10 мс")
        self.seq_text.setFont(QFont("Consolas", 10))
        seq_layout.addWidget(self.seq_text)
        
        self.seq_group.setLayout(seq_layout)
        layout.addWidget(self.seq_group)
        
        self.tabs.addTab(tab, "")
        self.tab_io_seq = tab

    # ==================== ЛОКАЛИЗАЦИЯ И ТЕМЫ ====================
    def on_lang_changed(self, index):
        self.current_lang = "ru" if index == 0 else "en"
        self.settings.setValue("language", self.current_lang)  # Сохраняем настройку
        self.retranslate_ui()
        
    def on_theme_changed(self, index):
        self.current_theme = "Light" if index == 0 else "Dark"
        self.settings.setValue("theme", self.current_theme)  # Сохраняем настройку
        QApplication.instance().setStyleSheet(THEMES[self.current_theme])
        
    def retranslate_ui(self):
        self.setWindowTitle(self.tr("app_title"))
        
        # Верхняя панель
        self.lbl_port.setText(self.tr("port"))
        self.lbl_baud.setText(self.tr("baud"))
        self.btn_refresh.setText(self.tr("refresh"))
        self.btn_connect.setText(self.tr("connect") if not (self.serial_port and self.serial_port.is_open) else self.tr("disconnect"))
        self.lbl_lang.setText(self.tr("language"))
        self.lbl_theme.setText(self.tr("theme"))
        
        # Вкладки
        self.tabs.setTabText(0, self.tr("tab_control"))
        self.tabs.setTabText(1, self.tr("tab_data"))
        self.tabs.setTabText(2, self.tr("tab_hex"))
        self.tabs.setTabText(3, self.tr("tab_disasm"))
        self.tabs.setTabText(4, self.tr("tab_test"))
        self.tabs.setTabText(5, self.tr("tab_io_seq"))
        
        # Вкладка "Управление"
        self.bus_group.setTitle(self.tr("bus_control"))
        self.btn_hold.setText(self.tr("hold"))
        self.btn_unhold.setText(self.tr("unhold"))
        self.file_group.setTitle(self.tr("files"))
        self.btn_save.setText(self.tr("save_dump"))
        self.btn_load.setText(self.tr("load_fw"))
        
        # Вкладка "Данные"
        self.mem_group.setTitle(self.tr("memory"))
        self.lbl_mem_addr.setText(self.tr("addr_hex"))
        self.lbl_mem_bits.setText(self.tr("bits"))
        self.lbl_mem_value.setText(self.tr("value_hex"))
        self.lbl_mem_endian.setText(self.tr("endian"))
        self.btn_mem_read.setText(self.tr("read"))
        self.btn_mem_write.setText(self.tr("write"))
        
        self.io_group.setTitle(self.tr("io_port"))
        self.lbl_io_addr.setText(self.tr("port_hex"))
        self.lbl_io_bits.setText(self.tr("bits"))
        self.lbl_io_value.setText(self.tr("value_hex"))
        self.lbl_io_endian.setText(self.tr("endian"))
        self.btn_io_read.setText(self.tr("read"))
        self.btn_io_write.setText(self.tr("write"))
        
        # Вкладка "Hex Редактор"
        self.btn_read_block.setText(self.tr("read_block"))
        self.update_range_label()
        
        # Вкладка "Дизассемблер"
        self.lbl_disasm_start.setText(self.tr("start"))
        self.lbl_disasm_len.setText(self.tr("len"))
        self.btn_disasm.setText(self.tr("disasm"))
        self.auto_disasm_check.setText(self.tr("auto_disasm"))
        self.btn_export_disasm.setText(self.tr("export"))
        
        # Вкладка "Тест Памяти"
        self.lbl_test_start.setText(self.tr("start"))
        self.lbl_test_end.setText("End:")
        self.lbl_test_pattern.setText(self.tr("pattern"))
        self.btn_test.setText(self.tr("start_test"))
        
        # Вкладка "IO Секвенсор"
        self.single_io_group.setTitle(self.tr("single_io"))
        self.lbl_io_seq_port.setText(self.tr("port_hex"))
        self.lbl_io_seq_data.setText(self.tr("value_hex"))
        self.btn_io_read_single.setText(self.tr("read_in"))
        self.btn_io_write_single.setText(self.tr("write_out"))
        self.seq_group.setTitle(self.tr("io_seq"))
        self.btn_seq_load.setText(self.tr("load_file"))
        self.btn_seq_run.setText(self.tr("run_seq"))
        
        # Лог
        self.lbl_log.setText(self.tr("log"))

    # ==================== ЛОГИКА ====================
    def refresh_ports(self):
        self.port_combo.clear()
        for p in serial.tools.list_ports.comports():
            self.port_combo.addItem(f"{p.device} - {p.description}", p.device)

    def toggle_connection(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.poll_timer.stop()
            self.btn_connect.setText(self.tr("connect"))
            self.status_label_conn.setText(self.tr("disconnected"))  # ← Добавить
            self.log(self.tr("disconnected"))
        else:
            port_name = self.port_combo.currentData()
            baud_rate = int(self.baud_combo.currentText())
            if not port_name:
                QMessageBox.warning(self, self.tr("error"), self.tr("err_port"))
                return
            try:
                self.serial_port = serial.Serial(port_name, baud_rate, timeout=0.1, write_timeout=1.0)
                self.poll_timer.start(50)
                self.btn_connect.setText(self.tr("disconnect"))
                self.status_label_conn.setText(f"{self.tr('connected')} ({baud_rate})")  # ← Добавить
                self.log(f"{self.tr('connected')} {port_name} ({baud_rate}).")
                
                self.log(self.tr("test_conn"))
                self.send_command(bytes([CMD_NOP]))
                
            except serial.SerialException as e:
                QMessageBox.critical(self, self.tr("err_connect"), f"{self.tr('err_open')} {port_name}:\n{e}")
                self.serial_port = None
            except Exception as e:
                QMessageBox.critical(self, self.tr("error"), str(e))

    def log(self, msg):
        self.log_text.append(msg)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def send_command(self, payload):
        if not self.serial_port or not self.serial_port.is_open:
            self.log(self.tr("err_not_open")); return
        try:
            self.serial_port.write(SlipProtocol.encode(payload))
            self.log(f"TX -> {payload.hex(' ').upper()}")
        except serial.SerialException as e:
            self.log(f"{self.tr('err_send')} {e}")

    def read_serial(self):
        if self.serial_port and self.serial_port.is_open and self.serial_port.in_waiting:
            try:
                self.rx_buffer.extend(self.serial_port.read(self.serial_port.in_waiting))
            except serial.SerialException as e:
                self.log(f"{self.tr('err_read_port')} {e}")
                return
                
            while _FEND in self.rx_buffer:
                end_idx = self.rx_buffer.index(_FEND)
                packet_raw = self.rx_buffer[:end_idx]
                self.rx_buffer = self.rx_buffer[end_idx+1:]
                if packet_raw:
                    self.process_response(SlipProtocol.decode(packet_raw))

    def process_response(self, data):
        if not data: return
        self.log(f"RX <- {data.hex(' ').upper()}")
        cmd = data[0]
        
        if cmd == ACK_NOP:
            self.log(f"  [{self.tr('ok')}] {self.tr('conn_est')}")
        elif cmd == ACK_MEM_READ_BYTE and len(data) >= 4:
            addr = (data[1] << 8) | data[2]
            self.mem_data[addr] = data[3]
            self.hex_model.update_data(self.mem_data)
            self.update_range_label()
            self.log(f"  [{self.tr('ok')}] 0x{addr:04X}: 0x{data[3]:02X}")
        elif cmd == ACK_IO_READ_BYTE and len(data) >= 4:
            addr = (data[1] << 8) | data[2]
            val = data[3]
            self.log(f"  [{self.tr('ok')}] IO Read 0x{addr:02X}: 0x{val:02X}")
        elif cmd == ACK_IO_WRITE_BYTE:
            self.log(f"  [{self.tr('ok')}] {self.tr('write_io')}.")
        elif cmd == ACK_ERROR:
            self.log(f"  [{self.tr('error')}] {self.tr('err_ack')}")

    def update_range_label(self):
        if self.mem_data:
            mn = min(self.mem_data.keys()); mx = max(self.mem_data.keys())
            self.lbl_range.setText(f"{self.tr('range')} 0x{mn:04X} - 0x{mx:04X} ({len(self.mem_data)} {self.tr('bytes')})")
            self.status_label_size.setText(f"{len(self.mem_data)} {self.tr('bytes')}")  # ← Добавить
        else:
            self.lbl_range.setText(f"{self.tr('range')} -")
            self.status_label_size.setText("0 bytes")  # ← Добавить
            
    # ==================== КОНВЕРТАЦИЯ ЗНАЧЕНИЙ ====================
    def value_to_bytes(self, value, bits, endian):
        size = bits // 8
        if endian == "Little":
            return [(value >> (8 * i)) & 0xFF for i in range(size)]
        else:
            return [(value >> (8 * (size - 1 - i))) & 0xFF for i in range(size)]

    def bytes_to_value(self, byte_list, bits, endian):
        size = bits // 8
        value = 0
        if endian == "Little":
            for i in range(size):
                value |= byte_list[i] << (8 * i)
        else:
            for i in range(size):
                value |= byte_list[i] << (8 * (size - 1 - i))
        return value

    # ==================== ЧТЕНИЕ/ЗАПИСЬ ДАННЫХ ====================
    def read_memory_data(self):
        try:
            addr = int(self.mem_data_addr.text(), 16)
            bits = int(self.mem_data_bits.currentText())
            size = bits // 8
            endian = self.mem_data_endian.currentText()
            self.pending_read = {"addr": addr, "bits": bits, "endian": endian, "is_io": False}
            self.start_worker("read_block", (addr, size))
        except ValueError:
            QMessageBox.warning(self, self.tr("error"), self.tr("err_addr"))

    def write_memory_data(self):
        try:
            addr = int(self.mem_data_addr.text(), 16)
            bits = int(self.mem_data_bits.currentText())
            endian = self.mem_data_endian.currentText()
            value = int(self.mem_data_value.text(), 16)
            byte_list = self.value_to_bytes(value, bits, endian)
            mem_dict = {addr + i: byte_list[i] for i in range(len(byte_list))}
            self.mem_data.update(mem_dict)
            self.hex_model.update_data(self.mem_data)
            self.update_range_label()
            self.start_worker("write_block", (mem_dict, addr))
        except ValueError:
            QMessageBox.warning(self, self.tr("error"), self.tr("err_addr_val"))

    def read_io_data(self):
        try:
            port = int(self.io_data_addr.text(), 16)
            bits = int(self.io_data_bits.currentText())
            size = bits // 8
            endian = self.io_data_endian.currentText()
            self.pending_read = {"addr": port, "bits": bits, "endian": endian, "is_io": True}
            self.start_worker("read_io_block", (port, size))
        except ValueError:
            QMessageBox.warning(self, self.tr("error"), self.tr("err_port_addr"))

    def write_io_data(self):
        try:
            port = int(self.io_data_addr.text(), 16)
            bits = int(self.io_data_bits.currentText())
            endian = self.io_data_endian.currentText()
            value = int(self.io_data_value.text(), 16)
            byte_list = self.value_to_bytes(value, bits, endian)
            io_dict = {port + i: byte_list[i] for i in range(len(byte_list))}
            self.start_worker("write_io_block", (io_dict, port))
        except ValueError:
            QMessageBox.warning(self, self.tr("error"), self.tr("err_addr_val"))

    # ==================== ФАЙЛЫ ====================
    def save_dump(self):
        if not self.mem_data:
            QMessageBox.warning(self, self.tr("err_empty"), self.tr("err_no_data"))
            return
        path, _ = QFileDialog.getSaveFileName(self, self.tr("save_as"), "", "Intel HEX (*.hex);;Binary (*.bin)")
        if path:
            if path.endswith(".hex"):
                with open(path, "w") as f: f.write(IntelHex.generate(self.mem_data))
            else:
                mn, mx = min(self.mem_data.keys()), max(self.mem_data.keys())
                with open(path, "wb") as f:
                    for i in range(mn, mx + 1): f.write(bytes([self.mem_data.get(i, 0xFF)]))
            self.log(f"{self.tr('save_as')}: {path}")

    def load_and_flash(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("load_fw_title"), "", "Intel HEX (*.hex);;Binary (*.bin)")
        if not path: return
        
        loaded_mem = {}
        if path.endswith(".hex"):
            with open(path, "r") as f: loaded_mem = IntelHex.parse(f.read())
        else:
            text, ok = QInputDialog.getText(self, self.tr("base_addr"), self.tr("base_addr_hint"))
            if not ok: return
            try:
                base = int(text, 16)
            except ValueError:
                QMessageBox.warning(self, self.tr("error"), self.tr("err_hex"))
                return
            with open(path, "rb") as f:
                data = f.read()
                for i, b in enumerate(data): loaded_mem[base + i] = b
                
        self.mem_data.update(loaded_mem)
        self.hex_model.update_data(self.mem_data)
        self.update_range_label()
        
        if self.auto_disasm_check.isChecked():
            self.auto_disasm()
        
        self.log(f"{self.tr('loaded')} {len(loaded_mem)} {self.tr('bytes_from_file')}")
        
        if QMessageBox.question(self, self.tr("flash_q"), self.tr("flash_msg")) == QMessageBox.Yes:
            self.start_worker("write_block", (loaded_mem, min(loaded_mem.keys())))

    # ==================== ДИЗАССЕМБЛЕР ====================
    def auto_disasm(self):
        if not self.mem_data:
            return
        mn = min(self.mem_data.keys())
        mx = max(self.mem_data.keys())
        length = mx - mn + 1
        
        self.disasm_start.setText(f"{mn:04X}")
        self.disasm_len.setText(f"{length:X}")
        
        lines = self.disassembler.disassemble(self.mem_data, mn, length)
        self.disasm_view.set_lines(lines)

    def run_disasm(self):
        try:
            start = int(self.disasm_start.text(), 16)
            length = int(self.disasm_len.text(), 16)
        except ValueError: return
        
        lines = self.disassembler.disassemble(self.mem_data, start, length)
        self.disasm_view.set_lines(lines)

    def on_hex_data_changed(self):
        """Вызывается при изменении данных в hex-редакторе"""
        if self.auto_disasm_check.isChecked():
            self.disasm_timer.start(200)  # Дебаунс 200 мс

    # ==================== БЛОКИ, ТЕСТЫ, IO ====================
    def show_read_block_dialog(self):
        text1, ok1 = QInputDialog.getText(self, self.tr("addr_hex"), "Start Address (HEX):")
        if not ok1: return
        try:
            addr = int(text1, 16)
        except ValueError:
            QMessageBox.warning(self, self.tr("error"), self.tr("err_hex"))
            return
            
        size, ok2 = QInputDialog.getInt(self, self.tr("len"), "Size (Dec):", 128, 1, 128)
        if not ok2: return
        self.start_worker("read_block", (addr, size))

    def start_mem_test(self):
        try:
            start = int(self.test_start.text(), 16)
            end = int(self.test_end.text(), 16)
            pat = self.test_pattern.currentText()
            self.start_worker("test_mem", (start, end, pat))
        except ValueError:
            QMessageBox.warning(self, self.tr("error"), self.tr("err_addr"))

    def io_read_single(self):
        try:
            port = int(self.io_addr.text(), 16)
            self.send_command(bytes([CMD_IO_READ_BYTE, (port >> 8) & 0xFF, port & 0xFF]))
        except ValueError:
            QMessageBox.warning(self, self.tr("error"), self.tr("err_port_addr"))

    def io_write_single(self):
        try:
            port = int(self.io_addr.text(), 16)
            data = int(self.io_data.text(), 16)
            self.send_command(bytes([CMD_IO_WRITE_BYTE, (port >> 8) & 0xFF, port & 0xFF, data]))
        except ValueError:
            QMessageBox.warning(self, self.tr("error"), self.tr("err_addr_val"))

    def load_sequence_file(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("load_file"), "", "Text Files (*.txt);;All Files (*)")
        if path:
            with open(path, 'r') as f:
                self.seq_text.setPlainText(f.read())
            self.log(f"{self.tr('load_file')}: {path}")

    def run_io_sequence(self):
        text = self.seq_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, self.tr("err_empty"), self.tr("err_no_data"))
            return
        sequence = text.strip().split('\n')
        self.start_worker("run_io_sequence", {'sequence': sequence})

    def start_worker(self, task, params):
        if not self.serial_port or not self.serial_port.is_open:
            self.log(self.tr("err_not_open")); return
            
        self.worker_thread = QThread()
        self.worker = BusWorker(self.serial_port, task, params, self.current_lang)
        self.worker.moveToThread(self.worker_thread)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker.log.connect(self.log)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        self.worker_thread.start()

    def on_worker_finished(self, result):
        if isinstance(result, dict) and result:
            if self.pending_read:
                addr = self.pending_read["addr"]
                bits = self.pending_read["bits"]
                endian = self.pending_read["endian"]
                is_io = self.pending_read["is_io"]
                
                byte_list = [result.get(addr + i, 0) for i in range(bits // 8)]
                value = self.bytes_to_value(byte_list, bits, endian)
                hex_digits = (bits // 8) * 2
                
                if is_io:
                    self.io_data_value.setText(f"{value:0{hex_digits}X}")
                else:
                    self.mem_data_value.setText(f"{value:0{hex_digits}X}")
                    self.mem_data.update(result)
                    self.hex_model.update_data(self.mem_data)
                    self.update_range_label()
                
                self.pending_read = None
                
                if self.auto_disasm_check.isChecked() and not is_io:
                    self.auto_disasm()
            else:
                self.mem_data.update(result)
                self.hex_model.update_data(self.mem_data)
                self.update_range_label()
                
                if self.auto_disasm_check.isChecked():
                    self.auto_disasm()
        
        self.log(self.tr("thread_done"))
            
    def on_status_update(self, addr, data, mnemonic):
        """Обновление статусной строки при наведении на ячейку"""
        self.status_label_addr.setText(f"Адрес: {addr}")
        self.status_label_data.setText(f"Данные: {data}")
        self.status_label_mnem.setText(f"Мнемоника: {mnemonic}")
	
    def export_disasm(self):
        """Экспорт дизассемблированного листинга в файл"""
        if not self.disasm_view.lines:
            QMessageBox.warning(self, self.tr("err_empty"), self.tr("err_no_data"))
            return
            
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Disassembly", 
            "", 
            "Assembly Files (*.asm);;Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return
            
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # Заголовок
                f.write("; ============================================\n")
                f.write("; i8080 Disassembly\n")
                f.write("; Generated by i8080-5 CI\n")
                f.write(f"; Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("; ============================================\n\n")
                
                # Тело
                for addr, size, asm, undoc, target in self.disasm_view.lines:
                    # Получаем байты для этой строки
                    bytes_str = " ".join(f"{self.mem_data.get(addr+k, 0):02X}" for k in range(size))
                    
                    # Форматируем строку
                    undoc_mark = " ; undocumented" if undoc else ""
                    target_comment = f" ; -> {target:04X}h" if target is not None else ""
                    
                    f.write(f"{addr:04X}  {bytes_str:<12} {asm}{undoc_mark}{target_comment}\n")
                    
            self.log(f"Disassembly exported to: {path}")
            self.statusBar.showMessage(f"Exported to {path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
