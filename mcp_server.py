"""
Встроенный MCP Server для i8080-5 Master Controller
Использует FastMCP API (стабильный и простой)
Транспорт: SSE (Server-Sent Events)
"""
import warnings

# Подавляем предупреждение pydantic_settings о lifespan
try:
    from pydantic_settings.sources.utils import IncompleteFieldDefinitionWarning
    warnings.filterwarnings("ignore", category=IncompleteFieldDefinitionWarning)
except ImportError:
    # Если класс недоступен, подавляем по сообщению
    warnings.filterwarnings("ignore", message=".*lifespan.*")
	
import asyncio
import json
import threading
from mcp.server.fastmcp import FastMCP


class MCPServerManager:
    """Управляет встроенным MCP Server"""
    
    def __init__(self, main_window, host="127.0.0.1", port=8000):
        self.mw = main_window
        self.host = host
        self.port = port
        self.thread = None
        self.running = False
        self.mcp = None
        
    def start(self):
        """Запускает MCP Server в отдельном потоке"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        self.mw.log(f"MCP Server started on http://{self.host}:{self.port}/sse")
        
    def stop(self):
        """Останавливает MCP Server"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self.mw.log("MCP Server stopped")
        
    def _run_server(self):
        """Запускает MCP Server"""
        try:
            self.mcp = self._create_server()
            # Запускаем SSE сервер
            self.mcp.run(transport="sse")
        except Exception as e:
            self.mw.log(f"MCP Server error: {e}")
            self.running = False
            
    def _create_server(self):
        """Создаёт и настраивает FastMCP Server"""
        # Создаём FastMCP с настройками хоста и порта
        mcp = FastMCP(
            "i8080-master-controller",
            host=self.host,
            port=self.port
        )
        
        # =============================================
        # TOOLS: Управление шиной
        # =============================================
        
        @mcp.tool()
        def hold_bus() -> bool:
            """Захватить шину i8080. Возвращает True если команда отправлена."""
            api = self._get_api()
            return api.hold_bus()
            
        @mcp.tool()
        def unhold_bus() -> bool:
            """Освободить шину i8080. Возвращает True если команда отправлена."""
            api = self._get_api()
            return api.unhold_bus()
            
        @mcp.tool()
        def wait_bus(timeout: float = 5.0) -> bool:
            """Ждать захвата шины. Возвращает True если шина захвачена."""
            api = self._get_api()
            return api.wait_bus(timeout)
            
        @mcp.tool()
        def wait_unhold(timeout: float = 5.0) -> bool:
            """Ждать освобождения шины. Возвращает True если шина освобождена."""
            api = self._get_api()
            return api.wait_unhold(timeout)
        
        # =============================================
        # TOOLS: Локальная память
        # =============================================
        
        @mcp.tool()
        def read_mem(addr: int) -> int | None:
            """Прочитать байт из локального образа памяти"""
            api = self._get_api()
            return api.read_mem(addr)
            
        @mcp.tool()
        def write_mem(addr: int, val: int) -> str:
            """Записать байт в локальный образ памяти"""
            api = self._get_api()
            api.write_mem(addr, val)
            return f"Written 0x{val:02X} to 0x{addr:04X}"
            
        @mcp.tool()
        def read_block(addr: int, size: int) -> list[int | None]:
            """Прочитать блок из локального образа памяти"""
            api = self._get_api()
            return api.read_block(addr, size)
            
        @mcp.tool()
        def write_block(addr: int, data: list[int]) -> str:
            """Записать блок в локальный образ памяти"""
            api = self._get_api()
            api.write_block(addr, data)
            return f"Written {len(data)} bytes to 0x{addr:04X}"
            
        @mcp.tool()
        def fill_mem(addr: int, size: int, val: int) -> str:
            """Заполнить диапазон памяти значением"""
            api = self._get_api()
            api.fill_mem(addr, size, val)
            return f"Filled {size} bytes with 0x{val:02X} starting at 0x{addr:04X}"
        
        # =============================================
        # TOOLS: Память устройства
        # =============================================
        
        @mcp.tool()
        def dev_read_mem(addr: int) -> int | None:
            """Прочитать байт из памяти УСТРОЙСТВА (требует шину)"""
            api = self._get_api()
            return api.dev_read_mem(addr)
            
        @mcp.tool()
        def dev_write_mem(addr: int, val: int) -> bool:
            """Записать байт в память УСТРОЙСТВА (требует шину)"""
            api = self._get_api()
            return api.dev_write_mem(addr, val)
            
        @mcp.tool()
        def dev_read_io(port: int) -> int | None:
            """Прочитать из IO-порта УСТРОЙСТВА (требует шину)"""
            api = self._get_api()
            return api.dev_read_io(port)
            
        @mcp.tool()
        def dev_write_io(port: int, val: int) -> bool:
            """Записать в IO-порт УСТРОЙСТВА (требует шину)"""
            api = self._get_api()
            return api.dev_write_io(port, val)
        
        # =============================================
        # TOOLS: Синхронизация
        # =============================================
        
        @mcp.tool()
        def download(addr: int, size: int) -> list[int] | None:
            """Считать блок из УСТРОЙСТВА в локальный образ"""
            api = self._get_api()
            return api.download(addr, size)
            
        @mcp.tool()
        def upload(addr: int, size: int) -> bool:
            """Записать блок из локального образа в УСТРОЙСТВО"""
            api = self._get_api()
            return api.upload(addr, size)
        
        # =============================================
        # TOOLS: Дизассемблирование и поиск
        # =============================================
        
        @mcp.tool()
        def disassemble(addr: int | None = None, length: int | None = None, show: bool = False) -> list[str]:
            """Дизассемблировать локальный образ памяти"""
            api = self._get_api()
            return api.disassemble(addr, length, show)
            
        @mcp.tool()
        def search(pattern: str, mode: str = "hex") -> list[int]:
            """Поиск в локальном образе памяти. mode: 'hex' или 'ascii'"""
            api = self._get_api()
            return api.search(pattern, mode)
        
        # =============================================
        # TOOLS: Файлы
        # =============================================
        
        @mcp.tool()
        def load_file(path: str, base_addr: int = 0) -> int:
            """Загрузить файл прошивки в локальный образ"""
            api = self._get_api()
            return api.load_file(path, base_addr)
            
        @mcp.tool()
        def save_file(path: str) -> bool:
            """Сохранить локальный образ в файл"""
            api = self._get_api()
            return api.save_file(path)
        
        # =============================================
        # TOOLS: Утилиты
        # =============================================
        
        @mcp.tool()
        def get_status() -> dict:
            """Получить текущее состояние программы"""
            api = self._get_api()
            return api.status()
            
        @mcp.tool()
        def refresh() -> str:
            """Принудительно обновить hex-редактор и дизассемблер"""
            api = self._get_api()
            api.refresh()
            return "GUI refreshed"
        
        # =============================================
        # RESOURCES
        # =============================================
        
        @mcp.resource("memory://current")
        def get_memory_dump() -> str:
            """Текущий дамп памяти в формате HEX"""
            lines = []
            for addr in sorted(self.mw.mem_data.keys()):
                lines.append(f"{addr:04X}: {self.mw.mem_data[addr]:02X}")
            return "\n".join(lines) if lines else "Memory is empty"
            
        @mcp.resource("memory://disassembly")
        def get_disassembly() -> str:
            """Дизассемблированный код текущего образа памяти"""
            if not self.mw.mem_data:
                return "No code to disassemble"
            api = self._get_api()
            lines = api.disassemble()
            return "\n".join(lines)
            
        @mcp.resource("status://info")
        def get_status_info() -> str:
            """Информация о текущем состоянии программы"""
            api = self._get_api()
            return json.dumps(api.status(), indent=2)
        
        # =============================================
        # PROMPTS
        # =============================================
        
        @mcp.prompt()
        def analyze_firmware(focus: str = "общий анализ") -> str:
            """Анализ прошивки i8080"""
            return f"""Проанализируй прошивку i8080, загруженную в программу.

Фокус анализа: {focus}

Используй доступные инструменты для:
1. Чтения памяти устройства (download)
2. Дизассемблирования кода (disassemble)
3. Поиска инструкций (search)
4. Анализа структуры программы

Предоставь подробный отчёт о:
- Структуре программы
- Найденных подпрограммах
- Точках входа
- Потенциальных проблемах"""
            
        @mcp.prompt()
        def find_bugs() -> str:
            """Поиск потенциальных багов в коде i8080"""
            return """Проанализируй код i8080 на предмет потенциальных багов.

Проверь:
1. Бесконечные циклы без выхода
2. Обращения к несуществующим адресам памяти
3. Некорректные команды (недокументированные опкоды)
4. Проблемы со стеком (PUSH без POP, переполнение стека)
5. Незавершённые подпрограммы (CALL без RET)

Используй инструменты disassemble и search для анализа."""
            
        @mcp.prompt()
        def create_test_program(description: str) -> str:
            """Создание тестовой программы для i8080"""
            return f"""Создай тестовую программу для i8080, которая:

{description}

Требования:
- Используй только стандартные команды i8080
- Программа должна начинаться с адреса 0x0000
- Добавь комментарии к каждой команде
- Заверши программу командой HLT или бесконечным циклом

После создания:
1. Запиши программу в память (write_block)
2. Дизассемблируй для проверки (disassemble)
3. Покажи результат пользователю"""
            
        @mcp.prompt()
        def explain_code(addr: str, length: str) -> str:
            """Объяснение дизассемблированного кода"""
            return f"""Объясни код i8080, начиная с адреса 0x{addr}, длиной {length} байт.

1. Сначала дизассемблируй код (disassemble)
2. Объясни каждую инструкцию
3. Опиши общее назначение этого участка кода
4. Укажи на особенности или потенциальные проблемы"""
        
        return mcp
        
    def _get_api(self):
        """Получает экземпляр AutomationAPI"""
        if hasattr(self.mw, '_automation_api'):
            return self.mw._automation_api
        # Создаём новый, если нет
        from i8080_controller_1 import AutomationAPI
        return AutomationAPI(self.mw)