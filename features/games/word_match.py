"""
Игра "Поиск соответствий" для изучения армянских слов.

Пользователь должен найти соответствия между словами на русском и армянском языках.
"""

import random
import logging
from typing import List, Dict, Tuple, Optional, Set

logger = logging.getLogger(__name__)

class WordMatchGame:
    """
    Класс для игры "Поиск соответствий".
    
    Attributes:
        word_pairs: Пары слов (русское - армянское).
        russian_words: Список русских слов.
        armenian_words: Список армянских слов.
        matched_pairs: Множество найденных пар.
        attempts: Количество попыток.
        selected_word: Текущее выбранное слово.
    """
    
    def __init__(self, word_pairs: List[Tuple[str, str]], shuffle: bool = True):
        """
        Инициализирует новую игру "Поиск соответствий".
        
        Args:
            word_pairs: Список пар слов в формате [(русское, армянское), ...].
            shuffle: Перемешивать ли слова.
        """
        self.word_pairs = word_pairs
        self.russian_words = [pair[0] for pair in word_pairs]
        self.armenian_words = [pair[1] for pair in word_pairs]
        
        if shuffle:
            random.shuffle(self.russian_words)
            random.shuffle(self.armenian_words)
        
        self.matched_pairs: Set[Tuple[str, str]] = set()
        self.attempts = 0
        self.selected_word: Optional[str] = None
        self.selected_language: Optional[str] = None
    
    def select_word(self, word: str, language: str) -> bool:
        """
        Выбирает слово для сопоставления.
        
        Args:
            word: Выбранное слово.
            language: Язык слова ('russian' или 'armenian').
            
        Returns:
            True, если слово успешно выбрано, иначе False.
        """
        # Проверяем, что слово еще не сопоставлено
        for rus, arm in self.matched_pairs:
            if (language == 'russian' and rus == word) or (language == 'armenian' and arm == word):
                return False
        
        # Если это первое выбранное слово
        if self.selected_word is None:
            self.selected_word = word
            self.selected_language = language
            return True
        
        # Если это второе выбранное слово, проверяем соответствие
        self.attempts += 1
        
        # Если выбраны слова на одном языке, сбрасываем выбор
        if self.selected_language == language:
            self.selected_word = word
            self.selected_language = language
            return True
        
        # Получаем пару для проверки
        russian_word = word if language == 'russian' else self.selected_word
        armenian_word = word if language == 'armenian' else self.selected_word
        
        # Проверяем соответствие
        for rus, arm in self.word_pairs:
            if rus == russian_word and arm == armenian_word:
                self.matched_pairs.add((rus, arm))
                self.selected_word = None
                self.selected_language = None
                return True
        
        # Если соответствие не найдено, сбрасываем выбор
        self.selected_word = None
        self.selected_language = None
        return False
    
    def check_match(self, russian_word: str, armenian_word: str) -> bool:
        """
        Проверяет соответствие между русским и армянским словами.
        
        Args:
            russian_word: Русское слово.
            armenian_word: Армянское слово.
            
        Returns:
            True, если слова образуют пару, иначе False.
        """
        for rus, arm in self.word_pairs:
            if rus == russian_word and arm == armenian_word:
                return True
        return False
    
    def is_completed(self) -> bool:
        """
        Проверяет, завершена ли игра.
        
        Returns:
            True, если все пары найдены, иначе False.
        """
        return len(self.matched_pairs) == len(self.word_pairs)
    
    def get_available_words(self, language: str) -> List[str]:
        """
        Возвращает список доступных слов на указанном языке.
        
        Args:
            language: Язык ('russian' или 'armenian').
            
        Returns:
            Список слов, которые еще не сопоставлены.
        """
        if language == 'russian':
            all_words = self.russian_words
        else:
            all_words = self.armenian_words
        
        # Исключаем сопоставленные слова
        matched_words = set()
        for rus, arm in self.matched_pairs:
            if language == 'russian':
                matched_words.add(rus)
            else:
                matched_words.add(arm)
        
        return [word for word in all_words if word not in matched_words]
    
    def get_status_message(self) -> str:
        """
        Формирует сообщение о текущем состоянии игры.
        
        Returns:
            Сообщение с информацией о текущем состоянии игры.
        """
        message = (
            f"🎮 <b>Игра 'Поиск соответствий'</b>\n\n"
            f"Найдено пар: <b>{len(self.matched_pairs)}/{len(self.word_pairs)}</b>\n"
            f"Попыток: <b>{self.attempts}</b>\n\n"
        )
        
        if self.selected_word:
            message += f"Выбрано слово: <b>{self.selected_word}</b>\n\n"
        
        message += "Выберите соответствующие пары русских и армянских слов.\n\n"
        
        # Добавляем найденные пары
        if self.matched_pairs:
            message += "<b>Найденные пары:</b>\n"
            for rus, arm in self.matched_pairs:
                message += f"• {rus} - {arm}\n"
        
        return message
    
    def get_game_result(self) -> str:
        """
        Формирует сообщение с результатом игры.
        
        Returns:
            Сообщение с результатом игры.
        """
        message = (
            f"🎉 <b>Игра завершена!</b>\n\n"
            f"Вы нашли все {len(self.word_pairs)} пар слов за {self.attempts} попыток!\n\n"
            f"<b>Правильные пары:</b>\n"
        )
        
        for rus, arm in self.word_pairs:
            message += f"• {rus} - {arm}\n"
        
        message += "\nХотите сыграть еще раз?"
        
        return message


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