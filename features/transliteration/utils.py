"""
Вспомогательные функции для модуля транслитерации.

Содержит утилиты для обработки текста, работы с неизвестными словами,
добавления переводов и т.д.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from core.database import (
    get_translation, add_translation as db_add_translation,
    update_unknown_word, check_unknown_word_threshold, remove_unknown_word
)
from data.dictionaries.transliteration import transliterate_text
from services.openai_service import translate_with_openai

logger = logging.getLogger(__name__)

async def process_text(text: str, db_path: str = 'translations.db') -> str:
    """
    Обрабатывает текст: разделяет на слова, транслитерирует и добавляет переводы.
    
    Args:
        text: Исходный текст.
        db_path: Путь к файлу базы данных.
        
    Returns:
        Обработанный текст с транслитерацией и переводами.
    """
    words = text.split()
    result = []
    
    for word in words:
        # Очищаем слово от знаков препинания для поиска перевода
        clean_word = re.sub(r'[^\w\s]', '', word).lower()
        
        if not clean_word:
            # Если слово состоит только из знаков препинания, просто добавляем его
            result.append(word)
            continue
        
        # Транслитерируем слово
        transliterated_word = transliterate_text(word)
        
        # Пытаемся найти перевод в базе данных
        translation = await get_translation(clean_word, db_path)
        
        if translation:
            # Если перевод найден, добавляем его в скобках
            transliterated_word += f" ({translation})"
        else:
            # Если перевод не найден, обрабатываем как неизвестное слово
            await process_unknown_word(clean_word, db_path)
        
        result.append(transliterated_word)
    
    return ' '.join(result)

async def process_unknown_word(word: str, db_path: str = 'translations.db',
                             threshold: int = 5) -> None:
    """
    Обрабатывает неизвестное слово: обновляет счетчик и запрашивает перевод при необходимости.
    
    Args:
        word: Неизвестное слово.
        db_path: Путь к файлу базы данных.
        threshold: Порог для запроса перевода.
    """
    if not word or len(word) <= 1:
        return
    
    try:
        # Обновляем счетчик неизвестного слова
        await update_unknown_word(word, 1, db_path)
        
        # Проверяем, не превысил ли счетчик порог
        if await check_unknown_word_threshold(word, threshold, db_path):
            # Запрашиваем перевод с помощью OpenAI
            translation = await translate_with_openai(word)
            
            if translation:
                # Добавляем перевод в словарь
                await add_translation(word, translation, db_path)
                
                # Удаляем слово из списка неизвестных
                await remove_unknown_word(word, db_path)
                
                logger.info(f"Добавлен новый перевод: '{word}' -> '{translation}'")
    except Exception as e:
        logger.error(f"Ошибка при обработке неизвестного слова '{word}': {e}")

async def add_translation(word: str, translation: str, db_path: str = 'translations.db') -> bool:
    """
    Добавляет новый перевод в базу данных и обновляет словарь.
    
    Args:
        word: Русское слово.
        translation: Армянский перевод.
        db_path: Путь к файлу базы данных.
        
    Returns:
        True, если перевод успешно добавлен, иначе False.
    """
    try:
        # Очищаем слово от знаков препинания
        clean_word = re.sub(r'[^\w\s]', '', word).lower()
        
        if not clean_word:
            return False
        
        # Добавляем перевод в базу данных
        success = await db_add_translation(clean_word, translation, db_path)
        
        # Обновляем словарь в памяти
        if success:
            from data.dictionaries.armenian_dict import enrich_dictionary_from_openai
            await enrich_dictionary_from_openai(clean_word, translation)
            
            # Удаляем слово из списка неизвестных, если оно там есть
            await remove_unknown_word(clean_word, db_path)
        
        return success
    except Exception as e:
        logger.error(f"Ошибка при добавлении перевода '{word}': {e}")
        return False

async def extract_word_and_translation(text: str) -> tuple[Optional[str], Optional[str]]:
    """
    Извлекает слово и перевод из текста.
    
    Поддерживает форматы:
    - "слово перевод"
    - "слово - перевод"
    - "слово = перевод"
    
    Args:
        text: Исходный текст.
        
    Returns:
        Кортеж (слово, перевод) или (None, None), если не удалось извлечь.
    """
    # Шаблоны для извлечения
    patterns = [
        r'^(\w+)\s+-\s+(\w+)$',  # слово - перевод
        r'^(\w+)\s+=\s+(\w+)$',  # слово = перевод
        r'^(\w+)\s+(\w+)$'       # слово перевод
    ]
    
    for pattern in patterns:
        match = re.match(pattern, text.strip())
        if match:
            return match.group(1).lower(), match.group(2)
    
    # Простой вариант: разделение по пробелу (если есть ровно 2 слова)
    parts = text.strip().split()
    if len(parts) == 2:
        return parts[0].lower(), parts[1]
    
    return None, None

async def process_batch_translation(text: str, db_path: str = 'translations.db') -> List[Dict[str, Any]]:
    """
    Обрабатывает пакетный ввод слов и переводов.
    
    Ожидает текст, где каждая строка содержит слово и перевод.
    
    Args:
        text: Текст с парами "слово перевод".
        db_path: Путь к файлу базы данных.
        
    Returns:
        Список результатов обработки каждой строки.
    """
    results = []
    
    for line in text.strip().split('\n'):
        if not line.strip():
            continue
        
        word, translation = await extract_word_and_translation(line)
        
        if word and translation:
            success = await add_translation(word, translation, db_path)
            results.append({
                'word': word,
                'translation': translation,
                'success': success
            })
        else:
            results.append({
                'line': line,
                'error': 'Неверный формат',
                'success': False
            })
    
    return results