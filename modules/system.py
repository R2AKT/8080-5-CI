"""
ComputerSystem — инкапсуляция полной компьютерной системы.
Итерация 9.3: интеграция всех модулей.

Объединяет:
- CPU (i8080 эмулятор)
- Шину памяти (MemoryBus)
- Все IO-устройства
- Профили систем (TOML)

Поддерживает:
- Загрузку из TOML-файла или профиля
- Динамическое добавление/удаление устройств
- Сохранение/восстановление состояний
"""
import os.path

from .memory.memory_bus import MemoryBus
from .config.device_config import DeviceConfig, DeviceFactory
from .config.system_profiles import get_profile, get_profile_names

class ComputerSystem:
    """Полная компьютерная система"""

    def __init__(self):
        self.bus = MemoryBus()
        self.devices = {}           # name -> device
        self.memory_regions = []    # список регионов памяти
        self.config = None          # текущая конфигурация
        self.profile_name = None    # имя профиля
        self.cpu = None             # ссылка на CPU (устанавливается извне)
        self._device_callbacks = {} # name -> callbacks (on_irq, on_drq и т.д.)

    def validate_profile_files(self):
        """Проверяет наличие файлов образов, указанных в конфигурации.
        Возвращает список ошибок (пустой список если всё в порядке)."""
        errors = []
        if self.config is None:
            return errors
        
        # Проверяем файлы образов из конфигурации
        for mem_config in self.config.memory_regions:
            if not isinstance(mem_config, dict):
                continue
            # Проверяем файл образа (если указан)
            image_file = mem_config.get("image_file") or mem_config.get("file")
            if image_file:
                # Относительный путь относительно рабочего каталога
                if not os.path.isabs(image_file):
                    image_path = os.path.join(os.getcwd(), image_file)
                else:
                    image_path = image_file
                if not os.path.isfile(image_path):
                    errors.append(f"Файл образа не найден: {image_file}")
        
        # Проверяем файлы устройств
        for dev_config in self.config.devices:
            if not isinstance(dev_config, dict):
                continue
            # Проверяем файлы образов устройств
            image_file = dev_config.get("image_file") or dev_config.get("file")
            if image_file:
                if not os.path.isabs(image_file):
                    image_path = os.path.join(os.getcwd(), image_file)
                else:
                    image_path = image_file
                if not os.path.isfile(image_path):
                    errors.append(f"Файл образа устройства не найден: {image_file}")
        
        return errors

    # =============================================
    # ЗАГРУЗКА КОНФИГУРАЦИИ
    # =============================================
    def load_from_toml_file(self, path):
        """Загрузить конфигурацию из TOML-файла"""
        self.config = DeviceConfig()
        self.config.load_from_file(path)
        self.profile_name = None
        self._apply_config()
        return self

    def load_from_toml_string(self, toml_string, name="Custom"):
        """Загрузить конфигурацию из TOML-строки"""
        self.config = DeviceConfig()
        self.config.load_from_string(toml_string)
        self.profile_name = name
        self._apply_config()
        return self

    def load_profile(self, profile_name):
        """Загрузка профиля системы (итерация 10.4)"""
        profile = get_profile(profile_name)
        if profile is None:
            raise ValueError(f"Профиль '{profile_name}' не найден. "
                             f"Доступные: {get_profile_names()}")

        # Внешний профиль: храним как dict
        if "config" in profile:
            self.config = DeviceConfig()
            self.config.load_from_dict(profile["config"])
            self.profile_name = profile_name
            self._apply_config()
            return self

        # Встроенный профиль: из TOML-строки
        return self.load_from_toml_string(profile.get("toml", ""), name=profile_name)

    # =============================================
    # ПРИМЕНЕНИЕ КОНФИГУРАЦИИ
    # =============================================
    def _apply_config(self):
        """Применить загруженную конфигурацию"""
        # Проверка конфигурации
        errors = self.config.validate()
        if errors:
            raise ValueError("Ошибки конфигурации:\n" + "\n".join(errors))

        # Очищаем предыдущее состояние
        self.reset_all()

        # Создаём и регистрируем память
        for mem_config in self.config.memory_regions:
            region = DeviceFactory.create_memory_region(mem_config)
            if region is not None:
                self.bus.register_memory(region)
                self.memory_regions.append(region)

        # Создаём и регистрируем устройства
        for dev_config in self.config.devices:
            device = DeviceFactory.create_device(dev_config, memory_bus=self.bus)
            if device is not None:
                name = dev_config.get("name", dev_config.get("type", "unknown"))
                self.devices[name] = device
                # Применяем дополнительные параметры
                self._apply_device_params(device, dev_config)

        # Виджет клавиатуры
        # === Подключаем клавиатуру к 8255 ===
        for dev_config in self.config.devices:
            dev_type = dev_config.get("type", "")
            dev_name = dev_config.get("name", "")
            
            if dev_type == "keyboard8x8":
                ppi_name = dev_config.get("ppi_device", "PPI")
                ppi = self.devices.get(ppi_name)
                kbd = self.devices.get(dev_name)
                if ppi and kbd:
                    output_port = dev_config.get("output_port", 0)
                    input_port = dev_config.get("input_port", 1)
                    kbd.connect_to_ppi(ppi, output_port, input_port)
            
            if dev_type == "keyboard8279":
                i8279_name = dev_config.get("i8279_device", "KBD")
                i8279 = self.devices.get(i8279_name)
                kbd = self.devices.get(dev_name)
                if i8279 and kbd:
                    kbd.connect_to_8279(i8279)
            
            # Подключаем чтение видеопамяти для CRT-контроллеров
            if dev_type in ("i8275", "i8276"):
                device = self.devices.get(dev_name)
                if device:
                    device.on_dma_read = lambda addr: self.bus.read(addr)
            
        # === Подключаем виртуальные устройства к 8255 ===
        for dev_config in self.config.devices:
            dev_type = dev_config.get("type", "")
            dev_name = dev_config.get("name", "")
            
            if dev_type == "cube3d":
                ppi_name = dev_config.get("ppi_device", "PPI")
                ppi = self.devices.get(ppi_name)
                cube = self.devices.get(dev_name)
                if ppi and cube:
                    port_x = dev_config.get("port_x", 0)
                    port_y = dev_config.get("port_y", 1)
                    port_z = dev_config.get("port_z", 2)
                    cube.connect_to_ppi(ppi, port_x, port_y, port_z)

        # === Подключаем дискретное видео к шине памяти ===
        for dev_config in self.config.devices:
            dev_type = dev_config.get("type", "")
            dev_name = dev_config.get("name", "")
            
            if dev_type == "discrete_video":
                device = self.devices.get(dev_name)
                if device:
                    device.connect_to_bus(self.bus)

    def _apply_device_params(self, device, config):
        """Применение дополнительных параметров устройства"""
        # Подключение образа диска (для CFIDE, CH376S)
        if "disk_image" in config and hasattr(device, 'set_disk_image'):
            device.set_disk_image(
                config["disk_image"],
                size_mb=config.get("disk_size_mb", 32)
            )

        # Путь к файлу NVM (для 512ВИ1)
        if "nvm_file" in config and hasattr(device, 'set_nvm_file'):
            device.set_nvm_file(config["nvm_file"])
            device.load_nvm()

        # Загрузка ROM-файла (для устройств с поддержкой)
        if "rom_file" in config and hasattr(device, 'load_rom'):
            device.load_rom(config["rom_file"])

        # Шрифт знакогенератора (для CRT)
        if "font_file" in config and hasattr(device, 'load_font_from_file'):
            device.load_font_from_file(config["font_file"])

    # =============================================
    # СБРОС
    # =============================================
    def reset_all(self):
        """Полный сброс системы"""
        # Отключение устройств от шины (если поддерживается)
        for device in self.devices.values():
            if hasattr(device, 'reset'):
                device.reset()

        self.devices.clear()
        self.memory_regions.clear()
        # Очистка шины памяти
        self.bus = MemoryBus()

    def reset_cpu(self):
        """Сброс CPU"""
        if self.cpu is not None and hasattr(self.cpu, 'reset'):
            self.cpu.reset()

    # =============================================
    # УПРАВЛЕНИЕ УСТРОЙСТВАМИ
    # =============================================
    def get_device(self, name):
        """Получить устройство по имени"""
        return self.devices.get(name, None)

    def get_devices_by_type(self, device_type):
        """Получить все устройства определённого типа"""
        result = []
        for device in self.devices.values():
            if device.__class__.__name__.lower() == device_type.lower():
                result.append(device)
        return result

    def list_devices(self):
        """Список устройств для Диспетчера устройств"""
        result = []
        for name, device in self.devices.items():
            base_port = getattr(device, 'base_port', -1)
            if base_port >= 0:
                port_str = f"0x{base_port:02X}"
            else:
                port_str = "-"  # Виртуальные устройства без портов
            result.append({
                "name": name,
                "type": type(device).__name__,
                "base_port": port_str,
            })
        return result

    def set_callback(self, device_name, callback_name, callback):
        """Установить callback для устройства (on_irq, on_drq, on_wait и т.д.)"""
        device = self.devices.get(device_name)
        if device is None:
            return False
        if hasattr(device, callback_name):
            setattr(device, callback_name, callback)
            return True
        return False

    def connect_cpu(self, cpu):
        """Подключить CPU к системе"""
        self.cpu = cpu
        # Подключаем шину памяти к CPU
        if hasattr(cpu, 'memory_bus'):
            cpu.memory_bus = self.bus
        if hasattr(cpu, 'io_bus'):
            cpu.io_bus = self.bus
        # Подключение WAIT-сигналов
        self.connect_wait_signals()

    # =============================================
    # ОБНОВЛЕНИЕ (для tick-based устройств)
    # =============================================
    def tick(self, cycles=1):
        """Вызывается каждый такт CPU для tick-based устройств"""
        for device in self.devices.values():
            if hasattr(device, 'tick'):
                device.tick(cycles)

    # =============================================
    # СОХРАНЕНИЕ/ЗАГРУЗКА NVM
    # =============================================
    def save_all_nvram(self):
        """Сохранить все NVM (для RTC, батарейных устройств)"""
        saved = []
        for name, device in self.devices.items():
            if hasattr(device, 'save_nvm'):
                if device.save_nvm():
                    saved.append(name)
        return saved

    def load_all_nvram(self):
        """Загрузить все NVM"""
        loaded = []
        for name, device in self.devices.items():
            if hasattr(device, 'load_nvm'):
                if device.load_nvm():
                    loaded.append(name)
        return loaded

    # =============================================
    # СОСТОЯНИЕ СИСТЕМЫ
    # =============================================
    def get_state(self):
        """Полное состояние системы для отладки"""
        return {
            "profile_name": self.profile_name,
            "system_name": self.config.system_name if self.config else None,
            "cpu": self.config.cpu if self.config else None,
            "clock_mhz": self.config.clock_mhz if self.config else None,
            "memory_regions": len(self.memory_regions),
            "devices_count": len(self.devices),
            "devices": {
                name: device.get_state() if hasattr(device, 'get_state') else None
                for name, device in self.devices.items()
            },
        }

    def print_state(self):
        """Вывод состояния в консоль"""
        state = self.get_state()
        print("=" * 60)
        print(f" Система: {state['system_name']}")
        print(f" Профиль: {state['profile_name']}")
        print(f" CPU: {state['cpu']} @ {state['clock_mhz']} МГц")
        print(f" Регионов памяти: {state['memory_regions']}")
        print(f" Устройств: {state['devices_count']}")
        print("-" * 60)
        for name, dev_state in state['devices'].items():
            if dev_state:
                print(f"  [{name}] {dev_state.get('name', '?')} "
                      f"@ {dev_state.get('base_port', '?')}")
        print("=" * 60)

    # =============================================
    # ПРЕРЫВАНИЯ (итерация 10.1)
    # =============================================
    def check_interrupts(self):
        """Проверка прерываний от всех устройств.
        Вызывается после каждой инструкции CPU."""
        if self.cpu is None:
            return

        for name, device in self.devices.items():
            if not hasattr(device, 'has_interrupt'):
                continue
            if not device.has_interrupt():
                continue

            # Определяем вектор прерывания
            vector = self._get_interrupt_vector(name, device)
            if vector is not None:
                self.cpu.request_interrupt(vector)
                device.acknowledge_interrupt()
                break  # Обрабатываем одно прерывание за раз

    def _get_interrupt_vector(self, device_name, device):
        """Определить вектор прерывания для устройства.
        По умолчанию: RST 7 (0xFF). Можно переопределить в конфигурации."""
        # Проверяем, есть ли пользовательский вектор в конфигурации
        if self.config:
            for dev_config in self.config.devices:
                if dev_config.get("name") == device_name:
                    return dev_config.get("irq_vector", 0xFF)

        # Вектор по умолчанию: RST 7
        return 0xFF

    # =============================================
    # ПДП
    # =============================================
    def check_dma(self):
        """Проверка активных DMA-запросов.
        Вызывается перед выполнением инструкций.
        Возвращает True, если CPU должен быть приостановлен (HOLD)."""
        dma_devices = self.get_devices_by_type("I8237")
        for dma in dma_devices:
            if hasattr(dma, 'is_active') and dma.is_active():
                # Выполняем передачу
                if hasattr(dma, 'perform_transfer'):
                    dma.perform_transfer(self.bus)
                return True  # CPU приостановлен
        return False

    # =============================================
    # Wait-state
    # =============================================
    def check_wait(self):
        """Проверка WAIT-сигналов от всех устройств.
        Возвращает True, если CPU должен ждать."""
        if self.cpu is None:
            return False
        for name, device in self.devices.items():
            if hasattr(device, 'is_busy') and device.is_busy():
                return True
        return False

    def connect_wait_signals(self):
        """Подключить on_wait коллбэки устройств к CPU."""
        if self.cpu is None:
            return
        for name, device in self.devices.items():
            if hasattr(device, 'on_wait'):
                device.on_wait = lambda active: self.cpu.set_wait(active)
