"""
Профили систем: пресеты конфигурации для различных платформ.
Итерация 9.2: пресеты систем.

Поддерживаемые профили:
- empty: ПУСТОЙ (64кБ RAM, без устройств) 
- radio86rk: Радио-86РК
- micro80: Микро-80
- vector06c: Вектор-06Ц
- custom: Пользовательская конфигурация
"""
# =============================================
# ПРОФИЛЬ: ПУСТОЙ
# =============================================

EMPTY = """
[system]
name = "ПУСТОЙ"
cpu = "i8080"
clock_mhz = 2.5
description = "Пустой профиль"

# Память
[[memory]]
type = "ram"
start = 0x0000
end = 0xFFFF
name = "RAM-64K"
"""

# =============================================
# ПРОФИЛЬ: РАДИО-86РК
# =============================================

RADIO86RK = """
[system]
name = "Радио-86РК"
cpu = "i8080"
clock_mhz = 1.78
description = "Радио-86РК — одноплатный компьютер, 1986 г."

# Память
[[memory]]
type = "ram"
start = 0x0000
end = 0xBFFF
name = "RAM-48K"

[[memory]]
type = "rom"
start = 0xC000
end = 0xFFFF
name = "ROM-16K"
file = "radio86rk.rom"

# Устройства
[[devices]]
type = "i8255"
name = "PPI-0"
base_port = 0x00
description = "PPI для клавиатуры и дисплея"

[[devices]]
type = "i8253"
name = "PIT-0"
base_port = 0x04
description = "Таймер для звука"

# Настройки дисплея (эмуляция через PPI + RAM)
[display]
type = "text"
cols = 38
rows = 25
video_ram_start = 0x8000
font_start = 0xF800
"""

# =============================================
# ПРОФИЛЬ: МИКРО-80
# =============================================

MICRO80 = """
[system]
name = "Микро-80"
cpu = "i8080"
clock_mhz = 1.0
description = "Микро-80 — одноплатный компьютер, 1983 г."

# Память
[[memory]]
type = "ram"
start = 0x0000
end = 0x7FFF
name = "RAM-32K"

[[memory]]
type = "rom"
start = 0x8000
end = 0xFFFF
name = "ROM-32K"
file = "micro80.rom"

# Устройства
[[devices]]
type = "i8255"
name = "PPI-0"
base_port = 0x00
description = "PPI для клавиатуры и дисплея"

# Настройки дисплея
[display]
type = "text"
cols = 38
rows = 25
video_ram_start = 0x8000
font_start = 0xF800
"""

# =============================================
# ПРОФИЛЬ: ВЕКТОР-06Ц
# =============================================

VECTOR06C = """
[system]
name = "Вектор-06Ц"
cpu = "i8080"
clock_mhz = 3.0
description = "Вектор-06Ц — домашний компьютер, 1986 г."

# Память (банкирование через порты)
[[memory]]
type = "ram"
start = 0x0000
end = 0xFFFF
name = "RAM-64K"

[[memory]]
type = "rom"
start = 0xC000
end = 0xFFFF
name = "ROM-16K"
file = "vector06c.rom"

# Устройства
[[devices]]
type = "i8255"
name = "PPI-0"
base_port = 0x00
description = "PPI для клавиатуры"

[[devices]]
type = "i8253"
name = "PIT-0"
base_port = 0x04
description = "Таймер для звука"

[[devices]]
type = "i8257"
name = "DMA-0"
base_port = 0x08
description = "DMA для видео"

[[devices]]
type = "i8272"
name = "FDC-0"
base_port = 0x18
description = "Контроллер гибких дисков"

[[devices]]
type = "i8276"
name = "CRT-0"
base_port = 0x20
description = "CRT-контроллер"

[[devices]]
type = "lcd1602"
name = "LCD-0"
base_port = 0x30
description = "Символьный дисплей"

# Настройки дисплея
[display]
type = "graphics"
width = 512
height = 512
colors = 16
video_ram_start = 0x0000

# Настройки звука
[audio]
type = "beeper"
channels = 1
"""

# =============================================
# РЕЕСТР ПРОФИЛЕЙ
# =============================================

SYSTEM_PROFILES = {
    "empty": {
        "name": "ПУСТОЙ",
        "toml": EMPTY,
    },
    "radio86rk": {
        "name": "Радио-86РК",
        "toml": RADIO86RK,
    },
    "micro80": {
        "name": "Микро-80",
        "toml": MICRO80,
    },
    "vector06c": {
        "name": "Вектор-06Ц",
        "toml": VECTOR06C,
    },
}


def get_profile_names():
    """Список доступных профилей"""
    return list(SYSTEM_PROFILES.keys())


def get_profile(profile_name):
    """Получить профиль по имени"""
    return SYSTEM_PROFILES.get(profile_name, None)


def get_profile_toml(profile_name):
    """Получить TOML-строку профиля"""
    profile = SYSTEM_PROFILES.get(profile_name, None)
    if profile:
        return profile["toml"]
    return None
