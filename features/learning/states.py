"""
Состояния для модуля обучения.

Определяет состояния FSM (конечного автомата) для управления 
диалогами в модуле обучения.
"""

from aiogram.dispatcher.filters.state import State, StatesGroup

class LearningStates(StatesGroup):
    """Состояния для путей обучения."""
    choosing_path = State()  # Выбор пути обучения
    choosing_level = State()  # Выбор уровня
    learning = State()  # Изучение материала
    practicing = State()  # Практика
    waiting_for_input = State()  # Ожидание ввода ответа
    confirming_completion = State()  # Подтверждение завершения урока
    giving_feedback = State()  # Обратная связь по уроку

class QuizStates(StatesGroup):
    """Состояния для тестов."""
    waiting_for_answer = State()  # Ожидание ответа на вопрос
    choosing_quiz_type = State()  # Выбор типа теста
    reviewing_results = State()  # Просмотр результатов
    confirming_restart = State()  # Подтверждение перезапуска теста