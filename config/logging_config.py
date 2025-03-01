"""
Модуль для настройки логирования бота.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from os import getenv
import json
from datetime import datetime


class CustomJsonFormatter(logging.Formatter):
    """
    Кастомный форматтер для логирования в JSON формате.
    Полезно для последующего анализа логов.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Добавление информации об исключении, если оно есть
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_record)


def setup_logging():
    """
    Настраивает логирование для бота.
    
    Для вывода логов используется консоль и файл.
    Уровень логирования настраивается через переменную окружения LOG_LEVEL.
    """
    # Создание директории для логов, если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Получение настроек из переменных окружения
    log_level_name = getenv("LOG_LEVEL", "INFO")
    log_file = getenv("LOG_FILE", "bot.log")
    
    # Преобразование строкового уровня логирования в константу
    log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Очистка существующих обработчиков
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Создание и настройка консольного обработчика
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Создание и настройка файлового обработчика
    file_path = log_dir / log_file
    file_handler = RotatingFileHandler(
        file_path, 
        maxBytes=10*1024*1024,  # 10 МБ
        backupCount=5
    )
    file_handler.setLevel(log_level)
    
    # Использование JSON форматтера для файлового обработчика
    file_handler.setFormatter(CustomJsonFormatter())
    root_logger.addHandler(file_handler)
    
    # Создание отдельного логгера для библиотеки aiogram с более высоким порогом
    aiogram_logger = logging.getLogger('aiogram')
    aiogram_logger.setLevel(logging.WARNING)
    
    # Логирование информации о запуске
    root_logger.info(f"Логирование настроено. Уровень: {log_level_name}, файл: {file_path}")
    
    return root_logger