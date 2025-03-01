"""
Значения по умолчанию для настроек пользователя.

Определяет стандартные значения параметров для новых пользователей.
"""

from typing import Dict, Any

# Значения по умолчанию для параметров пользователя
DEFAULT_SETTINGS: Dict[str, Any] = {
    'reminder_time': '09:00',  # Время ежедневных напоминаний
    'difficulty_level': 'normal',  # Уровень сложности (easy, normal, hard, expert)
    'daily_goal': 5,  # Количество новых слов в день
    'notification_enabled': True,  # Включены ли уведомления
    'game_sounds': True,  # Включены ли звуки в играх
    'theme': 'default',  # Тема оформления (default, dark, light, vibrant)
    'custom_settings': {}  # Дополнительные настройки
}

# Допустимые значения для параметров
VALID_VALUES: Dict[str, list] = {
    'difficulty_level': ['easy', 'normal', 'hard', 'expert'],
    'daily_goal': [3, 5, 10, 15, 20, 25, 30],
    'theme': ['default', 'dark', 'light', 'vibrant']
}

# Описания параметров для пользователя
SETTINGS_DESCRIPTIONS: Dict[str, str] = {
    'reminder_time': 'Время ежедневных напоминаний',
    'difficulty_level': 'Уровень сложности заданий и тестов',
    'daily_goal': 'Количество новых слов для изучения каждый день',
    'notification_enabled': 'Получение уведомлений от бота',
    'game_sounds': 'Звуковые эффекты в играх',
    'theme': 'Тема оформления бота'
}

# Локализованные имена для значений
LOCALIZED_VALUES: Dict[str, Dict[str, str]] = {
    'difficulty_level': {
        'easy': 'Легкий',
        'normal': 'Нормальный',
        'hard': 'Сложный',
        'expert': 'Эксперт'
    },
    'theme': {
        'default': 'Стандартная',
        'dark': 'Темная',
        'light': 'Светлая',
        'vibrant': 'Яркая'
    }
}

def get_localized_value(setting_name: str, value: Any) -> str:
    """
    Возвращает локализованное значение параметра.
    
    Args:
        setting_name: Имя параметра.
        value: Значение параметра.
        
    Returns:
        Локализованное значение или исходное значение, если локализация не найдена.
    """
    if setting_name in LOCALIZED_VALUES and str(value) in LOCALIZED_VALUES[setting_name]:
        return LOCALIZED_VALUES[setting_name][str(value)]
    return str(value)