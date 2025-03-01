"""
Ядро приложения Armenian Learning Bot.

Этот пакет содержит основные компоненты, необходимые для работы бота:
- Настройка бота и его сессий
- Работа с базой данных
- Промежуточное ПО (middleware)
- Планировщик задач
"""

from core.bot import setup_bot
from core.database import get_db_connection, init_db
from core.middleware import setup_middlewares, RateLimitMiddleware, AccessControlMiddleware
from core.scheduler import setup_scheduler

__all__ = [
    'setup_bot',
    'get_db_connection',
    'init_db',
    'setup_middlewares',
    'RateLimitMiddleware',
    'AccessControlMiddleware',
    'setup_scheduler',
]