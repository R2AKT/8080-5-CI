"""
Шина памяти и IO для i8080-5 CI.
Итерация E1: фундамент модульности.

Модули памяти и IO подключаются к шине через register_memory / register_io.
Шина маршрутизирует чтение/запись по адресу (память) или порту (IO).
"""


class MemoryRegion:
    """Базовый регион памяти (абстрактный).
    Подклассы: RAMRegion, ROMRegion, ShadowROM, BankedMemory и т.д.
    """
    def __init__(self, start, end, name="region"):
        self.start = start & 0xFFFF
        self.end = end & 0xFFFF
        self.name = name

    def contains(self, addr):
        """Проверяет, принадлежит ли адрес региону"""
        return self.start <= addr <= self.end

    def read(self, addr):
        """Чтение байта. Переопределяется подклассами."""
        return 0xFF

    def write(self, addr, value):
        """Запись байта. Переопределяется подклассами."""
        pass

    def reset(self):
        """Сброс региона (например, при сбросе системы)."""
        pass


class RAMRegion(MemoryRegion):
    """RAM: чтение и запись. Может использовать внешний dict как хранилище."""
    def __init__(self, start, end, data=None, name="RAM"):
        super().__init__(start, end, name)
        self.data = data if data is not None else {}

    def read(self, addr):
        return self.data.get(addr, 0x00)

    def write(self, addr, value):
        self.data[addr] = value & 0xFF

    def reset(self):
        """Очистить RAM"""
        self.data.clear()


class ROMRegion(MemoryRegion):
    """ROM: только чтение. Запись игнорируется."""
    def __init__(self, start, end, data=None, name="ROM"):
        super().__init__(start, end, name)
        self.data = dict(data) if data else {}

    def read(self, addr):
        return self.data.get(addr, 0xFF)

    def write(self, addr, value):
        pass  # ROM не пишется

    def reset(self):
        pass  # ROM не сбрасывается


