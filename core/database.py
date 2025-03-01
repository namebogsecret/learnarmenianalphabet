"""
Модуль для работы с базой данных.

Обеспечивает асинхронное взаимодействие с SQLite базой данных через aiosqlite.
"""

import aiosqlite
import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

logger = logging.getLogger(__name__)

# Тип для представления данных результата запроса
QueryResult = Union[List[Dict[str, Any]], List[tuple], None]

async def get_db_connection(db_path: str = 'translations.db') -> aiosqlite.Connection:
    """
    Создает и возвращает соединение с базой данных.
    
    Args:
        db_path: Путь к файлу базы данных.
        
    Returns:
        Соединение с базой данных.
    """
    try:
        # Создаем директорию для БД, если она не существует
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        # Устанавливаем соединение
        connection = await aiosqlite.connect(db_path)
        # Настройка соединения для возврата строк как dict
        connection.row_factory = aiosqlite.Row
        
        return connection
    except Exception as e:
        logger.error(f"Ошибка при подключении к базе данных: {e}")
        raise

async def execute_query(
    query: str, 
    params: tuple = (), 
    db_path: str = 'translations.db',
    fetch: bool = False
) -> QueryResult:
    """
    Выполняет SQL-запрос к базе данных.
    
    Args:
        query: SQL-запрос.
        params: Параметры для SQL-запроса.
        db_path: Путь к файлу базы данных.
        fetch: Если True, возвращает результат запроса.
        
    Returns:
        Результат запроса, если fetch=True, иначе None.
    """
    connection = None
    try:
        connection = await get_db_connection(db_path)
        cursor = await connection.cursor()
        
        await cursor.execute(query, params)
        
        if fetch:
            rows = await cursor.fetchall()
            # Преобразуем результат в список словарей
            result = [dict(row) for row in rows]
            return result
        else:
            await connection.commit()
            return None
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        if connection:
            await connection.rollback()
        raise
    finally:
        if connection:
            await connection.close()

async def execute_script(script: str, db_path: str = 'translations.db') -> None:
    """
    Выполняет SQL-скрипт в базе данных.
    
    Args:
        script: SQL-скрипт.
        db_path: Путь к файлу базы данных.
    """
    connection = None
    try:
        connection = await get_db_connection(db_path)
        await connection.executescript(script)
        await connection.commit()
    except Exception as e:
        logger.error(f"Ошибка при выполнении скрипта: {e}")
        if connection:
            await connection.rollback()
        raise
    finally:
        if connection:
            await connection.close()

async def get_translation(word: str, db_path: str = 'translations.db') -> Optional[str]:
    """
    Получает перевод слова из базы данных.
    
    Args:
        word: Слово для перевода.
        db_path: Путь к файлу базы данных.
        
    Returns:
        Перевод слова или None, если перевод не найден.
    """
    try:
        result = await execute_query(
            "SELECT translation FROM translation_dict WHERE word = ?",
            (word.lower(),),
            db_path,
            fetch=True
        )
        
        if result and result[0]:
            return result[0].get('translation')
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении перевода: {e}")
        return None

