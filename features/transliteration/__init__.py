"""
Модуль транслитерации текста с русского на армянский.

Основной модуль, обеспечивающий базовую функциональность бота.
"""

from features.transliteration.handlers import register_transliteration_handlers
from features.transliteration.utils import process_unknown_word, process_text, add_translation

__all__ = [
    'register_transliteration_handlers',
    'process_unknown_word',
    'process_text',
    'add_translation'
]