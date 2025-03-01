"""
Пакет миграций базы данных.

Содержит скрипты для инициализации и обновления структуры базы данных.
"""

from data.migrations.init_db import run_migrations, setup_basic_tables

__all__ = ['run_migrations', 'setup_basic_tables']