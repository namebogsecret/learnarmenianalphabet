"""
Модуль инлайн-клавиатур для Armenian Learning Bot.

Содержит функции для создания и настройки инлайн-клавиатур.
"""

from typing import List, Optional, Dict, Any, Union
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру главного меню бота.
    
    Returns:
        Инлайн-клавиатура с кнопками главного меню.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("📚 Учить слова", callback_data="menu:learn"),
        InlineKeyboardButton("🔄 Повторение", callback_data="menu:review"),
        InlineKeyboardButton("🎮 Игры", callback_data="menu:games"),
        InlineKeyboardButton("📊 Статистика", callback_data="menu:stats"),
        InlineKeyboardButton("⚙️ Настройки", callback_data="menu:settings"),
        InlineKeyboardButton("ℹ️ Помощь", callback_data="menu:help")
    ]
    
    keyboard.add(*buttons)
    return keyboard

def get_learning_paths_keyboard(
    user_id: int = None,
    db_path: str = 'translations.db'
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру выбора пути обучения.
    
    Args:
        user_id: ID пользователя для персонализации клавиатуры.
        db_path: Путь к файлу базы данных.
        
    Returns:
        Инлайн-клавиатура с доступными путями обучения.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    # Пути обучения
    paths = [
        {"id": "basics", "name": "Основы армянского", "description": "Базовые фразы, приветствия, числа"},
        {"id": "everyday", "name": "Повседневные разговоры", "description": "Бытовые темы, покупки, транспорт"},
        {"id": "intermediate", "name": "Средний уровень", "description": "Грамматика, сложные конструкции"},
        {"id": "advanced", "name": "Продвинутый", "description": "Культура, история, литература"}
    ]
    
    for path in paths:
        button_text = f"{path['name']} - {path['description']}"
        keyboard.add(InlineKeyboardButton(
            button_text,
            callback_data=f"path:{path['id']}"
        ))
    
    # Кнопка возврата в главное меню
    keyboard.add(InlineKeyboardButton(
        "↩️ Главное меню",
        callback_data="menu:main"
    ))
    
    return keyboard

def get_quiz_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру выбора типа теста.
    
    Returns:
        Инлайн-клавиатура с доступными типами тестов.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("🔤 Слова", callback_data="quiz:words"),
        InlineKeyboardButton("🗣️ Фразы", callback_data="quiz:phrases"),
        InlineKeyboardButton("🎯 Случайный", callback_data="quiz:random"),
        InlineKeyboardButton("🧩 По категории", callback_data="quiz:category")
    ]
    
    keyboard.add(*buttons)
    
    # Кнопка возврата в главное меню
    keyboard.add(InlineKeyboardButton(
        "↩️ Главное меню",
        callback_data="menu:main"
    ))
    
    return keyboard

def get_settings_keyboard(settings: Dict[str, Any] = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру настроек пользователя.
    
    Args:
        settings: Текущие настройки пользователя.
        
    Returns:
        Инлайн-клавиатура с настройками.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    # Если настройки не предоставлены, используем значения по умолчанию
    if not settings:
        from features.user_settings.defaults import DEFAULT_SETTINGS
        settings = DEFAULT_SETTINGS
    
    # Кнопка напоминаний
    notification_status = "Вкл" if settings.get('notification_enabled', True) else "Выкл"
    keyboard.add(InlineKeyboardButton(
        f"⏰ Напоминания: {notification_status}",
        callback_data="settings:toggle_notifications"
    ))
    
    # Кнопка времени напоминаний
    reminder_time = settings.get('reminder_time', '09:00')
    keyboard.add(InlineKeyboardButton(
        f"🕒 Время напоминаний: {reminder_time}",
        callback_data="settings:reminder_time"
    ))
    
    # Кнопка ежедневной цели
    daily_goal = settings.get('daily_goal', 5)
    keyboard.add(InlineKeyboardButton(
        f"🎯 Ежедневная цель: {daily_goal} слов",
        callback_data="settings:daily_goal"
    ))
    
    # Кнопка сложности
    difficulty = settings.get('difficulty_level', 'normal')
    difficulty_names = {
        'easy': 'Легкий',
        'normal': 'Нормальный',
        'hard': 'Сложный',
        'expert': 'Эксперт'
    }
    difficulty_name = difficulty_names.get(difficulty, difficulty)
    keyboard.add(InlineKeyboardButton(
        f"🔄 Сложность: {difficulty_name}",
        callback_data="settings:difficulty"
    ))
    
    # Кнопка звуков в играх
    sounds_status = "Вкл" if settings.get('game_sounds', True) else "Выкл"
    keyboard.add(InlineKeyboardButton(
        f"🔊 Звуки в играх: {sounds_status}",
        callback_data="settings:toggle_sounds"
    ))
    
    # Кнопка темы
    theme = settings.get('theme', 'default')
    theme_names = {
        'default': 'Стандартная',
        'dark': 'Темная',
        'light': 'Светлая',
        'vibrant': 'Яркая'
    }
    theme_name = theme_names.get(theme, theme)
    keyboard.add(InlineKeyboardButton(
        f"🎨 Тема: {theme_name}",
        callback_data="settings:theme"
    ))
    
    # Кнопка сброса настроек
    keyboard.add(InlineKeyboardButton(
        "🔄 Сбросить настройки",
        callback_data="settings:reset"
    ))
    
    # Кнопка возврата в главное меню
    keyboard.add(InlineKeyboardButton(
        "↩️ Главное меню",
        callback_data="menu:main"
    ))
    
    return keyboard

def get_rating_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для оценки ответа в системе интервального повторения.
    
    Returns:
        Инлайн-клавиатура с кнопками оценки.
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    # Создаем кнопки для оценки от 0 до 5
    buttons = []
    for i in range(6):
        label = {
            0: "Забыл",
            1: "Почти",
            2: "Трудно",
            3: "С усилием",
            4: "Хорошо",
            5: "Отлично"
        }.get(i, str(i))
        
        buttons.append(InlineKeyboardButton(
            label,
            callback_data=f"rate:{i}"
        ))
    
    keyboard.add(*buttons)
    return keyboard

def get_confirmation_keyboard(action: str, yes_text: str = "Да", no_text: str = "Нет") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру подтверждения действия.
    
    Args:
        action: Действие для подтверждения (используется в callback_data).
        yes_text: Текст кнопки "Да".
        no_text: Текст кнопки "Нет".
        
    Returns:
        Инлайн-клавиатура с кнопками подтверждения.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton(yes_text, callback_data=f"confirm:{action}:yes"),
        InlineKeyboardButton(no_text, callback_data=f"confirm:{action}:no")
    )
    
    return keyboard

