import sys
import time
import serial
import serial.tools.list_ports
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QPushButton, QComboBox, QLabel, 
                               QLineEdit, QTextEdit, QGroupBox, QMessageBox, QTableWidget, QTableWidgetItem,
                               QTabWidget, QTableView, QHeaderView, QFileDialog,
                               QProgressBar, QSpinBox, QCheckBox, QScrollArea, QInputDialog,
                               QToolTip, QStyle, QStatusBar, QDialog, QListWidget, QListWidgetItem, QMenu)

from PySide6.QtCore import Qt, QTimer, QThread, QObject, Signal, QAbstractTableModel, QModelIndex, QEvent, QLocale, QSettings, QRect
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QShortcut, QKeySequence

from i8080_emulator import I8080Emulator

# === MCP Server (опционально) ===
try:
    from mcp_server import MCPServerManager
    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False
    print(f"MCP Server недоступен: {e}")
	
# ==================== ЛОКАЛИЗАЦИЯ И ТЕМЫ ====================
LANGS = {
    "en": {
        "app_title": "i8080-5 CI",
        "port": "Port:", "baud": "Baud:", "connect": "Connect", "disconnect": "Disconnect",
        "refresh": "Refresh", "tab_control": "Control", "tab_data": "Data", "tab_hex": "Hex Editor",
        "tab_disasm": "Disassembler", "tab_test": "Memory Test", "tab_io_seq": "IO Sequencer",
        "log": "Log:", "bus_control": "Bus Control", "hold": "Hold Bus (HOLD)", "unhold": "Release Bus (UnHOLD)",
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
        "expected": "Expected", "got": "Got", "export": "Export", "search": "Search",
        "goto_addr": "Goto Address", "fill_range": "Fill Range", "copy_addr": "Copy Address",
        "copy_val": "Copy Value", "invert_byte": "Invert Byte", "disasm_from": "Disassemble from",
        "text_column": "Text", "addr_column": "Addr", "tab_compare": "Compare",
        "load_compare": "Load File to Compare", "btn_compare": "Compare", "export_report": "Export Report",
        "compare_addr": "Address", "compare_current": "Current", "compare_file": "File", "compare_status": "Status",
        "status_changed": "Changed", "status_added": "Added in File", "status_removed": "Removed in File",
        "no_compare_file": "No file loaded for comparison", "compare_loaded": "Loaded", 
        "run_compare_first": "Run compare first!", "compare_found": "differences found",
        "compare_complete": "Compare complete", "compare_exported": "Compare report exported to",
        "load_compare_title": "Load File to Compare", "export_compare_title": "Export Compare Report",
		"tab_scripts": "Scripts", "run_script": "▶ Run Script", "load_script": "Load Script",
		"save_script": "Save Script", "clear_output": "Clear Output", "script_output": "Output:",
		# Эмулятор
        "tab_emulator": "Emulator", "emulator_registers": "Registers", "emulator_flags": "Flags",
        "emulator_stats": "Statistics", "emulator_control": "Control", "emulator_current_instr": "Current Instruction",
        "emulator_breakpoints": "Breakpoints", "emulator_reset": "Reset", "emulator_set_pc": "Set PC...",
        "emulator_step_into": "Step Into (F11)", "emulator_step_over": "Step Over (F10)",
        "emulator_run": "▶ Run (F5)", "emulator_stop": "■ Stop", "emulator_add_bp": "Add",
        "emulator_clear_bp": "Clear All", "end": "End:",
    },
    "ru": {
        "app_title": "i8080-5 CI",
        "port": "Порт:", "baud": "Скорость:", "connect": "Подключиться", "disconnect": "Отключиться",
        "refresh": "Обновить", "tab_control": "Управление", "tab_data": "Данные", "tab_hex": "Hex Редактор",
        "tab_disasm": "Дизассемблер", "tab_test": "Тест Памяти", "tab_io_seq": "IO Секвенсор",
        "log": "Журнал:", "bus_control": "Управление шиной", "hold": "Захватить шину (HOLD)", "unhold": "Освободить шину (UnHOLD)",
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
        "expected": "Ожидалось", "got": "Получено", "export": "Экспорт", "search": "Поиск",
        "goto_addr": "Перейти к адресу", "fill_range": "Заполнить диапазон", "copy_addr": "Копировать адрес",
        "copy_val": "Копировать значение", "invert_byte": "Инвертировать байт", "disasm_from": "Дизассемблировать от",
        "text_column": "Текст", "addr_column": "Адрес", "tab_compare": "Сравнение",
        "load_compare": "Загрузить файл для сравнения", "btn_compare": "Сравнить", "export_report": "Экспорт отчёта",
        "compare_addr": "Адрес", "compare_current": "Текущий", "compare_file": "Файл", "compare_status": "Статус",
        "status_changed": "Изменено", "status_added": "Добавлено в файле", "status_removed": "Удалено в файле",
        "no_compare_file": "Файл для сравнения не загружен", "compare_loaded": "Загружено", 
        "run_compare_first": "Сначала выполните сравнение!", "compare_found": "различий найдено",
        "compare_complete": "Сравнение завершено", "compare_exported": "Отчёт о сравнении экспортирован в",
        "load_compare_title": "Загрузить файл для сравнения", "export_compare_title": "Экспорт отчёта о сравнении",
		"tab_scripts": "Скрипты", "run_script": "▶ Выполнить скрипт", "load_script": "Загрузить скрипт",
		"save_script": "Сохранить скрипт", "clear_output": "Очистить вывод", "script_output": "Вывод:",
		# Эмулятор
        "tab_emulator": "Эмулятор", "emulator_registers": "Регистры", "emulator_flags": "Флаги", "emulator_stats": "Статистика",
        "emulator_control": "Управление", "emulator_current_instr": "Текущая инструкция", "emulator_breakpoints": "Точки останова",
        "emulator_reset": "Сброс", "emulator_set_pc": "Установить PC...", "emulator_step_into": "Шаг с заходом (F11)",
        "emulator_step_over": "Шаг без захода (F10)", "emulator_run": "▶ Запуск (F5)", "emulator_stop": "■ Стоп",
        "emulator_add_bp": "Добавить", "emulator_clear_bp": "Очистить все", "end": "Конец:",
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
CMD_GET_SIZE_SETUP = 0x40
CMD_SET_POLARITY_SETUP = 0x41
ACK_GET_SIZE_SETUP = 0x40
ACK_SET_POLARITY_SETUP = 0x41
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
        
        # LXI: 0x01, 0x11, 0x21, 0x31
        for i in range(4): t[0x01 + i*16] = (3, f"LXI {self.RP[i]},{{1:02X}}{{0:02X}}h")
        
        # DAD: 0x09, 0x19, 0x29, 0x39 ← ДОБАВЛЕНО
        for i in range(4): t[0x09 + i*16] = (1, f"DAD {self.RP[i]}")
        
        # INX: 0x03, 0x13, 0x23, 0x33
        for i in range(4): t[0x03 + i*16] = (1, f"INX {self.RP[i]}")
        
        # DCX: 0x0B, 0x1B, 0x2B, 0x3B
        for i in range(4): t[0x0B + i*16] = (1, f"DCX {self.RP[i]}")
        
        # INR: 0x04, 0x0C, 0x14, 0x1C, 0x24, 0x2C, 0x34, 0x3C
        for i in range(8): t[0x04 + i*8] = (1, f"INR {self.REGS[i]}")
        
        # DCR: 0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D
        for i in range(8): t[0x05 + i*8] = (1, f"DCR {self.REGS[i]}")
        
        # MVI: 0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E
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
    toggleBreakpoint = Signal(int)  # Сигнал для установки/удаления breakpoint
    
    def __init__(self, mem_data, parent=None):
        super().__init__(parent)
        self.lines = []
        self.mem_data = mem_data
        self.line_height = 22
        self.addr_to_index = {}
        self.font_size = 10
        self.setFont(QFont("Consolas", self.font_size))
        self.setMinimumWidth(700)
        self.arrow_margin = 30
        self.is_dark_theme = False
        self.setup_colors()
        self.highlight_addr = None  # Адрес для подсветки (PC эмулятора)
        self.breakpoints = set()  # Точки останова для отрисовки
        
    def set_highlight(self, addr):
        """Установить подсветку строки (PC эмулятора)"""
        self.highlight_addr = addr
        self.update()
        
    def setup_colors(self):
        """Настраивает цвета в зависимости от темы"""
        if self.is_dark_theme:
            # Тёмная тема
            self.colors = {
                "bg": QColor("#1e1e1e"),
                "addr": QColor("#858585"),
                "bytes": QColor("#6a6a6a"),
                "jump": QColor("#569cd6"),      # Синий
                "memory": QColor("#6bcf7f"),    # Зелёный
                "io": QColor("#c586c0"),        # Фиолетовый
                "control": QColor("#858585"),   # Серый
                "register": QColor("#ce9178"),  # Оранжевый
                "alu": QColor("#dcdcaa"),       # Жёлтый
                "stack": QColor("#4ec9b0"),     # Бирюзовый
                "undoc": QColor("#ff6b6b"),     # Красный
                "comment": QColor("#569cd6"),   # Голубой
                "text": QColor("#d4d4d4"),      # Основной текст
            }
        else:
            # Светлая тема (яркие, контрастные цвета на белом фоне)
            self.colors = {
                "bg": QColor("#ffffff"),        # Белый фон
                "addr": QColor("#808080"),      # Серый
                "bytes": QColor("#666666"),     # Тёмно-серый
                "jump": QColor("#0055cc"),      # Тёмно-синий
                "memory": QColor("#007700"),    # Тёмно-зелёный
                "io": QColor("#8800aa"),        # Фиолетовый
                "control": QColor("#666666"),   # Серый
                "register": QColor("#cc5500"),  # Тёмно-оранжевый
                "alu": QColor("#886600"),       # Тёмно-жёлтый
                "stack": QColor("#008888"),     # Тёмно-бирюзовый
                "undoc": QColor("#cc0000"),     # Красный
                "comment": QColor("#0055cc"),   # Голубой
                "text": QColor("#000000"),      # Чёрный текст
            }
        
    def set_theme(self, is_dark):
        """Устанавливает тему"""
        self.is_dark_theme = is_dark
        self.setup_colors()
        self.update()
        
    def set_lines(self, lines):
        self.lines = lines
        self.addr_to_index = {line[0]: i for i, line in enumerate(lines)}
        self.setFixedHeight(len(lines) * self.line_height + 10)
        self.repaint()
        if self.parent():
            self.parent().update()
            
    def get_instruction_color(self, asm):
        """Возвращает цвет для команды в зависимости от её типа"""
        parts = asm.split()
        if not parts:
            return self.colors["text"]
            
        mnemonic = parts[0].upper()
        
        # Недокументированные команды
        if asm.endswith("*"):
            return self.colors["undoc"]
        
        # Переходы: JMP, CALL, Jcc, Ccc, RST
        if mnemonic in ["JMP", "CALL", "RST"]:
            return self.colors["jump"]
        if len(mnemonic) > 1:
            suffix = mnemonic[1:]
            if mnemonic[0] == 'J' and suffix in ["NZ", "Z", "NC", "C", "PO", "PE", "P", "M"]:
                return self.colors["jump"]
            if mnemonic[0] == 'C' and suffix in ["NZ", "Z", "NC", "C", "PO", "PE", "P", "M"]:
                return self.colors["jump"]
        
        # Память
        if mnemonic in ["LDA", "STA", "LHLD", "SHLD", "LDAX", "STAX", "XCHG", "XTHL"]:
            return self.colors["memory"]
        if mnemonic == "MOV" and len(parts) > 1 and "M" in parts[1]:
            return self.colors["memory"]
        
        # Ввод-вывод
        if mnemonic in ["IN", "OUT"]:
            return self.colors["io"]
        
        # Управление
        if mnemonic in ["NOP", "HLT", "DI", "EI", "RET", "PCHL", "SPHL"]:
            return self.colors["control"]
        
        # Регистры и данные
        if mnemonic in ["MVI", "LXI", "INR", "DCR", "MOV", "INX", "DCX"]:
            return self.colors["register"]
        
        # Арифметика и логика (включая DAD)
        if mnemonic in ["ADD", "ADC", "SUB", "SBB", "ANA", "XRA", "ORA", "CMP",
                        "RLC", "RRC", "RAL", "RAR", "DAA", "CMA", "STC", "CMC",
                        "ADI", "ACI", "SUI", "SBI", "ANI", "XRI", "ORI", "CPI",
                        "DAD"]:
            return self.colors["alu"]
        
        # Стек
        if mnemonic in ["PUSH", "POP"]:
            return self.colors["stack"]
        
        return self.colors["text"]
        
    def wheelEvent(self, event):
        """Ctrl + колесо мыши для изменения размера шрифта"""
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.font_size = min(self.font_size + 1, 36)
            else:
                self.font_size = max(self.font_size - 1, 8)
                
            self.setFont(QFont("Consolas", self.font_size))
            self.line_height = self.font_size + 12
            self.setFixedHeight(len(self.lines) * self.line_height + 10)
            self.update()
            event.accept()
        else:
            super().wheelEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self.font())
        
        # Фон (белый для светлой темы)
        painter.fillRect(self.rect(), self.colors["bg"])
        
        # Получаем ширину символа для выравнивания
        font_metrics = painter.fontMetrics()
        char_width = font_metrics.averageCharWidth()
        
        # Фиксированные позиции колонок
        addr_x = self.arrow_margin + 10
        bytes_x = addr_x + 6 * char_width
        asm_x = bytes_x + 14 * char_width
        
        # Рисуем строки
        for i, (addr, size, asm, undoc, target) in enumerate(self.lines):
            y = i * self.line_height + self.line_height // 2 + 5
                   
            # === Подсветка текущей инструкции (PC эмулятора) ===
            if self.highlight_addr is not None and addr == self.highlight_addr:
                # Жёлтый фон для текущей инструкции
                highlight_rect = QRect(
                    self.arrow_margin + 5,
                    i * self.line_height + 2,
                    self.width() - self.arrow_margin - 10,
                    self.line_height - 4
                )
                painter.fillRect(highlight_rect, QColor("#fff3cd"))  # Светло-жёлтый
                
                # Стрелка слева
                painter.setPen(QColor("#ff9800"))
                painter.drawText(5, y, "►")
                
            # === Точки останова (красные кружки) ===
            if addr in self.breakpoints:
                bp_x = self.arrow_margin + 2
                bp_y = i * self.line_height + self.line_height // 2
                painter.setBrush(QColor("#f44336"))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(bp_x - 4, bp_y - 4, 8, 8)
				
            # Адрес
            painter.setPen(self.colors["addr"])
            painter.drawText(addr_x, y, f"{addr:04X}")
            
            # Байты
            bytes_str = " ".join(f"{self.mem_data.get(addr+k, 0):02X}" for k in range(size))
            painter.setPen(self.colors["bytes"])
            painter.drawText(bytes_x, y, bytes_str)
            
            # Команда
            asm_text = f"{asm} {undoc}".strip()
            color = self.get_instruction_color(asm_text)
            painter.setPen(color)
            painter.drawText(asm_x, y, asm_text)
            
            # Комментарий перехода
            if target is not None:
                comment = f"; -> {target:04X}h"
                comment_x = asm_x + len(asm_text) * char_width + 3 * char_width
                painter.setPen(self.colors["comment"])
                painter.drawText(comment_x, y, comment)
                
        # Рисуем стрелки переходов
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
				
    def mouseDoubleClickEvent(self, event):
        """Двойной клик — установить/удалить точку останова"""
        y = event.position().y()
        line_idx = int((y - 5) / self.line_height)
        
        if 0 <= line_idx < len(self.lines):
            addr = self.lines[line_idx][0]
            # Излучаем сигнал для MainWindow
            self.toggleBreakpoint.emit(addr)
        
        super().mouseDoubleClickEvent(event)
        
    def set_breakpoints(self, breakpoints):
        """Установить точки останова для отрисовки"""
        self.breakpoints = breakpoints
        self.update()

# ==================== МОДЕЛЬ ДАННЫХ HEX-РЕДАКТОРА ====================
class HexModel(QAbstractTableModel):
    dataEdited = Signal()
    
    def __init__(self, mem_dict=None):
        super().__init__()
        self.mem = mem_dict if mem_dict is not None else {}
        self.min_addr = 0
        self.max_addr = 0
        self.lang = "en"  # ← Добавлено для локализации заголовков
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

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Заголовки колонок"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return LANGS.get(self.lang, LANGS['en']).get('addr_column', 'Addr')
            elif 1 <= section <= 16:
                return f"{section - 1:X}"  # 0, 1, 2, ... F
            elif section == 17:
                return LANGS.get(self.lang, LANGS['en']).get('text_column', 'Text')
        return super().headerData(section, orientation, role)

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
                    old_val = self.mem.get(addr, 0)
                    if old_val != val:  # Только если значение изменилось
                        self.mem[addr] = val
                        self.last_edit = (addr, old_val, val)  # ← Сохраняем для undo
                        self.dataChanged.emit(index, index, [Qt.DisplayRole])
                        self.dataEdited.emit()
                    return True
            except ValueError: pass
        return False

# ==================== КАСТОМНАЯ ТАБЛИЦА HEX-РЕДАКТОРА С ПОДСКАЗКАМИ ====================
class HexTableView(QTableView):
    editOperation = Signal(list)  # ← Добавлено: [(addr, old_val, new_val), ...]
    statusUpdate = Signal(str, str, str)
    gotoAddress = Signal(int)
    
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
        
    def contextMenuEvent(self, event):
        """Контекстное меню при правом клике"""
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
            
        menu = QMenu(self)
        
        # Определяем адрес ячейки
        addr = None
        if 1 <= index.column() <= 16:
            model = self.model()
            if model and hasattr(model, 'min_addr'):
                row = index.row()
                col = index.column()
                addr = model.min_addr + (row * 16) + col - 1
        
        if addr is not None and addr in self.mem_data:
            byte_val = self.mem_data[addr]
            
            # Копировать адрес
            act_copy_addr = menu.addAction(f"Copy Address (0x{addr:04X})")
            act_copy_addr.triggered.connect(lambda: self.copy_to_clipboard(f"{addr:04X}"))
            
            # Копировать значение
            act_copy_val = menu.addAction(f"Copy Value (0x{byte_val:02X})")
            act_copy_val.triggered.connect(lambda: self.copy_to_clipboard(f"{byte_val:02X}"))
            
            menu.addSeparator()
            
            # Инвертировать байт
            act_invert = menu.addAction(f"Invert Byte (0x{~byte_val & 0xFF:02X})")
            act_invert.triggered.connect(lambda: self.invert_byte(addr))
            
            # Заполнить диапазон
            act_fill = menu.addAction("Fill Range...")
            act_fill.triggered.connect(lambda: self.fill_range(addr))
            
            menu.addSeparator()
            
            # Дизассемблировать отсюда
            act_disasm = menu.addAction(f"Disassemble from 0x{addr:04X}")
            act_disasm.triggered.connect(lambda: self.disasm_from(addr))
            
            # Перейти к адресу
            act_goto = menu.addAction("Goto Address...")
            act_goto.triggered.connect(lambda: self.goto_dialog())
            
        menu.exec(event.globalPos())
        
    def copy_to_clipboard(self, text):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        
    def invert_byte(self, addr):
        """Инвертирует байт по адресу"""
        if addr in self.mem_data:
            old_val = self.mem_data[addr]
            new_val = ~old_val & 0xFF
            self.mem_data[addr] = new_val
            self.editOperation.emit([(addr, old_val, new_val)])  # ← Для undo
            model = self.model()
            if model:
                model.update_data({addr: new_val})
                
    def fill_range(self, start_addr):
        """Заполняет диапазон значением"""
        text, ok = QInputDialog.getText(self, "Fill Range", "Value (HEX):")
        if not ok: return
        try:
            val = int(text, 16)
        except ValueError:
            return
            
        size, ok2 = QInputDialog.getInt(self, "Fill Range", "Size (Dec):", 16, 1, 4096)
        if not ok2: return
        
        changes = []
        for i in range(size):
            addr = start_addr + i
            old_val = self.mem_data.get(addr, 0)
            self.mem_data[addr] = val
            changes.append((addr, old_val, val))
            
        self.editOperation.emit(changes)  # ← Для undo
        model = self.model()
        if model:
            model.update_data({start_addr + i: val for i in range(size)})
            
    def disasm_from(self, addr):
        """Дизассемблировать от указанного адреса"""
        self.parent().parent().parent().parent().disasm_from_address(addr)
        
    def goto_dialog(self):
        """Диалог перехода к адресу"""
        text, ok = QInputDialog.getText(self, "Goto Address", "Address (HEX):")
        if not ok: return
        try:
            addr = int(text, 16)
            self.gotoAddress.emit(addr)
        except ValueError:
            pass

class SearchDialog(QDialog):
    searchRequested = Signal(str, str)  # pattern, mode
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Memory")
        self.resize(400, 300)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Поле ввода паттерна
        input_layout = QHBoxLayout()
        self.lbl_pattern = QLabel("Pattern:")
        self.txt_pattern = QLineEdit()
        self.txt_pattern.setPlaceholderText("C3 00 10 or HELLO")
        input_layout.addWidget(self.lbl_pattern)
        input_layout.addWidget(self.txt_pattern)
        layout.addLayout(input_layout)
        
        # Режим поиска
        mode_layout = QHBoxLayout()
        self.lbl_mode = QLabel("Mode:")
        self.cmb_mode = QComboBox()
        self.cmb_mode.addItems(["HEX Bytes", "ASCII String", "HEX with Mask (??)"])
        mode_layout.addWidget(self.lbl_mode)
        mode_layout.addWidget(self.cmb_mode)
        layout.addLayout(mode_layout)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_find = QPushButton("Find Next")
        self.btn_find_all = QPushButton("Find All")
        self.btn_close = QPushButton("Close")
        self.btn_find.clicked.connect(self.on_find)
        self.btn_find_all.clicked.connect(self.on_find_all)
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_find)
        btn_layout.addWidget(self.btn_find_all)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        
        # Результаты
        self.lbl_results = QLabel("Results:")
        layout.addWidget(self.lbl_results)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_result_double_click)
        layout.addWidget(self.results_list)
        
    def on_find(self):
        pattern = self.txt_pattern.text().strip()
        mode = self.cmb_mode.currentText()
        if pattern:
            self.searchRequested.emit(pattern, mode)
            
    def on_find_all(self):
        pattern = self.txt_pattern.text().strip()
        mode = self.cmb_mode.currentText()
        if pattern:
            self.searchRequested.emit(pattern, mode)
            
    def on_result_double_click(self, item):
        # Извлекаем адрес из текста элемента
        text = item.text()
        if ":" in text:
            addr_str = text.split(":")[0].strip()
            try:
                addr = int(addr_str, 16)
                self.parent().goto_address(addr)
            except ValueError:
                pass
                
    def show_results(self, results):
        """Отображает результаты поиска"""
        self.results_list.clear()
        for addr, matched_bytes in results:
            bytes_str = " ".join(f"{b:02X}" for b in matched_bytes)
            self.results_list.addItem(QListWidgetItem(f"{addr:04X}: {bytes_str}"))