class MemoryBus:
    """Шина памяти и IO.
    Маршрутизирует обращения по адресу к соответствующему модулю.
    """
    def __init__(self, size=0x10000):
        self.size = size
        self.memory_regions = []
        self.io_devices = {}
        self.io_range_devices = []
        self._unmapped_read = 0xFF

    # =============================================
    # РЕГИСТРАЦИЯ МОДУЛЕЙ
    # =============================================
    def register_memory(self, region):
        """Зарегистрировать регион памяти."""
        self.memory_regions.append(region)

    def unregister_memory(self, region):
        """Удалить регион памяти"""
        if region in self.memory_regions:
            self.memory_regions.remove(region)

    def register_io(self, port, device):
        """Зарегистрировать IO-устройство по порту"""
        self.io_devices[port & 0xFF] = device

    def unregister_io(self, port):
        """Удалить IO-устройство"""
        port &= 0xFF
        if port in self.io_devices:
            del self.io_devices[port]

    # =============================================
    # ЧТЕНИЕ / ЗАПИСЬ ПАМЯТИ
    # =============================================
    # def read(self, addr):
        # """Чтение байта из памяти"""
        # addr &= 0xFFFF
        # for region in self.memory_regions:
            # if region.contains(addr):
                # return region.read(addr)
        # return self._unmapped_read
    def read(self, addr):
        """Чтение байта из памяти"""
        addr &= 0xFFFF
        # Уведомляем ShadowROM о чтении адресов, НЕ принадлежащих ROM
        for region in self.memory_regions:
            if isinstance(region, ShadowROMRegion) and not region.contains(addr):
                region.read(addr)
        # Читаем из регионов
        for region in self.memory_regions:
            if region.contains(addr):
                return region.read(addr)
        return self._unmapped_read

    # def write(self, addr, value):
        # """Запись байта в память"""
        # addr &= 0xFFFF
        # for region in self.memory_regions:
            # if region.contains(addr):
                # region.write(addr, value)
                # return
    def write(self, addr, value):
        """Запись байта в память"""
        addr &= 0xFFFF
        # Уведомляем ShadowROM о записи адресов, НЕ принадлежащих ROM
        for region in self.memory_regions:
            if isinstance(region, ShadowROMRegion) and not region.contains(addr):
                region.write(addr, value)
        # Записываем в регионы
        for region in self.memory_regions:
            if region.contains(addr):
                region.write(addr, value)
                return

    def read_word(self, addr):
        """Чтение слова (little-endian)"""
        addr &= 0xFFFF
        low = self.read(addr)
        high = self.read((addr + 1) & 0xFFFF)
        return (high << 8) | low

    def write_word(self, addr, value):
        """Запись слова (little-endian)"""
        addr &= 0xFFFF
        self.write(addr, value & 0xFF)
        self.write((addr + 1) & 0xFFFF, (value >> 8) & 0xFF)

    # =============================================
    # ЧТЕНИЕ / ЗАПИСЬ IO
    # =============================================
    # def io_read(self, port):
        # """Чтение из IO-порта"""
        # port &= 0xFF
        # if port in self.io_devices:
            # return self.io_devices[port].io_read(port)
        # return 0xFF
    def io_read(self, port):
        """Чтение из IO-порта"""
        port &= 0xFF
        # Сначала проверяем регионы памяти (банковые/теневые)
        for region in self.memory_regions:
            if hasattr(region, 'io_read'):
                result = region.io_read(port)
                if result is not None:
                    return result
            if hasattr(region, 'io_access'):
                region.io_access(port, is_write=False)
        # Затем IO-устройства
        if port in self.io_devices:
            return self.io_devices[port].io_read(port)
        return 0xFF

    # def io_write(self, port, value):
        # """Запись в IO-порт. Сначала проверяет регионы памяти
        # (для переключения банков), затем IO-устройства."""
        # port &= 0xFF
        # # Сначала проверяем регионы памяти (переключение банков)
        # for region in self.memory_regions:
            # if hasattr(region, 'io_write') and region.io_write(port, value):
                # return  # Банк переключён, дальше не идём
        # # Затем IO-устройства
        # if port in self.io_devices:
            # self.io_devices[port].io_write(port, value)    
    def io_write(self, port, value):
        """Запись в IO-порт"""
        port &= 0xFF
        # Сначала проверяем регионы памяти (банковые/теневые)
        for region in self.memory_regions:
            if hasattr(region, 'io_write'):
                if region.io_write(port, value):
                    return  # Запись обработана регионом
            if hasattr(region, 'io_access'):
                region.io_access(port, is_write=True)
        # Затем IO-устройства
        if port in self.io_devices:
            self.io_devices[port].io_write(port, value)
    
    # =============================================
    # УТИЛИТЫ
    # =============================================
    def reset(self):
        """Сброс всех модулей шины"""
        for region in self.memory_regions:
            region.reset()
        for device in self.io_devices.values():
            if hasattr(device, 'reset'):
                device.reset()
    
    def get_memory_map(self):
        """Вернуть карту памяти для отображения/отладки"""
        result = []
        for region in self.memory_regions:
            entry = {
                "name": region.name,
                "start": region.start,
                "end": region.end,
                "size": region.end - region.start + 1,
                "type": type(region).__name__
            }
            # Для банковой памяти добавляем информацию о банках
            if isinstance(region, BankedRegion):
                entry["current_bank"] = region.current_bank
                entry["num_banks"] = region.num_banks
            result.append(entry)
        return result

class IOBus:
    """Шина IO: порты 0x00-0xFF."""
    def __init__(self):
        self.ports = {}

    def read(self, port):
        return self.ports.get(port & 0xFF, 0xFF)

    def write(self, port, value):
        self.ports[port & 0xFF] = value & 0xFF
        
