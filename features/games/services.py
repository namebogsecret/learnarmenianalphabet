"""
Сервисные функции для игр.
"""
import logging
import random
from typing import List, Tuple

logger = logging.getLogger(__name__)


async def get_random_word_for_game(user_id: int, db_path: str = 'translations.db') -> Tuple[str, str]:
    """
    Получает случайное слово из базы данных для игры.
    
    Args:
        user_id: ID пользователя.
        db_path: Путь к файлу базы данных.
        
    Returns:
        Кортеж (слово, перевод).
    """
    from core.database import execute_query
    
    try:
        # Сначала пытаемся получить слова из карточек пользователя
        cards = await execute_query(
            """
            SELECT word, translation 
            FROM srs_cards 
            WHERE user_id = ?
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (user_id,),
            db_path,
            fetch=True
        )
        
        if cards and cards[0]:
            return cards[0]['word'], cards[0]['translation']
        
        # Если у пользователя нет карточек, берем из общего словаря
        words = await execute_query(
            """
            SELECT word, translation 
            FROM translation_dict
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (),
            db_path,
            fetch=True
        )
        
        if words and words[0]:
            return words[0]['word'], words[0]['translation']
        
        # Если в базе нет слов, возвращаем дефолтное
        return "армянский", "հայերեն"
        
    except Exception as e:
        logger.error(f"Ошибка при получении случайного слова: {e}")
        return "язык", "լեզու"

async def get_word_for_scramble(user_id: int, min_length: int = 4, max_length: int = 8, db_path: str = 'translations.db') -> Tuple[str, str]:
    """
    Получает подходящее слово для игры "Расшифровка слов".
    
    Args:
        user_id: ID пользователя.
        min_length: Минимальная длина слова.
        max_length: Максимальная длина слова.
        db_path: Путь к файлу базы данных.
        
    Returns:
        Кортеж (слово, перевод).
    """
    from core.database import execute_query
    
    try:
        # Пытаемся получить слово из карточек пользователя
        cards = await execute_query(
            """
            SELECT word, translation 
            FROM srs_cards 
            WHERE user_id = ? AND length(word) BETWEEN ? AND ?
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (user_id, min_length, max_length),
            db_path,
            fetch=True
        )
        
        if cards and cards[0]:
            return cards[0]['word'], cards[0]['translation']
        
        # Если у пользователя нет подходящих карточек, берем из общего словаря
        words = await execute_query(
            """
            SELECT word, translation 
            FROM translation_dict
            WHERE length(word) BETWEEN ? AND ?
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (min_length, max_length),
            db_path,
            fetch=True
        )
        
        if words and words[0]:
            return words[0]['word'], words[0]['translation']
        
        # Если в базе нет подходящих слов, возвращаем дефолтное
        return "армянский", "հայերեն"
        
    except Exception as e:
        logger.error(f"Ошибка при получении слова для игры 'Расшифровка слов': {e}")
        return "язык", "լեզու"


async def get_pairs_for_word_match(user_id: int, count: int = 5, db_path: str = 'translations.db') -> List[Tuple[str, str]]:
    """
    Получает пары слов для игры "Поиск соответствий".
    
    Args:
        user_id: ID пользователя.
        count: Количество пар слов.
        db_path: Путь к файлу базы данных.
        
    Returns:
        Список пар слов в формате [(русское, армянское), ...].
    """
    from core.database import execute_query
    
    try:
        # Пытаемся получить слова из карточек пользователя
        cards = await execute_query(
            """
            SELECT word, translation 
            FROM srs_cards 
            WHERE user_id = ?
            ORDER BY RANDOM()
            LIMIT ?
            """,
            (user_id, count),
            db_path,
            fetch=True
        )
        
        pairs = [(card['word'], card['translation']) for card in cards] if cards else []
        
        # Если у пользователя недостаточно карточек, добираем из общего словаря
        if len(pairs) < count:
            words = await execute_query(
                """
                SELECT word, translation 
                FROM translation_dict
                WHERE word NOT IN (SELECT word FROM srs_cards WHERE user_id = ?)
                ORDER BY RANDOM()
                LIMIT ?
                """,
                (user_id, count - len(pairs)),
                db_path,
                fetch=True
            )
            
            pairs.extend([(word['word'], word['translation']) for word in words] if words else [])
        
        # Если в базе недостаточно слов, добавляем дефолтные
        if len(pairs) < count:
            default_pairs = [
                ("привет", "բարև"),
                ("спасибо", "շնորհակալություն"),
                ("пожалуйста", "խնդրեմ"),
                ("да", "այո"),
                ("нет", "ոչ"),
                ("армянский", "հայերեն"),
                ("язык", "լեզու"),
                ("изучать", "սովորել"),
                ("слово", "բառ"),
                ("перевод", "թարգմանություն")
            ]
            
            # Добавляем только недостающие пары
            for i in range(min(count - len(pairs), len(default_pairs))):
                pairs.append(default_pairs[i])
        
        return pairs
        
    except Exception as e:
        logger.error(f"Ошибка при получении пар слов для игры 'Поиск соответствий': {e}")
        
        # В случае ошибки возвращаем базовые пары
        return [
            ("привет", "բարև"),
            ("спасибо", "շնորհակալություն"),
            ("да", "այո"),
            ("нет", "ոչ"),
            ("язык", "լեզու")
        ]