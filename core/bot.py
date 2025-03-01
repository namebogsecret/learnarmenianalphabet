"""
Модуль для настройки и конфигурации бота.

Включает функции для создания и настройки экземпляра бота.
"""

import logging
from typing import Tuple
from typing import List, Dict, Optional
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config.config import Config

logger = logging.getLogger(__name__)

def setup_bot(config: Config) -> Tuple[Bot, Dispatcher]:
    """
    Создает и настраивает экземпляры бота и диспетчера.
    
    Args:
        config: Объект конфигурации.
        
    Returns:
        Кортеж (бот, диспетчер).
    """
    # Проверка наличия токена
    if not config.telegram_token:
        logger.error("Токен Telegram не указан. Проверьте переменную TELEGRAM_API в .env файле.")
        raise ValueError("Токен Telegram не указан")
    
    # Создание бота с настройками из конфигурации
    bot = Bot(token=config.telegram_token)
    
    # Использование хранилища в памяти для FSM
    # В продакшн-среде можно заменить на другое хранилище (Redis, MongoDB)
    storage = MemoryStorage()
    
    # Создание диспетчера
    dp = Dispatcher(bot, storage=storage)
    
    # Логирование информации о боте
    bot_info = None
    
    async def get_bot_info():
        nonlocal bot_info
        try:
            bot_info = await bot.get_me()
            logger.info(f"Бот запущен. ID: {bot_info.id}, Имя: {bot_info.full_name}, Юзернейм: @{bot_info.username}")
            return bot_info
        except Exception as e:
            logger.error(f"Ошибка при получении информации о боте: {e}")
            raise
    
    # Запланировать получение информации о боте при старте диспетчера
    dp.loop.create_task(get_bot_info())
    
    return bot, dp

async def send_message_to_admin(bot: Bot, config: Config, message: str) -> None:
    """
    Отправляет сообщение администратору бота.
    
    Args:
        bot: Экземпляр бота.
        config: Объект конфигурации.
        message: Текст сообщения.
    """
    if not config.allowed_users:
        logger.warning("Список администраторов пуст. Сообщение не отправлено.")
        return
    
    try:
        # Отправляем сообщение первому пользователю из списка разрешенных
        admin_id = config.allowed_users[0]
        await bot.send_message(admin_id, message)
        logger.info(f"Сообщение отправлено администратору {admin_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения администратору: {e}")

async def broadcast_message(bot: Bot, user_ids: List[int], message: str, parse_mode: str = None) -> Dict:
    """
    Отправляет сообщение нескольким пользователям.
    
    Args:
        bot: Экземпляр бота.
        user_ids: Список ID пользователей.
        message: Текст сообщения.
        parse_mode: Режим форматирования текста.
        
    Returns:
        Словарь с результатами отправки: {'success': количество успешных, 'failed': количество неудачных}.
    """
    results = {'success': 0, 'failed': 0}
    
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, message, parse_mode=parse_mode)
            results['success'] += 1
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
            results['failed'] += 1
    
    logger.info(f"Broadcast завершен. Успешно: {results['success']}, Неудачно: {results['failed']}")
    return results