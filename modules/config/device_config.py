try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


class DeviceConfig:
    """Парсер TOML-конфигурации устройств"""

    def __init__(self):
        self.system_name = ""
        self.cpu = "i8080"
        self.clock_mhz = 1.78
        self.memory_regions = []  # [{type, start, end, name, file, ...}]
        self.devices = []         # [{type, name, base_port, ...}]

    def load_from_dict(self, config_dict):
        """Загрузить конфигурацию из dict (внешний профиль)"""
        system_cfg = config_dict.get("system", {})
        self.system_name = system_cfg.get("name", "Custom")
        self.cpu = system_cfg.get("cpu", "i8080")
        self.clock_mhz = system_cfg.get("clock_mhz", 2)

        self.memory_regions = config_dict.get("memory", {}).get("regions", [])
        self.devices = config_dict.get("devices", [])

        errors = self.validate()
        if errors:
            raise ValueError("Ошибки конфигурации:\n" + "\n".join(errors))
        
    def load_from_file(self, path):
        """Загрузить конфигурацию из TOML-файла"""
        if tomllib is None:
            raise ImportError("tomllib/tomli не установлен. Установите: pip install tomli")
        with open(path, 'rb') as f:
            data = tomllib.load(f)
        self._parse(data)
        return self

    def load_from_string(self, toml_string):
        """Загрузить конфигурацию из TOML-строки"""
        if not toml_string or not toml_string.strip():
            # Пустая строка — создаём пустую конфигурацию
            self.system_name = "Empty System"
            self.cpu = "i8080"
            self.clock_mhz = 2
            self.memory_regions = []
            self.devices = []
            return
        
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                # Если нет tomllib, создаём пустую конфигурацию
                self.system_name = "Empty System"
                self.cpu = "i8080"
                self.clock_mhz = 2
                self.memory_regions = []
                self.devices = []
                return
        
        try:
            data = tomllib.loads(toml_string)
            self._parse(data)
        except Exception as e:
            # При ошибке парсинга создаём пустую конфигурацию
            self.system_name = "Empty System"
            self.cpu = "i8080"
            self.clock_mhz = 2
            self.memory_regions = []
            self.devices = []

    def _parse(self, data):
        """Парсинг конфигурации из словаря"""
        # Защита от пустых или некорректных данных
        if not data or not isinstance(data, dict):
            self.system_name = "Empty System"
            self.cpu = "i8080"
            self.clock_mhz = 2
            self.memory_regions = []
            self.devices = []
            return

        # Секция [system]
        system = data.get("system", {})
        if not isinstance(system, dict):
            system = {}
        self.system_name = system.get("name", "Empty System")
        self.cpu = system.get("cpu", "i8080")
        self.clock_mhz = system.get("clock_mhz", 2)

        # Секция [memory]
        memory = data.get("memory", {})
        if not isinstance(memory, dict):
            memory = {}
        
        regions = memory.get("regions", [])
        if not isinstance(regions, list):
            regions = []
        
        self.memory_regions = []
        for mem in regions:
            if not isinstance(mem, dict):
                continue  # Пропускаем некорректные записи
            self.memory_regions.append({
                "type": mem.get("type", "ram"),
                "start": mem.get("start", 0),
                "end": mem.get("end", 0xFFFF),
                "name": mem.get("name", "RAM"),
                "image_file": mem.get("image_file", None),
            })

        # Секция [devices]
        devices = data.get("devices", [])
        if not isinstance(devices, list):
            devices = []
        
        self.devices = []
        for dev in devices:
            if not isinstance(dev, dict):
                continue
            self.devices.append(dev)

    @staticmethod
    def _parse_addr(value):
        """Парсинг адреса: '0x1234', '0X1234', 0x1234, 4660"""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            value = value.strip()
            if value.lower().startswith("0x"):
                return int(value, 16)
            return int(value)
        return int(value)

    def validate(self):
        """Проверка конфигурации на конфликты адресов"""
        errors = []
        # Проверка конфликтов портов
        port_ranges = []
        for dev in self.devices:
            dev_type = dev.get("type", "")
            base = dev.get("base_port", 0)
            port_count = DeviceFactory.get_port_count(dev_type)
            end_port = base + port_count - 1
            port_ranges.append((base, end_port, dev.get("name", dev_type)))

        # Проверка пересечений
        for i in range(len(port_ranges)):
            for j in range(i + 1, len(port_ranges)):
                s1, e1, n1 = port_ranges[i]
                s2, e2, n2 = port_ranges[j]
                if s1 <= e2 and s2 <= e1:
                    errors.append(
                        f"Конфликт портов: {n1} [{s1:02X}-{e1:02X}] "
                        f"пересекается с {n2} [{s2:02X}-{e2:02X}]"
                    )
        return errors

    def to_dict(self):
        """Конфигурация в виде словаря (для отладки)"""
        return {
            "system": {
                "name": self.system_name,
                "cpu": self.cpu,
                "clock_mhz": self.clock_mhz,
            },
            "memory": self.memory_regions,
            "devices": self.devices,
        }


