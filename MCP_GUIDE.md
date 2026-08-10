# 🤖 MCP Server — интеграция с AI

**i8080-5 Master Controller** поддерживает **Model Context Protocol (MCP)**, что позволяет подключать AI-приложения (Claude, Cursor и др.) для интеллектуальной работы с прошивками i8080.

## 🚀 Быстрый старт

### 1. Запустите i8080 Master Controller

### 2. Включите MCP Server
Нажмите кнопку **"MCP Server: ON"** в интерфейсе.

### 3. Подключите AI-приложение

#### Claude Desktop
Отредактируйте `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "i8080": {
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}
```

Перезапустите Claude Desktop.

#### Cursor
**Settings → MCP** → добавьте URL `http://127.0.0.1:8000/sse`

## 📋 Доступные возможности

### Tools (21 инструмент)
- **Управление шиной**: `hold_bus`, `unhold_bus`, `wait_bus`
- **Локальная память**: `read_mem`, `write_mem`, `read_block`, `write_block`
- **Память устройства**: `dev_read_mem`, `dev_write_mem`, `dev_read_io`, `dev_write_io`
- **Синхронизация**: `download`, `upload`
- **Анализ**: `disassemble`, `search`
- **Файлы**: `load_file`, `save_file`
- **Утилиты**: `get_status`, `refresh`

### Resources (3 ресурса)
- `memory://current` — дамп памяти в HEX
- `memory://disassembly` — дизассемблированный код
- `status://info` — состояние программы

### Prompts (4 шаблона)
- `analyze_firmware` — анализ прошивки
- `find_bugs` — поиск багов
- `create_test_program` — создание тестовой программы
- `explain_code` — объяснение кода

## 💡 Примеры использования

### Анализ прошивки
```
Вы: Проанализируй прошивку i8080

Claude: [Вызывает download, disassemble, search]
        Найдено 15 команд JMP, 3 подпрограммы...
```

### Создание тестовой программы
```
Вы: Создай программу, которая мигает светодиодом на порту 0x01

Claude: [Создаёт программу, записывает в память, дизассемблирует]
        Программа готова и загружена в память!
```

### Поиск багов
```
Вы: Найди потенциальные баги в коде

Claude: [Анализирует код]
        Нашёл бесконечный цикл без выхода на адресе 0x0100...
```

## 🔧 Тестирование

Для проверки MCP сервера используйте тестовый клиент:
```bash
python test_mcp_client.py
```

## 📦 Зависимости

```bash
pip install fastmcp uvicorn starlette
```

## 🎯 Что можно делать с AI

- Автоматический анализ прошивок
- Поиск и исправление багов
- Создание тестовых программ
- Объяснение сложного кода
- Реверс-инжиниринг
- Оптимизация кода