async def add_translation(word: str, translation: str, db_path: str = 'translations.db') -> bool:
    """
    Добавляет новый перевод в базу данных.
    
    Args:
        word: Слово для перевода.
        translation: Перевод слова.
        db_path: Путь к файлу базы данных.
        
    Returns:
        True, если перевод успешно добавлен, иначе False.
    """
    try:
        await execute_query(
            "INSERT OR REPLACE INTO translation_dict (word, translation) VALUES (?, ?)",
            (word.lower(), translation),
            db_path
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка при добавлении перевода: {e}")
        return False

async def update_unknown_word(word: str, count: int = 1, db_path: str = 'translations.db') -> bool:
    """
    Обновляет счетчик неизвестного слова или добавляет его в базу.
    
    Args:
        word: Неизвестное слово.
        count: Значение счетчика.
        db_path: Путь к файлу базы данных.
        
    Returns:
        True, если слово успешно обновлено, иначе False.
    """
    try:
        # Проверяем, существует ли слово в таблице
        result = await execute_query(
            "SELECT count FROM unknown_words WHERE word = ?",
            (word.lower(),),
            db_path,
            fetch=True
        )
        
        if result and result[0]:
            # Слово существует, обновляем счетчик
            await execute_query(
                "UPDATE unknown_words SET count = count + ? WHERE word = ?",
                (count, word.lower()),
                db_path
            )
        else:
            # Слово не существует, добавляем его
            await execute_query(
                "INSERT INTO unknown_words (word, count) VALUES (?, ?)",
                (word.lower(), count),
                db_path
            )
        return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении неизвестного слова: {e}")
        return False

async def check_unknown_word_threshold(word: str, threshold: int = 10, db_path: str = 'translations.db') -> bool:
    """
    Проверяет, превысил ли счетчик неизвестного слова указанный порог.
    
    Args:
        word: Неизвестное слово.
        threshold: Пороговое значение счетчика.
        db_path: Путь к файлу базы данных.
        
    Returns:
        True, если счетчик превысил порог, иначе False.
    """
    try:
        result = await execute_query(
            "SELECT count FROM unknown_words WHERE word = ?",
            (word.lower(),),
            db_path,
            fetch=True
        )
        
        if result and result[0] and result[0].get('count', 0) >= threshold:
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке порога неизвестного слова: {e}")
        return False

async def remove_unknown_word(word: str, db_path: str = 'translations.db') -> bool:
    """
    Удаляет неизвестное слово из базы данных.
    
    Args:
        word: Неизвестное слово.
        db_path: Путь к файлу базы данных.
        
    Returns:
        True, если слово успешно удалено, иначе False.
    """
    try:
        await execute_query(
            "DELETE FROM unknown_words WHERE word = ?",
            (word.lower(),),
            db_path
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка при удалении неизвестного слова: {e}")
        return False

async def init_db(db_path: str = 'translations.db') -> None:
    """
    Инициализирует базу данных, создавая необходимые таблицы.
    
    Args:
        db_path: Путь к файлу базы данных.
    """
    init_script = """
    CREATE TABLE IF NOT EXISTS translation_dict (
        word TEXT PRIMARY KEY,
        translation TEXT
    );
    
    CREATE TABLE IF NOT EXISTS unknown_words (
        word TEXT PRIMARY KEY,
        count INTEGER DEFAULT 1
    );
    
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        user_name TEXT,
        times INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        await execute_script(init_script, db_path)
        logger.info(f"База данных инициализирована: {db_path}")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise

# Функции для работы с пользователями

async def add_or_update_user(user_id: int, username: str = None, db_path: str = 'translations.db') -> int:
    """
    Добавляет нового пользователя или обновляет существующего.
    
    Args:
        user_id: ID пользователя.
        username: Имя пользователя (опционально).
        db_path: Путь к файлу базы данных.
        
    Returns:
        Количество обращений пользователя к боту.
    """
    try:
        # Проверяем, существует ли пользователь
        result = await execute_query(
            "SELECT user_id, times FROM users WHERE user_id = ?",
            (user_id,),
            db_path,
            fetch=True
        )
        
        if result and result[0]:
            # Пользователь существует, обновляем счетчик и время последней активности
            await execute_query(
                """
                UPDATE users 
                SET times = times + 1, 
                    last_active = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                (user_id,),
                db_path
            )
            
            # Получаем обновленное значение счетчика
            updated_result = await execute_query(
                "SELECT times FROM users WHERE user_id = ?",
                (user_id,),
                db_path,
                fetch=True
            )
            
            return updated_result[0].get('times', 1) if updated_result else 1
        else:
            # Пользователь не существует, добавляем его
            await execute_query(
                """
                INSERT INTO users (user_id, user_name, times) 
                VALUES (?, ?, 1)
                """,
                (user_id, username),
                db_path
            )
            return 1
    except Exception as e:
        logger.error(f"Ошибка при добавлении/обновлении пользователя: {e}")
        return 1  # Возвращаем 1 в случае ошибки, предполагая первое обращение

async def get_user_count(db_path: str = 'translations.db') -> int:
    """
    Получает общее количество пользователей.
    
    Args:
        db_path: Путь к файлу базы данных.
        
    Returns:
        Количество пользователей.
    """
    try:
        result = await execute_query(
            "SELECT COUNT(*) as count FROM users",
            (),
            db_path,
            fetch=True
        )
        
        if result and result[0]:
            return result[0].get('count', 0)
        return 0
    except Exception as e:
        logger.error(f"Ошибка при получении количества пользователей: {e}")
        return 0

async def get_active_users(days: int = 7, db_path: str = 'translations.db') -> List[int]:
    """
    Получает список ID активных пользователей за указанный период.
    
    Args:
        days: Количество дней для определения активности.
        db_path: Путь к файлу базы данных.
        
    Returns:
        Список ID активных пользователей.
    """
    try:
        result = await execute_query(
            """
            SELECT user_id 
            FROM users 
            WHERE datetime(last_active) > datetime('now', ?)
            """,
            (f'-{days} days',),
            db_path,
            fetch=True
        )
        
        if result:
            return [row.get('user_id') for row in result]
        return []
    except Exception as e:
        logger.error(f"Ошибка при получении активных пользователей: {e}")
        return []