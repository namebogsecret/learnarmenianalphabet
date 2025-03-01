"""
Модуль интервального повторения для Armenian Learning Bot.

Реализует алгоритм SuperMemo-2 для оптимального запоминания слов.
"""

from features.spaced_repetition.handlers import register_srs_handlers
from features.spaced_repetition.states import SRSStates

__all__ = [
    'register_srs_handlers',
    'SRSStates'
]