class AutomationAPI:
    """API для автоматизации работы с программой из скриптов
    
    Разделение методов:
    - read_mem, write_mem, ... — работа с ЛОКАЛЬНЫМ образом
    - dev_read_mem, dev_write_mem, ... — работа с УСТРОЙСТВОМ
    - download, upload — синхронизация между устройством и локальным образом
    """
    
    def __init__(self, main_window):
        self.mw = main_window
        
    # =============================================
    # ПРОВЕРКИ СОСТОЯНИЯ
    # =============================================
    def _check_connected(self):
        """Проверяет подключение к устройству"""
        if not self.mw.is_connected:
            raise RuntimeError("Device not connected!")
            
    def _check_bus(self):
        """Проверяет подключение и захват шины"""
        self._check_connected()
        if not self.mw.bus_active:
            raise RuntimeError("Bus not active! Call hold_bus() and wait_bus() first.")
        return True
        
    # =============================================
    # УПРАВЛЕНИЕ ШИНОЙ
    # =============================================
    def hold_bus(self):
        """Захватить шину. Возвращает True, если команда отправлена."""
        self._check_connected()
        if self.mw.bus_active:
            return True
        self.mw.send_command(bytes([CMD_HOLD]))
        return True
        
    def unhold_bus(self):
        """Освободить шину. Возвращает True, если команда отправлена."""
        self._check_connected()
        if not self.mw.bus_active:
            return True
        self.mw.send_command(bytes([CMD_UNHOLD]))
        return True
        
    def wait_bus(self, timeout=5.0):
        """Ждёт захвата шины. Возвращает True, если шина захвачена."""
        start = time.time()
        while time.time() - start < timeout:
            if self.mw.bus_active:
                return True
            time.sleep(0.05)
            QApplication.processEvents()
        return False
        
    def wait_unhold(self, timeout=5.0):
        """Ждёт освобождения шины. Возвращает True, если шина освобождена."""
        start = time.time()
        while time.time() - start < timeout:
            if not self.mw.bus_active:
                return True
            time.sleep(0.05)
            QApplication.processEvents()
        return False
        
    # =============================================
    # ЛОКАЛЬНАЯ ПАМЯТЬ (не требует подключения)
    # =============================================
    def read_mem(self, addr):
        """Прочитать байт из локального образа"""
        return self.mw.mem_data.get(addr, None)
        
    def write_mem(self, addr, val):
        """Записать байт в локальный образ"""
        self.mw.mem_data[addr] = val & 0xFF
        self.mw.hex_model.update_data({addr: val & 0xFF})
        
    def read_block(self, addr, size):
        """Прочитать блок из локального образа"""
        return [self.mw.mem_data.get(addr + i, None) for i in range(size)]
        
    def write_block(self, addr, data):
        """Записать блок в локальный образ"""
        changes = {addr + i: data[i] & 0xFF for i in range(len(data))}
        self.mw.mem_data.update(changes)
        self.mw.hex_model.update_data(changes)
        
    def fill_mem(self, addr, size, val):
        """Заполнить диапазон в локальном образе"""
        changes = {addr + i: val & 0xFF for i in range(size)}
        self.mw.mem_data.update(changes)
        self.mw.hex_model.update_data(changes)
        
    # =============================================
    # ПАМЯТЬ УСТРОЙСТВА (требует шину)
    # =============================================
    def dev_read_mem(self, addr):
        """Прочитать байт из памяти УСТРОЙСТВА"""
        self._check_bus()
        payload = bytes([CMD_MEM_READ_BYTE, (addr >> 8) & 0xFF, addr & 0xFF])
        resp = self.mw.sync_send_and_recv(payload)
        if resp and resp[0] == ACK_MEM_READ_BYTE and len(resp) >= 4:
            return resp[3]
        return None
        
    def dev_write_mem(self, addr, val):
        """Записать байт в память УСТРОЙСТВА"""
        self._check_bus()
        payload = bytes([CMD_MEM_WRITE_BYTE, (addr >> 8) & 0xFF, addr & 0xFF, val & 0xFF])
        resp = self.mw.sync_send_and_recv(payload)
        return resp is not None and resp[0] == ACK_MEM_WRITE_BYTE
        
    def dev_read_io(self, port):
        """Прочитать из IO-порта УСТРОЙСТВА"""
        self._check_bus()
        payload = bytes([CMD_IO_READ_BYTE, (port >> 8) & 0xFF, port & 0xFF])
        resp = self.mw.sync_send_and_recv(payload)
        if resp and resp[0] == ACK_IO_READ_BYTE and len(resp) >= 4:
            return resp[3]
        return None
        
    def dev_write_io(self, port, val):
        """Записать в IO-порт УСТРОЙСТВА"""
        self._check_bus()
        payload = bytes([CMD_IO_WRITE_BYTE, (port >> 8) & 0xFF, port & 0xFF, val & 0xFF])
        resp = self.mw.sync_send_and_recv(payload)
        return resp is not None and resp[0] == ACK_IO_WRITE_BYTE
        
    # =============================================
    # СИНХРОНИЗАЦИЯ (устройство ↔ локальный образ)
    # =============================================
    def download(self, addr, size):
        """Считать блок из УСТРОЙСТВА в локальный образ
        
        Возвращает список прочитанных байтов или None при ошибке.
        """
        self._check_bus()
        
        result = []
        remaining = size
        current_addr = addr
        
        while remaining > 0:
            chunk_size = min(remaining, self.mw.max_block_size)
            payload = bytes([CMD_MEM_READ_BLOCK, chunk_size & 0xFF, 
                           (current_addr >> 8) & 0xFF, current_addr & 0xFF])
            resp = self.mw.sync_send_and_recv(payload)
            
            if resp and resp[0] == ACK_MEM_READ_BLOCK:
                for i in range(resp[1]):
                    if 3 + i < len(resp):
                        val = resp[3 + i]
                        result.append(val)
                        self.mw.mem_data[current_addr + i] = val
            else:
                self.mw.log(f"Download error at 0x{current_addr:04X}")
                return None
                
            current_addr += chunk_size
            remaining -= chunk_size
            
        # Обновляем hex-редактор
        self.mw.hex_model.update_data(self.mw.mem_data)
        self.mw.update_range_label()
        if self.mw.auto_disasm_check.isChecked():
            self.mw.auto_disasm()
            
        return result
        
    def upload(self, addr, size):
        """Записать блок из локального образа в УСТРОЙСТВО
        
        Возвращает True при успехе.
        """
        self._check_bus()
        
        remaining = size
        current_addr = addr
        
        while remaining > 0:
            chunk_size = min(remaining, self.mw.max_block_size)
            chunk_data = [self.mw.mem_data.get(current_addr + i, 0xFF) for i in range(chunk_size)]
            
            cmd = bytearray([CMD_MEM_WRITE_BLOCK, chunk_size & 0xFF,
                           (current_addr >> 8) & 0xFF, current_addr & 0xFF])
            cmd.extend(chunk_data)
            
            resp = self.mw.sync_send_and_recv(bytes(cmd))
            if not resp or resp[0] != ACK_MEM_WRITE_BLOCK:
                self.mw.log(f"Upload error at 0x{current_addr:04X}")
                return False
                
            current_addr += chunk_size
            remaining -= chunk_size
            
        return True
        
    def download_all(self, start=0x0000, end=0xFFFF):
        """Считать всю память устройства в локальный образ"""
        return self.download(start, end - start + 1)
        
    def upload_all(self):
        """Записать весь локальный образ в память устройства"""
        if not self.mw.mem_data:
            return False
        mn = min(self.mw.mem_data.keys())
        mx = max(self.mw.mem_data.keys())
        return self.upload(mn, mx - mn + 1)
        
    # =============================================
    # ФАЙЛЫ
    # =============================================
    def load_file(self, path, base_addr=0):
        """Загрузить файл в локальный образ"""
        loaded_mem = {}
        if path.endswith(".hex"):
            with open(path, "r") as f:
                loaded_mem = IntelHex.parse(f.read())
        else:
            with open(path, "rb") as f:
                data = f.read()
                for i, b in enumerate(data):
                    loaded_mem[base_addr + i] = b
                    
        self.mw.mem_data.update(loaded_mem)
        self.mw.hex_model.update_data(loaded_mem)
        self.mw.update_range_label()
        return len(loaded_mem)
        
    def save_file(self, path):
        """Сохранить локальный образ в файл"""
        if not self.mw.mem_data:
            return False
        if path.endswith(".hex"):
            with open(path, "w") as f:
                f.write(IntelHex.generate(self.mw.mem_data))
        else:
            mn, mx = min(self.mw.mem_data.keys()), max(self.mw.mem_data.keys())
            with open(path, "wb") as f:
                for i in range(mn, mx + 1):
                    f.write(bytes([self.mw.mem_data.get(i, 0xFF)]))
        return True
        
    # =============================================
    # ДИЗАССЕМБЛЕР И ПОИСК (локально)
    # =============================================
    def disassemble(self, addr=None, length=None, show=False):
        """Дизассемблировать локальный образ.
        
        Args:
            addr: начальный адрес (по умолчанию — минимальный адрес в памяти)
            length: длина (по умолчанию — вся память)
            show: если True, обновляет окно дизассемблера в GUI
        
        Returns:
            Список строк дизассемблированного кода.
        """
        if not self.mw.mem_data:
            return []
            
        if addr is None:
            addr = min(self.mw.mem_data.keys())
        if length is None:
            length = max(self.mw.mem_data.keys()) - addr + 1
            
        # Дизассемблируем
        lines = self.mw.disassembler.disassemble(self.mw.mem_data, addr, length)
        result = []
        for line_addr, size, asm, undoc, target in lines:
            bytes_str = " ".join(f"{self.mw.mem_data.get(line_addr+k, 0):02X}" for k in range(size))
            result.append(f"{line_addr:04X}  {bytes_str:<12} {asm} {undoc}".strip())
        
        # Обновляем GUI, если запрошено
        if show:
            self.mw.disasm_start.setText(f"{addr:04X}")
            self.mw.disasm_len.setText(f"{length:X}")
            self.mw.disasm_view.set_lines(lines)
            self.mw.tabs.setCurrentWidget(self.mw.tab_disasm)
        
        return result
        
    def search(self, pattern, mode="hex"):
        """Поиск в локальном образе"""
        results = []
        if mode == "hex":
            try:
                pattern_bytes = bytes.fromhex(pattern.replace(" ", ""))
            except ValueError:
                return []
            for addr in sorted(self.mw.mem_data.keys()):
                match = True
                for i, b in enumerate(pattern_bytes):
                    if addr + i not in self.mw.mem_data or self.mw.mem_data[addr + i] != b:
                        match = False
                        break
                if match:
                    results.append(addr)
        elif mode == "ascii":
            pattern_bytes = pattern.encode('ascii')
            for addr in sorted(self.mw.mem_data.keys()):
                match = True
                for i, b in enumerate(pattern_bytes):
                    if addr + i not in self.mw.mem_data or self.mw.mem_data[addr + i] != b:
                        match = False
                        break
                if match:
                    results.append(addr)
        return results
        
    def refresh(self):
        """Принудительно обновить hex-редактор и дизассемблер в GUI"""
        self.mw.hex_model.layoutChanged.emit()
        self.mw.update_range_label()
        # Обновляем дизассемблер, если включено автодизассемблирование
        if self.mw.auto_disasm_check.isChecked() and self.mw.mem_data:
            self.mw.auto_disasm()
		
    # =============================================
    # УТИЛИТЫ
    # =============================================
    def log(self, msg):
        """Вывод в журнал программы"""
        self.mw.log(str(msg))
        
    def status(self):
        """Текущее состояние программы"""
        return {
            "connected": self.mw.is_connected,
            "bus_active": self.mw.bus_active,
            "mem_size": len(self.mw.mem_data),
            "max_block_size": self.mw.max_block_size,
        }
        
    def goto(self, addr):
        """Переход к адресу в hex-редакторе"""
        self.mw.goto_address(addr)

