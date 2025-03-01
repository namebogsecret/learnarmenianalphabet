"""
Модуль для инициализации и миграции базы данных.

Содержит скрипты для создания необходимых таблиц и заполнения начальными данными.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiosqlite
from core.database import execute_script, execute_query
from data.dictionaries.armenian_dict import TRANSLATION_DICT

logger = logging.getLogger(__name__)

# Таблицы базы данных с их SQL-определениями
TABLES: Dict[str, str] = {
    # Основные таблицы
    "translation_dict": """
        CREATE TABLE IF NOT EXISTS translation_dict (
            word TEXT PRIMARY KEY,
            translation TEXT
        )
    """,
    
    "unknown_words": """
        CREATE TABLE IF NOT EXISTS unknown_words (
            word TEXT PRIMARY KEY,
            count INTEGER DEFAULT 1
        )
    """,
    
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            user_name TEXT,
            times INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    # Таблицы для расширенных функций
    "user_progress": """
        CREATE TABLE IF NOT EXISTS user_progress (
            user_id INTEGER,
            path TEXT,
            level INTEGER,
            completed_words TEXT,
            completed_phrases TEXT,
            PRIMARY KEY (user_id, path)
        )
    """,
    
    "srs_cards": """
        CREATE TABLE IF NOT EXISTS srs_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            word TEXT,
            translation TEXT,
            easiness REAL DEFAULT 2.5,
            interval INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            next_review DATE,
            last_review DATE
        )
    """,
    
    "user_settings": """
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            reminder_time TEXT DEFAULT '09:00',
            difficulty_level TEXT DEFAULT 'normal',
            daily_goal INTEGER DEFAULT 5,
            notification_enabled BOOLEAN DEFAULT 1,
            game_sounds BOOLEAN DEFAULT 1,
            theme TEXT DEFAULT 'default',
            custom_settings TEXT
        )
    """,
    
    "user_activity": """
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity_type TEXT,
            timestamp DATETIME,
            details TEXT
        )
    """,
    
    "user_stats": """
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            words_translated INTEGER DEFAULT 0,
            words_learned INTEGER DEFAULT 0,
            quiz_score INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            last_active DATE
        )
    """,
    
    # Таблицы для функций сообщества
    "community_content": """
        CREATE TABLE IF NOT EXISTS community_content (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            content_type TEXT,
            russian_text TEXT,
            armenian_text TEXT,
            description TEXT,
            tags TEXT,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            created_at TIMESTAMP
        )
    """,
    
    "user_collections": """
        CREATE TABLE IF NOT EXISTS user_collections (
            user_id INTEGER,
            collection_name TEXT,
            content_ids TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            PRIMARY KEY (user_id, collection_name)
        )
    """,
    
    "content_ratings": """
        CREATE TABLE IF NOT EXISTS content_ratings (
            user_id INTEGER,
            content_id TEXT,
            rating INTEGER,
            PRIMARY KEY (user_id, content_id)
        )
    """
}

# Индексы для оптимизации запросов
INDICES: Dict[str, str] = {
    "idx_user_activity_user_id": "CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity (user_id)",
    "idx_user_activity_timestamp": "CREATE INDEX IF NOT EXISTS idx_user_activity_timestamp ON user_activity (timestamp)",
    "idx_srs_cards_next_review": "CREATE INDEX IF NOT EXISTS idx_srs_cards_next_review ON srs_cards (next_review)",
    "idx_srs_cards_user_id": "CREATE INDEX IF NOT EXISTS idx_srs_cards_user_id ON srs_cards (user_id)",
    "idx_community_content_tags": "CREATE INDEX IF NOT EXISTS idx_community_content_tags ON community_content (tags)",
    "idx_community_content_user_id": "CREATE INDEX IF NOT EXISTS idx_community_content_user_id ON community_content (user_id)",
    "idx_unknown_words_count": "CREATE INDEX IF NOT EXISTS idx_unknown_words_count ON unknown_words (count)"
}

async def setup_basic_tables(db_path: str = 'translations.db') -> None:
    """
    Создает основные таблицы базы данных.
    
    Args:
        db_path: Путь к файлу базы данных.
    """
    # Создаем базовые таблицы
    basic_tables = ["translation_dict", "unknown_words", "users"]
    
    conn = None
    try:
        conn = await aiosqlite.connect(db_path)
        
        for table_name in basic_tables:
            if table_name in TABLES:
                await conn.execute(TABLES[table_name])
        
        await conn.commit()
        logger.info(f"Основные таблицы созданы в базе данных: {db_path}")
    except Exception as e:
        logger.error(f"Ошибка при создании основных таблиц: {e}")
        if conn:
            await conn.rollback()
        raise
    finally:
        if conn:
            await conn.close()

async def setup_advanced_tables(db_path: str = 'translations.db') -> None:
    """
    Создает дополнительные таблицы для расширенных функций.
    
    Args:
        db_path: Путь к файлу базы данных.
    """
    # Создаем расширенные таблицы
    advanced_tables = [
        "user_progress", "srs_cards", "user_settings", 
        "user_activity", "user_stats", "community_content", 
        "user_collections", "content_ratings"
    ]
    
    conn = None
    try:
        conn = await aiosqlite.connect(db_path)
        
        for table_name in advanced_tables:
            if table_name in TABLES:
                await conn.execute(TABLES[table_name])
        
        # Создаем индексы
        for index_name, index_sql in INDICES.items():
            await conn.execute(index_sql)
        
        await conn.commit()
        logger.info(f"Дополнительные таблицы и индексы созданы в базе данных: {db_path}")
    except Exception as e:
        logger.error(f"Ошибка при создании дополнительных таблиц: {e}")
        if conn:
            await conn.rollback()
        raise
    finally:
        if conn:
            await conn.close()

async def fill_translation_dict(db_path: str = 'translations.db') -> None:
    """
    Заполняет таблицу translation_dict начальными данными из словаря.
    
    Args:
        db_path: Путь к файлу базы данных.
    """
    conn = None
    try:
        conn = await aiosqlite.connect(db_path)
        
        # Подготовка данных для массовой вставки
        data = [(word, translation) for word, translation in TRANSLATION_DICT.items()]
        
        # Вставка данных пакетами по 100 записей
        batch_size = 100
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            await conn.executemany(
                "INSERT OR IGNORE INTO translation_dict (word, translation) VALUES (?, ?)",
                batch
            )
        
        await conn.commit()
        logger.info(f"Словарь переводов заполнен {len(data)} записями")
    except Exception as e:
        logger.error(f"Ошибка при заполнении словаря переводов: {e}")
        if conn:
            await conn.rollback()
        raise
    finally:
        if conn:
            await conn.close()

async def run_migrations(db_path: str = 'translations.db') -> None:
    """
    Запускает все миграции базы данных.
    
    Args:
        db_path: Путь к файлу базы данных.
    """
    try:
        # Шаг 1: Создание основных таблиц
        await setup_basic_tables(db_path)
        
        # Шаг 2: Заполнение словаря переводов
        await fill_translation_dict(db_path)
        
        # Шаг 3: Создание дополнительных таблиц
        await setup_advanced_tables(db_path)
        
        logger.info(f"Миграции успешно выполнены для базы данных: {db_path}")
    except Exception as e:
        logger.error(f"Ошибка при выполнении миграций: {e}")
        raise

async def check_db_version(db_path: str = 'translations.db') -> int:
    """
    Проверяет версию базы данных для определения необходимых миграций.
    
    Args:
        db_path: Путь к файлу базы данных.
        
    Returns:
        Версия базы данных или 0, если версия не определена.
    """
    conn = None
    try:
        conn = await aiosqlite.connect(db_path)
        
        # Проверяем, существует ли таблица с версиями
        cursor = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='db_version'"
        )
        exists = await cursor.fetchone()
        
        if not exists:
            # Создаем таблицу с версиями, если её нет
            await conn.execute(
                "CREATE TABLE db_version (version INTEGER, updated_at TIMESTAMP)"
            )
            await conn.execute(
                "INSERT INTO db_version (version, updated_at) VALUES (1, CURRENT_TIMESTAMP)"
            )
            await conn.commit()
            return 1
        
        # Получаем текущую версию
        cursor = await conn.execute("SELECT version FROM db_version ORDER BY updated_at DESC LIMIT 1")
        version = await cursor.fetchone()
        
        return version[0] if version else 0
    except Exception as e:
        logger.error(f"Ошибка при проверке версии базы данных: {e}")
        return 0
    finally:
        if conn:
            await conn.close()

async def update_db_version(version: int, db_path: str = 'translations.db') -> None:
    """
    Обновляет версию базы данных.
    
    Args:
        version: Новая версия.
        db_path: Путь к файлу базы данных.
    """
    conn = None
    try:
        conn = await aiosqlite.connect(db_path)
        
        await conn.execute(
            "INSERT INTO db_version (version, updated_at) VALUES (?, CURRENT_TIMESTAMP)",
            (version,)
        )
        await conn.commit()
        
        logger.info(f"Версия базы данных обновлена до {version}")
    except Exception as e:
        logger.error(f"Ошибка при обновлении версии базы данных: {e}")
        if conn:
            await conn.rollback()
    finally:
        if conn:
            await conn.close()

async def run_specific_migration(version: int, db_path: str = 'translations.db') -> bool:
    """
    Запускает конкретную миграцию по её версии.
    
    Args:
        version: Версия миграции.
        db_path: Путь к файлу базы данных.
        
    Returns:
        True, если миграция успешно выполнена, иначе False.
    """
    try:
        if version == 1:
            # Базовая миграция (уже реализована в других функциях)
            await setup_basic_tables(db_path)
            await fill_translation_dict(db_path)
            await update_db_version(1, db_path)
            return True
        
        elif version == 2:
            # Миграция для добавления расширенных функций
            await setup_advanced_tables(db_path)
            await update_db_version(2, db_path)
            return True
        
        elif version == 3:
            # Пример миграции для будущих обновлений
            # Здесь можно добавить новые таблицы или изменить существующие
            conn = await aiosqlite.connect(db_path)
            
            # Пример: добавление нового поля в таблицу пользователей
            await conn.execute(
                "ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT 0"
            )
            
            await conn.commit()
            await conn.close()
            
            await update_db_version(3, db_path)
            return True
        
        else:
            logger.warning(f"Миграция версии {version} не найдена")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при выполнении миграции версии {version}: {e}")
        return False

async def run_incremental_migrations(db_path: str = 'translations.db') -> None:
    """
    Запускает инкрементальные миграции, начиная с текущей версии.
    
    Args:
        db_path: Путь к файлу базы данных.
    """
    # Получаем текущую версию
    current_version = await check_db_version(db_path)
    
    # Максимальная доступная версия
    max_version = 2  # Обновляйте это значение при добавлении новых миграций
    
    logger.info(f"Текущая версия базы данных: {current_version}, доступные миграции до версии: {max_version}")
    
    # Выполняем все недостающие миграции последовательно
    for version in range(current_version + 1, max_version + 1):
        logger.info(f"Запуск миграции версии {version}")
        success = await run_specific_migration(version, db_path)
        
        if not success:
            logger.error(f"Миграция версии {version} не выполнена. Прерывание процесса.")
            break
    
    logger.info(f"Инкрементальные миграции завершены. Текущая версия: {await check_db_version(db_path)}")