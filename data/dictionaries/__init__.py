"""
Пакет словарей для перевода.

Включает словари для армянского языка и функции транслитерации.
"""

from data.dictionaries.armenian_dict import TRANSLATION_DICT, get_armenian_translation
from data.dictionaries.transliteration import TRANSLITERATION_MAP, transliterate_text

__all__ = [
    'TRANSLATION_DICT',
    'get_armenian_translation',
    'TRANSLITERATION_MAP',
    'transliterate_text'
]