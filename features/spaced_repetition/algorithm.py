"""
Алгоритм интервального повторения.

Реализует алгоритм SuperMemo-2 для оптимального интервала повторения карточек.
"""

import math
import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class SM2Algorithm:
    """
    Реализация алгоритма SuperMemo-2 для интервального повторения.
    
    Алгоритм основан на оценке качества ответа (0-5) и корректировке 
    интервала повторения и фактора легкости соответственно.
    """
    
    def __init__(self, min_interval: int = 1, max_interval: int = 365):
        """
        Инициализирует алгоритм SM2.
        
        Args:
            min_interval: Минимальный интервал повторения в днях.
            max_interval: Максимальный интервал повторения в днях.
        """
        self.min_interval = min_interval
        self.max_interval = max_interval
    
    def process_response(self, 
                         quality: int, 
                         easiness: float, 
                         interval: int, 
                         repetitions: int) -> Tuple[float, int, int, datetime]:
        """
        Обрабатывает ответ пользователя и обновляет параметры карточки.
        
        Параметры алгоритма SM2:
        - quality: оценка качества ответа (0-5)
        - easiness: фактор легкости (1.3-2.5)
        - interval: текущий интервал повторения в днях
        - repetitions: количество успешных повторений подряд
        
        Args:
            quality: Оценка качества ответа (0-5).
            easiness: Текущий фактор легкости.
            interval: Текущий интервал повторения в днях.
            repetitions: Количество успешных повторений подряд.
            
        Returns:
            Кортеж (новый фактор легкости, новый интервал, новое количество повторений, 
            дата следующего повторения).
        """
        # Ограничиваем качество ответа диапазоном 0-5
        quality = max(0, min(5, quality))
        
        # Обновляем фактор легкости
        easiness = self._update_easiness(easiness, quality)
        
        # Обновляем интервал и количество повторений
        if quality < 3:
            # Если ответ плохой, сбрасываем интервал и счетчик повторений
            repetitions = 0
            interval = self.min_interval
        else:
            # Если ответ хороший, увеличиваем интервал
            repetitions += 1
            interval = self._calculate_interval(easiness, interval, repetitions)
        
        # Ограничиваем интервал максимальным значением
        interval = min(interval, self.max_interval)
        
        # Рассчитываем дату следующего повторения
        next_date = datetime.now() + timedelta(days=interval)
        
        return easiness, interval, repetitions, next_date
    
    def _update_easiness(self, easiness: float, quality: int) -> float:
        """
        Обновляет фактор легкости на основе качества ответа.
        
        Args:
            easiness: Текущий фактор легкости.
            quality: Оценка качества ответа (0-5).
            
        Returns:
            Обновленный фактор легкости.
        """
        # Формула SM2 для обновления фактора легкости
        new_easiness = easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        
        # Ограничиваем фактор легкости минимальным значением 1.3
        return max(1.3, new_easiness)
    
    def _calculate_interval(self, easiness: float, interval: int, repetitions: int) -> int:
        """
        Рассчитывает новый интервал повторения.
        
        Args:
            easiness: Фактор легкости.
            interval: Текущий интервал.
            repetitions: Количество успешных повторений подряд.
            
        Returns:
            Новый интервал повторения в днях.
        """
        if repetitions == 1:
            return 1
        elif repetitions == 2:
            return 6
        else:
            # Для последующих повторений масштабируем интервал фактором легкости
            return math.ceil(interval * easiness)
    
    def get_estimated_retention(self, days_since_review: int, easiness: float) -> float:
        """
        Оценивает вероятность удержания информации в памяти.
        
        Возвращает приблизительную оценку вероятности того, что пользователь 
        всё ещё помнит информацию через указанное количество дней.
        
        Args:
            days_since_review: Количество дней с момента последнего повторения.
            easiness: Фактор легкости карточки.
            
        Returns:
            Вероятность удержания информации (0.0-1.0).
        """
        # Простая модель кривой забывания Эббингауза
        # с коррекцией на фактор легкости
        retention = math.exp(-0.5 * days_since_review / easiness)
        return max(0.0, min(1.0, retention))