class BankedRegion(MemoryRegion):
    """Банковая память: окно в адресном пространстве, через которое
    виден один из банков физической памяти.
    
    Переключение банков:
    - через IO-порт (switch_port) — запись в порт выбирает банк
    - через адрес памяти (switch_addr) — запись по адресу выбирает банк
    
    Пример для Радио-86РК:
    - Окно: 0x0000-0xFFFF (всё адресное пространство)
    - 4 банка по 64 КБ
    - Переключение через порт 0x00
    """
    
    def __init__(self, start, end, num_banks=2, switch_port=None, 
                 switch_addr=None, name="BankedRAM"):
        super().__init__(start, end, name)
        self.window_size = end - start + 1
        self.num_banks = num_banks
        self.switch_port = switch_port      # Порт IO для переключения
        self.switch_addr = switch_addr      # Адрес памяти для переключения
        self.current_bank = 0
        # Банки физической памяти
        self.banks = [{} for _ in range(num_banks)]
        # Флаг: переключение по записи в switch_addr
        self._switch_pending = False
    
    def select_bank(self, bank_num):
        """Переключить банк"""
        bank_num &= 0xFF
        if bank_num < self.num_banks:
            self.current_bank = bank_num
        else:
            # Если банк вне диапазона, берём по модулю
            self.current_bank = bank_num % self.num_banks
    
    def read(self, addr):
        """Чтение из текущего банка"""
        if not self.contains(addr):
            return 0xFF
        offset = addr - self.start
        return self.banks[self.current_bank].get(offset, 0x00)
    
    def write(self, addr, value):
        """Запись в текущий банк, или переключение банка"""
        if not self.contains(addr):
            return
        # Переключение банка по записи в switch_addr
        if self.switch_addr is not None and addr == self.switch_addr:
            self.select_bank(value)
            return
        # Обычная запись в текущий банк
        offset = addr - self.start
        self.banks[self.current_bank][offset] = value & 0xFF
    
    def io_write(self, port, value):
        """Обработка записи в IO-порт (переключение банка)"""
        if self.switch_port is not None and port == self.switch_port:
            self.select_bank(value)
            return True
        return False
    
    def get_state(self):
        """Текущее состояние банков"""
        return {
            "current_bank": self.current_bank,
            "num_banks": self.num_banks,
            "window": f"0x{self.start:04X}-0x{self.end:04X}",
            "switch_port": self.switch_port,
            "switch_addr": self.switch_addr
        }
    
    def reset(self):
        """Сброс на банк 0"""
        self.current_bank = 0

class BankedROMRegion(MemoryRegion):
    """Банковое ПЗУ: окно в адресном пространстве, через которое
    виден один из банков ROM.
    
    Переключение банков:
    - через IO-порт (switch_port) — запись в порт выбирает банк
    - через адрес памяти (switch_addr) — запись по адресу выбирает банк
    
    В отличие от BankedRegion (RAM), данные ROM не изменяются.
    Применение: Вектор-06Ц, Орион-128 и другие системы с банковым ПЗУ.
    """
    
    def __init__(self, start, end, banks=None, switch_port=None,
                 switch_addr=None, name="BankedROM"):
        """
        Args:
            start, end: окно в адресном пространстве
            banks: список банков ROM, каждый банк — dict {offset: byte}
            switch_port: порт IO для переключения банков
            switch_addr: адрес памяти для переключения банков
        """
        super().__init__(start, end, name)
        self.window_size = end - start + 1
        self.banks = banks if banks is not None else []
        self.num_banks = len(self.banks)
        self.switch_port = switch_port
        self.switch_addr = switch_addr
        self.current_bank = 0
    
    def select_bank(self, bank_num):
        """Переключить банк"""
        if self.num_banks == 0:
            return
        bank_num &= 0xFF
        self.current_bank = bank_num % self.num_banks
    
    def read(self, addr):
        """Чтение из текущего банка ROM"""
        if not self.contains(addr):
            return 0xFF
        if self.num_banks == 0:
            return 0xFF
        offset = addr - self.start
        return self.banks[self.current_bank].get(offset, 0xFF)
    
    def write(self, addr, value):
        """Запись игнорируется (ROM), но switch_addr переключает банк.
        Возвращает True, если запись обработана (переключение банка)."""
        if self.switch_addr is not None and addr == self.switch_addr:
            self.select_bank(value)
            return True
        return False  # ROM не пишется
    
    def io_write(self, port, value):
        """Обработка записи в IO-порт (переключение банка)"""
        if self.switch_port is not None and port == self.switch_port:
            self.select_bank(value)
            return True
        return False
    
    def load_bank(self, bank_num, data):
        """Загрузить данные в банк.
        Args:
            bank_num: номер банка
            data: dict {offset: byte} или list байт
        """
        # Расширяем список банков при необходимости
        while len(self.banks) <= bank_num:
            self.banks.append({})
        self.num_banks = len(self.banks)
        # Загружаем данные
        if isinstance(data, (list, tuple, bytes)):
            self.banks[bank_num] = {i: b for i, b in enumerate(data)}
        else:
            self.banks[bank_num] = dict(data)
    
    def get_state(self):
        """Текущее состояние банков"""
        return {
            "current_bank": self.current_bank,
            "num_banks": self.num_banks,
            "window": f"0x{self.start:04X}-0x{self.end:04X}",
            "switch_port": self.switch_port,
            "switch_addr": self.switch_addr
        }
    
    def reset(self):
        """Сброс на банк 0"""
        self.current_bank = 0

