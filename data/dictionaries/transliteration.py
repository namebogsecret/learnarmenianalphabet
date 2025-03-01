"""
Модуль с функциями транслитерации.

Реализует функциональность для преобразования русских букв в армянские.
"""

import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Словарь для транслитерации русских букв в армянские
TRANSLITERATION_MAP: Dict[str, List[str]] = {
    'А': ['Ա', 'Ը'],
    'Б': ['Բ'],
    'В': ['Վ'],
    'Г': ['Գ'],
    'Д': ['Դ'],
    'Е': ['Ե', 'Է'],
    'Ё': ['Յո'],
    'Ж': ['Ժ'],
    'З': ['Զ'],
    'И': ['Ի'],
    'Й': ['Յ'],
    'К': ['Կ'],
    'Л': ['Լ'],
    'М': ['Մ'],
    'Н': ['Ն'],
    'О': ['Ո'],
    'П': ['Պ'],
    'Р': ['Ռ'],
    'С': ['Ս'],
    'Т': ['Տ'],
    'У': ['Ու'],
    'Ф': ['Ֆ'],
    'Х': ['Խ', 'Հ'],
    'Ц': ['Ց'],
    'Ч': ['Չ'],
    'Ш': ['Շ'],
    'Щ': ['Շ'],
    'Ъ': [''],
    'Ы': ['Ը'],
    'Ь': [''],
    'Э': ['Է'],
    'Ю': ['Յու'],
    'Я': ['Յա'],
    'а': ['ա', 'ը'],
    'б': ['բ'],
    'в': ['վ'],
    'г': ['գ'],
    'д': ['դ'],
    'е': ['ե', 'է'],
    'ё': ['յո'],
    'ж': ['ժ'],
    'з': ['զ'],
    'и': ['ի'],
    'й': ['յ'],
    'к': ['կ'],
    'л': ['լ'],
    'м': ['մ'],
    'н': ['ն'],
    'о': ['ո'],
    'п': ['պ'],
    'р': ['ռ'],
    'с': ['ս'],
    'т': ['տ'],
    'у': ['ու'],
    'ф': ['ֆ'],
    'х': ['խ', 'հ'],
    'ц': ['ց'],
    'ч': ['չ'],
    'ш': ['շ'],
    'щ': ['շ'],
    'ъ': [''],
    'ы': ['ը'],
    'ь': [''],
    'э': ['է'],
    'ю': ['յու'],
    'я': ['յա']
}

def transliterate_char(char: str) -> str:
    """
    Транслитерирует одну русскую букву в армянскую.
    
    Args:
        char: Русская буква.
        
    Returns:
        Армянская буква или исходная буква, если транслитерация не найдена.
    """
    if char in TRANSLITERATION_MAP:
        # Если есть несколько вариантов, выбираем случайный
        options = TRANSLITERATION_MAP[char]
        return random.choice(options) if options else char
    
    return char

def transliterate_text(text: str) -> str:
    """
    Транслитерирует русский текст на армянский.
    
    Args:
        text: Русский текст.
        
    Returns:
        Транслитерированный армянский текст.
    """
    result = ''.join(transliterate_char(char) for char in text)
    return result

async def transliterate_with_translation(text: str, include_translations: bool = True) -> str:
    """
    Транслитерирует текст и добавляет переводы слов в скобках, если они есть в словаре.
    
    Args:
        text: Исходный текст.
        include_translations: Флаг для включения переводов.
        
    Returns:
        Транслитерированный текст с переводами в скобках.
    """
    from data.dictionaries.armenian_dict import get_armenian_translation
    
    words = text.split()
    result = []
    
    for word in words:
        # Транслитерация слова
        transliterated_word = transliterate_text(word)
        
        # Если нужно добавить перевод и он есть в словаре
        if include_translations:
            translation = get_armenian_translation(word)
            if translation:
                transliterated_word += f" ({translation})"
        
        result.append(transliterated_word)
    
    return ' '.join(result)