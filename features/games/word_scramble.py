"""
Игра "Расшифровка слов" для изучения армянских слов.

Пользователь должен собрать правильное слово из перемешанных букв.
"""

import random
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

class WordScrambleGame:
    """
    Класс для игры "Расшифровка слов".
    
    Attributes:
        word: Исходное слово.
        translation: Перевод слова.
        scrambled_word: Перемешанное слово.
        hints_left: Количество оставшихся подсказок.
        attempts: Количество попыток.
    """
    
    def __init__(self, word: str, translation: str, max_hints: int = 2):
        """
        Инициализирует новую игру "Расшифровка слов".
        
        Args:
            word: Исходное слово.
            translation: Перевод слова.
            max_hints: Максимальное количество подсказок.
        """
        self.word = word.lower()
        self.translation = translation
        self.scrambled_word = self._scramble_word()
        self.hints_left = max_hints
        self.attempts = 0
    
    def _scramble_word(self) -> str:
        """
        Перемешивает буквы в слове.
        
        Returns:
            Перемешанное слово.
        """
        # Разбиваем слово на символы
        chars = list(self.word)
        
        # Проверяем, чтобы перемешанное слово не совпадало с исходным
        scrambled = ''.join(chars)
        while scrambled == self.word and len(chars) > 1:
            random.shuffle(chars)
            scrambled = ''.join(chars)
        
        return scrambled
    
    def check_answer(self, answer: str) -> bool:
        """
        Проверяет ответ пользователя.
        
        Args:
            answer: Ответ пользователя.
            
        Returns:
            True, если ответ правильный, иначе False.
        """
        self.attempts += 1
        return answer.lower() == self.word.lower()
    
    def get_hint(self) -> str:
        """
        Предоставляет подсказку - раскрывает часть слова.
        
        Returns:
            Подсказка или сообщение о том, что подсказок не осталось.
        """
        if self.hints_left <= 0:
            return "У вас не осталось подсказок."
        
        self.hints_left -= 1
        
        # Генерируем подсказку, раскрывая часть слова
        revealed_count = min(len(self.word) // 2, self.hints_left + 1)
        positions = random.sample(range(len(self.word)), revealed_count)
        
        hint = []
        for i, char in enumerate(self.word):
            if i in positions:
                hint.append(char)
            else:
                hint.append("_")
        
        return f"Подсказка: {''.join(hint)}"
    
    def get_status_message(self) -> str:
        """
        Формирует сообщение о текущем состоянии игры.
        
        Returns:
            Сообщение с информацией о текущем состоянии игры.
        """
        message = (
            f"🎮 <b>Игра 'Расшифровка слов'</b>\n\n"
            f"Соберите правильное слово из букв: <b>{' '.join(self.scrambled_word)}</b>\n\n"
            f"Перевод: <b>{self.translation}</b>\n\n"
            f"Количество попыток: <b>{self.attempts}</b>\n"
            f"Доступно подсказок: <b>{self.hints_left}</b>\n\n"
            f"Введите ваш ответ или нажмите кнопку 'Подсказка'."
        )
        
        return message


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