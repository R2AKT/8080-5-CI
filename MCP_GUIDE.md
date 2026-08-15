# MCP_GUIDE.md — Руководство по MCP-интеграции i8080-5 CI

> **Версия:** 1.0  
> **Дата:** 2026-08-15  
> **Протокол:** MCP (Model Context Protocol) через SSE-транспорт  
> **Зависимости:** `mcp`, `uvicorn`, `starlette`

---

## 📋 Содержание

1. [Обзор](#1-обзор)
2. [Установка и запуск](#2-установка-и-запуск)
3. [Подключение к MCP-серверу](#3-подключение-к-mcp-серверу)
4. [Tools — Управление эмулятором](#4-tools--управление-эмулятором)
5. [Tools — Состояние эмулятора](#5-tools--состояние-эмулятора)
6. [Tools — Точки останова](#6-tools--точки-останова)
7. [Tools — Анализ и трассировка](#7-tools--анализ-и-трассировка)
8. [Tools — Работа с устройством](#8-tools--работа-с-устройством)
9. [Tools — Память и файлы](#9-tools--память-и-файлы)
10. [Resources](#10-resources)
11. [Prompts](#11-prompts)
12. [Примеры рабочих процессов](#12-примеры-рабочих-процессов)
13. [Устранение неполадок](#13-устранение-неполадок)

---

## 1. Обзор

**i8080-5 CI** — комплексная среда для работы с процессором Intel 8080 и устройствами на его базе. Программа предоставляет:

- 🖥️ **Эмулятор i8080** — полная эмуляция процессора с отладчиком
- 🔌 **Работа с устройством** — чтение/запись памяти и портов через SLIP-протокол
- 🔍 **Дизассемблер** — дизассемблирование кода i8080
- 🤖 **MCP-сервер** — интеграция с AI-ассистентами через Model Context Protocol

**MCP-сервер** позволяет AI-ассистентам (Claude, Cursor, VS Code и др.) управлять программой через стандартизированный протокол MCP.

---

## 2. Установка и запуск

### 2.1. Установка зависимостей

```bash
pip install mcp uvicorn starlette pydantic pydantic-settings

### 2.2. Запуск программы с MCP-сервером

1.Запустите программу:
```bash
python i8080_CI.py

2.Перейдите на вкладку «Управление»
3.Нажмите кнопку «MCP Server: OFF» — она переключится на «MCP Server: ON»
4.MCP-сервер запустится по адресу: http://127.0.0.1:8000/sse

⚠️ Важно: MCP-сервер работает в отдельном потоке. Программа должна быть запущена для работы MCP-сервера.

## 3. Подключение к MCP-серверу

###3.1. Конфигурация для Claude Desktop
В файле claude_desktop_config.json:
```claude_desktop_config.json
{
  "mcpServers": {
    "i8080-ci": {
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}

### 3.3. Подключение через Python (для скриптов)
```python
from mcp.client.sse import sse_client
from mcp import ClientSession

async def connect():
    async with sse_client("http://127.0.0.1:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Список доступных tools
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  {tool.name}: {tool.description}")
## 4. Tools — Управление эмулятором

### 4.1. emu_reset — Сброс эмулятора
Сбрасывает все регистры, PC=0x0000, SP=0xFFFF, очищает IO-порты.

```json
{
  "tool": "emu_reset"
}

Ответ: "Эмулятор сброшен. PC=0x0000"

### 4.2. emu_step_into — Шаг с заходом (Step Into)
Выполняет одну инструкцию. Заходит внутрь CALL.

```json
{
  "tool": "emu_step_into"
}

### 4.3. emu_step_over — Шаг без захода (Step Over)
Выполняет одну инструкцию. CALL выполняется целиком.
```json
{
  "tool": "emu_step_over"
}

### 4.4. emu_run — Запуск эмулятора
Запускает эмулятор до точки останова, HLT или достижения лимита инструкций.
```json
{
  "tool": "emu_run",
  "arguments": { "max_instructions": 10000 }
}

Ответ: "Executed 1234 instructions. Status: halted. PC=0x0012"

### 4.5. emu_run_to — Выполнять до адреса (Run to Cursor)
``json
{
  "tool": "emu_run_to",
  "arguments": { "addr": 256 }
}

### 4.6. emu_stop — Остановить эмулятор
```json
{
  "tool": "emu_stop"
}

## 5. Tools — Состояние эмулятора

### 5.1. emu_get_state — Полное состояние
Возвращает все регистры, флаги, PC, SP, такты.
``json
{
  "tool": "emu_get_state"
}

Ответ:
```json
{
  "A": 85, "B": 0, "C": 0, "D": 0, "E": 0, "H": 0, "L": 0,
  "SP": 65535, "PC": 1,
  "BC": 0, "DE": 0, "HL": 0,
  "flags": {"S": 0, "Z": 0, "AC": 0, "P": 1, "CY": 0},
  "cycles": 7,
  "halted": 0, "running": 0, "interrupts": 0
}

### 5.2. emu_get_reg / emu_set_reg — Работа с регистрами
Допустимые регистры: A, B, C, D, E, H, L, BC, DE, HL, SP, PC
```json
{
  "tool": "emu_get_reg",
  "arguments": { "reg": "A" }
}

Ответ: "A = 0x55 (85)"
```json
{
  "tool": "emu_set_reg",
  "arguments": { "reg": "A", "val": 255 }
}

### 5.3. emu_get_psw / emu_set_psw — Работа с PSW
PSW = A (старший байт) + флаги (младший байт)
```json
{
  "tool": "emu_get_psw"
}
```json
{
  "tool": "emu_get_psw"
}
Ответ: "PSW = 0x5502"

### 5.4. emu_get_flags / emu_set_flag — Работа с флагами
Допустимые флаги: S, Z, AC, P, CY

```json
{
  "tool": "emu_get_flags"
}

Ответ:
```json
{ "S": 0, "Z": 0, "AC": 0, "P": 1, "CY": 0 }

```json
{
  "tool": "emu_set_flag",
  "arguments": { "flag": "CY", "val": true }
}

## 6. Tools — Точки останова

### 6.1. emu_add_breakpoint — Добавить точку останова
```json
{
  "tool": "emu_add_breakpoint",
  "arguments": { "addr": 256 }
}

### 6.2. emu_remove_breakpoint — Удалить точку останова
```json
{
  "tool": "emu_remove_breakpoint",
  "arguments": { "addr": 256 }
}

### 6.3. emu_list_breakpoints — Список всех точек останова
```json
{
  "tool": "emu_list_breakpoints"
}

Ответ:
```json
[
  "0x0100 [A == 0x55] ×3",
  "0x0200 (disabled) ×0",
  "0x0300 ×12"
]

### 6.4. emu_clear_breakpoints — Удалить все точки останова
```json
{
  "tool": "emu_clear_breakpoints"
}

### 6.5. emu_add_conditional_breakpoint — Условная точка останова
```json
{
  "tool": "emu_add_conditional_breakpoint",
  "arguments": {
    "addr": 256,
    "condition": "A == 0x55"
  }
}

Доступные переменные в условиях:

	Переменная					Описание							Пример
A, B, C, D, E, H, L			8-битные регистры					A == 0x55
BC, DE, HL					16-битные регистровые пары			HL > 0x1000
SP, PC						Указатель стека и счётчик команд	SP < 0xF000
S, Z, AC, P, CY				Флаги (0 или 1)						Z == 1
cycles						Счётчик тактов						cycles > 10000
mem[addr]					Байт памяти по адресу				mem[0x0100] == 0xFF
io[port]					Байт из IO-порта					io[0x01] == 0xFF

Примеры условий:
A == 0x55                          — остановка когда A станет 0x55
HL > 0x1000                        — когда HL превысит 0x1000
mem[0x0100] == 0xFF                — когда ячейка памяти станет FF
Z == 1                             — когда флаг Zero установлен
cycles > 10000                     — после 10000 тактов
HL > 0x1000 and Z == 0             — комбинация условий

### 6.6. emu_set_bp_condition — Изменить условие существующей BP
```json
{
  "tool": "emu_set_bp_condition",
  "arguments": {
    "addr": 256,
    "condition": "HL > 0x2000"
  }
}
Пустое условие делает BP обычной (безусловной).

### 6.7. emu_toggle_bp_enabled — Включить/выключить BP
```json
{
  "tool": "emu_toggle_bp_enabled",
  "arguments": { "addr": 256 }
}

Ответ: "Breakpoint 0x0100 disabled" или "Breakpoint 0x0100 enabled"

### 6.8. emu_get_bp_info — Информация о точке останова
```json
{
  "tool": "emu_get_bp_info",
  "arguments": { "addr": 256 }
}

Ответ:
```json
{
  "addr": "0x0100",
  "condition": "A == 0x55",
  "enabled": true,
  "hit_count": 3
}

## 7. Tools — Анализ и трассировка

### 7.1. emu_disassemble — Дизассемблирование
Дизассемблирует область памяти вокруг указанного адреса (по умолчанию — вокруг PC).
```json
{
  "tool": "emu_disassemble",
  "arguments": { "addr": 256, "length": 32 }
}

Ответ:
```json
[
  "►● 0100  MVI A,55h",
  "  0102  INR A",
  "  0103  JMP 0103h ; -> 0103h"
]

### 7.2. emu_get_stack — Содержимое стека
```json
{
  "tool": "emu_get_stack",
  "arguments": { "depth": 8 }
}

Ответ:
```json
[
  "FFFF: 0000 ← SP",
  "0001: 0000",
  "0002: 0000"
]

### 7.3. emu_trace — Трассировка выполнения
Выполняет N инструкций и возвращает лог с состоянием регистров.
```json
{
  "tool": "emu_trace",
  "arguments": { "n": 10 }
}

Ответ:
```json
[
  "[0000] MVI A,55h       A=55 BC=0000 DE=0000 HL=0000 SP=FFFF CY=0 Z=0",
  "[0002] INR A           A=56 BC=0000 DE=0000 HL=0000 SP=FFFF CY=0 Z=0",
  "[0003] JMP 0103h       A=56 BC=0000 DE=0000 HL=0000 SP=FFFF CY=0 Z=0",
  "Executed 10 instructions. PC=0x0103"
]

### 7.4. emu_get_io_ports — Состояние IO-портов
```json
{
  "tool": "emu_get_io_ports"
}

Ответ:
```json
{ "0x01": 85, "0x02": 0 }

## 8. Tools — Работа с устройством

⚠️ Требуют захвата шины. Перед работой с устройством вызовите hold_bus() и дождитесь wait_bus().

8.1. hold_bus / unhold_bus — Управление шиной
```json
{ "tool": "hold_bus" }

```json
{ "tool": "unhold_bus" }

### 8.2. wait_bus / wait_unhold — Ожидание шины
```json
{
  "tool": "wait_bus",
  "arguments": { "timeout": 5.0 }
}

### 8.3. dev_read_mem / dev_write_mem — Память устройства
json
{
  "tool": "dev_read_mem",
  "arguments": { "addr": 256 }
}

```json
{
  "tool": "dev_write_mem",
  "arguments": { "addr": 256, "val": 85 }
}

### 8.4. dev_read_io / dev_write_io — IO-порты устройства
```json
{
  "tool": "dev_read_io",
  "arguments": { "port": 1 }
}

```json
{
  "tool": "dev_write_io",
  "arguments": { "port": 1, "val": 255 }
}

## 9. Tools — Память и файлы

### 9.1. read_mem / write_mem — Локальная память
```json
{ "tool": "read_mem", "arguments": { "addr": 256 } }

```json
{ "tool": "write_mem", "arguments": { "addr": 256, "val": 85 } }

### 9.2. read_block / write_block — Блочные операции
```json
{ "tool": "read_block", "arguments": { "addr": 256, "size": 16 } }

```json
{
  "tool": "write_block",
  "arguments": { "addr": 256, "data": [62, 85, 60, 118] }
}

### 9.3. fill_mem — Заполнение диапазона
```json
{
  "tool": "fill_mem",
  "arguments": { "addr": 0, "size": 256, "val": 85 }
}

### 9.4. download / upload — Синхронизация с устройством
```json
{ "tool": "download", "arguments": { "addr": 0, "size": 256 } }

```json
{ "tool": "upload", "arguments": { "addr": 0, "size": 256 } }

### 9.5. disassemble / search — Дизассемблирование и поиск
```json
{
  "tool": "disassemble",
  "arguments": { "addr": 0, "length": 256, "show": true }
}

```json
{
  "tool": "search",
  "arguments": { "pattern": "C3", "mode": "hex" }
}

### 9.6. load_file / save_file — Работа с файлами
```json
{
  "tool": "load_file",
  "arguments": { "path": "firmware.hex", "base_addr": 0 }
}

```json
{
  "tool": "save_file",
  "arguments": { "path": "firmware.hex" }
}

### 9.7. get_status / refresh — Утилиты
```json
{ "tool": "get_status" }

Ответ:
```json
{
  "connected": true,
  "bus_active": true,
  "mem_size": 256,
  "max_block_size": 128
}

```json
{ "tool": "refresh" }

## 10. Resources
MCP Resources предоставляют доступ к данным программы.

	URI										Описание
memory://current						Текущий дамп памяти в формате HEX
memory://disassembly					Дизассемблированный код текущего образа
status://info							Информация о текущем состоянии программы
emulator://state						Текущее состояние эмулятора i8080
emulator://stack						Содержимое стека эмулятора
emulator://breakpoints					Список точек останова с условиями

Пример чтения ресурса:
```json
{
  "method": "resources/read",
  "params": { "uri": "emulator://state" }
}

Ответ:
Регистры:
  A=0x55  B=0x00  C=0x00
  D=0x00  E=0x00  H=0x00  L=0x00
  BC=0x0000  DE=0x0000  HL=0x0000
  SP=0xFFFF  PC=0x0001
Флаги: S=0 Z=0 AC=0 P=1 CY=0
Тактов: 7
Состояние: READY

## 11. Prompts
MCP Prompts — готовые шаблоны для AI-ассистентов.

### 11.1. analyze_firmware — Анализ прошивки
Параметры: focus — фокус анализа (по умолчанию: «общий анализ»)
```json
{
  "method": "prompts/get",
  "params": {
    "name": "analyze_firmware",
    "arguments": { "focus": "поиск точек входа" }
  }
}

### 11.2. find_bugs — Поиск потенциальных багов
Проверяет:
Бесконечные циклы без выхода
Обращения к несуществующим адресам
Недокументированные опкоды
Проблемы со стеком
Незавершённые подпрограммы (CALL без RET)

### 11.3. create_test_program — Создание тестовой программы
Параметры: description — описание тестовой программы

### 11.4. explain_code — Объяснение кода
Параметры: addr — начальный адрес (HEX), length — длина

### 11.5. debug_program — Комплексная отладка
Параметры: description — фокус отладки

### 11.6. find_infinite_loop — Поиск бесконечного цикла
Алгоритм:
Сброс эмулятора
Трассировка 100 инструкций
Поиск повторяющихся значений PC
Дизассемблирование области цикла
Анализ условий выхода

### 11.7. explain_instruction — Объяснение текущей инструкции

### 11.8. trace_execution — Подробная трассировка
Параметры: num_steps — количество шагов (по умолчанию: 20)

### 11.9. setup_conditional_debugging — Настройка отладки с условными BP
Автоматически расставляет условные точки останова в стратегических местах программы.

## 12. Примеры рабочих процессов

### 12.1. Загрузка прошивки и дизассемблирование

1. load_file(path="firmware.hex", base_addr=0)
2. disassemble(addr=0, length=256, show=true)

### 12.2. Отладка с условными точками останова

1. emu_reset()
2. emu_add_conditional_breakpoint(addr=0x0100, condition="A == 0x55")
3. emu_run(max_instructions=10000)
4. emu_get_state()
5. emu_disassemble(addr=0x0100, length=16)

### 12.3. Поиск бесконечного цикла

1. emu_reset()
2. emu_trace(n=100)
3. Проанализировать лог на повторяющиеся PC
4. emu_disassemble(addr=<адрес цикла>, length=32)

### 12.4. Работа с устройством

1. hold_bus()
2. wait_bus(timeout=5.0)
3. dev_read_mem(addr=0x0000)
4. dev_write_mem(addr=0x0000, val=0x55)
5. unhold_bus()

### 12.5. Создание и отладка тестовой программы

1. write_block(addr=0, data=[0x3E, 0x55, 0x3C, 0x76])
2. emu_reset()
3. emu_add_breakpoint(addr=0x0002)
4. emu_run(max_instructions=100)
5. emu_get_state()

### 12.6. Трассировка выполнения

1. emu_reset()
2. emu_trace(n=20)
3. Проанализировать лог

## 13. Устранение неполадок

Ошибка: «Emulator not initialized»
Эмулятор не инициализирован. Убедитесь, что программа запущена и вкладка «Эмулятор» открыта.

Ошибка: «Device not connected»
Устройство не подключено. Подключите устройство через COM-порт.

Ошибка: «Bus not active»
Шина не захвачена. Вызовите hold_bus() и дождитесь wait_bus().

Ошибка: «Syntax error in condition»
Неверный синтаксис условия точки останова. Проверьте синтаксис:
✅ Правильно:
A == 0x55
HL > 0x1000
mem[0x0100] == 0xFF
Z == 1
cycles > 10000

❌ Неправильно:
A = 0x55 (используйте ==)
A == 0x55 and (незавершённое выражение)
A == 0x55 and B == (незавершённое выражение)

Ошибка подключения к MCP-серверу
Убедитесь, что программа запущена
Убедитесь, что MCP-сервер запущен (кнопка «MCP Server: ON»)
Проверьте адрес: http://127.0.0.1:8000/sse
Проверьте, что порт 8000 не занят другим приложением

Ошибка: «MCP Server недоступен»
Установите зависимости:
```bash
pip install mcp uvicorn starlette pydantic pydantic-settings

## 📎 Приложение: Быстрая справка по Tools

### Эмулятор
	Tool					Описание
emu_reset				Сброс эмулятора
emu_step_into			Шаг с заходом
emu_step_over			Шаг без захода
emu_run					Запуск эмулятора
emu_run_to				Выполнять до адреса
emu_stop				Остановить эмулятор

### Состояние

			Tool					Описание
emu_get_state					Полное состояние
emu_get_reg / emu_set_reg		Работа с регистрами
emu_get_psw / emu_set_psw		Работа с PSW
emu_get_flags / emu_set_flag	Работа с флагами

### Точки останова

	Tool								Описание
emu_add_breakpoint					Добавить BP
emu_remove_breakpoint				Удалить BP
emu_list_breakpoints				Список всех BP
emu_clear_breakpoints				Удалить все BP
emu_add_conditional_breakpoint		Условная BP
emu_set_bp_condition				Изменить условие BP
emu_toggle_bp_enabled				Включить/выключить BP
emu_get_bp_info						Информация о BP

### Анализ

	Tool						Описание
emu_disassemble				Дизассемблирование
emu_get_stack				Содержимое стека
emu_trace					Трассировка выполнения
emu_get_io_ports			Состояние IO-портов

### Устройство

	Tool							Описание
hold_bus / unhold_bus			Управление шиной
wait_bus / wait_unhold			Ожидание шины
dev_read_mem / dev_write_mem	Память устройства
dev_read_io / dev_write_io		IO-порты устройства

### Память и файлы

	Tool							Описание
read_mem / write_mem			Локальная память
read_block / write_block		Блочные операции
fill_mem						Заполнение диапазона
download / upload				Синхронизация с устройством
disassemble / search			Дизассемблирование и поиск
load_file / save_file			Работа с файлами
get_status / refresh			Утилиты


Документация сгенерирована автоматически. Версия 1.0, 2026-08-15.
</think>