class ShadowROMRegion(MemoryRegion):
    """Теневое ПЗУ с переключением.
    
    Режимы переключения:
      MODE_M1        — по N чтениям из ROM (Радио-86РК: 3 чтения = размер JMP)
      MODE_MEM_READ  — по чтению из ячейки памяти
      MODE_MEM_WRITE — по записи в ячейку памяти
      MODE_MEM_RW    — по чтению или записи ячейки памяти
      MODE_IO_READ   — по чтению из IO-порта
      MODE_IO_WRITE  — по записи в IO-порт
      MODE_IO_RW     — по чтению или записи IO-порта
    
    Действия после переключения:
      ACTION_MOVE    — переместить ROM на high_addr
      ACTION_DISABLE — полностью отключить ROM
    
    Состояния:
      STATE_LOW      — ROM виден по low_addr (после сброса)
      STATE_HIGH     — ROM виден по high_addr (после переключения)
      STATE_DISABLED — ROM полностью отключён
    """
    
    # Режимы переключения
    MODE_M1 = "m1"
    MODE_MEM_READ = "mem_read"
    MODE_MEM_WRITE = "mem_write"
    MODE_MEM_RW = "mem_rw"
    MODE_IO_READ = "io_read"
    MODE_IO_WRITE = "io_write"
    MODE_IO_RW = "io_rw"
    
    # Действия после переключения
    ACTION_MOVE = "move"
    ACTION_DISABLE = "disable"
    
    # Состояния
    STATE_LOW = "low"
    STATE_HIGH = "high"
    STATE_DISABLED = "disabled"
    
    def __init__(self, data, low_addr=0x0000, high_addr=0xF800,
                 mode=MODE_M1, action=ACTION_MOVE,
                 trigger_addr=None, trigger_port=None,
                 m1_count=3, name="ShadowROM"):
        """
        Args:
            data: dict {offset: byte} — данные ROM
            low_addr: адрес, по которому ROM виден после сброса
            high_addr: адрес, по которому ROM виден после переключения
            mode: режим переключения (MODE_*)
            action: действие после переключения (ACTION_*)
            trigger_addr: адрес памяти для триггера (для MODE_MEM_*)
            trigger_port: порт IO для триггера (для MODE_IO_*)
            m1_count: количество чтений для переключения (для MODE_M1)
            name: имя региона
        """
        super().__init__(low_addr, low_addr + len(data) - 1, name)
        self.data = dict(data) if data else {}
        self.size = len(self.data)
        self.low_addr = low_addr & 0xFFFF
        self.high_addr = high_addr & 0xFFFF
        self.mode = mode
        self.action = action
        self.trigger_addr = trigger_addr & 0xFFFF if trigger_addr is not None else None
        self.trigger_port = trigger_port & 0xFF if trigger_port is not None else None
        self.m1_count = m1_count
        self.state = self.STATE_LOW
        self._read_counter = 0
    
    # =============================================
    # ПРОВЕРКА СОДЕРЖИМОГО АДРЕСА
    # =============================================
    def contains(self, addr):
        """Проверяет, содержится ли адрес в текущем состоянии ROM"""
        if self.state == self.STATE_LOW:
            return self.low_addr <= addr < self.low_addr + self.size
        elif self.state == self.STATE_HIGH:
            return self.high_addr <= addr < self.high_addr + self.size
        return False  # STATE_DISABLED
    
    # =============================================
    # ЧТЕНИЕ
    # =============================================
    # def read(self, addr):
        # """Чтение байта из ROM. Может вызвать переключение."""
        # if self.state == self.STATE_LOW:
            # if self.low_addr <= addr < self.low_addr + self.size:
                # offset = addr - self.low_addr
                # # Режим M1: считаем чтения
                # if self.mode == self.MODE_M1:
                    # self._read_counter += 1
                    # if self._read_counter >= self.m1_count:
                        # self._do_switch()
                # return self.data.get(offset, 0xFF)
            # return 0xFF
        # elif self.state == self.STATE_HIGH:
            # if self.high_addr <= addr < self.high_addr + self.size:
                # offset = addr - self.high_addr
                # return self.data.get(offset, 0xFF)
            # return 0xFF
        # return 0xFF  # STATE_DISABLED
    def read(self, addr):
        """Чтение байта из ROM"""
        if self.state == self.STATE_LOW:
            if self.low_addr <= addr < self.low_addr + self.size:
                offset = addr - self.low_addr
                # Режим M1: считаем чтения только для адресов ROM
                if self.mode == self.MODE_M1:
                    self._read_counter += 1
                    if self._read_counter >= self.m1_count:
                        self._do_switch()
                return self.data.get(offset, 0xFF)
            else:
                # Адрес вне ROM: проверяем триггер MEM_READ / MEM_RW
                if self.mode in (self.MODE_MEM_READ, self.MODE_MEM_RW):
                    if self.trigger_addr is not None and addr == self.trigger_addr:
                        self._do_switch()
                return 0xFF
        elif self.state == self.STATE_HIGH:
            if self.high_addr <= addr < self.high_addr + self.size:
                offset = addr - self.high_addr
                return self.data.get(offset, 0xFF)
            return 0xFF
        return 0xFF
    # =============================================
    # ЗАПИСЬ (ROM не пишется, но может быть триггером)
    # =============================================
    # def write(self, addr, value):
        # """Запись в ROM. ROM не пишется, но запись может быть триггером.
        # Возвращает True, если запись обработана (триггер сработал).
        # Возвращает False, если запись должна пройти в другой регион.
        # """
        # if self.state != self.STATE_LOW:
            # return False  # После переключения ROM не участвует в записи
        
        # # Проверяем триггер по записи в память
        # if self.mode in (self.MODE_MEM_WRITE, self.MODE_MEM_RW):
            # if self.trigger_addr is not None and addr == self.trigger_addr:
                # self._do_switch()
                # return True  # Запись обработана как триггер
        
        # return False  # ROM не пишется, запись должна пройти в другой регион
    def write(self, addr, value):
        """Запись в ROM (игнорируется, но может быть триггером)"""
        if self.state != self.STATE_LOW:
            return
        # Триггер MEM_WRITE / MEM_RW — адрес не обязан принадлежать ROM
        if self.mode in (self.MODE_MEM_WRITE, self.MODE_MEM_RW):
            if self.trigger_addr is not None and addr == self.trigger_addr:
                self._do_switch()
                
    # =============================================
    # ОБРАЩЕНИЕ К IO-ПОРТУ (может быть триггером)
    # =============================================
    def io_access(self, port, is_write):
        """Уведомление об обращении к IO-порту.
        Вызывается из MemoryBus.io_read / io_write.
        """
        if self.state != self.STATE_LOW:
            return
        
        if self.trigger_port is not None and port == self.trigger_port:
            if self.mode == self.MODE_IO_READ and not is_write:
                self._do_switch()
            elif self.mode == self.MODE_IO_WRITE and is_write:
                self._do_switch()
            elif self.mode == self.MODE_IO_RW:
                self._do_switch()
    
    # =============================================
    # ПЕРЕКЛЮЧЕНИЕ
    # =============================================
    def _do_switch(self):
        """Выполнить переключение"""
        if self.action == self.ACTION_MOVE:
            self.state = self.STATE_HIGH
            self.start = self.high_addr
            self.end = self.high_addr + self.size - 1
        elif self.action == self.ACTION_DISABLE:
            self.state = self.STATE_DISABLED
            self.start = 0
            self.end = 0  # Пустой диапазон — регион не содержит ни одного адреса
    
    # =============================================
    # СБРОС
    # =============================================
    def reset(self):
        """Сброс: ROM снова виден по low_addr"""
        self.state = self.STATE_LOW
        self.start = self.low_addr
        self.end = self.low_addr + self.size - 1
        self._read_counter = 0
    
    # =============================================
    # ИНФОРМАЦИЯ О СОСТОЯНИИ
    # =============================================
    def get_state_info(self):
        """Информация о состоянии для отладки"""
        return {
            "state": self.state,
            "mode": self.mode,
            "action": self.action,
            "low_addr": self.low_addr,
            "high_addr": self.high_addr,
            "size": self.size,
            "read_counter": self._read_counter,
            "m1_count": self.m1_count,
        }

