"""
Service for text translation.

Provides functions for translating text between languages.
"""

import logging
from typing import Optional, Dict, List, Tuple
from core.database import get_translation as db_get_translation, add_translation as db_add_translation
from services.openai_service import translate_with_openai, get_armenian_translation
from data.dictionaries.armenian_dict import TRANSLATION_DICT

logger = logging.getLogger(__name__)

async def get_translation(word: str, db_path: str = 'translations.db') -> Optional[str]:
    """
    Get translation for a word using the database and OpenAI if needed.
    
    Args:
        word: Word to translate.
        db_path: Path to the database file.
        
    Returns:
        Translation or None if not found.
    """
    # Try to get from database first
    translation = await db_get_translation(word.lower(), db_path)
    
    if translation:
        logger.debug(f"Translation for '{word}' found in database: {translation}")
        return translation
    
    # Try to get from static dictionary
    word_lower = word.lower()
    if word_lower in TRANSLATION_DICT:
        translation = TRANSLATION_DICT[word_lower]
        logger.debug(f"Translation for '{word}' found in static dictionary: {translation}")
        
        # Save to database for future use
        await db_add_translation(word_lower, translation, db_path)
        
        return translation
    
    return None

async def translate_and_save(word: str, db_path: str = 'translations.db', force_openai: bool = False) -> Optional[str]:
    """
    Translate a word and save it to the database.
    
    Args:
        word: Word to translate.
        db_path: Path to the database file.
        force_openai: Whether to force using OpenAI even if translation exists.
        
    Returns:
        Translation or None if failed.
    """
    if not force_openai:
        # Try to get existing translation
        translation = await get_translation(word, db_path)
        
        if translation:
            return translation
    
    try:
        # Get translation from OpenAI
        translation = await get_armenian_translation(word)
        
        if translation:
            # Save to database
            await db_add_translation(word.lower(), translation, db_path)
            logger.info(f"New translation added to database: '{word}' -> '{translation}'")
            
            # Add to static dictionary (for current session)
            from data.dictionaries.armenian_dict import enrich_dictionary_from_openai
            await enrich_dictionary_from_openai(word.lower(), translation)
            
            return translation
        
    except Exception as e:
        logger.error(f"Error translating word '{word}': {e}")
    
    return None

async def batch_translate(words: List[str], db_path: str = 'translations.db') -> Dict[str, Optional[str]]:
    """
    Translate a batch of words.
    
    Args:
        words: List of words to translate.
        db_path: Path to the database file.
        
    Returns:
        Dictionary mapping words to their translations.
    """
    result = {}
    
    for word in words:
        translation = await get_translation(word, db_path)
        
        if not translation:
            # If not found in database, try to get from OpenAI
            translation = await translate_and_save(word, db_path)
        
        result[word] = translation
    
    return result