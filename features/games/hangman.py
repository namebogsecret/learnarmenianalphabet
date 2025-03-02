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




    