class PagedRegion(MemoryRegion):
    """Страничная память: адресное пространство разбито на страницы,
    каждая страница независимо маппится на физическую страницу.
    
    Переключение страниц:
    - через порты IO (по порту на каждую виртуальную страницу)
    - через адреса памяти (по адресу на каждую виртуальную страницу)
    
    Пример:
    - Адресное пространство 64КБ разбито на 4 страницы по 16КБ
    - 16 физических страниц по 16КБ (всего 256КБ физической памяти)
    - Порты 0x00-0x03 выбирают физические страницы для виртуальных страниц 0-3
    """
    
    def __init__(self, start, end, page_size=16384, num_physical_pages=16,
                 switch_ports=None, switch_addrs=None, name="PagedRAM"):
        """
        Args:
            start, end: окно в адресном пространстве
            page_size: размер страницы в байтах (1024, 4096, 16384)
            num_physical_pages: количество физических страниц
            switch_ports: список портов IO для каждой виртуальной страницы
            switch_addrs: список адресов памяти для каждой виртуальной страницы
        """
        super().__init__(start, end, name)
        self.page_size = page_size
        self.num_virtual_pages = (end - start + 1) // page_size
        self.num_physical_pages = num_physical_pages
        self.switch_ports = switch_ports or []
        self.switch_addrs = switch_addrs or []
        
        # Физические страницы
        self.physical_pages = [{} for _ in range(num_physical_pages)]
        
        # Таблица маппинга: виртуальная страница -> физическая страница
        self.page_table = [i % num_physical_pages for i in range(self.num_virtual_pages)]
    
    def _get_virtual_page(self, addr):
        """Определить виртуальную страницу для адреса"""
        return (addr - self.start) // self.page_size
    
    def _get_page_offset(self, addr):
        """Определить смещение внутри страницы"""
        return (addr - self.start) % self.page_size
    
    def read(self, addr):
        """Чтение из текущей физической страницы"""
        if not self.contains(addr):
            return 0xFF
        vpage = self._get_virtual_page(addr)
        offset = self._get_page_offset(addr)
        ppage = self.page_table[vpage]
        return self.physical_pages[ppage].get(offset, 0x00)
    
    def write(self, addr, value):
        """Запись в текущую физическую страницу, или переключение страницы"""
        if not self.contains(addr):
            return
        
        # Переключение страницы по записи в switch_addr
        if addr in self.switch_addrs:
            vpage = self.switch_addrs.index(addr)
            if vpage < self.num_virtual_pages:
                self.page_table[vpage] = value % self.num_physical_pages
                return
        
        # Обычная запись
        vpage = self._get_virtual_page(addr)
        offset = self._get_page_offset(addr)
        ppage = self.page_table[vpage]
        self.physical_pages[ppage][offset] = value & 0xFF
    
    def io_write(self, port, value):
        """Обработка записи в IO-порт (переключение страницы)"""
        if port in self.switch_ports:
            vpage = self.switch_ports.index(port)
            if vpage < self.num_virtual_pages:
                self.page_table[vpage] = value % self.num_physical_pages
                return True
        return False
    
    def get_state(self):
        """Текущее состояние таблицы маппинга"""
        return {
            "page_table": self.page_table.copy(),
            "num_virtual_pages": self.num_virtual_pages,
            "num_physical_pages": self.num_physical_pages,
            "page_size": self.page_size
        }
    
    def reset(self):
        """Сброс таблицы маппинга"""
        self.page_table = [i % self.num_physical_pages for i in range(self.num_virtual_pages)]

