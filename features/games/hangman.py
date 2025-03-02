"""
Игра "Виселица" для изучения армянских слов.

Пользователь угадывает буквы в скрытом слове, имея ограниченное количество попыток.

Обработчики сообщений для модуля игр.

Содержит функции для работы с играми "Виселица", "Расшифровка слов" и "Поиск соответствий".
"""

import logging
import asyncio
import random
from typing import Dict, List, Optional, Any, Union, Set, Tuple

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config.config import Config
from features.games.states import GameStates
from features.games.hangman import HangmanGame, get_random_word_for_game
from features.games.word_scramble import WordScrambleGame, get_word_for_scramble
from features.games.word_match import WordMatchGame, get_pairs_for_word_match
from keyboards.inline import get_games_keyboard, get_back_button, get_confirmation_keyboard
from services.translation import translate_and_save

logger = logging.getLogger(__name__)

# Словари для хранения активных игр пользователей
hangman_games: Dict[int, HangmanGame] = {}
scramble_games: Dict[int, WordScrambleGame] = {}
match_games: Dict[int, WordMatchGame] = {}

class HangmanGame:
    """
    Класс для игры "Виселица".
    
    Attributes:
        word: Загаданное слово.
        translation: Перевод слова.
        guessed_letters: Множество угаданных букв.
        wrong_letters: Множество неправильно угаданных букв.
        max_attempts: Максимальное количество ошибок.
        attempts_left: Оставшееся количество попыток.
    """
    
    def __init__(self, word: str, translation: str, max_attempts: int = 6):
        """
        Инициализирует новую игру "Виселица".
        
        Args:
            word: Загаданное слово на русском.
            translation: Перевод слова на армянский.
            max_attempts: Максимальное количество ошибок.
        """
        self.word = word.lower()
        self.translation = translation
        self.guessed_letters: Set[str] = set()
        self.wrong_letters: Set[str] = set()
        self.max_attempts = max_attempts
        self.attempts_left = max_attempts
    
    def guess_letter(self, letter: str) -> bool:
        """
        Проверяет букву и обновляет состояние игры.
        
        Args:
            letter: Буква для проверки (в нижнем регистре).
            
        Returns:
            True, если буква присутствует в слове, иначе False.
        """
        if not letter or len(letter) != 1:
            return False
        
        letter = letter.lower()
        
        # Если буква уже была угадана или использована, считаем неправильным ходом
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False
        
        if letter in self.word:
            self.guessed_letters.add(letter)
            return True
        else:
            self.wrong_letters.add(letter)
            self.attempts_left -= 1
            return False
    
    def get_masked_word(self) -> str:
        """
        Возвращает слово с угаданными буквами и скрытыми неугаданными.
        
        Returns:
            Строка с угаданными и скрытыми буквами.
        """
        return ''.join([letter if letter in self.guessed_letters or letter.isspace() else '_' for letter in self.word])
    
    def get_status_message(self) -> str:
        """
        Формирует сообщение о текущем состоянии игры.
        
        Returns:
            Сообщение с информацией о текущем состоянии игры.
        """
        masked_word = self.get_masked_word()
        
        message = f"🎮 <b>Игра 'Виселица'</b>\n\n"
        message += f"Слово: <b>{' '.join(masked_word)}</b>\n\n"
        
        if self.wrong_letters:
            message += f"Неправильные буквы: <b>{', '.join(sorted(self.wrong_letters))}</b>\n"
        
        message += f"Осталось попыток: <b>{self.attempts_left}</b> из <b>{self.max_attempts}</b>\n\n"
        
        # Добавляем графическое представление виселицы
        hangman_stages = [
            # 0 ошибок
            """
            --------
            |      
            |      
            |     
            |     
            |     
            ---------
            """,
            # 1 ошибка - голова
            """
            --------
            |      O
            |      
            |     
            |     
            |     
            ---------
            """,
            # 2 ошибки - голова и туловище
            """
            --------
            |      O
            |      |
            |     
            |     
            |     
            ---------
            """,
            # 3 ошибки - голова, туловище и одна рука
            """
            --------
            |      O
            |     /|
            |     
            |     
            |     
            ---------
            """,
            # 4 ошибки - голова, туловище и обе руки
            """
            --------
            |      O
            |     /|\\
            |     
            |     
            |     
            ---------
            """,
            # 5 ошибок - голова, туловище, обе руки и одна нога
            """
            --------
            |      O
            |     /|\\
            |     / 
            |     
            |     
            ---------
            """,
            # 6 ошибок - полностью нарисованная виселица
            """
            --------
            |      O
            |     /|\\
            |     / \\
            |     
            |     
            ---------
            """
        ]
        
        # Отображаем текущую стадию виселицы
        error_count = self.max_attempts - self.attempts_left
        if 0 <= error_count < len(hangman_stages):
            message += f"<pre>{hangman_stages[error_count]}</pre>\n"
        
        return message
    
    def is_game_over(self) -> bool:
        """
        Проверяет, завершена ли игра.
        
        Returns:
            True, если игра завершена (победа или поражение), иначе False.
        """
        return self.is_win() or self.attempts_left <= 0
    
    def is_win(self) -> bool:
        """
        Проверяет, выиграна ли игра.
        
        Returns:
            True, если все буквы в слове угаданы, иначе False.
        """
        for letter in self.word:
            if letter not in self.guessed_letters and letter.isalpha():
                return False
        return True
    
    def get_game_result(self) -> str:
        """
        Формирует сообщение с результатом игры.
        
        Returns:
            Сообщение с результатом игры.
        """
        if self.is_win():
            return (
                f"🎉 <b>Поздравляем! Вы победили!</b>\n\n"
                f"Загаданное слово: <b>{self.word}</b>\n"
                f"Перевод: <b>{self.translation}</b>\n\n"
                f"Вы использовали {self.max_attempts - self.attempts_left} неверных попыток."
            )
        else:
            return (
                f"😢 <b>Игра окончена!</b>\n\n"
                f"Загаданное слово: <b>{self.word}</b>\n"
                f"Перевод: <b>{self.translation}</b>\n\n"
                f"Не расстраивайтесь, попробуйте еще раз!"
            )


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
    

