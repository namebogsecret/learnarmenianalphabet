armenian_bot/
│
├── main.py                      # Основной файл запуска бота
├── .env                         # Файл с переменными окружения (API-ключи)
├── .gitignore                   # Игнорируемые файлы для Git
├── requirements.txt             # Зависимости проекта
│
├── config/                      # Файлы конфигурации
│   ├── __init__.py
│   ├── config.py                # Основные настройки
│   └── logging_config.py        # Конфигурация логирования
│
├── core/                        # Ядро приложения
│   ├── __init__.py
│   ├── database.py              # Асинхронные операции с базой данных (aiosqlite)
│   ├── bot.py                   # Конфигурация бота
│   ├── middleware.py            # Мидлвар для бота (логирование, ограничение доступа)
│   └── scheduler.py             # Планировщик для регулярных задач
│
├── data/                        # Данные и модели
│   ├── __init__.py
│   ├── models.py                # Модели данных
│   ├── dictionaries/            # Словари для перевода
│   │   ├── __init__.py
│   │   ├── armenian_dict.py     # Словарь армянских слов
│   │   └── transliteration.py   # Функции транслитерации
│   └── migrations/              # Миграции базы данных
│       ├── __init__.py
│       └── init_db.py           # Инициализация базы данных
│
├── services/                    # Сервисы приложения
│   ├── __init__.py
│   ├── translation.py           # Сервис перевода
│   ├── openai_service.py        # Взаимодействие с OpenAI API
│   ├── tts_service.py           # Сервис озвучивания текста
│   ├── analytics_service.py     # Сервис аналитики
│   └── user_service.py          # Сервис пользователей
│
├── features/                    # Функциональные модули
│   ├── __init__.py
│   ├── transliteration/         # Модуль транслитерации
│   │   ├── __init__.py
│   │   ├── handlers.py
│   │   └── utils.py
│   ├── learning/                # Модуль обучения
│   │   ├── __init__.py
│   │   ├── handlers.py
│   │   ├── states.py
│   │   └── utils.py
│   ├── spaced_repetition/       # Интервальное повторение
│   │   ├── __init__.py
│   │   ├── handlers.py
│   │   ├── states.py
│   │   ├── algorithm.py
│   │   └── utils.py
│   ├── games/                   # Модуль игр
│   │   ├── __init__.py
│   │   ├── handlers.py
│   │   ├── states.py
│   │   ├── hangman.py
│   │   ├── word_scramble.py
│   │   └── word_match.py
│   ├── voice_learning/          # Модуль голосового обучения
│   │   ├── __init__.py
│   │   ├── handlers.py
│   │   └── utils.py
│   ├── basic_expressions/       # Базовые слова и выражения
│   │   ├── __init__.py
│   │   └── utils.py
│   ├── community/               # Модуль сообщества
│   │   ├── __init__.py
│   │   ├── handlers.py
│   │   ├── states.py
│   │   └── utils.py
│   ├── analytics/               # Модуль аналитики
│   │   ├── __init__.py
│   │   ├── handlers.py
│   │   └── reports.py
│   └── user_settings/           # Настройки пользователя
│       ├── __init__.py
│       ├── handlers.py
│       ├── states.py
│       └── defaults.py
│
├── keyboards/                   # Клавиатуры для бота
│   ├── __init__.py
│   ├── inline.py                # Инлайн клавиатуры
│   └── reply.py                 # Обычные клавиатуры
│
├── utils/                       # Вспомогательные утилиты
│   ├── __init__.py
│   ├── helpers.py               # Общие вспомогательные функции
│   └── exceptions.py            # Пользовательские исключения
│
├── tests/                       # Тесты
│   ├── __init__.py
│   ├── test_translations.py
│   ├── test_spaced_repetition.py
│   └── test_games.py
│
└── docs/                        # Документация
    ├── README.md                # Основная документация
    ├── SETUP.md                 # Инструкция по установке
    └── FEATURES.md              # Описание функций бота