class SegmentedRegion(MemoryRegion):
    """Сегментная память: адресное пространство разбито на сегменты,
    каждый сегмент имеет базовый адрес в физической памяти.
    
    Переключение сегментов:
    - через порт IO (запись в порт выбирает текущий сегмент)
    - через адрес памяти
    
    Пример:
    - Адресное пространство 64КБ
    - Сегментный регистр определяет текущий сегмент
    - Физическая память: 16 сегментов по 64КБ (всего 1МБ)
    - Запись в порт 0x00 выбирает сегмент
    """
    
    def __init__(self, start, end, num_segments=16,
                 switch_port=None, switch_addr=None, name="SegmentedRAM"):
        """
        Args:
            start, end: окно в адресном пространстве
            num_segments: количество сегментов в физической памяти
            switch_port: порт IO для переключения сегмента
            switch_addr: адрес памяти для переключения сегмента
        """
        super().__init__(start, end, name)
        self.num_segments = num_segments
        self.switch_port = switch_port
        self.switch_addr = switch_addr
        
        # Сегменты физической памяти
        self.segments = [{} for _ in range(num_segments)]
        
        # Текущий сегмент
        self.current_segment = 0
    
    def read(self, addr):
        """Чтение из текущего сегмента"""
        if not self.contains(addr):
            return 0xFF
        offset = addr - self.start
        return self.segments[self.current_segment].get(offset, 0x00)
    
    def write(self, addr, value):
        """Запись в текущий сегмент, или переключение сегмента"""
        if not self.contains(addr):
            return
        
        # Переключение сегмента по записи в switch_addr
        if self.switch_addr is not None and addr == self.switch_addr:
            self.current_segment = value % self.num_segments
            return
        
        # Обычная запись
        offset = addr - self.start
        self.segments[self.current_segment][offset] = value & 0xFF
    
    def io_write(self, port, value):
        """Обработка записи в IO-порт (переключение сегмента)"""
        if self.switch_port is not None and port == self.switch_port:
            self.current_segment = value % self.num_segments
            return True
        return False
    
    def get_state(self):
        """Текущее состояние"""
        return {
            "current_segment": self.current_segment,
            "num_segments": self.num_segments
        }
    
    def reset(self):
        """Сброс на сегмент 0"""
        self.current_segment = 0

