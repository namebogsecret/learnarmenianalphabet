"""
Модуль планировщика задач для бота.

Предоставляет функциональность для выполнения регулярных задач,
таких как отправка напоминаний, отчетов, обновление словаря и т.д.
"""

import asyncio
import logging
import aioschedule
from datetime import datetime, time
from typing import Optional, Callable, Awaitable, List
from aiogram import Bot
from config.config import Config
from core.database import get_active_users

logger = logging.getLogger(__name__)

# Тип для функции задачи
TaskFunc = Callable[[Bot], Awaitable[None]]

# Словарь с зарегистрированными задачами
_tasks: List[str] = []

async def _run_scheduler():
    """
    Запускает планировщик задач в бесконечном цикле.
    
    Эта функция должна быть запущена как отдельная задача.
    """
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def setup_scheduler(bot: Bot, config: Config) -> aioschedule.Scheduler:
    """
    Настраивает планировщик задач.
    
    Args:
        bot: Экземпляр бота для передачи в задачи.
        config: Конфигурация с настройками планировщика.
        
    Returns:
        Объект планировщика.
    """
    # Регистрация ежедневных напоминаний
    daily_reminder_time = config.daily_reminder_time
    aioschedule.every().day.at(daily_reminder_time).do(send_daily_reminder, bot)
    logger.info(f"Запланирована задача: ежедневные напоминания в {daily_reminder_time}")
    _tasks.append(f"Ежедневные напоминания в {daily_reminder_time}")
    
    # Регистрация еженедельных отчетов
    weekly_report_day = config.weekly_report_day
    weekly_report_time = config.weekly_report_time
    
    day_names = [
        "понедельник", "вторник", "среда", "четверг",
        "пятница", "суббота", "воскресенье"
    ]
    
    if weekly_report_day == 0:
        aioschedule.every().monday.at(weekly_report_time).do(send_weekly_reports, bot)
    elif weekly_report_day == 1:
        aioschedule.every().tuesday.at(weekly_report_time).do(send_weekly_reports, bot)
    elif weekly_report_day == 2:
        aioschedule.every().wednesday.at(weekly_report_time).do(send_weekly_reports, bot)
    elif weekly_report_day == 3:
        aioschedule.every().thursday.at(weekly_report_time).do(send_weekly_reports, bot)
    elif weekly_report_day == 4:
        aioschedule.every().friday.at(weekly_report_time).do(send_weekly_reports, bot)
    elif weekly_report_day == 5:
        aioschedule.every().saturday.at(weekly_report_time).do(send_weekly_reports, bot)
    elif weekly_report_day == 6:
        aioschedule.every().sunday.at(weekly_report_time).do(send_weekly_reports, bot)
    
    logger.info(f"Запланирована задача: еженедельные отчеты по {day_names[weekly_report_day]} в {weekly_report_time}")
    _tasks.append(f"Еженедельные отчеты по {day_names[weekly_report_day]} в {weekly_report_time}")
    
    # Запуск планировщика в отдельной задаче
    asyncio.create_task(_run_scheduler())
    
    logger.info(f"Планировщик запущен с {len(_tasks)} задачами")
    return aioschedule

async def register_task(task_func: TaskFunc, schedule: str, time_str: str = None, bot: Bot = None) -> bool:
    """
    Регистрирует новую задачу в планировщике.
    
    Args:
        task_func: Функция задачи, принимающая бота как аргумент.
        schedule: Расписание ("daily", "weekly", "monthly" или custom).
        time_str: Время выполнения (в формате "HH:MM").
        bot: Экземпляр бота.
        
    Returns:
        True если задача зарегистрирована успешно, иначе False.
    """
    try:
        if schedule == "daily":
            if time_str:
                aioschedule.every().day.at(time_str).do(task_func, bot)
                _tasks.append(f"{task_func.__name__} ежедневно в {time_str}")
            else:
                aioschedule.every().day.do(task_func, bot)
                _tasks.append(f"{task_func.__name__} ежедневно")
        elif schedule == "weekly":
            if time_str:
                aioschedule.every().monday.at(time_str).do(task_func, bot)
                _tasks.append(f"{task_func.__name__} еженедельно по понедельникам в {time_str}")
            else:
                aioschedule.every().monday.do(task_func, bot)
                _tasks.append(f"{task_func.__name__} еженедельно по понедельникам")
        elif schedule == "monthly":
            # Для ежемесячных задач нужна дополнительная логика,
            # так как aioschedule не поддерживает месячные интервалы напрямую
            async def monthly_wrapper(bot):
                now = datetime.now()
                if now.day == 1:  # Выполняем только в первый день месяца
                    await task_func(bot)
            
            if time_str:
                aioschedule.every().day.at(time_str).do(monthly_wrapper, bot)
                _tasks.append(f"{task_func.__name__} ежемесячно в {time_str}")
            else:
                aioschedule.every().day.do(monthly_wrapper, bot)
                _tasks.append(f"{task_func.__name__} ежемесячно")
        else:
            # Для custom расписания просто используем переданную строку
            # Это менее безопасно, но позволяет использовать сложные расписания
            eval(f"aioschedule.every().{schedule}.do(task_func, bot)")
            _tasks.append(f"{task_func.__name__} по расписанию {schedule}")
        
        logger.info(f"Задача {task_func.__name__} успешно зарегистрирована")
        return True
    except Exception as e:
        logger.error(f"Ошибка при регистрации задачи {task_func.__name__}: {e}")
        return False