class DeviceFactory:
    """Фабрика устройств: создаёт устройства из конфигурации"""

    # Размер портов для каждого типа устройства
    PORT_COUNTS = {
        "i8255": 4,      # PPI: порты A, B, C, Control
        "i8253": 4,      # PIT: 3 канала + Control
        "i8259": 2,      # PIC: 2 порта
        "i8257": 16,     # DMA: 16 портов
        "i8251": 2,      # USART: Data + Control
        "i16550": 8,     # UART: 8 регистров
        "i8279": 2,      # Клавиатура/дисплей: 2 порта
        "i8276": 2,      # CRT: 2 порта
        "i8272": 4,      # FDC: 4 порта
        "i512vi1": 2,    # RTC: Address + Data
        "cf_ide": 8,     # CF IDE: 8 портов
        "ch376s": 2,     # USB: Data + Command
        "am9511": 2,     # APU: Data + Command
        "lcd1602": 2,    # LCD: Data + Control
        "lcd2004": 2,    # LCD: Data + Control
        "tft8080": 2,    # TFT: 2 порта
    }

    @classmethod
    def get_port_count(cls, device_type):
        """Размер портов для типа устройства"""
        return cls.PORT_COUNTS.get(device_type, 2)

    @classmethod
    def create_device(cls, device_config, memory_bus=None):
        """Создать устройство из конфигурации"""
        dev_type = device_config.get("type", "")
        name = device_config.get("name", dev_type)
        base_port = device_config.get("base_port", 0)

        # Ленивый импорт для избежания циклических зависимостей
        device = cls._create_instance(dev_type, base_port, name)

        if device is None:
            return None

        # Регистрация на шине
        if memory_bus is not None and hasattr(device, 'register_to_bus'):
            device.register_to_bus(memory_bus)

        return device

    @classmethod
    def _create_instance(cls, dev_type, base_port, name):
        """Создать экземпляр устройства"""
        # Ленивые импорты
        try:
            if dev_type == "i8255":
                from modules.io.i8255 import I8255
                return I8255(base_port=base_port, name=name)
            elif dev_type == "i8253":
                from modules.io.i8253 import I8253
                return I8253(base_port=base_port, name=name)
            elif dev_type == "i8259":
                from modules.io.i8259 import I8259
                return I8259(base_port=base_port, name=name)
            elif dev_type == "i8257":
                from modules.io.i8257 import I8257
                return I8257(base_port=base_port, name=name)
            elif dev_type == "i8251":
                from modules.io.i8251 import I8251
                return I8251(base_port=base_port, name=name)
            elif dev_type == "i16550":
                from modules.io.i16550 import I16550
                return I16550(base_port=base_port, name=name)
            elif dev_type == "i8279":
                from modules.io.i8279 import I8279
                return I8279(base_port=base_port, name=name)
            elif dev_type == "i8276":
                from modules.io.i8276 import I8276
                return I8276(base_port=base_port, name=name)
            elif dev_type == "i8272":
                from modules.io.i8272 import I8272
                return I8272(base_port=base_port, name=name)
            elif dev_type == "i512vi1":
                from modules.io.i512vi1 import I512VI1
                return I512VI1(base_port=base_port, name=name)
            elif dev_type == "cf_ide":
                from modules.io.cf_ide import CFIDE
                return CFIDE(base_port=base_port, name=name)
            elif dev_type == "ch376s":
                from modules.io.ch376s import CH376S
                return CH376S(base_port=base_port, name=name)
            elif dev_type == "am9511":
                from modules.io.am9511 import AM9511
                return AM9511(base_port=base_port, name=name)
            elif dev_type == "lcd1602":
                from modules.io.lcd1602 import LCD1602
                return LCD1602(base_port=base_port, name=name)
            elif dev_type == "lcd2004":
                from modules.io.lcd2004 import LCD2004
                return LCD2004(base_port=base_port, name=name)
            elif dev_type == "tft8080":
                from modules.io.tft8080 import TFT8080
                return TFT8080(base_port=base_port, name=name)
            else:
                return None
        except ImportError:
            return None

    @classmethod
    def create_memory_region(cls, mem_config):
        """Создать регион памяти из конфигурации"""
        mem_type = mem_config.get("type", "ram")
        start = mem_config.get("start", 0)
        end = mem_config.get("end", 0xFFFF)
        name = mem_config.get("name", "RAM")
        file_path = mem_config.get("file", None)

        if mem_type == "ram":
            from modules.memory.memory_bus import RAMRegion
            return RAMRegion(start, end, name=name)
        elif mem_type == "rom":
            from modules.memory.memory_bus import ROMRegion
            data = {}
            if file_path:
                data = cls._load_rom_file(file_path, start)
            return ROMRegion(start, end, data=data, name=name)
        else:
            return None

    @staticmethod
    def _load_rom_file(path, start_addr):
        """Загрузить ROM-файл"""
        data = {}
        try:
            with open(path, 'rb') as f:
                rom_data = f.read()
            for i, byte in enumerate(rom_data):
                data[start_addr + i] = byte
        except Exception:
            pass
        return data
