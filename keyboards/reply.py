"""
Модуль обычных клавиатур для Armenian Learning Bot.

Содержит функции для создания и настройки обычных (reply) клавиатур.
"""

from typing import List, Optional
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def get_start_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает стартовую клавиатуру с основными действиями.
    
    Returns:
        Обычная клавиатура с основными кнопками.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.row(
        KeyboardButton("📚 Учить"),
        KeyboardButton("🔄 Повторять"),
        KeyboardButton("🎮 Игры")
    )
    
    keyboard.row(
        KeyboardButton("📊 Статистика"),
        KeyboardButton("⚙️ Настройки"),
        KeyboardButton("ℹ️ Помощь")
    )
    
    return keyboard

def get_language_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру выбора языка интерфейса.
    
    Returns:
        Клавиатура с доступными языками.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.row(
        KeyboardButton("🇷🇺 Русский"),
        KeyboardButton("🇦🇲 Армянский"),
        KeyboardButton("🇬🇧 English")
    )
    
    return keyboard

def get_remove_keyboard() -> ReplyKeyboardRemove:
    """
    Создает объект для удаления клавиатуры.
    
    Returns:
        Объект для удаления клавиатуры.
    """
    return ReplyKeyboardRemove()

def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с запросом контакта пользователя.
    
    Returns:
        Клавиатура с кнопкой запроса контакта.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.add(KeyboardButton(
        "📱 Поделиться контактом",
        request_contact=True
    ))
    
    keyboard.add(KeyboardButton("Отмена"))
    
    return keyboard

def get_location_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с запросом местоположения пользователя.
    
    Returns:
        Клавиатура с кнопкой запроса местоположения.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.add(KeyboardButton(
        "📍 Поделиться местоположением",
        request_location=True
    ))
    
    keyboard.add(KeyboardButton("Отмена"))
    
    return keyboard

def get_quiz_answer_keyboard(options: List[str]) -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с вариантами ответов для теста.
    
    Args:
        options: Список вариантов ответов.
        
    Returns:
        Клавиатура с вариантами ответов.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Добавляем варианты ответов по 2 в ряд
    row = []
    for idx, option in enumerate(options):
        row.append(KeyboardButton(option))
        
        if idx % 2 == 1 or idx == len(options) - 1:
            keyboard.row(*row)
            row = []
    
    # Добавляем кнопку пропуска
    keyboard.row(KeyboardButton("Пропустить"))
    
    return keyboard

def get_continue_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой продолжения.
    
    Returns:
        Клавиатура с кнопкой продолжения.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Продолжить"))
    return keyboard

def get_yes_no_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с кнопками "Да" и "Нет".
    
    Returns:
        Клавиатура с кнопками "Да" и "Нет".
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.row(
        KeyboardButton("Да"),
        KeyboardButton("Нет")
    )
    
    return keyboard

def get_difficulty_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру выбора сложности.
    
    Returns:
        Клавиатура с уровнями сложности.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.row(
        KeyboardButton("Легкий"),
        KeyboardButton("Нормальный")
    )
    
    keyboard.row(
        KeyboardButton("Сложный"),
        KeyboardButton("Эксперт")
    )
    
    keyboard.row(KeyboardButton("Отмена"))
    
    return keyboard

def get_rating_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для оценки знания слова.
    
    Returns:
        Клавиатура с оценками от 0 до 5.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.row(
        KeyboardButton("0 - Забыл"),
        KeyboardButton("1 - Почти")
    )
    
    keyboard.row(
        KeyboardButton("2 - Трудно"),
        KeyboardButton("3 - С усилием")
    )
    
    keyboard.row(
        KeyboardButton("4 - Хорошо"),
        KeyboardButton("5 - Отлично")
    )
    
    return keyboard

def get_custom_keyboard(buttons: List[str], row_width: int = 2) -> ReplyKeyboardMarkup:
    """
    Создает пользовательскую клавиатуру с указанными кнопками.
    
    Args:
        buttons: Список текстов кнопок.
        row_width: Количество кнопок в ряду.
        
    Returns:
        Пользовательская клавиатура.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Разбиваем кнопки на ряды
    row = []
    for idx, button_text in enumerate(buttons):
        row.append(KeyboardButton(button_text))
        
        if idx % row_width == row_width - 1 or idx == len(buttons) - 1:
            keyboard.row(*row)
            row = []
    
    return keyboard