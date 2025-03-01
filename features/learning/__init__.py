"""
Модуль обучения для Armenian Learning Bot.

Реализует структурированные пути обучения, уроки и тесты.
"""

from features.learning.handlers import register_learning_handlers
from features.learning.states import LearningStates, QuizStates

__all__ = [
    'register_learning_handlers',
    'LearningStates',
    'QuizStates'
]