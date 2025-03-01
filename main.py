#!/usr/bin/env python
import asyncio
import logging
import sys
import nest_asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from config.config import load_config
from config.logging_config import setup_logging
from data.migrations.init_db import run_migrations

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
        await run_migrations(config.db_path)
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return
    
    # Add after config is loaded but before bot starts polling
    from data.migrations import run_migrations
    await run_migrations(config.db_path)

    # Применение nest_asyncio для работы в Jupyter Notebook, если нужно
    nest_asyncio.apply()
    
    # Инициализация бота и диспетчера
    bot = Bot(token=config.telegram_token)
    dp = Dispatcher(bot)
    dp.middleware.setup(LoggingMiddleware())
    
    # Импорт здесь, чтобы избежать циклических импортов
    from features.transliteration.handlers import register_transliteration_handlers
    
    # Ensure config is passed to the transliteration handler registration
    register_transliteration_handlers(dp, config)
    
    # Запускаем бота
    try:
        logger.info("Bot started polling")
        await dp.start_polling()
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