def get_back_button(callback_data: str = "menu:main", text: str = "↩️ Назад") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой "Назад".
    
    Args:
        callback_data: Callback-данные для кнопки.
        text: Текст кнопки.
        
    Returns:
        Инлайн-клавиатура с кнопкой "Назад".
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text, callback_data=callback_data))
    return keyboard

def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    prefix: str,
    item_id: Optional[str] = None
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для пагинации контента.
    
    Args:
        current_page: Текущая страница.
        total_pages: Общее количество страниц.
        prefix: Префикс для callback_data.
        item_id: ID элемента (опционально).
        
    Returns:
        Инлайн-клавиатура с кнопками навигации.
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    nav_buttons = []
    
    # Кнопка "Назад", если не на первой странице
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(
            "⬅️",
            callback_data=f"{prefix}:page:{current_page-1}{'_' + item_id if item_id else ''}"
        ))
    
    # Текущая страница
    nav_buttons.append(InlineKeyboardButton(
        f"{current_page+1}/{total_pages}",
        callback_data=f"{prefix}:noop"
    ))
    
    # Кнопка "Вперед", если не на последней странице
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(
            "➡️",
            callback_data=f"{prefix}:page:{current_page+1}{'_' + item_id if item_id else ''}"
        ))
    
    keyboard.add(*nav_buttons)
    
    # Кнопка "Назад в меню"
    keyboard.add(InlineKeyboardButton(
        "↩️ Назад в меню",
        callback_data=f"{prefix}:back"
    ))
    
    return keyboard

def get_answer_options_keyboard(
    options: List[str],
    callback_prefix: str = "answer"
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с вариантами ответов для тестов.
    
    Args:
        options: Список вариантов ответов.
        callback_prefix: Префикс для callback_data.
        
    Returns:
        Инлайн-клавиатура с вариантами ответов.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for idx, option in enumerate(options):
        keyboard.add(InlineKeyboardButton(
            option,
            callback_data=f"{callback_prefix}:{idx}"
        ))
    
    # Кнопка пропуска вопроса
    keyboard.add(InlineKeyboardButton(
        "⏭️ Пропустить",
        callback_data=f"{callback_prefix}:skip"
    ))
    
    return keyboard

def get_games_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру выбора игры.
    
    Returns:
        Инлайн-клавиатура с доступными играми.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("🎯 Виселица", callback_data="game:hangman"),
        InlineKeyboardButton("🔤 Расшифровка", callback_data="game:scramble"),
        InlineKeyboardButton("🧩 Соответствия", callback_data="game:wordmatch"),
        InlineKeyboardButton("🏆 Мои результаты", callback_data="game:results")
    ]
    
    keyboard.add(*buttons)
    
    # Кнопка возврата в главное меню
    keyboard.add(InlineKeyboardButton(
        "↩️ Главное меню",
        callback_data="menu:main"
    ))
    
    return keyboard

def get_community_actions_keyboard(content_id: str = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру действий с контентом сообщества.
    
    Args:
        content_id: ID контента.
        
    Returns:
        Инлайн-клавиатура с действиями.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    if content_id:
        # Действия с конкретным контентом
        keyboard.add(
            InlineKeyboardButton("👍", callback_data=f"community:upvote:{content_id}"),
            InlineKeyboardButton("👎", callback_data=f"community:downvote:{content_id}")
        )
        keyboard.add(
            InlineKeyboardButton("В коллекцию", callback_data=f"community:save:{content_id}"),
            InlineKeyboardButton("Поделиться", callback_data=f"community:share:{content_id}")
        )
    else:
        # Общие действия с сообществом
        keyboard.add(
            InlineKeyboardButton("🔍 Поиск", callback_data="community:search"),
            InlineKeyboardButton("📚 Мои коллекции", callback_data="community:collections")
        )
        keyboard.add(
            InlineKeyboardButton("➕ Добавить контент", callback_data="community:add"),
            InlineKeyboardButton("🔝 Лучшее", callback_data="community:top")
        )
    
    # Кнопка возврата в главное меню
    keyboard.add(InlineKeyboardButton(
        "↩️ Главное меню",
        callback_data="menu:main"
    ))
    
    return keyboard