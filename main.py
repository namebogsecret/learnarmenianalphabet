#!/usr/bin/env python
import asyncio
import logging
import sys
import nest_asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from config.config import load_config
from config.logging_config import setup_logging

# Импорт миграций
from data.migrations import run_migrations

# Инициализация логирования
logger = logging.getLogger(__name__)

async def main():
    # Настройка логирования
    setup_logging()
    logger.info("Starting Armenian Learning Bot")
    
    # Загрузка конфигурации
    config = load_config()
    
    # Проверка конфигурации
    if not config.telegram_token:
        logger.error("Telegram token is missing. Please set TELEGRAM_API in .env file.")
        return
    
    # Инициализация базы данных
    try:
        logger.info("Initializing database...")
        from core.database import init_db
        await init_db(config.db_path)
        await run_migrations(config.db_path)
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return

    # Применение nest_asyncio для работы в Jupyter Notebook, если нужно
    nest_asyncio.apply()
    
    # Инициализация бота и диспетчера
    from core.bot import setup_bot
    bot, dp = await setup_bot(config)
    
    # Настройка FSM
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(LoggingMiddleware())
    
    # Настройка middleware
    from core.middleware import setup_middlewares
    setup_middlewares(dp, config)
    
    # Регистрация обработчиков транслитерации
    from features.transliteration.handlers import register_transliteration_handlers
    register_transliteration_handlers(dp, config)
    
    # Регистрация обработчиков SRS (интервальное повторение) если модуль существует
    try:
        from features.spaced_repetition.handlers import register_srs_handlers
        register_srs_handlers(dp, config)
        logger.info("SRS handlers registered successfully")
    except ImportError as e:
        logger.warning(f"SRS module not available: {e}")
    
    # Регистрация обработчиков игр если модуль существует
    try:
        # Проверяем, существует ли команда /games
        from features.games.handlers import cmd_games
        
        # Регистрируем обработчик команды /games
        dp.register_message_handler(cmd_games, commands=["games"])
        logger.info("Games command handler registered")
        
    except ImportError as e:
        logger.warning(f"Games module not available: {e}")
    
    # Запускаем бота с параметрами для предотвращения конфликтов
    try:
        logger.info("Bot started polling")
        await dp.start_polling(
            # Добавлены параметры для предотвращения конфликтов
            timeout=20,  # Увеличенный таймаут
            relax=0.1,   # Небольшая пауза между запросами
            reset_webhook=True  # Сбросить существующие вебхуки
        )
    except Exception as e:
        logger.error(f"Error during bot polling: {e}")
    finally:
        await bot.close()
        logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user or system")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        sys.exit(1)