"""
Обработчики базовых команд бота.

Содержит обработчики для команд /start и /help.
"""

import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from config.config import Config
from core.database import add_or_update_user
from keyboards.inline import get_main_menu_keyboard

logger = logging.getLogger(__name__)


async def start_handler(message: types.Message, config: Config = None):
    """
    Обработчик команды /start.

    Приветствует пользователя и описывает возможности бота.
    """
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    db_path = config.db_path if config else 'translations.db'

    logger.info(f"User {username} ({user_id}) started the bot")

    try:
        # Обновляем информацию о пользователе
        await add_or_update_user(user_id, username, db_path)

        welcome_message = (
            f"Բարև, {message.from_user.first_name}! 👋\n\n"
            "Добро пожаловать в Armenian Learning Bot! 🇦🇲\n\n"
            "Этот бот поможет вам изучить армянский алфавит и базовые слова.\n\n"
            "**Основные возможности:**\n"
            "• 📝 Транслитерация русского текста на армянский\n"
            "• 🎮 Обучающие игры (Виселица, Расшифровка слов, Поиск соответствий)\n"
            "• 🔄 Система интервального повторения (SRS)\n"
            "• 💬 Работа с базовыми выражениями\n"
            "• ❓ Ответы на вопросы об армянском языке (начните сообщение с '?')\n\n"
            "Используйте команду /help для получения подробной информации о командах."
        )

        await message.answer(welcome_message, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in start_handler: {e}")
        await message.answer("Произошла ошибка при запуске бота. Попробуйте еще раз.")


async def help_handler(message: types.Message, config: Config = None):
    """
    Обработчик команды /help.

    Отправляет пользователю справку по использованию бота.
    """
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    logger.info(f"User {username} ({user_id}) requested help")

    help_message = (
        "**📚 Справка по командам Armenian Learning Bot**\n\n"
        "**Основные команды:**\n"
        "• /start - Начать работу с ботом\n"
        "• /help - Показать эту справку\n\n"
        "**🎮 Игры:**\n"
        "• /games - Главное меню игр\n"
        "• /hangman - Игра 'Виселица'\n"
        "• /scramble - Расшифровка слов\n"
        "• /match - Поиск соответствий\n\n"
        "**📝 Транслитерация:**\n"
        "• Просто отправьте текст на русском - получите транслитерацию на армянском\n"
        "• /add_word [слово] [перевод] - Добавить слово в словарь\n"
        "• /unknown - Показать неизвестные слова\n\n"
        "**🔄 Интервальное повторение (SRS):**\n"
        "• /review - Начать повторение карточек\n"
        "• /add_card [слово] [перевод] - Добавить карточку\n"
        "• /stats - Посмотреть статистику\n\n"
        "**❓ Вопросы:**\n"
        "• Начните сообщение с '?' для вопроса об армянском языке\n"
        "• Пример: '?Как сказать привет на армянском?'\n\n"
        "**💡 Совет:** Регулярные занятия по 10-15 минут в день дадут лучший результат!"
    )

    await message.answer(help_message, parse_mode="Markdown")


async def menu_callback_handler(
    callback_query: types.CallbackQuery,
    state: FSMContext,
    config: Config = None,
):
    """
    Обрабатывает навигационные callback-запросы из главного меню.

    Позволяет возвращаться в главное меню или раздел игр из любого состояния,
    чтобы кнопки меню всегда давали отклик.
    """

    await callback_query.answer()

    section = callback_query.data.split(":", 1)[1]

    # При переходе по меню завершаем активное состояние, чтобы избежать конфликтов FSM
    await state.finish()

    if section == "main":
        keyboard = get_main_menu_keyboard()
        await callback_query.message.answer(
            "🏠 Главное меню. Выберите раздел:", reply_markup=keyboard
        )
        return

    if section == "games":
        from features.games.handlers import cmd_games

        await cmd_games(callback_query.message)
        return

    if section == "help":
        await help_handler(callback_query.message, config)
        return

    if section == "review":
        await callback_query.message.answer(
            "Для повторения карточек используйте команду /review."
        )
        return

    if section == "learn":
        await callback_query.message.answer(
            "Раздел обучения готовится. Пока что можно изучать слова через /add_word и /unknown."
        )
        return

    if section == "stats":
        await callback_query.message.answer(
            "Статистика будет доступна позже. Сейчас можно проверить прогресс через /stats."
        )
        return

    if section == "settings":
        await callback_query.message.answer(
            "Настройки пока доступны через команду /settings (в разработке)."
        )
        return


def register_common_handlers(dp: Dispatcher, config: Config):
    """
    Регистрирует обработчики базовых команд.

    Args:
        dp: Экземпляр Dispatcher
        config: Конфигурация бота
    """
    logger.info("Регистрация обработчиков базовых команд")

    # Создаем обертки для передачи config
    async def start_wrapper(message: types.Message):
        await start_handler(message, config)

    async def help_wrapper(message: types.Message):
        await help_handler(message, config)

    async def menu_callback_wrapper(
        callback_query: types.CallbackQuery, state: FSMContext
    ):
        await menu_callback_handler(callback_query, state, config)

    # Регистрируем обработчики
    dp.register_message_handler(start_wrapper, commands=['start'])
    dp.register_message_handler(help_wrapper, commands=['help'])
    dp.register_callback_query_handler(
        menu_callback_wrapper,
        lambda c: c.data and c.data.startswith('menu:'),
        state="*",
    )

    logger.info("Обработчики базовых команд успешно зарегистрированы")