async def update_card_after_review(
    card_id: int,
    quality: int,
    user_id: int,
    db_path: str = 'translations.db'
) -> bool:
    """
    Обновляет карточку после повторения.
    
    Args:
        card_id: ID карточки.
        quality: Оценка качества ответа (0-5).
        user_id: ID пользователя.
        db_path: Путь к файлу базы данных.
        
    Returns:
        True, если карточка успешно обновлена, иначе False.
    """
    from core.database import execute_query
    
    try:
        # Получаем текущие данные карточки
        card_data = await execute_query(
            """
            SELECT easiness, interval, repetitions 
            FROM srs_cards 
            WHERE id = ? AND user_id = ?
            """,
            (card_id, user_id),
            db_path,
            fetch=True
        )
        
        if not card_data:
            logger.error(f"Карточка с ID {card_id} не найдена для пользователя {user_id}")
            return False
        
        # Инициализируем алгоритм SM2
        sm2 = SM2Algorithm()
        
        # Получаем данные из результата запроса
        easiness = card_data[0].get('easiness', 2.5)
        interval = card_data[0].get('interval', 1)
        repetitions = card_data[0].get('repetitions', 0)
        
        # Обрабатываем ответ
        new_easiness, new_interval, new_repetitions, next_review = sm2.process_response(
            quality, easiness, interval, repetitions
        )
        
        # Форматируем дату для SQLite
        next_review_str = next_review.strftime('%Y-%m-%d')
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        # Обновляем карточку в базе данных
        await execute_query(
            """
            UPDATE srs_cards 
            SET easiness = ?, 
                interval = ?, 
                repetitions = ?, 
                next_review = ?, 
                last_review = ?
            WHERE id = ? AND user_id = ?
            """,
            (new_easiness, new_interval, new_repetitions, next_review_str, today_str, card_id, user_id),
            db_path
        )
        
        logger.info(f"Карточка {card_id} обновлена для пользователя {user_id}")
        return True
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении карточки {card_id}: {e}")
        return False


async def get_cards_due_review(user_id: int, limit: int = 10, db_path: str = 'translations.db'):
    """
    Получает карточки, подлежащие повторению на сегодня.
    
    Args:
        user_id: ID пользователя.
        limit: Максимальное количество карточек.
        db_path: Путь к файлу базы данных.
        
    Returns:
        Список карточек для повторения.
    """
    from core.database import execute_query
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        cards = await execute_query(
            """
            SELECT id, word, translation, easiness, interval, repetitions 
            FROM srs_cards 
            WHERE user_id = ? AND next_review <= ?
            ORDER BY next_review
            LIMIT ?
            """,
            (user_id, today, limit),
            db_path,
            fetch=True
        )
        
        return cards
    
    except Exception as e:
        logger.error(f"Ошибка при получении карточек для пользователя {user_id}: {e}")
        return []


async def add_card_to_srs(
    user_id: int,
    word: str,
    translation: str,
    db_path: str = 'translations.db'
) -> bool:
    """
    Добавляет новую карточку в систему интервального повторения.
    
    Args:
        user_id: ID пользователя.
        word: Слово для изучения.
        translation: Перевод слова.
        db_path: Путь к файлу базы данных.
        
    Returns:
        True, если карточка успешно добавлена, иначе False.
    """
    from core.database import execute_query
    
    try:
        # Проверяем, существует ли уже такая карточка
        existing_card = await execute_query(
            "SELECT id FROM srs_cards WHERE user_id = ? AND word = ?",
            (user_id, word.lower()),
            db_path,
            fetch=True
        )
        
        if existing_card:
            logger.info(f"Карточка со словом '{word}' уже существует для пользователя {user_id}")
            return False
        
        # Устанавливаем начальные значения
        easiness = 2.5
        interval = 1
        repetitions = 0
        
        # Рассчитываем даты
        today = datetime.now().strftime('%Y-%m-%d')
        next_review = (datetime.now() + timedelta(days=interval)).strftime('%Y-%m-%d')
        
        # Добавляем карточку
        await execute_query(
            """
            INSERT INTO srs_cards 
            (user_id, word, translation, easiness, interval, repetitions, next_review, last_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, word.lower(), translation, easiness, interval, repetitions, next_review, today),
            db_path
        )
        
        logger.info(f"Карточка со словом '{word}' добавлена для пользователя {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при добавлении карточки '{word}' для пользователя {user_id}: {e}")
        return False