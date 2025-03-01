"""
Пакет конфигурации Armenian Learning Bot.

Здесь находятся модули для настройки бота, логирования и других параметров.
"""

from config.config import load_config, Config
from config.logging_config import setup_logging

__all__ = ['load_config', 'Config', 'setup_logging']