class SegmentedPagedRegion(MemoryRegion):
    """Сегментно-страничная память: 64КБ разбиты на сегменты,
    внутри каждого сегмента переключение страниц через порты IO.
    Количество портов соответствует количеству сегментов.
    
    Пример:
    - 64КБ разбиты на 4 сегмента по 16КБ
    - Каждый сегмент имеет свой порт IO для переключения страниц
    - Порт 0x00 для сегмента 0 (0x0000-0x3FFF)
    - Порт 0x01 для сегмента 1 (0x4000-0x7FFF)
    - Порт 0x02 для сегмента 2 (0x8000-0xBFFF)
    - Порт 0x03 для сегмента 3 (0xC000-0xFFFF)
    - Запись в порт выбирает физическую страницу для сегмента
    """
    
    def __init__(self, start, end, segment_size=16384, num_physical_pages=16,
                 base_port=0x00, name="SegmentedPagedRAM"):
        """
        Args:
            start, end: окно в адресном пространстве (обычно 0x0000-0xFFFF)
            segment_size: размер сегмента в байтах (обычно 16384)
            num_physical_pages: количество физических страниц
            base_port: базовый порт IO (порты base_port..base_port+num_segments-1)
        """
        super().__init__(start, end, name)
        self.segment_size = segment_size
        self.num_segments = (end - start + 1) // segment_size
        self.num_physical_pages = num_physical_pages
        self.base_port = base_port
        
        # Физические страницы
        self.physical_pages = [{} for _ in range(num_physical_pages)]
        
        # Таблица маппинга: сегмент -> физическая страница
        self.segment_table = [i % num_physical_pages for i in range(self.num_segments)]
    
    def _get_segment(self, addr):
        """Определить сегмент для адреса"""
        return (addr - self.start) // self.segment_size
    
    def _get_segment_offset(self, addr):
        """Определить смещение внутри сегмента"""
        return (addr - self.start) % self.segment_size
    
    def read(self, addr):
        """Чтение из текущей физической страницы сегмента"""
        if not self.contains(addr):
            return 0xFF
        segment = self._get_segment(addr)
        offset = self._get_segment_offset(addr)
        ppage = self.segment_table[segment]
        return self.physical_pages[ppage].get(offset, 0x00)
    
    def write(self, addr, value):
        """Запись в текущую физическую страницу сегмента"""
        if not self.contains(addr):
            return
        segment = self._get_segment(addr)
        offset = self._get_segment_offset(addr)
        ppage = self.segment_table[segment]
        self.physical_pages[ppage][offset] = value & 0xFF
    
    def io_write(self, port, value):
        """Обработка записи в IO-порт (переключение страницы сегмента)"""
        if self.base_port <= port < self.base_port + self.num_segments:
            segment = port - self.base_port
            self.segment_table[segment] = value % self.num_physical_pages
            return True
        return False
    
    def get_state(self):
        """Текущее состояние таблицы сегментов"""
        return {
            "segment_table": self.segment_table.copy(),
            "num_segments": self.num_segments,
            "num_physical_pages": self.num_physical_pages,
            "segment_size": self.segment_size,
            "base_port": self.base_port
        }
    
    def reset(self):
        """Сброс таблицы сегментов"""
        self.segment_table = [i % self.num_physical_pages for i in range(self.num_segments)]
