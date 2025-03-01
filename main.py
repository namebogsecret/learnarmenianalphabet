#!/usr/bin/env python
import asyncio
import logging
import sys
import nest_asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from config.config import load_config
from config.logging_config import setup_logging

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
    
    # Применение nest_asyncio для работы в Jupyter Notebook, если нужно
    nest_asyncio.apply()
    
    # Инициализация бота и диспетчера
    bot = Bot(token=config.telegram_token)
    dp = Dispatcher(bot)
    dp.middleware.setup(LoggingMiddleware())
    
    # Импорт здесь, чтобы избежать циклических импортов
    from core.middleware import setup_middlewares
    from features.transliteration.handlers import register_transliteration_handlers
    from features.learning.handlers import register_learning_handlers
    from features.spaced_repetition.handlers import register_srs_handlers
    from features.games.handlers import register_games_handlers
    from features.voice_learning.handlers import register_voice_handlers
    from features.community.handlers import register_community_handlers
    from features.analytics.handlers import register_analytics_handlers
    from features.user_settings.handlers import register_settings_handlers
    
    # Настройка middleware
    setup_middlewares(dp, config)
    
    # Регистрация обработчиков
    register_transliteration_handlers(dp)
    
    # Регистрация новых обработчиков (если соответствующие модули готовы)
    # Раскомментируйте по мере имплементации каждого модуля
    # register_learning_handlers(dp)
    # register_srs_handlers(dp)
    # register_games_handlers(dp)
    # register_voice_handlers(dp)
    # register_community_handlers(dp)
    # register_analytics_handlers(dp)
    # register_settings_handlers(dp)
    
    # Импорт и настройка планировщика задач
    from core.scheduler import setup_scheduler
    scheduler = await setup_scheduler(bot, config)
    
    try:
        # Запуск сервисов
        logger.info("Bot started polling")
        await dp.start_polling()
    finally:
        # Закрытие сессий и соединений
        await bot.close()
        if scheduler and scheduler.running:
            scheduler.shutdown()
        logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user or system")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        sys.exit(1)