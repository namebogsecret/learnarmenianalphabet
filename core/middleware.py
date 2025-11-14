"""
Модуль с middleware для бота.

Включает промежуточное ПО для ограничения доступа, ограничения скорости запросов
и другие компоненты, встраиваемые в цепочку обработки сообщений.
"""

import logging
import time
from typing import Dict, Set, Callable, Any, Union
from datetime import datetime, timedelta
from aiogram import Dispatcher, types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from config.config import Config
from core.database import add_or_update_user

logger = logging.getLogger(__name__)

class AccessControlMiddleware(BaseMiddleware):
    """
    Middleware для контроля доступа к боту.
    
    Проверяет, находится ли пользователь в списке разрешенных
    или не превышено ли максимальное количество пользователей.
    """
    
    def __init__(self, config: Config):
        """
        Инициализирует middleware контроля доступа.

        Args:
            config: Конфигурация с настройками доступа.
        """
        super().__init__()
        self.allowed_users = set(config.allowed_users)
        self.max_users = config.max_users
        self.db_path = config.db_path
        self.admin_username = config.admin_username
        self.test_message_limit = 5  # Количество тестовых сообщений для новых пользователей
    
    async def on_pre_process_message(self, message: types.Message, data: Dict):
        """
        Проверяет доступ пользователя перед обработкой сообщения.
        
        Args:
            message: Сообщение от пользователя.
            data: Данные обработчика.
            
        Raises:
            CancelHandler: Если пользователь не имеет доступа.
        """
        user_id = message.from_user.id
        username = message.from_user.username
        
        # Проверка, является ли пользователь разрешенным
        if user_id in self.allowed_users:
            # Обновляем статистику использования
            await add_or_update_user(user_id, username, self.db_path)
            return
        
        # Получаем количество обращений пользователя
        times = await add_or_update_user(user_id, username, self.db_path)
        
        # Проверка на тестовые сообщения
        if times == 1:
            await message.answer(f"У вас есть {self.test_message_limit} тестовых сообщений. Для продолжения работы обратитесь к администратору: @{self.admin_username}")
        elif times > self.test_message_limit:
            await message.answer(f"Ваши тестовые сообщения закончились. Для продолжения работы обратитесь к администратору: @{self.admin_username}")
            logger.info(f"Пользователь {user_id} ({username}) превысил лимит тестовых сообщений")
            raise CancelHandler()
    
    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: Dict):
        """
        Проверяет доступ пользователя перед обработкой callback query.
        
        Args:
            query: Запрос обратного вызова.
            data: Данные обработчика.
            
        Raises:
            CancelHandler: Если пользователь не имеет доступа.
        """
        user_id = query.from_user.id
        username = query.from_user.username
        
        # Проверка, является ли пользователь разрешенным
        if user_id in self.allowed_users:
            return
        
        # Получаем количество обращений пользователя
        times = await add_or_update_user(user_id, username, self.db_path)
        
        # Проверка на тестовые сообщения
        if times > self.test_message_limit:
            await query.answer("Ваши тестовые сообщения закончились. Для продолжения работы обратитесь к администратору.", show_alert=True)
            logger.info(f"Пользователь {user_id} ({username}) превысил лимит тестовых сообщений в callback query")
            raise CancelHandler()


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware для ограничения частоты запросов.
    
    Предотвращает слишком частые запросы от одного пользователя.
    """
    
    def __init__(self, limit: int = 5, period: int = 10):
        """
        Инициализирует middleware ограничения скорости.
        
        Args:
            limit: Максимальное количество запросов.
            period: Период времени в секундах.
        """
        super().__init__()
        self.limit = limit  # Максимальное количество запросов
        self.period = period  # Период в секундах
        self.user_requests: Dict[int, list] = {}  # {user_id: [timestamp1, timestamp2, ...]}
    
    def _clean_old_requests(self, user_id: int):
        """
        Очищает устаревшие запросы пользователя.
        
        Args:
            user_id: ID пользователя.
        """
        if user_id not in self.user_requests:
            return
        
        current_time = time.time()
        # Оставляем только запросы, произошедшие в течение заданного периода
        self.user_requests[user_id] = [
            timestamp for timestamp in self.user_requests[user_id]
            if current_time - timestamp < self.period
        ]
    
    async def on_pre_process_message(self, message: types.Message, data: Dict):
        """
        Проверяет ограничение скорости перед обработкой сообщения.
        
        Args:
            message: Сообщение от пользователя.
            data: Данные обработчика.
            
        Raises:
            CancelHandler: Если достигнут лимит запросов.
        """
        user_id = message.from_user.id
        current_time = time.time()
        
        # Очищаем устаревшие запросы
        self._clean_old_requests(user_id)
        
        # Добавляем текущий запрос
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        self.user_requests[user_id].append(current_time)
        
        # Проверяем, не превышен ли лимит
        if len(self.user_requests[user_id]) > self.limit:
            wait_time = int(self.period - (current_time - self.user_requests[user_id][0])) + 1
            await message.answer(f"Слишком много запросов. Пожалуйста, подождите {wait_time} секунд.")
            logger.warning(f"Пользователь {user_id} превысил лимит запросов")
            raise CancelHandler()


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для расширенного логирования запросов.
    
    Фиксирует информацию о входящих сообщениях и запросах.
    """
    
    def __init__(self):
        """Инициализирует middleware логирования."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    async def on_pre_process_message(self, message: types.Message, data: Dict):
        """
        Логирует входящее сообщение.
        
        Args:
            message: Сообщение от пользователя.
            data: Данные обработчика.
        """
        user = message.from_user
        text = message.text or message.caption or "[Нет текста]"
        
        log_text = (
            f"Сообщение от {user.full_name} (@{user.username}, ID: {user.id}): "
            f"'{text[:100]}{'...' if len(text) > 100 else ''}'"
        )
        
        if message.content_type != 'text':
            log_text += f" [content_type: {message.content_type}]"
        
        self.logger.info(log_text)
    
    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: Dict):
        """
        Логирует входящий callback query.
        
        Args:
            query: Запрос обратного вызова.
            data: Данные обработчика.
        """
        user = query.from_user
        
        log_text = (
            f"Callback query от {user.full_name} (@{user.username}, ID: {user.id}): "
            f"'{query.data}'"
        )
        
        self.logger.info(log_text)


def setup_middlewares(dp: Dispatcher, config: Config):
    """
    Настраивает все middleware для диспетчера.
    
    Args:
        dp: Диспетчер бота.
        config: Конфигурация бота.
    """
    # Middleware логирования
    dp.middleware.setup(LoggingMiddleware())
    
    # Middleware контроля доступа
    dp.middleware.setup(AccessControlMiddleware(config))
    
    # Middleware ограничения скорости
    dp.middleware.setup(RateLimitMiddleware(limit=10, period=15))
    
    logger.info("Middleware настроены")