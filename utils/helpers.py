"""
Вспомогательные функции для Armenian Learning Bot.

Содержит общие утилиты, используемые в разных частях приложения.
"""

import re
import json
import random
import logging
from typing import List, Dict, Any, Optional, Union, Iterable, TypeVar, Iterator
from datetime import datetime, date, time

logger = logging.getLogger(__name__)

T = TypeVar('T')

def format_time(t: time) -> str:
    """
    Форматирует объект времени в строку.
    
    Args:
        t: Объект времени.
        
    Returns:
        Отформатированная строка времени (HH:MM).
    """
    return t.strftime("%H:%M")

def parse_time(time_str: str) -> Optional[time]:
    """
    Парсит строку времени в объект времени.
    
    Args:
        time_str: Строка времени в формате "HH:MM".
        
    Returns:
        Объект времени или None, если парсинг не удался.
    """
    try:
        # Проверяем формат с помощью регулярного выражения
        if not re.match(r'^\d{1,2}:\d{2}$', time_str):
            return None
        
        hours, minutes = map(int, time_str.split(':'))
        
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return time(hours, minutes)
        
        return None
    except (ValueError, TypeError):
        return None

def sanitize_text(text: str) -> str:
    """
    Очищает текст от лишних символов и пробелов.
    
    Args:
        text: Исходный текст.
        
    Returns:
        Очищенный текст.
    """
    if not text:
        return ""
    
    # Заменяем множественные пробелы на один
    text = re.sub(r'\s+', ' ', text)
    # Удаляем пробелы в начале и конце
    text = text.strip()
    
    return text

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Обрезает текст до указанной длины.
    
    Args:
        text: Исходный текст.
        max_length: Максимальная длина текста.
        suffix: Суффикс, добавляемый к обрезанному тексту.
        
    Returns:
        Обрезанный текст с суффиксом, если текст был обрезан.
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Обрезаем до max_length - длина суффикса
    return text[:max_length - len(suffix)] + suffix

def escape_markdown(text: str) -> str:
    """
    Экранирует специальные символы Markdown.
    
    Args:
        text: Исходный текст.
        
    Returns:
        Текст с экранированными символами Markdown.
    """
    if not text:
        return ""
    
    # Экранируем символы Markdown
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    
    return text

def get_random_praise() -> str:
    """
    Возвращает случайную похвалу для поощрения пользователя.
    
    Returns:
        Случайная фраза похвалы.
    """
    praises = [
        "Отлично! 👏",
        "Молодец! 🎉",
        "Так держать! 💪",
        "Прекрасно! ✨",
        "Великолепно! 🌟",
        "Супер! 🔥",
        "Браво! 👌",
        "Впечатляет! 🚀",
        "Замечательно! 💯",
        "Вы на правильном пути! 🏆"
    ]
    
    return random.choice(praises)

def calculate_percentage(part: Union[int, float], total: Union[int, float]) -> float:
    """
    Вычисляет процент от общего значения.
    
    Args:
        part: Часть значения.
        total: Общее значение.
        
    Returns:
        Процент от общего значения (0-100).
    """
    if total == 0:
        return 0.0
    
    return (part / total) * 100

def format_date(d: date, format_str: str = "%d.%m.%Y") -> str:
    """
    Форматирует объект даты в строку.
    
    Args:
        d: Объект даты.
        format_str: Строка формата даты.
        
    Returns:
        Отформатированная строка даты.
    """
    return d.strftime(format_str)

def chunked(iterable: Iterable[T], size: int) -> Iterator[List[T]]:
    """
    Разбивает итерируемый объект на чанки указанного размера.
    
    Args:
        iterable: Итерируемый объект.
        size: Размер чанка.
        
    Returns:
        Итератор чанков.
    """
    it = iter(iterable)
    while True:
        chunk = list(iter(lambda: next(it, None), None))[:size]
        if not chunk:
            break
        yield chunk

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Вычисляет расстояние Левенштейна между двумя строками.
    
    Args:
        s1: Первая строка.
        s2: Вторая строка.
        
    Returns:
        Расстояние Левенштейна.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Загружает данные из JSON файла.
    
    Args:
        file_path: Путь к JSON файлу.
        
    Returns:
        Словарь с данными или None, если произошла ошибка.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка при загрузке JSON из файла {file_path}: {e}")
        return None