async def get_scheduled_tasks() -> List[str]:
    """
    Возвращает список запланированных задач.
    
    Returns:
        Список строк с описанием задач.
    """
    return _tasks.copy()

#
# Стандартные задачи для планировщика
#

async def send_daily_reminder(bot: Bot) -> None:
    """
    Отправляет ежедневные напоминания пользователям.
    
    Args:
        bot: Экземпляр бота.
    """
    try:
        # Получаем активных пользователей за последние 7 дней
        active_users = await get_active_users(days=7)
        
        if not active_users:
            logger.info("Нет активных пользователей для отправки напоминаний")
            return
        
        reminder_message = (
            "🔔 *Ежедневное напоминание*\n\n"
            "Не забудьте уделить время изучению армянского языка сегодня!\n"
            "Всего 10-15 минут практики каждый день помогут вам значительно улучшить ваши навыки.\n\n"
            "• Используйте команду /quiz для проверки знаний\n"
            "• Используйте команду /review для повторения карточек\n"
            "• Используйте команду /learn для продолжения обучения"
        )
        
        # Счетчики успешных и неудачных отправок
        success_count = 0
        failed_count = 0
        
        for user_id in active_users:
            try:
                await bot.send_message(user_id, reminder_message, parse_mode="Markdown")
                success_count += 1
            except Exception as e:
                logger.error(f"Ошибка при отправке напоминания пользователю {user_id}: {e}")
                failed_count += 1
        
        logger.info(f"Отправлены ежедневные напоминания. Успешно: {success_count}, Неудачно: {failed_count}")
    except Exception as e:
        logger.error(f"Ошибка при отправке ежедневных напоминаний: {e}")

async def send_weekly_reports(bot: Bot) -> None:
    """
    Отправляет еженедельные отчеты пользователям.
    
    Args:
        bot: Экземпляр бота.
    """
    try:
        # Получаем активных пользователей за последние 30 дней
        active_users = await get_active_users(days=30)
        
        if not active_users:
            logger.info("Нет активных пользователей для отправки отчетов")
            return
        
        # В реальном сценарии здесь должна быть вызвана функция из модуля analytics
        # для генерации персонализированных отчетов
        
        report_message = (
            "📊 *Еженедельный отчет о прогрессе*\n\n"
            "Вот статистика вашего обучения за прошедшую неделю:\n\n"
            "• Изучено новых слов: ...\n"
            "• Повторено карточек: ...\n"
            "• Точность ответов: ...%\n"
            "• Наиболее сложные слова: ...\n\n"
            "Продолжайте в том же духе! Регулярная практика - ключ к успеху."
        )
        
        # Счетчики успешных и неудачных отправок
        success_count = 0
        failed_count = 0
        
        for user_id in active_users:
            try:
                await bot.send_message(user_id, report_message, parse_mode="Markdown")
                success_count += 1
            except Exception as e:
                logger.error(f"Ошибка при отправке отчета пользователю {user_id}: {e}")
                failed_count += 1
        
        logger.info(f"Отправлены еженедельные отчеты. Успешно: {success_count}, Неудачно: {failed_count}")
    except Exception as e:
        logger.error(f"Ошибка при отправке еженедельных отчетов: {e}")