"""
Обработчики сообщений для модуля интервального повторения.

Содержит функции для работы с системой интервального повторения (SRS) на основе алгоритма SM2.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.config import Config
from core.database import get_db_connection
from features.spaced_repetition.algorithm import (
    add_card_to_srs, update_card_after_review, get_cards_due_review
)
from features.spaced_repetition.states import SRSStates
from keyboards.inline import get_rating_keyboard, get_confirmation_keyboard, get_back_button
from services.translation import get_translation, translate_and_save

logger = logging.getLogger(__name__)

# Словарь для хранения текущей сессии повторения для каждого пользователя
# {user_id: {'cards': [...], 'current_index': int, 'correct': int, 'total': int}}
active_reviews: Dict[int, Dict[str, Any]] = {}

async def cmd_review(message: types.Message, state: FSMContext, config: Config = None):
    """
    Обработчик команды /review.
    
    Начинает сеанс повторения для пользователя.
    
    Args:
        message: Сообщение пользователя.
        state: Состояние FSM.
        config: Конфигурация бота.
    """
    user_id = message.from_user.id
    db_path = config.db_path if config else 'translations.db'
    
    # Получаем карточки для повторения
    cards = await get_cards_due_review(user_id, limit=10, db_path=db_path)
    
    if not cards:
        await message.answer(
            "У вас нет карточек для повторения на сегодня. "
            "Добавьте новые карточки командой /add_card или "
            "вернитесь позже, когда существующие карточки будут готовы к повторению."
        )
        return
    
    # Инициализируем сессию повторения
    active_reviews[user_id] = {
        'cards': cards,
        'current_index': 0,
        'correct': 0,
        'total': len(cards)
    }
    
    # Отправляем первую карточку
    await show_card(message.chat.id, user_id)
    
    # Устанавливаем состояние
    await SRSStates.answering.set()

async def show_card(chat_id: int, user_id: int):
    """
    Показывает текущую карточку пользователю.
    
    Args:
        chat_id: ID чата.
        user_id: ID пользователя.
    """
    review_data = active_reviews.get(user_id)
    if not review_data:
        return
    
    cards = review_data['cards']
    current_index = review_data['current_index']
    
    if current_index >= len(cards):
        # Все карточки просмотрены
        return
    
    card = cards[current_index]
    
    # Формируем сообщение с карточкой
    message_text = (
        f"Карточка {current_index + 1}/{len(cards)}\n\n"
        f"<b>{card['word']}</b>\n\n"
        "Вспомните перевод и нажмите кнопку, чтобы проверить."
    )
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Показать перевод", callback_data="srs:show_translation"))
    keyboard.add(types.InlineKeyboardButton("Пропустить", callback_data="srs:skip"))
    
    await types.Bot.get_current().send_message(
        chat_id=chat_id,
        text=message_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

async def process_show_translation(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку "Показать перевод".
    
    Args:
        callback_query: Запрос обратного вызова.
        state: Состояние FSM.
    """
    user_id = callback_query.from_user.id
    review_data = active_reviews.get(user_id)
    
    if not review_data:
        await callback_query.answer("Сессия повторения истекла. Начните новую командой /review")
        await state.finish()
        return
    
    cards = review_data['cards']
    current_index = review_data['current_index']
    
    if current_index >= len(cards):
        await callback_query.answer("Все карточки просмотрены")
        await finish_review(callback_query.message.chat.id, user_id, state)
        return
    
    card = cards[current_index]
    
    # Показываем перевод и запрашиваем оценку
    message_text = (
        f"Карточка {current_index + 1}/{len(cards)}\n\n"
        f"<b>{card['word']}</b>\n\n"
        f"Перевод: <b>{card['translation']}</b>\n\n"
        "Оцените, насколько хорошо вы знали ответ:"
    )
    
    # Получаем клавиатуру с оценками
    keyboard = get_rating_keyboard()
    
    await callback_query.message.edit_text(
        text=message_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    # Изменяем состояние на оценку
    await SRSStates.rating.set()

async def process_rating(callback_query: types.CallbackQuery, state: FSMContext, config: Config = None):
    """
    Обрабатывает оценку качества ответа.
    
    Args:
        callback_query: Запрос обратного вызова.
        state: Состояние FSM.
        config: Конфигурация бота.
    """
    user_id = callback_query.from_user.id
    db_path = config.db_path if config else 'translations.db'
    
    review_data = active_reviews.get(user_id)
    if not review_data:
        await callback_query.answer("Сессия повторения истекла. Начните новую командой /review")
        await state.finish()
        return
    
    # Получаем оценку из callback_data (rate:0, rate:1, ..., rate:5)
    rating_data = callback_query.data.split(":")
    if len(rating_data) != 2 or not rating_data[1].isdigit():
        await callback_query.answer("Некорректная оценка")
        return
    
    quality = int(rating_data[1])
    
    # Если оценка хорошая (>=3), увеличиваем счетчик правильных ответов
    if quality >= 3:
        review_data['correct'] += 1
    
    # Обновляем карточку в базе данных
    cards = review_data['cards']
    current_index = review_data['current_index']
    card = cards[current_index]
    
    await update_card_after_review(card['id'], quality, user_id, db_path)
    
    # Переходим к следующей карточке
    review_data['current_index'] += 1
    
    if review_data['current_index'] >= len(cards):
        # Все карточки просмотрены
        await finish_review(callback_query.message.chat.id, user_id, state)
    else:
        # Показываем следующую карточку
        await show_card(callback_query.message.chat.id, user_id)
        # Возвращаемся в состояние ответа
        await SRSStates.answering.set()
    
    await callback_query.answer()

async def process_skip(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает пропуск карточки.
    
    Args:
        callback_query: Запрос обратного вызова.
        state: Состояние FSM.
    """
    user_id = callback_query.from_user.id
    review_data = active_reviews.get(user_id)
    
    if not review_data:
        await callback_query.answer("Сессия повторения истекла. Начните новую командой /review")
        await state.finish()
        return
    
    # Показываем перевод и автоматически ставим низкую оценку (1)
    cards = review_data['cards']
    current_index = review_data['current_index']
    
    if current_index >= len(cards):
        await callback_query.answer("Все карточки просмотрены")
        await finish_review(callback_query.message.chat.id, user_id, state)
        return
    
    card = cards[current_index]
    
    # Показываем перевод
    message_text = (
        f"Карточка {current_index + 1}/{len(cards)}\n\n"
        f"<b>{card['word']}</b>\n\n"
        f"Перевод: <b>{card['translation']}</b>\n\n"
        "Карточка пропущена и будет показана снова скоро."
    )
    
    await callback_query.message.edit_text(
        text=message_text,
        parse_mode="HTML"
    )
    
    # Короткая пауза, чтобы пользователь успел прочитать перевод
    await asyncio.sleep(2)
    
    # Переходим к следующей карточке
    review_data['current_index'] += 1
    
    if review_data['current_index'] >= len(cards):
        # Все карточки просмотрены
        await finish_review(callback_query.message.chat.id, user_id, state)
    else:
        # Показываем следующую карточку
        await show_card(callback_query.message.chat.id, user_id)
    
    await callback_query.answer()

async def finish_review(chat_id: int, user_id: int, state: FSMContext):
    """
    Завершает сеанс повторения и показывает результаты.
    
    Args:
        chat_id: ID чата.
        user_id: ID пользователя.
        state: Состояние FSM.
    """
    review_data = active_reviews.get(user_id)
    if not review_data:
        return
    
    correct = review_data['correct']
    total = review_data['total']
    
    # Формируем сообщение с результатами
    if total > 0:
        percentage = round(correct / total * 100)
        
        if percentage >= 80:
            emoji = "🎉"
            message = "Отличный результат! Продолжайте в том же духе!"
        elif percentage >= 60:
            emoji = "👍"
            message = "Хороший результат! Вы на правильном пути."
        else:
            emoji = "🔄"
            message = "Продолжайте тренироваться, и результаты улучшатся!"
        
        result_text = (
            f"{emoji} Повторение завершено!\n\n"
            f"Правильно: {correct} из {total} ({percentage}%)\n\n"
            f"{message}"
        )
    else:
        result_text = "Повторение завершено!"
    
    # Создаем клавиатуру с кнопками действий
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("📚 Новое повторение", callback_data="srs:new_review"))
    keyboard.add(types.InlineKeyboardButton("➕ Добавить карточку", callback_data="srs:add_card"))
    keyboard.add(types.InlineKeyboardButton("📊 Статистика", callback_data="srs:stats"))
    keyboard.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="menu:main"))
    
    await types.Bot.get_current().send_message(
        chat_id=chat_id,
        text=result_text,
        reply_markup=keyboard
    )
    
    # Очищаем данные сессии
    if user_id in active_reviews:
        del active_reviews[user_id]
    
    # Сбрасываем состояние
    await state.finish()

async def cmd_add_card(message: types.Message, state: FSMContext):
    """
    Обработчик команды /add_card.
    
    Начинает процесс добавления новой карточки.
    
    Args:
        message: Сообщение пользователя.
        state: Состояние FSM.
    """
    # Парсим аргументы команды
    args = message.get_args().split(None, 1)
    
    if len(args) == 2:
        # Если указаны слово и перевод, сразу добавляем карточку
        word = args[0].lower()
        translation = args[1]
        await add_card_direct(message, word, translation)
    else:
        # Запрашиваем слово для добавления
        await message.answer(
            "Пожалуйста, отправьте слово, которое хотите добавить в карточки."
        )
        
        # Устанавливаем состояние
        await SRSStates.adding_card.set()
        
        # Сохраняем шаг (ожидание слова)
        await state.update_data(step="waiting_for_word")

async def add_card_direct(message: types.Message, word: str, translation: str, config: Config = None):
    """
    Добавляет карточку напрямую, без запроса дополнительной информации.
    
    Args:
        message: Сообщение пользователя.
        word: Слово для добавления.
        translation: Перевод слова.
        config: Конфигурация бота.
    """
    user_id = message.from_user.id
    db_path = config.db_path if config else 'translations.db'
    
    # Добавляем карточку в SRS
    success = await add_card_to_srs(user_id, word, translation, db_path)
    
    if success:
        # Добавляем перевод в общий словарь
        from features.transliteration.utils import add_translation
        await add_translation(word, translation, db_path)
        
        await message.answer(
            f"Карточка '{word}' → '{translation}' успешно добавлена!\n\n"
            "Используйте команду /review для повторения карточек."
        )
    else:
        await message.answer(
            f"Карточка со словом '{word}' уже существует или произошла ошибка."
        )

async def process_add_card_step(message: types.Message, state: FSMContext, config: Config = None):
    """
    Обрабатывает шаги добавления карточки.
    
    Args:
        message: Сообщение пользователя.
        state: Состояние FSM.
        config: Конфигурация бота.
    """
    db_path = config.db_path if config else 'translations.db'
    
    # Получаем текущие данные состояния
    data = await state.get_data()
    step = data.get("step", "waiting_for_word")
    
    if step == "waiting_for_word":
        # Получили слово, сохраняем его
        word = message.text.lower()
        
        # Проверяем наличие перевода в словаре
        translation = await get_translation(word, db_path)
        
        if translation:
            # Если перевод найден, предлагаем использовать его
            await message.answer(
                f"Найден перевод для слова '{word}': '{translation}'\n\n"
                "Хотите использовать этот перевод?"
            )
            
            # Создаем клавиатуру с вариантами ответа
            keyboard = get_confirmation_keyboard("use_translation", "Да, использовать", "Нет, другой перевод")
            
            await message.answer(
                "Выберите действие:",
                reply_markup=keyboard
            )
            
            # Сохраняем слово и перевод
            await state.update_data(word=word, translation=translation, step="confirmation")
        else:
            # Если перевод не найден, запрашиваем его
            await message.answer(
                f"Введите перевод для слова '{word}':"
            )
            
            # Сохраняем слово и обновляем шаг
            await state.update_data(word=word, step="waiting_for_translation")
    
    elif step == "waiting_for_translation":
        # Получили перевод
        translation = message.text
        word = data.get("word", "")
        
        # Добавляем карточку
        await add_card_direct(message, word, translation, config)
        
        # Сбрасываем состояние
        await state.finish()

async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext, config: Config = None):
    """
    Обрабатывает подтверждение для действий SRS.
    
    Args:
        callback_query: Запрос обратного вызова.
        state: Состояние FSM.
        config: Конфигурация бота.
    """
    user_id = callback_query.from_user.id
    db_path = config.db_path if config else 'translations.db'
    
    # Получаем действие из callback_data
    action_data = callback_query.data.split(":")
    if len(action_data) < 3:
        await callback_query.answer("Некорректные данные")
        return
    
    action = action_data[1]
    answer = action_data[2]
    
    if action == "use_translation" and answer == "yes":
        # Пользователь согласен использовать найденный перевод
        data = await state.get_data()
        word = data.get("word", "")
        translation = data.get("translation", "")
        
        # Добавляем карточку
        success = await add_card_to_srs(user_id, word, translation, db_path)
        
        if success:
            await callback_query.message.edit_text(
                f"Карточка '{word}' → '{translation}' успешно добавлена!\n\n"
                "Используйте команду /review для повторения карточек."
            )
        else:
            await callback_query.message.edit_text(
                f"Карточка со словом '{word}' уже существует или произошла ошибка."
            )
        
        # Сбрасываем состояние
        await state.finish()
    
    elif action == "use_translation" and answer == "no":
        # Пользователь хочет ввести свой перевод
        data = await state.get_data()
        word = data.get("word", "")
        
        await callback_query.message.edit_text(
            f"Введите перевод для слова '{word}':"
        )
        
        # Обновляем шаг
        await state.update_data(step="waiting_for_translation")
    
    else:
        await callback_query.answer("Неизвестное действие")

async def cmd_cards(message: types.Message, config: Config = None):
    """
    Обработчик команды /cards.
    
    Показывает список карточек пользователя.
    
    Args:
        message: Сообщение пользователя.
        config: Конфигурация бота.
    """
    user_id = message.from_user.id
    db_path = config.db_path if config else 'translations.db'
    
    # Получаем информацию о карточках пользователя
    async with await get_db_connection(db_path) as conn:
        cursor = await conn.execute(
            """
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN next_review <= date('now') THEN 1 ELSE 0 END) as due
            FROM srs_cards
            WHERE user_id = ?
            """,
            (user_id,)
        )
        stats = await cursor.fetchone()
    
    if not stats or stats[0] == 0:
        await message.answer(
            "У вас еще нет карточек для повторения.\n\n"
            "Вы можете добавить карточки с помощью команды /add_card <слово> <перевод>"
        )
        return
    
    total = stats[0]
    due = stats[1] or 0
    
    # Формируем сообщение
    message_text = (
        "📚 <b>Ваши карточки</b>\n\n"
        f"Всего карточек: <b>{total}</b>\n"
        f"Доступно для повторения: <b>{due}</b>\n\n"
    )
    
    if due > 0:
        message_text += "Вы можете начать повторение с помощью команды /review"
    else:
        message_text += "На данный момент у вас нет карточек для повторения. Проверьте позже!"
    
    await message.answer(message_text, parse_mode="HTML")

async def process_new_review(callback_query: types.CallbackQuery, state: FSMContext, config: Config = None):
    """
    Обрабатывает запрос на новое повторение.
    
    Args:
        callback_query: Запрос обратного вызова.
        state: Состояние FSM.
        config: Конфигурация бота.
    """
    # Имитируем команду /review
    message = callback_query.message
    message.from_user = callback_query.from_user
    message.text = "/review"
    
    await cmd_review(message, state, config)
    await callback_query.answer()

def register_srs_handlers(dp: Dispatcher, config: Config = None):
    """
    Регистрирует обработчики модуля интервального повторения.
    
    Args:
        dp: Диспетчер бота.
        config: Конфигурация бота.
    """
    # Регистрируем обработчики команд
    dp.register_message_handler(lambda msg: cmd_review(msg, dp.current_state(), config), commands=["review"])
    dp.register_message_handler(lambda msg: cmd_add_card(msg, dp.current_state()), commands=["add_card"])
    dp.register_message_handler(lambda msg: cmd_cards(msg, config), commands=["cards"])
    
    # Регистрируем обработчики состояний
    dp.register_message_handler(
        lambda msg: process_add_card_step(msg, dp.current_state(), config),
        state=SRSStates.adding_card
    )
    
    # Регистрируем обработчики callback-запросов
    dp.register_callback_query_handler(
        process_show_translation,
        lambda c: c.data == "srs:show_translation",
        state=SRSStates.answering
    )
    
    dp.register_callback_query_handler(
        process_skip,
        lambda c: c.data == "srs:skip",
        state=SRSStates.answering
    )
    
    dp.register_callback_query_handler(
        lambda c: process_rating(c, dp.current_state(), config),
        lambda c: c.data.startswith("rate:"),
        state=SRSStates.rating
    )
    
    dp.register_callback_query_handler(
        lambda c: process_confirmation(c, dp.current_state(), config),
        lambda c: c.data.startswith("confirm:"),
        state=SRSStates.adding_card
    )
    
    dp.register_callback_query_handler(
        lambda c: process_new_review(c, dp.current_state(), config),
        lambda c: c.data == "srs:new_review"
    )
    
    logger.info("Обработчики модуля интервального повторения зарегистрированы")