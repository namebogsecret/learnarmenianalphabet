#!/bin/bash

# Устанавливаем базовую директорию проекта
BASE_DIR="/root/learnarmenianalphabet"
cd "$BASE_DIR" || { echo "Директория $BASE_DIR не существует!"; exit 1; }

# Создаем основные файлы в корне проекта
touch main.py
touch .env
touch .gitignore
touch requirements.txt

# Создаем директорию config и файлы
mkdir -p config
touch config/__init__.py
touch config/config.py
touch config/logging_config.py

# Создаем директорию core и файлы
mkdir -p core
touch core/__init__.py
touch core/database.py
touch core/bot.py
touch core/middleware.py
touch core/scheduler.py

# Создаем директорию data и файлы
mkdir -p data
touch data/__init__.py
touch data/models.py

# Создаем поддиректорию dictionaries и файлы
mkdir -p data/dictionaries
touch data/dictionaries/__init__.py
touch data/dictionaries/armenian_dict.py
touch data/dictionaries/transliteration.py

# Создаем поддиректорию migrations и файлы
mkdir -p data/migrations
touch data/migrations/__init__.py
touch data/migrations/init_db.py

# Создаем директорию services и файлы
mkdir -p services
touch services/__init__.py
touch services/translation.py
touch services/openai_service.py
touch services/tts_service.py
touch services/analytics_service.py
touch services/user_service.py

# Создаем директорию features и поддиректории
mkdir -p features
touch features/__init__.py

# transliteration
mkdir -p features/transliteration
touch features/transliteration/__init__.py
touch features/transliteration/handlers.py
touch features/transliteration/utils.py

# learning
mkdir -p features/learning
touch features/learning/__init__.py
touch features/learning/handlers.py
touch features/learning/states.py
touch features/learning/utils.py

# spaced_repetition
mkdir -p features/spaced_repetition
touch features/spaced_repetition/__init__.py
touch features/spaced_repetition/handlers.py
touch features/spaced_repetition/states.py
touch features/spaced_repetition/algorithm.py
touch features/spaced_repetition/utils.py

# games
mkdir -p features/games
touch features/games/__init__.py
touch features/games/handlers.py
touch features/games/states.py
touch features/games/hangman.py
touch features/games/word_scramble.py
touch features/games/word_match.py

# voice_learning
mkdir -p features/voice_learning
touch features/voice_learning/__init__.py
touch features/voice_learning/handlers.py
touch features/voice_learning/utils.py

# community
mkdir -p features/community
touch features/community/__init__.py
touch features/community/handlers.py
touch features/community/states.py
touch features/community/utils.py

# analytics
mkdir -p features/analytics
touch features/analytics/__init__.py
touch features/analytics/handlers.py
touch features/analytics/reports.py

# user_settings
mkdir -p features/user_settings
touch features/user_settings/__init__.py
touch features/user_settings/handlers.py
touch features/user_settings/states.py
touch features/user_settings/defaults.py

# Создаем директорию keyboards и файлы
mkdir -p keyboards
touch keyboards/__init__.py
touch keyboards/inline.py
touch keyboards/reply.py

# Создаем директорию utils и файлы
mkdir -p utils
touch utils/__init__.py
touch utils/helpers.py
touch utils/exceptions.py

# Создаем директорию tests и файлы
mkdir -p tests
touch tests/__init__.py
touch tests/test_translations.py
touch tests/test_spaced_repetition.py
touch tests/test_games.py

# Создаем директорию docs и файлы
mkdir -p docs
touch docs/README.md
touch docs/SETUP.md
touch docs/FEATURES.md

echo "Структура проекта успешно создана в директории $BASE_DIR!"