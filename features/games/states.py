"""
Состояния для модуля игр.

Определяет состояния FSM (конечного автомата) для управления 
процессом игры.
"""

from aiogram.dispatcher.filters.state import State, StatesGroup

class GameStates(StatesGroup):
    """Состояния для игровых режимов."""
    playing_hangman = State()  # Игра "Виселица"
    playing_wordmatch = State()  # Игра "Поиск соответствий"
    playing_scramble = State()  # Игра "Расшифровка слов"
    choosing_difficulty = State()  # Выбор сложности
    choosing_category = State()  # Выбор категории слов
    getting_results = State()  # Получение результатов