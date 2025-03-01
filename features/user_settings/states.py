"""
Состояния для модуля настроек пользователя.

Определяет состояния FSM (конечного автомата) для управления 
процессом настройки параметров бота.
"""

from aiogram.dispatcher.filters.state import State, StatesGroup

class SettingsStates(StatesGroup):
    """Состояния для настроек пользователя."""
    choosing_option = State()  # Выбор параметра для настройки
    setting_reminder = State()  # Настройка напоминаний
    setting_difficulty = State()  # Настройка сложности
    setting_daily_goal = State()  # Настройка ежедневной цели
    setting_theme = State()  # Настройка темы
    confirming_reset = State()  # Подтверждение сброса настроек