/*
 @licstart  The following is the entire license notice for the JavaScript code in this file.

 The MIT License (MIT)

 Copyright (C) 1997-2020 by Dimitri van Heesch

 Permission is hereby granted, free of charge, to any person obtaining a copy of this software
 and associated documentation files (the "Software"), to deal in the Software without restriction,
 including without limitation the rights to use, copy, modify, merge, publish, distribute,
 sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all copies or
 substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
 BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

 @licend  The above is the entire license notice for the JavaScript code in this file
*/
var NAVTREE =
[
  [ "8080-5 CI", "index.html", [
    [ "MCP_GUIDE.md — Руководство по MCP-интеграции i8080-5 CI", "md__m_c_p___g_u_i_d_e.html", [
      [ "Содержание", "md__m_c_p___g_u_i_d_e.html#autotoc_md2", null ],
      [ "Обзор", "md__m_c_p___g_u_i_d_e.html#autotoc_md4", null ],
      [ "Запуск и подключение", "md__m_c_p___g_u_i_d_e.html#autotoc_md6", [
        [ "Запуск сервера", "md__m_c_p___g_u_i_d_e.html#autotoc_md7", null ],
        [ "Claude Desktop (claude_desktop_config.json)", "md__m_c_p___g_u_i_d_e.html#autotoc_md8", null ],
        [ "Cursor (.cursor/mcp.json)", "md__m_c_p___g_u_i_d_e.html#autotoc_md9", null ],
        [ "Python-клиент", "md__m_c_p___g_u_i_d_e.html#autotoc_md10", null ]
      ] ],
      [ "Tools: управление эмулятором", "md__m_c_p___g_u_i_d_e.html#autotoc_md12", null ],
      [ "Tools: состояние эмулятора", "md__m_c_p___g_u_i_d_e.html#autotoc_md14", null ],
      [ "Tools: точки останова", "md__m_c_p___g_u_i_d_e.html#autotoc_md16", [
        [ "Переменные условий", "md__m_c_p___g_u_i_d_e.html#autotoc_md17", null ]
      ] ],
      [ "Tools: анализ и трассировка", "md__m_c_p___g_u_i_d_e.html#autotoc_md19", null ],
      [ "Tools: шина и устройство", "md__m_c_p___g_u_i_d_e.html#autotoc_md21", null ],
      [ "Tools: память, файлы, утилиты", "md__m_c_p___g_u_i_d_e.html#autotoc_md23", null ],
      [ "Resources", "md__m_c_p___g_u_i_d_e.html#autotoc_md25", null ],
      [ "Prompts", "md__m_c_p___g_u_i_d_e.html#autotoc_md27", null ],
      [ "Типовые сценарии", "md__m_c_p___g_u_i_d_e.html#autotoc_md29", [
        [ "Загрузка и анализ прошивки", "md__m_c_p___g_u_i_d_e.html#autotoc_md30", null ],
        [ "Отладка с условной BP", "md__m_c_p___g_u_i_d_e.html#autotoc_md31", null ],
        [ "Поиск бесконечного цикла", "md__m_c_p___g_u_i_d_e.html#autotoc_md32", null ],
        [ "Дамп устройства", "md__m_c_p___g_u_i_d_e.html#autotoc_md33", null ]
      ] ],
      [ "Устранение неполадок", "md__m_c_p___g_u_i_d_e.html#autotoc_md35", null ]
    ] ],
    [ "SCRIPTS_GUIDE.md — Руководство по скриптам i8080-5 CI", "md__s_c_r_i_p_t_s___g_u_i_d_e.html", [
      [ "Содержание", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md39", null ],
      [ "Открытие вкладки скриптов", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md41", null ],
      [ "Интерфейс вкладки", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md42", null ],
      [ "Как пишутся скрипты", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md44", null ],
      [ "Справочник функций", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md46", [
        [ "📦 Локальная память (не требует устройства)", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md47", null ],
        [ "🔌 Память и порты устройства (требуют шину)", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md48", null ],
        [ "🔄 Синхронизация устройство ↔ образ (требуют шину)", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md49", null ],
        [ "🚌 Шина (требуют подключения)", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md50", null ],
        [ "📁 Файлы", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md51", null ],
        [ "🛠 Утилиты", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md52", null ]
      ] ],
      [ "Функции эмулятора (через api)", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md54", null ],
      [ "Примеры скриптов", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md56", [
        [ "Пример 1: Заполнить память паттерном", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md57", null ],
        [ "Пример 2: Дизассемблировать и вывести", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md58", null ],
        [ "Пример 3: Поиск в памяти", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md59", null ],
        [ "Пример 4: Поиск ASCII-строки", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md60", null ],
        [ "Пример 5: Работа с эмулятором", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md61", null ],
        [ "Пример 6: Проверка значения памяти", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md62", null ],
        [ "Пример 7: Работа с устройством (требует подключения)", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md63", null ],
        [ "Пример 8: Считать память устройства в образ", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md64", null ],
        [ "Пример 9: Состояние программы", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md65", null ],
        [ "Пример 10: Сложный скрипт — анализ диапазона", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md66", null ]
      ] ],
      [ "Советы и ограничения", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md68", [
        [ "✅ Советы", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md69", null ],
        [ "⚠️ Ограничения", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md70", null ],
        [ "🔍 Пример обработки ошибок подключения", "md__s_c_r_i_p_t_s___g_u_i_d_e.html#autotoc_md71", null ]
      ] ]
    ] ],
    [ "USER_GUIDE.md — Руководство пользователя i8080-5 CI", "md__u_s_e_r___g_u_i_d_e.html", [
      [ "Содержание", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md75", null ],
      [ "Обзор программы", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md77", null ],
      [ "Установка и запуск", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md79", [
        [ "2.1. Требования", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md80", null ],
        [ "2.2. Установка зависимостей", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md81", null ],
        [ "2.3. Запуск", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md82", null ]
      ] ],
      [ "Обзор интерфейса", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md84", [
        [ "Порядок вкладок", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md85", null ]
      ] ],
      [ "Вкладка «Управление»", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md87", [
        [ "4.1. Подключение к устройству", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md88", null ],
        [ "4.2. Управление шиной", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md89", null ],
        [ "4.3. Файлы", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md90", null ],
        [ "4.4. MCP-сервер", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md91", null ]
      ] ],
      [ "Вкладка «Данные»", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md93", [
        [ "5.1. Память (RAM/ROM)", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md94", null ],
        [ "5.2. IO-порты", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md95", null ]
      ] ],
      [ "Вкладка «Hex Редактор»", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md97", [
        [ "6.1. Обзор", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md98", null ],
        [ "6.2. Возможности", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md99", null ],
        [ "6.3. Диапазон", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md100", null ]
      ] ],
      [ "Вкладка «Дизассемблер»", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md102", [
        [ "7.1. Обзор", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md103", null ],
        [ "7.2. Управление", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md104", null ],
        [ "7.3. Изменение размера шрифта", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md105", null ]
      ] ],
      [ "Вкладка «Тест Памяти»", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md107", [
        [ "Параметры", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md108", null ],
        [ "Запуск", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md109", null ]
      ] ],
      [ "Вкладка «IO Секвенсор»", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md111", [
        [ "9.1. Одиночные операции IO", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md112", null ],
        [ "9.2. Последовательности", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md113", null ],
        [ "Управление", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md114", null ]
      ] ],
      [ "Вкладка «Сравнение»", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md116", [
        [ "Использование", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md117", null ],
        [ "Результаты", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md118", null ]
      ] ],
      [ "Вкладка «Скрипты»", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md120", [
        [ "Интерфейс", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md121", null ],
        [ "Доступные функции", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md122", null ]
      ] ],
      [ "Вкладка «Эмулятор»", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md124", [
        [ "12.1. Колонка 1: Дизассемблированный код", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md125", null ],
        [ "12.2. Колонка 2: Watch", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md126", null ],
        [ "12.3. Колонка 3: Breakpoints", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md127", null ],
        [ "12.4. Колонка 4: Регистры, Флаги, Стек, Статистика", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md128", null ],
        [ "12.5. Нижняя панель управления", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md129", null ],
        [ "12.6. Условные точки останова", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md130", null ]
      ] ],
      [ "Вкладка «Трассировка»", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md132", [
        [ "13.1. Панель управления", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md133", null ],
        [ "13.2. Поиск", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md134", null ],
        [ "13.3. Таблица трассировки", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md135", null ],
        [ "13.4. Экспорт", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md136", null ]
      ] ],
      [ "Горячие клавиши", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md138", [
        [ "Общие", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md139", null ],
        [ "Эмулятор", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md140", null ]
      ] ],
      [ "MCP-интеграция", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md142", [
        [ "Включение MCP-сервера", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md143", null ],
        [ "Конфигурация для Claude Desktop", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md144", null ]
      ] ],
      [ "Типовые сценарии работы", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md146", [
        [ "16.1. Загрузка и дизассемблирование прошивки", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md147", null ],
        [ "16.2. Отладка программы в эмуляторе", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md148", null ],
        [ "16.3. Условная отладка", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md149", null ],
        [ "16.4. Анализ с трассировкой", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md150", null ],
        [ "16.5. Работа с реальным устройством", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md151", null ],
        [ "16.6. Тестирование памяти устройства", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md152", null ],
        [ "16.7. Сравнение образов", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md153", null ]
      ] ],
      [ "Приложения", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md155", [
        [ "A. Поддерживаемые инструкции i8080", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md156", null ],
        [ "B. Протокол связи с устройством", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md157", null ],
        [ "C. Форматы файлов", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md158", null ],
        [ "D. Форматы пресетов", "md__u_s_e_r___g_u_i_d_e.html#autotoc_md159", null ]
      ] ]
    ] ],
    [ "Namespaces", "namespaces.html", [
      [ "Namespace List", "namespaces.html", "namespaces_dup" ],
      [ "Namespace Members", "namespacemembers.html", [
        [ "All", "namespacemembers.html", "namespacemembers_dup" ],
        [ "Functions", "namespacemembers_func.html", null ],
        [ "Variables", "namespacemembers_vars.html", "namespacemembers_vars" ]
      ] ]
    ] ],
    [ "Data Structures", "annotated.html", [
      [ "Data Structures", "annotated.html", "annotated_dup" ],
      [ "Data Structure Index", "classes.html", null ],
      [ "Class Hierarchy", "hierarchy.html", "hierarchy" ],
      [ "Data Fields", "functions.html", [
        [ "All", "functions.html", "functions_dup" ],
        [ "Functions", "functions_func.html", "functions_func" ],
        [ "Variables", "functions_vars.html", "functions_vars" ]
      ] ]
    ] ],
    [ "Files", "files.html", [
      [ "File List", "files.html", "files_dup" ]
    ] ]
  ] ]
];

var NAVTREEINDEX =
[
"_p_p_i__3_d__8x8x8___flame_8py.html",
"classi8080___c_i_1_1_disasm_view.html#aac9cbc85d83cab3705e7aa85899e8ebf",
"classi8080___c_i_1_1_main_window.html#a2f783dc0885a795152bcef5f9e05b507",
"classi8080___c_i_1_1_main_window.html#a7a2ca3426a468c6c4f456322d2430bf4",
"classi8080___c_i_1_1_main_window.html#ac316c659ceae0722a1b730e1d0abc511",
"classi8080___c_i_1_1_watch_model.html#a2d316aad921b4c8954cc8ce590bfdfd5",
"classmodules_1_1config_1_1device__config_1_1_device_config.html#a9bc4f015298fa46506b7b0dc2d9bfafe",
"classmodules_1_1io_1_1ch376s_1_1_c_h376_s.html#a694764ecc81574b23bb4cfcb282577ad",
"classmodules_1_1io_1_1i16550_1_1_i16550.html#adf4bd2d7d05db99d756c4214df41f08a",
"classmodules_1_1io_1_1i8255_1_1_i8255.html#ad7007b1de5637f55dfeeef586f13922f",
"classmodules_1_1io_1_1i8272_1_1_i8272.html#a5a7effb58abe0ae24336d8fa9e22581d",
"classmodules_1_1io_1_1i8275_1_1_i8275.html#aecbc052233262275fc20a8ee8dfb8a47",
"classmodules_1_1io_1_1keyboard8x8_1_1_keyboard8x8.html#ab1c71ea67aedbe0a4693720e04a8e8d7",
"classmodules_1_1memory_1_1memory__bus_1_1_r_a_m_region.html#aecbc052233262275fc20a8ee8dfb8a47",
"classtest__integration__full_1_1_mock_system.html#ac10f44caa2d44481ab51c01e8478c4a8",
"classui_1_1display__widgets_1_1_l_c_d_widget.html#adbdec58595587fea1750c91cd18315fb",
"functions_vars_p.html",
"namespace_p_p_i__3_d__8x8x8___rain.html#a343e78fb6e36c1ee55ef943361746f6e",
"namespacetest__banked__rom.html#ad5aa9f204496233a703e39fac5ca616a",
"namespacetest__i8255.html#abbff9c0a7a34491921148324d0ac11d9",
"namespacetest__system__integration.html#a993c16e0b66f383b44436c6b6223a67a"
];

var SYNCONMSG = 'click to disable panel synchronization';
var SYNCOFFMSG = 'click to enable panel synchronization';