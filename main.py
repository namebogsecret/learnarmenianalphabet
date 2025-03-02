#!/usr/bin/env python
import asyncio
import logging
import sys
import nest_asyncio
from aiogram import Bot, Dispatcher, types
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
    # In main.py, after setting up the dispatcher
    bot, dp = await setup_bot(config)

    # Now you can safely schedule tasks
    async def get_bot_info():
        try:
            bot_info = await bot.get_me()
            logger.info(f"Бот запущен. ID: {bot_info.id}, Имя: {bot_info.full_name}, Юзернейм: @{bot_info.username}")
            return bot_info
        except Exception as e:
            logger.error(f"Ошибка при получении информации о боте: {e}")
            raise

    # Now dp is fully initialized and has a loop
    asyncio.create_task(get_bot_info())
    
    # Настройка FSM
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(LoggingMiddleware())
    # async def log_all_messages(message: types.Message):
    #     logger.info(f"Received message: {message.text} from user {message.from_user.id}")
    #     return True

    # dp.register_message_handler(log_all_messages, lambda message: True, state="*")
    # Настройка middleware
    from core.middleware import setup_middlewares
    setup_middlewares(dp, config)

    # Регистрация обработчиков игр
    try:
        logger.info("Регистрация обработчиков игр")
        from features.games.handlers import register_games_handlers
        register_games_handlers(dp, config)
        logger.info("Обработчики игр успешно зарегистрированы")
    except Exception as e:
        logger.error(f"Ошибка при регистрации модуля игр: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
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