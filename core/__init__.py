"""
Ядро приложения Armenian Learning Bot.

Этот пакет содержит основные компоненты, необходимые для работы бота:
- Настройка бота и его сессий
- Работа с базой данных
- Промежуточное ПО (middleware)
- Планировщик задач
"""

"""Core utilities for the bot."""

__all__ = [
    "setup_bot",
    "get_db_connection",
    "init_db",
    "setup_middlewares",
    "RateLimitMiddleware",
    "AccessControlMiddleware",
    "setup_scheduler",
]

def __getattr__(name):
    if name == "setup_bot":
        from .bot import setup_bot
        return setup_bot
    if name == "get_db_connection":
        from .database import get_db_connection
        return get_db_connection
    if name == "init_db":
        from .database import init_db
        return init_db
    if name == "setup_middlewares":
        from .middleware import setup_middlewares
        return setup_middlewares
    if name == "RateLimitMiddleware":
        from .middleware import RateLimitMiddleware
        return RateLimitMiddleware
    if name == "AccessControlMiddleware":
        from .middleware import AccessControlMiddleware
        return AccessControlMiddleware
    if name == "setup_scheduler":
        from .scheduler import setup_scheduler
        return setup_scheduler
    raise AttributeError(name)