def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """
    Сохраняет данные в JSON файл.
    
    Args:
        data: Данные для сохранения.
        file_path: Путь к JSON файлу.
        
    Returns:
        True, если сохранение успешно, иначе False.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении JSON в файл {file_path}: {e}")
        return False

def is_valid_word(word: str) -> bool:
    """
    Проверяет, является ли строка допустимым словом.
    
    Args:
        word: Строка для проверки.
        
    Returns:
        True, если строка является допустимым словом, иначе False.
    """
    # Проверяем, что строка содержит только буквы и не пуста
    return bool(word) and all(c.isalpha() or c.isspace() for c in word)

def extract_command_args(text: str) -> List[str]:
    """
    Извлекает аргументы команды из текста.
    
    Args:
        text: Текст команды.
        
    Returns:
        Список аргументов.
    """
    # Удаляем саму команду (первое слово, начинающееся с /)
    command_match = re.match(r'^/\w+', text)
    if command_match:
        text = text[command_match.end():].strip()
    
    # Разбиваем аргументы, учитывая кавычки
    args = []
    current_arg = []
    in_quotes = False
    quote_char = None
    
    for char in text:
        if char in ('"', "'") and (not in_quotes or char == quote_char):
            in_quotes = not in_quotes
            quote_char = char if in_quotes else None
        elif char.isspace() and not in_quotes:
            if current_arg:
                args.append(''.join(current_arg))
                current_arg = []
        else:
            current_arg.append(char)
    
    if current_arg:
        args.append(''.join(current_arg))
    
    return args

def get_user_mention(user_id: int, username: Optional[str] = None, full_name: Optional[str] = None) -> str:
    """
    Создает упоминание пользователя для сообщений.
    
    Args:
        user_id: ID пользователя.
        username: Имя пользователя (опционально).
        full_name: Полное имя пользователя (опционально).
        
    Returns:
        Строка с упоминанием пользователя.
    """
    if username:
        return f"@{username}"
    elif full_name:
        return f"[{full_name}](tg://user?id={user_id})"
    else:
        return f"[Пользователь](tg://user?id={user_id})"

def get_time_diff_text(dt: datetime) -> str:
    """
    Возвращает текстовое представление разницы между текущим временем и указанной датой.
    
    Args:
        dt: Дата для сравнения.
        
    Returns:
        Текстовое представление разницы времени.
    """
    now = datetime.now()
    diff = now - dt
    
    if diff.days < 0:
        # Дата в будущем
        return "в будущем"
    
    if diff.days == 0:
        # Сегодня
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        if hours == 0:
            if minutes == 0:
                return "только что"
            elif minutes == 1:
                return "минуту назад"
            elif minutes < 5:
                return f"{minutes} минуты назад"
            else:
                return f"{minutes} минут назад"
        elif hours == 1:
            return "час назад"
        elif hours < 5:
            return f"{hours} часа назад"
        else:
            return f"{hours} часов назад"
    
    elif diff.days == 1:
        # Вчера
        return "вчера"
    
    elif diff.days < 7:
        # На этой неделе
        return f"{diff.days} дней назад"
    
    elif diff.days < 30:
        # В этом месяце
        weeks = diff.days // 7
        if weeks == 1:
            return "неделю назад"
        elif weeks < 5:
            return f"{weeks} недели назад"
        else:
            return f"{weeks} недель назад"
    
    elif diff.days < 365:
        # В этом году
        months = diff.days // 30
        if months == 1:
            return "месяц назад"
        elif months < 5:
            return f"{months} месяца назад"
        else:
            return f"{months} месяцев назад"
    
    else:
        # Более года назад
        years = diff.days // 365
        if years == 1:
            return "год назад"
        elif years < 5:
            return f"{years} года назад"
        else:
            return f"{years} лет назад"