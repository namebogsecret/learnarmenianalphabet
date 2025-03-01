"""
Пакет данных Armenian Learning Bot.

Содержит модели данных, словари для перевода и миграции базы данных.
"""

from data.models import (
    TranslationEntry,
    UnknownWordEntry,
    UserEntry
)

__all__ = [
    'TranslationEntry',
    'UnknownWordEntry',
    'UserEntry'
]