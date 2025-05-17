"""
Модуль транслитерации текста с русского на армянский.

Основной модуль, обеспечивающий базовую функциональность бота.
"""

"""Transliteration package."""

__all__ = [
    "register_transliteration_handlers",
    "process_unknown_word",
    "process_text",
    "add_translation",
]

def __getattr__(name):
    if name == "register_transliteration_handlers":
        from .handlers import register_transliteration_handlers
        return register_transliteration_handlers
    if name == "process_unknown_word":
        from .utils import process_unknown_word
        return process_unknown_word
    if name == "process_text":
        from .utils import process_text
        return process_text
    if name == "add_translation":
        from .utils import add_translation
        return add_translation
    raise AttributeError(name)
