"""
Модуль игр для Armenian Learning Bot.

Содержит различные игры для изучения армянского языка:
- Виселица
- Поиск соответствий
- Расшифровка слов
"""

from features.games.handlers import register_games_handlers
from features.games.states import GameStates

__all__ = [
    'register_games_handlers',
    'GameStates'
]