# ==================== РАБОЧИЙ ПОТОК ====================
class BusWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal(dict)
    
    def __init__(self, serial_port, task, params, lang="en", max_block_size=128):
        super().__init__()
        self.ser = serial_port
        self.task = task
        self.params = params
        self.is_running = True
        self.lang = lang
        self.max_block_size = max_block_size

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
        for i in range(0, len(addrs), self.max_block_size):
            if not self.is_running: break
            chunk_addrs = addrs[i:i+self.max_block_size]
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
        for i in range(0, len(addrs), self.max_block_size):
            if not self.is_running: break
            chunk_addrs = addrs[i:i+self.max_block_size]
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
        chunk_size = self.max_block_size
        
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
        
        # ============================================================
        # 1. ЗАГРУЗКА НАСТРОЕК
        # ============================================================
        self.settings = QSettings("8080-5 CI", "8080-5 CI application")
        saved_lang = self.settings.value("language", None)
        saved_theme = self.settings.value("theme", None)
        
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
        
        # ============================================================
        # 2. ИНИЦИАЛИЗАЦИЯ ДАННЫХ (до создания UI)
        # ============================================================
        self.serial_port = None
        self.rx_buffer = bytearray()
        self.mem_data = {}
        self.disassembler = I8080Disassembler()
        self.hex_model = HexModel(self.mem_data)
        
        self.worker = None
        self.worker_thread = None
        self.pending_read = None
        self.is_connected = False
        self.bus_active = False
        self.max_block_size = 128
        
        # === Очередь команд ===
        self.command_queue = []
        self.waiting_response = False
        self.worker_active = False
        
        # === Undo/Redo ===
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_depth = 100
        
        # ============================================================
        # 3. ЭМУЛЯТОР i8080 (до init_ui, так как create_tab_emulator 
        #    обращается к self.emulator)
        # ============================================================
        self.emulator = I8080Emulator(self.mem_data)
        self.emulator.state_changed.connect(self.update_emulator_ui)
        self.emulator.log_message.connect(self.log)
        
        # ============================================================
        # 4. СОЗДАНИЕ UI
        # ============================================================
        self.init_ui()
        
        # ============================================================
        # 5. СТАТУСНАЯ СТРОКА (после init_ui)
        # ============================================================
        self.statusBar = self.statusBar()
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
        
        # ============================================================
        # 6. MCP SERVER (после инициализации данных и UI)
        # ============================================================
        self._automation_api = AutomationAPI(self)
        self.mcp_server = None
        if MCP_AVAILABLE:
            try:
                self.mcp_server = MCPServerManager(self, host="127.0.0.1", port=8000)
            except Exception as e:
                self.log(f"MCP Server initialization failed: {e}")
        
        # ============================================================
        # 7. ЛОКАЛИЗАЦИЯ И ТЕМА
        # ============================================================
        self.retranslate_ui()
        QApplication.instance().setStyleSheet(THEMES[self.current_theme])
        
        # Применяем тему к дизассемблеру
        is_dark = (self.current_theme == "Dark")
        self.disasm_view.set_theme(is_dark)
        
        # ============================================================
        # 8. ТАЙМЕРЫ
        # ============================================================
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.read_serial)
        
        self.disasm_timer = QTimer()
        self.disasm_timer.setSingleShot(True)
        self.disasm_timer.timeout.connect(self.auto_disasm)
        
        # ============================================================
        # 9. ФИНАЛЬНАЯ НАСТРОЙКА
        # ============================================================
        self.update_ui_state()
        self.setup_shortcuts()
        
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
        self.baud_combo.addItems(["9600", "38400", "57600", "115200"])
        self.baud_combo.setCurrentText("9600")
        
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
        self.create_tab_compare()
        self.create_tab_scripts()
        
        self.lbl_log = QLabel()
        main_layout.addWidget(self.lbl_log)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("font-family: Consolas, Courier New, monospace;")
        main_layout.addWidget(self.log_text)
        
        # Подключаем сигнал изменения данных в hex-редакторе
        self.hex_model.dataEdited.connect(self.on_hex_data_changed)
        
        # Эмулятор
        self.create_tab_emulator()
        
    def update_emulator_ui(self):
        """Обновляет UI эмулятора"""
        state = self.emulator.get_state()
        
        # Обновляем регистры
        for reg in ['A', 'B', 'C', 'D', 'E', 'H', 'L']:
            self.reg_labels[reg].setText(f"{state[reg]:02X}")
        for reg in ['SP', 'PC', 'BC', 'DE', 'HL']:
            self.reg_labels[reg].setText(f"{state[reg]:04X}")
            
        # Обновляем флаги
        for flag in ['S', 'Z', 'AC', 'P', 'CY']:
            val = 1 if state['flags'][flag] else 0
            self.flag_labels[flag].setText(f"{flag}: {val}")
            if val:
                self.flag_labels[flag].setStyleSheet("color: red; font-weight: bold;")
            else:
                self.flag_labels[flag].setStyleSheet("color: black;")
                
        # Обновляем статистику
        self.cycles_label.setText(f"Такты: {state['cycles']}")
        status = "Остановлен" if state['halted'] else ("Выполняется" if state['running'] else "Готов")
        self.halted_label.setText(f"Состояние: {status}")
        
        # Обновляем текущую инструкцию
        pc = state['PC']
        opcode = self.mem_data.get(pc, 0x00)
        
        # Получаем дизассемблированную команду
        lines = self.disassembler.disassemble(self.mem_data, pc, 1)
        if lines:
            _, size, asm, undoc, target = lines[0]
            bytes_str = " ".join(f"{self.mem_data.get(pc+i, 0):02X}" for i in range(size))
            self.current_instr_label.setText(
                f"Адрес: {pc:04X}\n"
                f"Опкод: {bytes_str}\n"
                f"Команда: {asm} {undoc}"
            )
        else:
            self.current_instr_label.setText(f"Адрес: {pc:04X}\nОпкод: {opcode:02X}\nКоманда: --")
            
        # Подсвечиваем текущую строку в hex-редакторе
        self.highlight_pc_in_hex(pc)
        
    def highlight_pc_in_hex(self, pc):
        """Подсвечивает текущий PC в hex-редакторе"""
        model = self.hex_model
        if not model or not model.mem:
            return
            
        offset = pc - model.min_addr
        if offset < 0:
            return
        row = offset // 16
        col = (offset % 16) + 1
        
        index = model.index(row, col)
        if index.isValid():
            self.table.scrollTo(index, QTableView.PositionAtCenter)
            
    def emulator_step(self):
        """Пошаговое выполнение"""
        self.emulator.step()
        self.update_emulator_ui()
        
    def emulator_run(self):
        """Выполнение до точки останова"""
        cycles = self.emulator.run(max_cycles=10000)
        self.log(f"Executed {cycles} cycles")
        self.update_emulator_ui()
        
    def set_pc_dialog(self):
        """Диалог установки PC"""
        text, ok = QInputDialog.getText(self, "Set PC", "Address (HEX):")
        if ok:
            try:
                addr = int(text, 16)
                self.emulator.set_pc(addr)
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid address!")
                
    def add_breakpoint_dialog(self):
        """Диалог добавления точки останова"""
        text, ok = QInputDialog.getText(self, "Add Breakpoint", "Address (HEX):")
        if ok:
            try:
                addr = int(text, 16)
                self.emulator.add_breakpoint(addr)
                self.bp_list.addItem(f"0x{addr:04X}")
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid address!")
                
    def clear_breakpoints(self):
        """Очистить все точки останова"""
        self.emulator.breakpoints.clear()
        self.bp_list.clear()
        
    def create_tab_control(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.bus_group = QGroupBox()
        bus_layout = QHBoxLayout()
        self.btn_hold = QPushButton()
        self.btn_unhold = QPushButton()
        #self.btn_hold.clicked.connect(lambda: self.send_command(bytes([CMD_HOLD])))
        #self.btn_unhold.clicked.connect(lambda: self.send_command(bytes([CMD_UNHOLD])))
        self.btn_hold.clicked.connect(self.on_hold_clicked)
        self.btn_unhold.clicked.connect(self.on_unhold_clicked)
        #
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
		
        self.btn_mcp = QPushButton("MCP Server: OFF")
        self.btn_mcp.clicked.connect(self.on_mcp_toggle)
        layout.addWidget(self.btn_mcp)

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
        self.btn_search = QPushButton()
        self.btn_search.clicked.connect(self.show_search_dialog)
        ctrl_layout.addWidget(self.lbl_range)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(self.btn_read_block)
        ctrl_layout.addWidget(self.btn_search)
        layout.addLayout(ctrl_layout)
        
        self.table = HexTableView(self.disassembler, self.mem_data)
        self.table.setModel(self.hex_model)
        
        # === Размеры колонок ===
        # Колонка 0 (Addr): по содержимому
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        # Колонки 1-16 (данные): узкие, фиксированные
        for i in range(1, 17):
            self.table.setColumnWidth(i, 32)
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
        
        # Колонка 17 (ASCII/Текст): растягивается на оставшееся место
        self.table.horizontalHeader().setSectionResizeMode(17, QHeaderView.Stretch)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setFont(QFont("Consolas", 10))
        layout.addWidget(self.table)
        
        # Подключаем сигналы
        self.table.statusUpdate.connect(self.on_status_update)
        self.table.gotoAddress.connect(self.goto_address)
        self.table.editOperation.connect(self.push_undo)
        
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
        
        self.disasm_view = DisasmView(self.mem_data)
        self.disasm_scroll = QScrollArea()
        self.disasm_scroll.setWidget(self.disasm_view)
        self.disasm_scroll.setWidgetResizable(True)
        self.disasm_view.toggleBreakpoint.connect(self.on_toggle_breakpoint)
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

        # Обновляем тему дизассемблера
        is_dark = (self.current_theme == "Dark")
        self.disasm_view.set_theme(is_dark)
        
    def retranslate_ui(self):
        self.setWindowTitle(self.tr("app_title"))
        
        # ============================================================
        # ВЕРХНЯЯ ПАНЕЛЬ
        # ============================================================
        self.lbl_port.setText(self.tr("port"))
        self.lbl_baud.setText(self.tr("baud"))
        self.btn_refresh.setText(self.tr("refresh"))
        self.btn_connect.setText(
            self.tr("connect") if not (self.serial_port and self.serial_port.is_open) 
            else self.tr("disconnect")
        )
        self.lbl_lang.setText(self.tr("language"))
        self.lbl_theme.setText(self.tr("theme"))
        
        # ============================================================
        # ВКЛАДКИ (в порядке создания)
        # ============================================================
        self.tabs.setTabText(0, self.tr("tab_control"))    # Управление
        self.tabs.setTabText(1, self.tr("tab_data"))       # Данные
        self.tabs.setTabText(2, self.tr("tab_hex"))        # Hex Редактор
        self.tabs.setTabText(3, self.tr("tab_disasm"))     # Дизассемблер
        self.tabs.setTabText(4, self.tr("tab_test"))       # Тест Памяти
        self.tabs.setTabText(5, self.tr("tab_io_seq"))     # IO Секвенсор
        self.tabs.setTabText(6, self.tr("tab_compare"))    # Сравнение
        self.tabs.setTabText(7, self.tr("tab_scripts"))    # Скрипты
        self.tabs.setTabText(8, self.tr("tab_emulator"))   # Эмулятор
        
        # ============================================================
        # ВКЛАДКА "УПРАВЛЕНИЕ"
        # ============================================================
        self.bus_group.setTitle(self.tr("bus_control"))
        self.btn_hold.setText(self.tr("hold"))
        self.btn_unhold.setText(self.tr("unhold"))
        self.file_group.setTitle(self.tr("files"))
        self.btn_save.setText(self.tr("save_dump"))
        self.btn_load.setText(self.tr("load_fw"))
        
        # ============================================================
        # ВКЛАДКА "ДАННЫЕ"
        # ============================================================
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
        
        # ============================================================
        # ВКЛАДКА "HEX РЕДАКТОР"
        # ============================================================
        self.btn_read_block.setText(self.tr("read_block"))
        self.btn_search.setText(self.tr("search"))
        self.update_range_label()
        
        # ============================================================
        # ВКЛАДКА "ДИЗАССЕМБЛЕР"
        # ============================================================
        self.lbl_disasm_start.setText(self.tr("start"))
        self.lbl_disasm_len.setText(self.tr("len"))
        self.btn_disasm.setText(self.tr("disasm"))
        self.auto_disasm_check.setText(self.tr("auto_disasm"))
        self.btn_export_disasm.setText(self.tr("export"))
        
        # ============================================================
        # ВКЛАДКА "ТЕСТ ПАМЯТИ"
        # ============================================================
        self.lbl_test_start.setText(self.tr("start"))
        self.lbl_test_end.setText(self.tr("end"))
        self.lbl_test_pattern.setText(self.tr("pattern"))
        self.btn_test.setText(self.tr("start_test"))
        
        # ============================================================
        # ВКЛАДКА "IO СЕКВЕНСОР"
        # ============================================================
        self.single_io_group.setTitle(self.tr("single_io"))
        self.lbl_io_seq_port.setText(self.tr("port_hex"))
        self.lbl_io_seq_data.setText(self.tr("value_hex"))
        self.btn_io_read_single.setText(self.tr("read_in"))
        self.btn_io_write_single.setText(self.tr("write_out"))
        self.seq_group.setTitle(self.tr("io_seq"))
        self.btn_seq_load.setText(self.tr("load_file"))
        self.btn_seq_run.setText(self.tr("run_seq"))
        
        # ============================================================
        # ВКЛАДКА "СРАВНЕНИЕ"
        # ============================================================
        self.btn_load_compare.setText(self.tr("load_compare"))
        self.btn_compare.setText(self.tr("btn_compare"))
        self.btn_export_compare.setText(self.tr("export_report"))
        self.lbl_compare_info.setText(self.tr("no_compare_file"))
        
        # Заголовки таблицы сравнения
        self.compare_table.setHorizontalHeaderLabels([
            self.tr("compare_addr"),
            self.tr("compare_current"),
            self.tr("compare_file"),
            self.tr("compare_status")
        ])
        self.compare_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # ============================================================
        # ВКЛАДКА "СКРИПТЫ"
        # ============================================================
        self.btn_run_script.setText(self.tr("run_script"))
        self.btn_load_script.setText(self.tr("load_script"))
        self.btn_save_script.setText(self.tr("save_script"))
        self.btn_clear_output.setText(self.tr("clear_output"))
        
        # ============================================================
        # ВКЛАДКА "ЭМУЛЯТОР"
        # ============================================================
        self.emulator_retranslate()
        
        # ============================================================
        # ЛОГ
        # ============================================================
        self.lbl_log.setText(self.tr("log"))
        
        # ============================================================
        # ОБНОВЛЕНИЕ ЯЗЫКА МОДЕЛИ
        # ============================================================
        self.hex_model.lang = self.current_lang
        self.hex_model.layoutChanged.emit()
        
    # ==================== ЛОГИКА ====================
    def refresh_ports(self):
        self.port_combo.clear()
        for p in serial.tools.list_ports.comports():
            self.port_combo.addItem(f"{p.device} - {p.description}", p.device)

    def toggle_connection(self):
        if self.serial_port and self.serial_port.is_open:
            # === Отключение ===
            # Очищаем очередь
            self.command_queue.clear()
            self.waiting_response = False
            
            if self.bus_active:
                self.log("Releasing bus before disconnect...")
                try:
                    self.serial_port.write(SlipProtocol.encode(bytes([CMD_UNHOLD])))
                    self.serial_port.flush()
                    time.sleep(0.5)
                except serial.SerialException:
                    pass
            
            self.serial_port.close()
            self.poll_timer.stop()
            self.is_connected = False
            self.bus_active = False
            self.btn_connect.setText(self.tr("connect"))
            self.update_ui_state()
            self.log(self.tr("disconnected"))
        else:
            # === Подключение ===
            port_name = self.port_combo.currentData()
            baud_rate = int(self.baud_combo.currentText())
            if not port_name:
                QMessageBox.warning(self, self.tr("error"), self.tr("err_port"))
                return
            try:
                self.serial_port = serial.Serial(port_name, baud_rate, timeout=0.1, write_timeout=1.0)
                self.serial_port.dtr = False
                self.serial_port.rts = False
                time.sleep(2)
                self.serial_port.reset_input_buffer()
                self.serial_port.reset_output_buffer()
                
                self.poll_timer.start(50)
                self.is_connected = True
                self.bus_active = False
                self.btn_connect.setText(self.tr("disconnect"))
                self.update_ui_state()
                self.log(f"{self.tr('connected')} {port_name} ({baud_rate}).")
                
                # Отправляем команды через очередь (последовательно)
                #self.log(self.tr("test_conn"))
                self.send_command(bytes([CMD_NOP]))
                
                #self.log("Requesting max block size...")
                self.send_command(bytes([CMD_GET_SIZE_SETUP]))
                
            except serial.SerialException as e:
                QMessageBox.critical(self, self.tr("err_connect"), f"{self.tr('err_open')} {port_name}:\n{e}")
                self.serial_port = None
                self.is_connected = False
                self.update_ui_state()
            except Exception as e:
                QMessageBox.critical(self, self.tr("error"), str(e))
                self.is_connected = False
                self.update_ui_state()
				
    def log(self, msg):
        self.log_text.append(msg)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def send_command(self, payload):
        """Добавляет команду в очередь отправки"""
        self.command_queue.append(payload)
        self.process_command_queue()
        
    def process_command_queue(self):
        """Обрабатывает очередь команд"""
        if self.waiting_response or not self.command_queue or self.worker_active:
            return
            
        if not self.serial_port or not self.serial_port.is_open:
            self.command_queue.clear()
            return
            
        payload = self.command_queue.pop(0)
        try:
            # Логируем команду при реальной отправке
            cmd_name = self.get_command_name(payload[0] if payload else 0)
            self.log(f"TX [{cmd_name}] -> {payload.hex(' ').upper()}")
            
            self.serial_port.write(SlipProtocol.encode(payload))
            self.serial_port.flush()
            self.waiting_response = True
            
            QTimer.singleShot(2000, self.on_command_timeout)
        except serial.SerialException as e:
            self.log(f"{self.tr('err_send')} {e}")
            self.waiting_response = False
            self.process_command_queue()
            
    def get_command_name(self, cmd):
        """Возвращает имя команды для лога"""
        names = {
            0x00: "NOP",
            0x01: "HOLD",
            0x02: "UNHOLD",
            0x10: "MEM_R",
            0x11: "MEM_R_BLK",
            0x12: "MEM_W",
            0x13: "MEM_W_BLK",
            0x20: "IO_R",
            0x21: "IO_R_BLK",
            0x22: "IO_W",
            0x23: "IO_W_BLK",
            0x32: "EEPROM_W",
            0x33: "EEPROM_W_BLK",
            0x40: "GET_SIZE",
            0x41: "SET_POLARITY",
        }
        return names.get(cmd, f"CMD_{cmd:02X}")
            
    def on_command_timeout(self):
        """Таймаут ожидания ответа на команду"""
        if self.waiting_response:
            self.log("Command timeout!")
            self.waiting_response = False
            self.process_command_queue()
    	
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
        
        # Определяем, является ли ответ финальным
        is_final = True
        if cmd == CMD_HOLD and len(data) >= 2:
            ack = data[1]
            if ack in [0x00, 0x01]:  # AckHoldWaitLow, AckHoldWaitHigh
                is_final = False
        elif cmd == CMD_UNHOLD and len(data) >= 2:
            ack = data[1]
            if ack == 0xF1:  # AckWaitUnHold
                is_final = False
        
        # === СНАЧАЛА обработка ответа ===
        if cmd == ACK_NOP:
            self.log(f"  [{self.tr('ok')}] {self.tr('conn_est')}")
            
        elif cmd == ACK_GET_SIZE_SETUP and len(data) >= 2:
            self.max_block_size = data[1]
            self.log(f"  [{self.tr('ok')}] Max block size: {self.max_block_size}")
            
        elif cmd == CMD_HOLD and len(data) >= 2:
            ack = data[1]
            if ack == 0x03:
                self.bus_active = True
                self.update_ui_state()
                self.log(f"  [{self.tr('ok')}] Bus HOLD active.")
            elif ack == 0x00:
                self.log(f"  [WAIT] HLDA low...")
            elif ack == 0x01:
                self.log(f"  [WAIT] HLDA high...")
                
        elif cmd == CMD_UNHOLD and len(data) >= 2:
            ack = data[1]
            if ack == 0xF2:
                self.bus_active = False
                self.update_ui_state()
                self.log(f"  [{self.tr('ok')}] Bus UNHOLD. CPU running.")
            elif ack == 0xF1:
                self.log(f"  [WAIT] HLDA high...")
                
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
        
        # === ЗАТЕМ снимаем флаг и отправляем следующую команду ===
        if is_final:
            self.waiting_response = False
            self.process_command_queue()
			
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
        path, _ = QFileDialog.getSaveFileName(self, self.tr("save_as"), "", "Binary (*.bin);;Intel HEX (*.hex)")
        if path:
            if path.endswith(".hex"):
                with open(path, "w") as f: f.write(IntelHex.generate(self.mem_data))
            else:
                mn, mx = min(self.mem_data.keys()), max(self.mem_data.keys())
                with open(path, "wb") as f:
                    for i in range(mn, mx + 1): f.write(bytes([self.mem_data.get(i, 0xFF)]))
            self.log(f"{self.tr('save_as')}: {path}")

    def load_and_flash(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("load_fw_title"), "", "Binary (*.bin);;Intel HEX (*.hex)")
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
        
        # Проверяем состояние перед записью
        if not self.is_connected:
            self.log("Device not connected. Firmware loaded to editor only.")
            return
            
        if not self.bus_active:
            self.log("Bus not active. Hold the bus before flashing.")
            QMessageBox.information(self, "Info", "Hold the bus (HOLD) before flashing.")
            return
        
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
        # Добавляем операцию в undo stack
        if hasattr(self.hex_model, 'last_edit') and self.hex_model.last_edit:
            addr, old_val, new_val = self.hex_model.last_edit
            self.push_undo([(addr, old_val, new_val)])
            self.hex_model.last_edit = None
        
        if self.auto_disasm_check.isChecked() and self.mem_data:
            self.auto_disasm()

    # ==================== БЛОКИ, ТЕСТЫ, IO ====================
    def show_read_block_dialog(self):
        text1, ok1 = QInputDialog.getText(self, self.tr("addr_hex"), "Start Address (HEX):")
        if not ok1: return
        try:
            addr = int(text1, 16)
        except ValueError:
            QMessageBox.warning(self, self.tr("error"), self.tr("err_hex"))
            return
            
        size, ok2 = QInputDialog.getInt(
            self, 
            self.tr("len"), 
            "Size (Dec):", 
            self.max_block_size,  # ← Значение по умолчанию
            1, 
            self.max_block_size   # ← Максимальное значение
        )
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
            self.log(self.tr("err_not_open"))
            QMessageBox.warning(self, self.tr("error"), self.tr("err_not_open"))
            return
            
        bus_required = ["read_block", "write_block", "test_mem", 
                        "read_io_block", "write_io_block", "run_io_sequence"]
        if task in bus_required and not self.bus_active:
            self.log("Bus not active! Hold the bus first.")
            QMessageBox.warning(self, self.tr("error"), "Bus not active! Hold the bus first.")
            return
            
        # Блокируем очередь на время работы worker
        self.worker_active = True
            
        self.worker_thread = QThread()
        self.worker = BusWorker(self.serial_port, task, params, 
                                self.current_lang, self.max_block_size)
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
        # Разблокируем очередь
        self.worker_active = False
        self.process_command_queue()
        
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

    def show_search_dialog(self):
        """Показывает диалог поиска"""
        if not hasattr(self, 'search_dialog'):
            self.search_dialog = SearchDialog(self)
            self.search_dialog.searchRequested.connect(self.perform_search)
        self.search_dialog.show()
        
    def perform_search(self, pattern, mode):
        """Выполняет поиск в памяти"""
        results = []
        
        if mode == "HEX Bytes":
            # Парсим HEX-паттерн
            try:
                pattern_bytes = bytes.fromhex(pattern.replace(" ", ""))
            except ValueError:
                QMessageBox.warning(self, self.tr("error"), "Invalid HEX pattern!")
                return
                
            for addr in sorted(self.mem_data.keys()):
                match = True
                matched = []
                for i, b in enumerate(pattern_bytes):
                    if addr + i not in self.mem_data or self.mem_data[addr + i] != b:
                        match = False
                        break
                    matched.append(b)
                if match:
                    results.append((addr, matched))
                    
        elif mode == "ASCII String":
            # Ищем ASCII-строку
            pattern_bytes = pattern.encode('ascii')
            for addr in sorted(self.mem_data.keys()):
                match = True
                matched = []
                for i, b in enumerate(pattern_bytes):
                    if addr + i not in self.mem_data or self.mem_data[addr + i] != b:
                        match = False
                        break
                    matched.append(b)
                if match:
                    results.append((addr, matched))
                    
        elif mode == "HEX with Mask (??)":
            # Парсим паттерн с маской
            parts = pattern.replace(" ", "").upper()
            if len(parts) % 2 != 0:
                QMessageBox.warning(self, self.tr("error"), "Invalid pattern length!")
                return
                
            pattern_list = []
            for i in range(0, len(parts), 2):
                byte_str = parts[i:i+2]
                if byte_str == "??":
                    pattern_list.append(None)
                else:
                    try:
                        pattern_list.append(int(byte_str, 16))
                    except ValueError:
                        QMessageBox.warning(self, self.tr("error"), f"Invalid byte: {byte_str}")
                        return
                        
            for addr in sorted(self.mem_data.keys()):
                match = True
                matched = []
                for i, pb in enumerate(pattern_list):
                    if addr + i not in self.mem_data:
                        match = False
                        break
                    if pb is not None and self.mem_data[addr + i] != pb:
                        match = False
                        break
                    matched.append(self.mem_data[addr + i])
                if match:
                    results.append((addr, matched))
                    
        # Отображаем результаты
        if hasattr(self, 'search_dialog'):
            self.search_dialog.show_results(results)
            
        self.statusBar.showMessage(f"Found {len(results)} matches", 3000)
        
    def goto_address(self, addr):
        """Переход к адресу в hex-редакторе"""
        model = self.hex_model
        if not model or not model.mem:
            return
            
        # Вычисляем row и col
        offset = addr - model.min_addr
        if offset < 0:
            return
        row = offset // 16
        col = (offset % 16) + 1  # +1 потому что колонка 0 - адрес
        
        index = model.index(row, col)
        if index.isValid():
            self.table.setCurrentIndex(index)
            self.table.scrollTo(index, QTableView.PositionAtCenter)
            self.tabs.setCurrentWidget(self.tab_hex)
            
    def disasm_from_address(self, addr):
        """Дизассемблировать от указанного адреса"""
        self.disasm_start.setText(f"{addr:04X}")
        self.tabs.setCurrentWidget(self.tab_disasm)
        self.run_disasm()
        
    def update_ui_state(self):
        """Обновляет доступность кнопок в зависимости от состояния"""
        connected = self.is_connected
        active = self.bus_active
        
        # Управление шиной
        self.btn_hold.setEnabled(connected and not active)
        self.btn_unhold.setEnabled(connected and active)
        
        # Чтение/запись данных (требуют захвата шины)
        self.btn_mem_read.setEnabled(connected and active)
        self.btn_mem_write.setEnabled(connected and active)
        self.btn_io_read.setEnabled(connected and active)
        self.btn_io_write.setEnabled(connected and active)
        
        # Hex-редактор
        self.btn_read_block.setEnabled(connected and active)
        
        # IO
        self.btn_io_read_single.setEnabled(connected and active)
        self.btn_io_write_single.setEnabled(connected and active)
        self.btn_seq_run.setEnabled(connected and active)
        
        # Тест памяти
        self.btn_test.setEnabled(connected and active)
        
        # Статусная строка
        if not connected:
            self.status_label_conn.setText(self.tr("disconnected"))
        elif active:
            self.status_label_conn.setText(f"{self.tr('connected')} | BUS ACTIVE")
        else:
            self.status_label_conn.setText(f"{self.tr('connected')} | BUS FREE")
			
    def closeEvent(self, event):
        """Освобождение шины при закрытии программы"""
        # Очищаем очередь
        self.command_queue.clear()
        self.waiting_response = False
        
        if self.serial_port and self.serial_port.is_open and self.bus_active:
            self.log("Releasing bus before exit...")
            try:
                self.serial_port.write(SlipProtocol.encode(bytes([CMD_UNHOLD])))
                self.serial_port.flush()
                time.sleep(0.5)
            except serial.SerialException:
                pass
                
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
			
        # Останавливаем MCP Server
        if self.mcp_server is not None and self.mcp_server.running:
            self.mcp_server.stop()
            
        event.accept()
		
    def on_hold_clicked(self):
        if not self.is_connected: 
            self.statusBar.showMessage("Not connected!", 2000)
            return
        if self.bus_active:
            self.statusBar.showMessage("Bus already active!", 2000)
            return
        self.send_command(bytes([CMD_HOLD]))
        self.btn_hold.setEnabled(False)
        
    def on_unhold_clicked(self):
        if not self.is_connected:
            self.statusBar.showMessage("Not connected!", 2000)
            return
        if not self.bus_active:
            self.statusBar.showMessage("Bus not active!", 2000)
            return
        self.send_command(bytes([CMD_UNHOLD]))
        self.btn_unhold.setEnabled(False)
        
    def toggle_mcp_server(self):
        """Включить/выключить MCP Server"""
        if self.mcp_server.running:
            self.mcp_server.stop()
        else:
            self.mcp_server.start()
        
    def setup_shortcuts(self):		
        """Настройка горячих клавиш"""
        # Файл
        QShortcut(QKeySequence("Ctrl+O"), self, self.load_and_flash)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_dump)
        QShortcut(QKeySequence("Ctrl+E"), self, self.export_disasm)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        
        # Поиск и навигация
        QShortcut(QKeySequence("Ctrl+F"), self, self.show_search_dialog)
        QShortcut(QKeySequence("Ctrl+G"), self, self.show_goto_dialog)
        
        # Дизассемблер
        QShortcut(QKeySequence("Ctrl+D"), self, self.run_disasm)
        
        # Устройство
        QShortcut(QKeySequence("Ctrl+H"), self, self.on_hold_clicked)
        QShortcut(QKeySequence("Ctrl+U"), self, self.on_unhold_clicked)
        
        # Обновление
        QShortcut(QKeySequence("F5"), self, self.refresh_all)
		
        # Undo/Redo
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self.redo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, self.redo)
		
        # Эмулятор (как в CodeWarrior)
        QShortcut(QKeySequence("F5"), self, self.emulator_run)
        QShortcut(QKeySequence("F10"), self, self.emulator_step_over)
        QShortcut(QKeySequence("F11"), self, self.emulator_step_into)
        QShortcut(QKeySequence("Shift+F5"), self, self.emulator_stop)
        QShortcut(QKeySequence("Ctrl+F2"), self, self.emulator_reset)
		
    def show_goto_dialog(self):
        """Диалог перехода к адресу (Ctrl+G)"""
        text, ok = QInputDialog.getText(self, self.tr("goto_addr"), "Address (HEX):")
        if not ok: return
        try:
            addr = int(text, 16)
            self.goto_address(addr)
        except ValueError:
            QMessageBox.warning(self, self.tr("error"), self.tr("err_hex"))
            
    def refresh_all(self):
        """Обновление всех данных (F5)"""
        self.hex_model.layoutChanged.emit()
        if self.auto_disasm_check.isChecked():
            self.auto_disasm()
        self.update_range_label()
        self.statusBar.showMessage("Refreshed", 2000)

    def push_undo(self, changes):
        """Добавляет операцию в стек undo"""
        if not changes: return
        self.undo_stack.append(changes)
        if len(self.undo_stack) > self.max_undo_depth:
            self.undo_stack.pop(0)
        self.redo_stack.clear()  # Очищаем redo при новом изменении
        self.statusBar.showMessage(f"Undo depth: {len(self.undo_stack)}", 2000)
        
    def undo(self):
        """Отмена последнего изменения (Ctrl+Z)"""
        if not self.undo_stack:
            self.statusBar.showMessage("Nothing to undo", 2000)
            return
        changes = self.undo_stack.pop()
        for addr, old_val, new_val in changes:
            self.mem_data[addr] = old_val
        self.redo_stack.append(changes)
        self.hex_model.update_data(self.mem_data)
        if self.auto_disasm_check.isChecked():
            self.auto_disasm()
        self.statusBar.showMessage(f"Undo: {len(changes)} bytes", 2000)
        
    def redo(self):
        """Повтор последнего изменения (Ctrl+Y)"""
        if not self.redo_stack:
            self.statusBar.showMessage("Nothing to redo", 2000)
            return
        changes = self.redo_stack.pop()
        for addr, old_val, new_val in changes:
            self.mem_data[addr] = new_val
        self.undo_stack.append(changes)
        self.hex_model.update_data(self.mem_data)
        if self.auto_disasm_check.isChecked():
            self.auto_disasm()
        self.statusBar.showMessage(f"Redo: {len(changes)} bytes", 2000)
		
    def create_tab_compare(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Кнопки управления
        ctrl_layout = QHBoxLayout()
        self.btn_load_compare = QPushButton()
        self.btn_load_compare.clicked.connect(self.load_compare_file)
        self.btn_compare = QPushButton()
        self.btn_compare.clicked.connect(self.run_compare)
        self.btn_export_compare = QPushButton()
        self.btn_export_compare.clicked.connect(self.export_compare_report)
        ctrl_layout.addWidget(self.btn_load_compare)
        ctrl_layout.addWidget(self.btn_compare)
        ctrl_layout.addWidget(self.btn_export_compare)
        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)
        
        # Информация о сравнении
        self.lbl_compare_info = QLabel()
        layout.addWidget(self.lbl_compare_info)
        
        # Таблица результатов
        self.compare_table = QTableWidget()
        self.compare_table.setColumnCount(4)
        self.compare_table.setFont(QFont("Consolas", 10))
        layout.addWidget(self.compare_table)
        
        self.compare_data = None
        self.compare_results = []
        
        self.tabs.addTab(tab, "")
        self.tab_compare = tab
	
    def load_compare_file(self):
        """Загружает файл для сравнения"""
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("load_compare_title"), "", 
            "Intel HEX (*.hex);;Binary (*.bin);;All Files (*)"
        )
        if not path: return
        
        loaded_mem = {}
        if path.endswith(".hex"):
            with open(path, "r") as f:
                loaded_mem = IntelHex.parse(f.read())
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
                for i, b in enumerate(data):
                    loaded_mem[base + i] = b
                    
        self.compare_data = loaded_mem
        self.lbl_compare_info.setText(f"{self.tr('compare_loaded')}: {path} ({len(loaded_mem)} {self.tr('bytes')})")
        self.log(f"Compare file loaded: {path} ({len(loaded_mem)} bytes)")
        
    def run_compare(self):
        """Выполняет сравнение текущего дампа с загруженным файлом"""
        if not self.compare_data:
            QMessageBox.warning(self, self.tr("error"), self.tr("load_compare"))
            return
            
        if not self.mem_data:
            QMessageBox.warning(self, self.tr("error"), self.tr("err_no_data"))
            return
        
        # Сравниваем
        all_addrs = set(self.mem_data.keys()) | set(self.compare_data.keys())
        self.compare_results = []
        
        for addr in sorted(all_addrs):
            val_current = self.mem_data.get(addr)
            val_file = self.compare_data.get(addr)
            
            if val_current is None:
                status_key = "status_added"  # ← Ключ для перевода
            elif val_file is None:
                status_key = "status_removed"  # ← Ключ для перевода
            elif val_current != val_file:
                status_key = "status_changed"  # ← Ключ для перевода
            else:
                continue  # Одинаковые — пропускаем
                
            self.compare_results.append((addr, val_current, val_file, status_key))
            
        # Отображаем результаты
        self.show_compare_results()
        
    def show_compare_results(self):
        """Отображает результаты сравнения в таблице"""
        self.compare_table.setRowCount(len(self.compare_results))
        
        for row, (addr, val_cur, val_file, status_key) in enumerate(self.compare_results):
            # Адрес
            item_addr = QTableWidgetItem(f"{addr:04X}")
            self.compare_table.setItem(row, 0, item_addr)
            
            # Текущее значение
            cur_str = f"{val_cur:02X}" if val_cur is not None else "--"
            item_cur = QTableWidgetItem(cur_str)
            self.compare_table.setItem(row, 1, item_cur)
            
            # Значение из файла
            file_str = f"{val_file:02X}" if val_file is not None else "--"
            item_file = QTableWidgetItem(file_str)
            self.compare_table.setItem(row, 2, item_file)
            
            # Статус (переведённый)
            status_text = self.tr(status_key)  # ← Переводим статус
            item_status = QTableWidgetItem(status_text)
            self.compare_table.setItem(row, 3, item_status)
            
            # Подсветка в зависимости от статуса
            if status_key == "status_changed":
                color = QColor("#fff3cd")  # Жёлтый
            elif status_key == "status_added":
                color = QColor("#d4edda")  # Зелёный
            elif status_key == "status_removed":
                color = QColor("#f8d7da")  # Красный
            else:
                color = None
                
            if color:
                for col in range(4):
                    item = self.compare_table.item(row, col)
                    if item:
                        item.setBackground(color)
                        
        self.statusBar.showMessage(
            f"{self.tr('compare_complete')}: {len(self.compare_results)} {self.tr('compare_found')}", 
            3000
        )
        self.log(f"Compare complete: {len(self.compare_results)} differences")
        
    def export_compare_report(self):
        """Экспортирует отчёт о сравнении"""
        if not self.compare_results:
            QMessageBox.warning(self, self.tr("error"), self.tr("run_compare_first"))
            return
            
        path, _ = QFileDialog.getSaveFileName(
            self, self.tr("export_compare_title"), "", 
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
        )
        if not path: return
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"{self.tr('compare_addr')},{self.tr('compare_current')},"
                        f"{self.tr('compare_file')},{self.tr('compare_status')}\n")
                for addr, val_cur, val_file, status_key in self.compare_results:
                    cur_str = f"{val_cur:02X}" if val_cur is not None else "--"
                    file_str = f"{val_file:02X}" if val_file is not None else "--"
                    status_text = self.tr(status_key)
                    f.write(f"{addr:04X},{cur_str},{file_str},{status_text}\n")
            self.log(f"{self.tr('compare_exported')}: {path}")
            self.statusBar.showMessage(f"{self.tr('compare_exported')}: {path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), str(e))

    def create_tab_scripts(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.btn_run_script = QPushButton("▶ Run Script")
        self.btn_run_script.clicked.connect(self.run_script)
        self.btn_load_script = QPushButton("Load Script")
        self.btn_load_script.clicked.connect(self.load_script_file)
        self.btn_save_script = QPushButton("Save Script")
        self.btn_save_script.clicked.connect(self.save_script_file)
        self.btn_clear_output = QPushButton("Clear Output")
        self.btn_clear_output.clicked.connect(lambda: self.script_output.clear())
        btn_layout.addWidget(self.btn_run_script)
        btn_layout.addWidget(self.btn_load_script)
        btn_layout.addWidget(self.btn_save_script)
        btn_layout.addWidget(self.btn_clear_output)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Редактор кода
        self.script_editor = QTextEdit()
        self.script_editor.setFont(QFont("Consolas", 10))
        self.script_editor.setPlaceholderText(
            "# Example script:\n"
            "# Fill memory with pattern\n"
            "api.fill_mem(0x0000, 256, 0x55)\n"
            "# Disassemble\n"
            "for line in api.disassemble(0x0000, 16):\n"
            "    print(line)\n"
            "# Search\n"
            "results = api.search('C3', 'hex')\n"
            "print(f'Found {len(results)} JMP instructions')"
        )
        layout.addWidget(self.script_editor)
        
        # Разделитель
        layout.addWidget(QLabel("Output:"))
        
        # Вывод
        self.script_output = QTextEdit()
        self.script_output.setReadOnly(True)
        self.script_output.setMaximumHeight(200)
        self.script_output.setFont(QFont("Consolas", 9))
        layout.addWidget(self.script_output)
        
        self.tabs.addTab(tab, "")
        self.tab_scripts = tab

    def run_script(self):
        """Выполняет скрипт из редактора"""
        code = self.script_editor.toPlainText()
        if not code.strip():
            self.script_output.append("No code to run.")
            return
            
        self.script_output.clear()
        self.script_output.append("Running script...")
        
        # Создаём API
        api = AutomationAPI(self)
        
        # Пространство имён для скрипта
        namespace = {
            'api': api,
            # Локальная память
            'read_mem': api.read_mem,
            'write_mem': api.write_mem,
            'read_block': api.read_block,
            'write_block': api.write_block,
            'fill_mem': api.fill_mem,
            # Память устройства
            'dev_read_mem': api.dev_read_mem,
            'dev_write_mem': api.dev_write_mem,
            'dev_read_io': api.dev_read_io,
            'dev_write_io': api.dev_write_io,
            # Синхронизация
            'download': api.download,
            'upload': api.upload,
            'download_all': api.download_all,
            'upload_all': api.upload_all,
            # Шина
            'hold_bus': api.hold_bus,
            'unhold_bus': api.unhold_bus,
            'wait_bus': api.wait_bus,
            'wait_unhold': api.wait_unhold,
            # Файлы
            'load_file': api.load_file,
            'save_file': api.save_file,
            # Утилиты
            'disassemble': api.disassemble,
            'refresh': api.refresh,
            'search': api.search,
            'log': api.log,
            'status': api.status,
            'goto': api.goto,
        }
        
        try:
            # Перенаправляем stdout
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            # Выполняем код
            exec(code, namespace)
            
            # Получаем вывод
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            if output:
                self.script_output.append(output.rstrip())
            self.script_output.append("\n✓ Script completed successfully.")
            self.statusBar.showMessage("Script completed", 3000)
            
        except Exception as e:
            sys.stdout = old_stdout
            self.script_output.append(f"\n✗ ERROR: {str(e)}")
            import traceback
            self.script_output.append(traceback.format_exc())
            self.statusBar.showMessage("Script error!", 3000)
            
    def load_script_file(self):
        """Загружает скрипт из файла"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Script", "", 
            "Python Scripts (*.py);;Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.script_editor.setPlainText(f.read())
                self.statusBar.showMessage(f"Script loaded: {path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, self.tr("error"), str(e))
                
    def save_script_file(self):
        """Сохраняет скрипт в файл"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Script", "", 
            "Python Scripts (*.py);;Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.script_editor.toPlainText())
                self.statusBar.showMessage(f"Script saved: {path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, self.tr("error"), str(e))

    def sync_send_and_recv(self, payload, timeout=2.0):
        """Синхронная отправка команды и ожидание ответа"""
        if not self.serial_port or not self.serial_port.is_open:
            return None
            
        # Останавливаем poll_timer, чтобы избежать конфликта
        self.poll_timer.stop()
        
        try:
            self.serial_port.write(SlipProtocol.encode(payload))
            self.serial_port.flush()
            
            buffer = bytearray()
            start_time = time.time()
            while time.time() - start_time < timeout:
                QApplication.processEvents()  # Обрабатываем события UI
                try:
                    if self.serial_port.in_waiting:
                        buffer.extend(self.serial_port.read(self.serial_port.in_waiting))
                        if _FEND in buffer:
                            end_idx = buffer.index(_FEND)
                            if end_idx > 0:
                                raw = buffer[:end_idx]
                                self.serial_port.reset_input_buffer()
                                return SlipProtocol.decode(raw)
                except serial.SerialException:
                    return None
                time.sleep(0.01)
            return None
        finally:
            # Запускаем poll_timer снова
            self.poll_timer.start(50)
			
    def on_mcp_toggle(self):
        if not MCP_AVAILABLE or self.mcp_server is None:
            QMessageBox.warning(self, "MCP", "MCP Server недоступен. Установите зависимости:\npip install mcp uvicorn starlette")
            return
            
        if self.mcp_server.running:
            self.mcp_server.stop()
            self.btn_mcp.setText("MCP Server: OFF")
        else:
            self.mcp_server.start()
            self.btn_mcp.setText("MCP Server: ON")
			
    def create_tab_emulator(self):
        """Создаёт вкладку эмулятора"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # =============================================
        # ЛЕВАЯ ЧАСТЬ: Регистры и флаги
        # =============================================
        left_layout = QVBoxLayout()
        
        # Регистры
        self.reg_group = QGroupBox("Registers")
        reg_layout = QGridLayout()
        
        self.reg_labels = {}
        regs = ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'SP', 'PC']
        for i, reg in enumerate(regs):
            reg_layout.addWidget(QLabel(f"{reg}:"), i, 0)
            lbl = QLabel("0000" if reg in ['SP', 'PC'] else "00")
            lbl.setFont(QFont("Consolas", 11))
            lbl.setStyleSheet("background-color: #f0f0f0; padding: 3px; border: 1px solid #ccc;")
            reg_layout.addWidget(lbl, i, 1)
            self.reg_labels[reg] = lbl
            
        # Пары регистров
        pairs = ['BC', 'DE', 'HL']
        for i, pair in enumerate(pairs):
            reg_layout.addWidget(QLabel(f"{pair}:"), i + len(regs), 0)
            lbl = QLabel("0000")
            lbl.setFont(QFont("Consolas", 11))
            lbl.setStyleSheet("background-color: #f0f0f0; padding: 3px; border: 1px solid #ccc;")
            reg_layout.addWidget(lbl, i + len(regs), 1)
            self.reg_labels[pair] = lbl
            
        self.reg_group.setLayout(reg_layout)
        left_layout.addWidget(self.reg_group)
        
        # Флаги
        self.flags_group = QGroupBox("Flags")
        flags_layout = QHBoxLayout()
        
        self.flag_labels = {}
        flags = ['S', 'Z', 'AC', 'P', 'CY']
        for flag in flags:
            lbl = QLabel(f"{flag}: 0")
            lbl.setFont(QFont("Consolas", 10))
            flags_layout.addWidget(lbl)
            self.flag_labels[flag] = lbl
            
        self.flags_group.setLayout(flags_layout)
        left_layout.addWidget(self.flags_group)
        
        # Статистика
        self.stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.cycles_label = QLabel("Cycles: 0")
        self.halted_label = QLabel("State: Halted")
        stats_layout.addWidget(self.cycles_label)
        stats_layout.addWidget(self.halted_label)
        
        self.stats_group.setLayout(stats_layout)
        left_layout.addWidget(self.stats_group)
        
        left_layout.addStretch()
        
        # =============================================
        # ПРАВАЯ ЧАСТЬ: Управление
        # =============================================
        right_layout = QVBoxLayout()
        
        # Кнопки управления (все как self.атрибуты)
        self.ctrl_group = QGroupBox("Control")
        ctrl_layout = QVBoxLayout()
        
        # Ряд 1: Reset / Set PC
        btn_row1 = QHBoxLayout()
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.emulator_reset)
        self.btn_set_pc = QPushButton("Set PC...")
        self.btn_set_pc.clicked.connect(self.set_pc_dialog)
        btn_row1.addWidget(self.btn_reset)
        btn_row1.addWidget(self.btn_set_pc)
        ctrl_layout.addLayout(btn_row1)
        
        # Ряд 2: Step Into / Step Over
        btn_row2 = QHBoxLayout()
        self.btn_step_into = QPushButton("Step Into (F11)")
        self.btn_step_into.clicked.connect(self.emulator_step_into)
        self.btn_step_over = QPushButton("Step Over (F10)")
        self.btn_step_over.clicked.connect(self.emulator_step_over)
        btn_row2.addWidget(self.btn_step_into)
        btn_row2.addWidget(self.btn_step_over)
        ctrl_layout.addLayout(btn_row2)
        
        # Ряд 3: Run / Stop
        btn_row3 = QHBoxLayout()
        self.btn_run = QPushButton("▶ Run (F5)")
        self.btn_run.clicked.connect(self.emulator_run)
        self.btn_stop = QPushButton("■ Stop")
        self.btn_stop.clicked.connect(self.emulator_stop)
        btn_row3.addWidget(self.btn_run)
        btn_row3.addWidget(self.btn_stop)
        ctrl_layout.addLayout(btn_row3)
        
        self.ctrl_group.setLayout(ctrl_layout)
        right_layout.addWidget(self.ctrl_group)
        
        # Текущая инструкция
        self.current_instr_group = QGroupBox("Current Instruction")
        instr_layout = QVBoxLayout()
        
        self.current_instr_label = QLabel("Address: 0000\nOpcode: --\nInstruction: --")
        self.current_instr_label.setFont(QFont("Consolas", 10))
        self.current_instr_label.setStyleSheet("background-color: #ffffd0; padding: 10px; border: 1px solid #ccc;")
        instr_layout.addWidget(self.current_instr_label)
        
        self.current_instr_group.setLayout(instr_layout)
        right_layout.addWidget(self.current_instr_group)
        
        # Точки останова
        self.bp_group = QGroupBox("Breakpoints")
        bp_layout = QVBoxLayout()
        
        bp_btn_layout = QHBoxLayout()
        self.btn_add_bp = QPushButton("Add")
        self.btn_add_bp.clicked.connect(self.add_breakpoint_dialog)
        self.btn_clear_bp = QPushButton("Clear All")
        self.btn_clear_bp.clicked.connect(self.clear_breakpoints)
        bp_btn_layout.addWidget(self.btn_add_bp)
        bp_btn_layout.addWidget(self.btn_clear_bp)
        bp_layout.addLayout(bp_btn_layout)
        
        self.bp_list = QListWidget()
        bp_layout.addWidget(self.bp_list)
        
        self.bp_group.setLayout(bp_layout)
        right_layout.addWidget(self.bp_group)
        
        right_layout.addStretch()
        
        # =============================================
        # СБОРКА
        # =============================================
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        
        self.tabs.addTab(tab, "")
        self.tab_emulator = tab
		
    def emulator_reset(self):
        """Сброс эмулятора"""
        self.emulator.reset()
        self.update_emulator_ui()
        # Обновляем подсветку в дизассемблере
        self.disasm_view.set_highlight(self.emulator.pc)
        
    def emulator_step_into(self):
        """Step Into: одна инструкция, заходя в CALL"""
        if self.emulator.halted:
            self.statusBar.showMessage("CPU halted. Press Reset.", 3000)
            return
        self.emulator.step_into()
        self.update_emulator_ui()
        self.update_disasm_highlight()
        
    def emulator_step_over(self):
        """Step Over: выполнить CALL как одну инструкцию"""
        if self.emulator.halted:
            self.statusBar.showMessage("CPU halted. Press Reset.", 3000)
            return
        self.emulator.step_over()
        self.update_emulator_ui()
        self.update_disasm_highlight()
        
    def emulator_run(self):
        """Запуск с обновлением UI через QTimer"""
        if self.emulator.halted:
            self.statusBar.showMessage("CPU halted. Press Reset.", 3000)
            return
        
        # Создаём таймер для периодического выполнения
        if not hasattr(self, 'run_timer'):
            self.run_timer = QTimer()
            self.run_timer.timeout.connect(self._run_tick)
        
        self.emulator.running = True
        self.run_timer.start(20)  # 20 мс между тиками (50 FPS)
        
    def _run_tick(self):
        """Один тик выполнения (вызывается QTimer)"""
        if not self.emulator.running or self.emulator.halted:
            self.run_timer.stop()
            self.emulator.running = False
            self.update_emulator_ui()
            self.update_disasm_highlight()
            return
        
        # Проверяем точки останова
        if self.emulator.pc in self.emulator.breakpoints:
            self.run_timer.stop()
            self.emulator.running = False
            self.emulator.breakpoint_hit.emit(self.emulator.pc)
            self.update_emulator_ui()
            self.update_disasm_highlight()
            return
        
        # Выполняем 10 инструкций за тик
        for _ in range(10):
            if not self.emulator.execute_instruction():
                break
            if self.emulator.pc in self.emulator.breakpoints:
                break
        
        # Обновляем UI
        self.update_emulator_ui()
        self.update_disasm_highlight()
        
    def emulator_stop(self):
        """Остановка выполнения"""
        self.emulator.stop()
        if hasattr(self, 'run_timer'):
            self.run_timer.stop()
        self.update_emulator_ui()
        self.update_disasm_highlight()
        sself.disasm_view.set_breakpoints(self.emulator.breakpoints)
        
    def update_disasm_highlight(self):
        """Обновляет подсветку PC в окне дизассемблера"""
        # Убеждаемся, что дизассемблер показывает актуальный код
        if self.mem_data:
            # Дизассемблируем текущую область
            pc = self.emulator.pc
            start_addr = max(0, pc - 32)
            length = 128
            
            lines = self.disassembler.disassemble(self.mem_data, start_addr, length)
            self.disasm_view.set_lines(lines)
            self.disasm_view.set_highlight(pc)
            
            # Прокручиваем к текущей инструкции
            if pc in self.disasm_view.addr_to_index:
                idx = self.disasm_view.addr_to_index[pc]
                scroll_y = idx * self.disasm_view.line_height
                self.disasm_view.parent().verticalScrollBar().setValue(scroll_y - 100)
		
    def on_toggle_breakpoint(self, addr):
        """Установка/удаление точки останова"""
        if addr in self.emulator.breakpoints:
            self.emulator.remove_breakpoint(addr)
            self.log(f"Breakpoint removed: 0x{addr:04X}")
        else:
            self.emulator.add_breakpoint(addr)
            self.log(f"Breakpoint set: 0x{addr:04X}")
        self.disasm_view.update()
		
    def emulator_retranslate(self):
        """Локализация элементов вкладки эмулятора"""
        # Заголовки групп
        self.reg_group.setTitle(self.tr("emulator_registers"))
        self.flags_group.setTitle(self.tr("emulator_flags"))
        self.stats_group.setTitle(self.tr("emulator_stats"))
        self.ctrl_group.setTitle(self.tr("emulator_control"))
        self.current_instr_group.setTitle(self.tr("emulator_current_instr"))
        self.bp_group.setTitle(self.tr("emulator_breakpoints"))
        
        # Кнопки
        self.btn_reset.setText(self.tr("emulator_reset"))
        self.btn_set_pc.setText(self.tr("emulator_set_pc"))
        self.btn_step_into.setText(self.tr("emulator_step_into"))
        self.btn_step_over.setText(self.tr("emulator_step_over"))
        self.btn_run.setText(self.tr("emulator_run"))
        self.btn_stop.setText(self.tr("emulator_stop"))
        self.btn_add_bp.setText(self.tr("emulator_add_bp"))
        self.btn_clear_bp.setText(self.tr("emulator_clear_bp"))
		
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
