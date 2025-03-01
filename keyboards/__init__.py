"""
Пакет клавиатур для Armenian Learning Bot.

Содержит модули для создания и управления клавиатурами Telegram.
"""

from keyboards.inline import (
    get_main_menu_keyboard,
    get_learning_paths_keyboard,
    get_quiz_keyboard,
    get_settings_keyboard,
    get_rating_keyboard,
    get_confirmation_keyboard,
    get_back_button
)

from keyboards.reply import (
    get_start_keyboard,
    get_language_keyboard,
    get_remove_keyboard
)

__all__ = [
    'get_main_menu_keyboard',
    'get_learning_paths_keyboard',
    'get_quiz_keyboard',
    'get_settings_keyboard',
    'get_rating_keyboard',
    'get_confirmation_keyboard',
    'get_back_button',
    'get_start_keyboard',
    'get_language_keyboard',
    'get_remove_keyboard'
]