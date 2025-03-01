# Установка и настройка Armenian Learning Bot

Это руководство поможет вам настроить и запустить Armenian Learning Bot на вашем сервере.

## Предварительные требования

Для работы бота вам потребуется:

1. Python 3.9 или выше
2. Токен Telegram Bot API
3. API ключ OpenAI
4. (Опционально) API ключ для Text-to-Speech сервиса
5. Базовые навыки работы с командной строкой

## Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/yourusername/armenian-learning-bot.git
cd armenian-learning-bot
```

## Шаг 2: Создание виртуального окружения

```bash
python -m venv venv

# Активация в Windows
venv\Scripts\activate

# Активация в Linux/Mac
source venv/bin/activate
```

## Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

## Шаг 4: Настройка переменных окружения

Создайте файл `.env` в корневой директории проекта и добавьте следующие переменные:

```
# API ключи
TELEGRAM_API=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
TTS_API_KEY=your_tts_service_api_key  # Опционально для голосовой функции

# Настройки бота
MAX_USERS=100  # Ограничение количества пользователей
USERS=416177154,1234567  # Список разрешенных пользователей через запятую

# Настройки базы данных
DB_PATH=translations.db

# Настройки логирования
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=bot.log

# Настройки планировщика
DAILY_REMINDER_TIME=09:00  # Время ежедневных напоминаний
WEEKLY_REPORT_DAY=1  # День недели для отправки еженедельных отчетов (0 - понедельник, 6 - воскресенье)
WEEKLY_REPORT_TIME=10:00  # Время отправки еженедельных отчетов

# Настройки производительности
REQUEST_TIMEOUT=60  # Таймаут для запросов к внешним API (в секундах)
```

### Получение Telegram Bot API токена

1. Обратитесь к [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания нового бота
4. После создания бота вы получите токен API

### Получение OpenAI API ключа

1. Зарегистрируйтесь на [OpenAI Platform](https://platform.openai.com/)
2. Перейдите в раздел API keys
3. Создайте новый ключ API

## Шаг 5: Инициализация базы данных

```bash
python -m data.migrations.init_db
```

## Шаг 6: Запуск бота

```bash
python main.py
```

## Запуск в фоновом режиме (на сервере)

### Использование Screen (Linux)

```bash
screen -S armenian_bot
python main.py
# Нажмите Ctrl+A, затем D для отсоединения
```

Для повторного подключения к сессии:

```bash
screen -r armenian_bot
```

### Использование Systemd (Linux)

Создайте файл службы `/etc/systemd/system/armenian-bot.service`:

```ini
[Unit]
Description=Armenian Learning Telegram Bot
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/armenian-learning-bot
ExecStart=/path/to/armenian-learning-bot/venv/bin/python main.py
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=armenian-bot

[Install]
WantedBy=multi-user.target
```

Затем включите и запустите службу:

```bash
sudo systemctl enable armenian-bot
sudo systemctl start armenian-bot
```

Для проверки статуса:

```bash
sudo systemctl status armenian-bot
```

## Проверка работоспособности

После запуска бота найдите его в Telegram по имени, которое вы указали при создании бота, и отправьте команду `/start`. Бот должен ответить приветственным сообщением.

## Обновление словаря

Вы можете обновить словарь армянских переводов, отредактировав файл `data/dictionaries/armenian_dict.py`.

## Создание резервных копий

Регулярно создавайте резервные копии файла базы данных `translations.db`, который содержит словарь переводов, данные пользователей и прогресс обучения.

```bash
# Пример скрипта для резервного копирования
mkdir -p backups
cp translations.db backups/translations_$(date +%Y%m%d).db
```

## Устранение неполадок

### Бот не отвечает

1. Проверьте, что скрипт запущен и не содержит ошибок
2. Убедитесь, что токен Telegram API действителен
3. Проверьте журналы на наличие ошибок: `tail -f bot.log`

### Ошибки API OpenAI

1. Проверьте действительность ключа API
2. Проверьте баланс и ограничения вашей учетной записи OpenAI
3. Увеличьте значение `REQUEST_TIMEOUT` в файле `.env`

### Проблемы с базой данных

1. Убедитесь, что у процесса бота есть права на запись в директорию с базой данных
2. Попробуйте восстановить базу данных из резервной копии
3. Если база данных повреждена, запустите инициализацию заново: `python -m data.migrations.init_db`

## Мониторинг работы бота

Для мониторинга работы бота вы можете использовать стандартные инструменты Linux, такие как `htop`, `ps`, и просмотр журналов:

```bash
# Мониторинг процесса
ps aux | grep python

# Просмотр журналов
tail -f bot.log
```

## Дополнительные настройки

### Настройка лимитов пользователей

В файле `.env` вы можете настроить:

- `MAX_USERS`: максимальное количество пользователей
- `USERS`: список ID разрешенных пользователей (при пустом значении доступ открыт всем)

### Настройка уведомлений

Настройте время отправки напоминаний и отчетов:

- `DAILY_REMINDER_TIME`: время ежедневных напоминаний
- `WEEKLY_REPORT_DAY`: день недели для отправки еженедельных отчетов
- `WEEKLY_REPORT_TIME`: время отправки еженедельных отчетов

## Дополнительная информация

Для получения информации о доступных функциях бота см. [FEATURES.md](FEATURES.md).