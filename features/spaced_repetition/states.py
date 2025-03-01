"""
Состояния для модуля интервального повторения.

Определяет состояния FSM (конечного автомата) для управления 
процессом повторения карточек.
"""

from aiogram.dispatcher.filters.state import State, StatesGroup

class SRSStates(StatesGroup):
    """Состояния для системы интервального повторения."""
    answering = State()  # Ответ на карточку
    rating = State()  # Оценка сложности карточки
    adding_card = State()  # Добавление новой карточки
    editing_card = State()  # Редактирование карточки
    confirming_delete = State()  # Подтверждение удаления карточки
    choosing_deck = State()  # Выбор колоды