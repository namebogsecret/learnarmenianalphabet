"""
Модуль для загрузки и управления конфигурацией бота.
"""

import os
from os import getenv
from datetime import time
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

def safe_int_env(env_var: str, default: int) -> int:
    """
    Safely convert environment variable to integer, 
    handling inline comments and unexpected values.
    
    :param env_var: Name of the environment variable
    :param default: Default value if conversion fails
    :return: Integer value of the environment variable
    """
    try:
        # Remove inline comments and whitespace
        value = os.getenv(env_var, str(default)).split('#')[0].strip()
        return int(value)
    except (ValueError, TypeError):
        # Log the error or handle it as needed
        print(f"Warning: Could not convert {env_var} to integer. Using default: {default}")
        return default

def parse_time_with_comment(time_str: Optional[str], default: str = "00:00") -> str:
    """
    Parse time string that may contain inline comments.
    
    :param time_str: Time string potentially with comments
    :param default: Default time if parsing fails
    :return: Parsed time as string in HH:MM format
    """
    if not time_str:
        return default
    
    # Remove inline comments and strip whitespace
    clean_time = time_str.split('#')[0].strip()
    
    try:
        # Validate time format
        hour, minute = map(int, clean_time.split(':'))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError()
        return clean_time
    except (ValueError, IndexError):
        print(f"Warning: Could not parse time '{clean_time}'. Using default: {default}")
        return default

class Config(BaseModel):
    """Модель конфигурации бота."""
    
    # API ключи
    telegram_token: str
    openai_api_key: str
    tts_api_key: Optional[str] = None
    
    # Настройки бота
    max_users: int = 100
    allowed_users: List[int] = []
    
    # Настройки базы данных
    db_path: str = "translations.db"
    
    # Настройки логирования
    log_level: str = "INFO"
    log_file: str = "bot.log"
    
    # Настройки планировщика
    daily_reminder_time: str = "09:00"
    weekly_report_day: int = 1  # Понедельник
    weekly_report_time: str = "10:00"
    
    # Настройки производительности
    request_timeout: int = 60  # Таймаут для запросов к внешним API (в секундах)
    
    @field_validator('weekly_report_day')
    def validate_day_of_week(cls, v):
        """Валидатор для проверки, что день недели в пределах 0-6."""
        if not (0 <= v <= 6):
            raise ValueError("День недели должен быть в диапазоне 0-6 (0 - понедельник, 6 - воскресенье)")
        return v
    
    @field_validator('daily_reminder_time', 'weekly_report_time')
    def validate_time_format(cls, v):
        """Валидатор для проверки формата времени."""
        try:
            hour, minute = map(int, v.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError()
        except (ValueError, IndexError):
            raise ValueError(f"Некорректный формат времени: {v}. Используйте формат HH:MM")
        return v

def load_config() -> Config:
    """
    Загружает конфигурацию из переменных окружения или .env файла.
    
    Returns:
        Config: Объект конфигурации.
    """
    # Определение пути к .env файлу
    env_path = Path(__file__).parent.parent / '.env'
    
    # Загрузка переменных из .env
    load_dotenv(env_path)
    
    # Парсинг списка пользователей
    users_str = getenv("USERS", "")
    allowed_users = [int(user_id.strip()) for user_id in users_str.split(",") if user_id.strip().isdigit()]
    
    # Создание объекта конфигурации
    config = Config(
        telegram_token=getenv("TELEGRAM_API", "").split('#')[0].strip(),
        openai_api_key=getenv("OPENAI_API_KEY", "").split('#')[0].strip(),
        tts_api_key=getenv("TTS_API_KEY", "").split('#')[0].strip(),
        max_users=safe_int_env("MAX_USERS", 100),
        allowed_users=allowed_users,
        db_path=getenv("DB_PATH", "translations.db").split('#')[0].strip(),
        log_level=getenv("LOG_LEVEL", "INFO").split('#')[0].strip(),
        log_file=getenv("LOG_FILE", "bot.log").split('#')[0].strip(),
        daily_reminder_time=parse_time_with_comment(
            getenv("DAILY_REMINDER_TIME", "09:00 # Время ежедневных напоминаний")
        ),
        weekly_report_day=safe_int_env("WEEKLY_REPORT_DAY", 1),
        weekly_report_time=parse_time_with_comment(
            getenv("WEEKLY_REPORT_TIME", "10:00 # Время отправки еженедельных отчетов")
        ),
        request_timeout=safe_int_env("REQUEST_TIMEOUT", 60),
    )
    
    return config