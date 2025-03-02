"""
Обработчики сообщений для модуля игр.

Содержит функции для работы с играми "Виселица", "Расшифровка слов" и "Поиск соответствий".
"""

import logging
import asyncio
import random
from typing import Dict, List, Optional, Any, Union

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config.config import Config
from features.games.states import GameStates
from keyboards.inline import get_games_keyboard, get_back_button, get_confirmation_keyboard

logger = logging.getLogger(__name__)

# Словари для хранения активных игр пользователей
hangman_games = {}
scramble_games = {}
match_games = {}


async def cmd_games(message: types.Message):
    """
    Обработчик команды /games.
    
    Показывает меню выбора игры.
    
    Args:
        message: Сообщение пользователя.
    """
    keyboard = get_games_keyboard()
    
    await message.answer(
        "🎮 <b>Игры для изучения армянского</b>\n\n"
        "Выберите игру, которая поможет вам запомнить слова и улучшить навыки:\n\n"
        "• <b>Виселица</b> - угадайте слово по буквам\n"
        "• <b>Расшифровка</b> - соберите слово из перемешанных букв\n"
        "• <b>Соответствия</b> - найдите пары русских и армянских слов\n\n"
        "Игры используют слова из ваших карточек для повторения и закрепления изученного материала.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

async def process_game_selection(callback_query: types.CallbackQuery, state: FSMContext, config: Config = None):
    """
    Обрабатывает выбор игры из меню.
    
    Args:
        callback_query: Запрос обратного вызова.
        state: Состояние FSM.
        config: Конфигурация бота.
    """
    await callback_query.answer()
    
    user_id = callback_query.from_user.id
    db_path = config.db_path if config else 'translations.db'
    
    # Получаем выбранную игру из callback_data
    game = callback_query.data.split(":")[1]
    
    if game == "hangman":
        # Запускаем игру "Виселица"
        await start_hangman_game(callback_query.message, user_id, db_path, state)
    
    elif game == "scramble":
        # Запускаем игру "Расшифровка слов"
        await start_scramble_game(callback_query.message, user_id, db_path, state)
    
    elif game == "wordmatch":
        # Запускаем игру "Поиск соответствий"
        await start_match_game(callback_query.message, user_id, db_path, state)
    
    elif game == "results":
        # Показываем результаты игр
        await show_game_stats(callback_query.message, user_id, db_path)
    
    else:
        await callback_query.message.answer("Неизвестная игра. Пожалуйста, выберите из списка.")

async def start_hangman_game(message: types.Message, user_id: int, db_path: str, state: FSMContext):
    """
    Запускает игру "Виселица".
    
    Args:
        message: Сообщение пользователя.
        user_id: ID пользователя.
        db_path: Путь к файлу базы данных.
        state: Состояние FSM.
    """
    # Получаем случайное слово для игры
    word, translation = await get_random_word_for_game(user_id, db_path)
    
    # Создаем новую игру
    game = HangmanGame(word, translation)
    hangman_games[user_id] = game
    
    # Отправляем начальное состояние игры
    await message.answer(
        game.get_status_message(),
        parse_mode="HTML"
    )
    
    # Предлагаем использовать буквы из клавиатуры
    keyboard = get_hangman_keyboard()
    
    await message.answer(
        "Выберите букву или введите её с клавиатуры:",
        reply_markup=keyboard
    )
    
    # Устанавливаем состояние
    await GameStates.playing_hangman.set()

def get_hangman_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с русскими буквами для игры "Виселица".
    
    Returns:
        Инлайн-клавиатура с буквами.
    """
    keyboard = InlineKeyboardMarkup(row_width=7)
    
    # Русский алфавит
    alphabet = [
        "а", "б", "в", "г", "д", "е", "ё",
        "ж", "з", "и", "й", "к", "л", "м", 
        "н", "о", "п", "р", "с", "т", "у", 
        "ф", "х", "ц", "ч", "ш", "щ", "ъ", 
        "ы", "ь", "э", "ю", "я"
    ]
    
    # Добавляем буквы в клавиатуру
    buttons = []
    for letter in alphabet:
        buttons.append(InlineKeyboardButton(letter, callback_data=f"letter:{letter}"))
    
    keyboard.add(*buttons)
    
    # Добавляем кнопку выхода из игры
    keyboard.add(InlineKeyboardButton("❌ Выйти из игры", callback_data="game:exit"))
    
    return keyboard

async def process_hangman_letter(message: types.Message, state: FSMContext):
    """
    Обрабатывает введенную букву для игры "Виселица".
    
    Args:
        message: Сообщение пользователя.
        state: Состояние FSM.
    """
    user_id = message.from_user.id
    
    # Проверяем, активна ли игра для пользователя
    if user_id not in hangman_games:
        await message.answer(
            "Игра не найдена. Начните новую игру с помощью команды /games."
        )
        await state.finish()
        return
    
    game = hangman_games[user_id]
    
    # Проверяем введенный текст
    text = message.text.strip().lower()
    
    if len(text) != 1 or not text.isalpha():
        await message.answer(
            "Пожалуйста, введите одну букву русского алфавита."
        )
        return
    
    # Делаем ход
    result = game.guess_letter(text)
    
    # Обновляем состояние игры
    await update_hangman_game(message.chat.id, user_id, message.message_id)

async def process_hangman_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на букву в клавиатуре для игры "Виселица".
    
    Args:
        callback_query: Запрос обратного вызова.
        state: Состояние FSM.
    """
    user_id = callback_query.from_user.id
    
    # Проверяем, активна ли игра для пользователя
    if user_id not in hangman_games:
        await callback_query.answer("Игра не найдена. Начните новую игру.")
        await state.finish()
        return
    
    # Получаем данные из callback_data
    data = callback_query.data.split(":")
    
    if data[0] == "letter":
        letter = data[1]
        game = hangman_games[user_id]
        
        # Делаем ход
        result = game.guess_letter(letter)
        
        # Показываем небольшое уведомление о результате
        if result:
            await callback_query.answer("Правильно!")
        else:
            await callback_query.answer("Неверно!")
        
        # Обновляем состояние игры
        await update_hangman_game(callback_query.message.chat.id, user_id, callback_query.message.message_id)
    
    elif data[0] == "game" and data[1] == "exit":
        # Завершаем игру по запросу пользователя
        await end_hangman_game(callback_query.message, user_id, state, "Игра прервана пользователем.")
        await callback_query.answer("Игра завершена")

async def update_hangman_game(chat_id: int, user_id: int, message_id: Optional[int] = None):
    """
    Обновляет состояние игры "Виселица" в сообщении.
    
    Args:
        chat_id: ID чата.
        user_id: ID пользователя.
        message_id: ID сообщения для обновления (опционально).
    """
    game = hangman_games[user_id]
    
    # Проверяем, завершена ли игра
    if game.is_game_over():
        await end_hangman_game_with_result(chat_id, user_id)
        return
    
    # Отправляем обновленное состояние игры
    status_message = game.get_status_message()
    keyboard = get_hangman_keyboard()
    
    try:
        if message_id:
            # Обновляем существующее сообщение
            await types.Bot.get_current().edit_message_text(
                status_message,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            # Отправляем новое сообщение
            await types.Bot.get_current().send_message(
                chat_id,
                status_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
    except Exception as e:
        # Если не удалось обновить сообщение (оно не изменилось или устарело),
        # отправляем новое
        await types.Bot.get_current().send_message(
            chat_id,
            status_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

async def end_hangman_game_with_result(chat_id: int, user_id: int):
    """
    Завершает игру "Виселица" и показывает результат.
    
    Args:
        chat_id: ID чата.
        user_id: ID пользователя.
    """
    game = hangman_games[user_id]
    
    # Получаем результат игры
    result_message = game.get_game_result()
    
    # Создаем клавиатуру для повторной игры
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🎮 Играть снова", callback_data="game:hangman"))
    keyboard.add(InlineKeyboardButton("🎮 Другие игры", callback_data="menu:games"))
    keyboard.add(InlineKeyboardButton("🏠 Главное меню", callback_data="menu:main"))
    
    await types.Bot.get_current().send_message(
        chat_id,
        result_message,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    # Удаляем игру из словаря
    if user_id in hangman_games:
        del hangman_games[user_id]

async def end_hangman_game(message: types.Message, user_id: int, state: FSMContext, reason: str = ""):
    """
    Завершает игру "Виселица" досрочно.
    
    Args:
        message: Сообщение пользователя.
        user_id: ID пользователя.
        state: Состояние FSM.
        reason: Причина завершения игры.
    """
    if user_id in hangman_games:
        game = hangman_games[user_id]
        
        # Формируем сообщение о завершении игры
        result_message = (
            f"🎮 <b>Игра 'Виселица' завершена</b>\n\n"
            f"{reason}\n\n"
            f"Загаданное слово: <b>{game.word}</b>\n"
            f"Перевод: <b>{game.translation}</b>"
        )
        
        # Создаем клавиатуру для повторной игры
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🎮 Играть снова", callback_data="game:hangman"))
        keyboard.add(InlineKeyboardButton("🎮 Другие игры", callback_data="menu:games"))
        keyboard.add(InlineKeyboardButton("🏠 Главное меню", callback_data="menu:main"))
        
        await message.answer(
            result_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        # Удаляем игру из словаря
        del hangman_games[user_id]
    
    # Сбрасываем состояние
    await state.finish()

async def start_scramble_game(message: types.Message, user_id: int, db_path: str, state: FSMContext):
    """
    Запускает игру "Расшифровка слов".
    
    Args:
        message: Сообщение пользователя.
        user_id: ID пользователя.
        db_path: Путь к файлу базы данных.
        state: Состояние FSM.
    """
    # Получаем подходящее слово для игры
    word, translation = await get_word_for_scramble(user_id, db_path=db_path)
    
    # Создаем новую игру
    game = WordScrambleGame(word, translation)
    scramble_games[user_id] = game
    
    # Отправляем начальное состояние игры
    await message.answer(
        game.get_status_message(),
        parse_mode="HTML"
    )
    
    # Создаем клавиатуру с кнопками действий
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💡 Подсказка", callback_data="scramble:hint"),
        InlineKeyboardButton("🔄 Другое слово", callback_data="scramble:new_word")
    )
    keyboard.add(InlineKeyboardButton("❌ Выйти из игры", callback_data="game:exit"))
    
    await message.answer(
        "Введите ваш ответ или воспользуйтесь подсказкой:",
        reply_markup=keyboard
    )
    
    # Устанавливаем состояние
    await GameStates.playing_scramble.set()

async def process_scramble_answer(message: types.Message, state: FSMContext):
    """
    Обрабатывает ответ пользователя для игры "Расшифровка слов".
    
    Args:
        message: Сообщение пользователя.
        state: Состояние FSM.
    """
    user_id = message.from_user.id
    
    # Проверяем, активна ли игра для пользователя
    if user_id not in scramble_games:
        await message.answer(
            "Игра не найдена. Начните новую игру с помощью команды /games."
        )
        await state.finish()
        return
    
    game = scramble_games[user_id]
    
    # Проверяем ответ
    answer = message.text.strip().lower()
    correct = game.check_answer(answer)
    
    if correct:
        # Правильный ответ - завершаем игру с победой
        await message.answer(
            f"🎉 <b>Правильно!</b>\n\n"
            f"Вы угадали слово <b>{game.word}</b> - <b>{game.translation}</b>\n\n"
            f"Количество попыток: <b>{game.attempts}</b>",
            parse_mode="HTML"
        )
        
        # Предлагаем сыграть еще раз
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🎮 Играть снова", callback_data="game:scramble"))
        keyboard.add(InlineKeyboardButton("🎮 Другие игры", callback_data="menu:games"))
        keyboard.add(InlineKeyboardButton("🏠 Главное меню", callback_data="menu:main"))
        
        await message.answer(
            "Хотите сыграть еще раз?",
            reply_markup=keyboard
        )
        
        # Удаляем игру из словаря
        del scramble_games[user_id]
        
        # Сбрасываем состояние
        await state.finish()
    else:
        # Неправильный ответ - показываем текущее состояние
        await message.answer(
            f"❌ Неверно, попробуйте еще раз.\n\n"
            f"{game.get_status_message()}",
            parse_mode="HTML"
        )
        
        # Обновляем клавиатуру
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("💡 Подсказка", callback_data="scramble:hint"),
            InlineKeyboardButton("🔄 Другое слово", callback_data="scramble:new_word")
        )
        keyboard.add(InlineKeyboardButton("❌ Выйти из игры", callback_data="game:exit"))
        
        await message.answer(
            "Введите ваш ответ или воспользуйтесь подсказкой:",
            reply_markup=keyboard
        )

async def process_scramble_callback(callback_query: types.CallbackQuery, state: FSMContext, config: Config = None):
    """
    Обрабатывает нажатие кнопок в игре "Расшифровка слов".
    
    Args:
        callback_query: Запрос обратного вызова.
        state: Состояние FSM.
        config: Конфигурация бота.
    """
    user_id = callback_query.from_user.id
    db_path = config.db_path if config else 'translations.db'
    
    # Проверяем, активна ли игра для пользователя
    if user_id not in scramble_games and not callback_query.data.startswith("game:"):
        await callback_query.answer("Игра не найдена. Начните новую игру.")
        await state.finish()
        return
    
    # Обрабатываем нажатие кнопок
    if callback_query.data == "scramble:hint":
        game = scramble_games[user_id]
        hint = game.get_hint()
        
        await callback_query.answer()
        await callback_query.message.answer(
            f"💡 <b>Подсказка</b>\n\n{hint}",
            parse_mode="HTML"
        )
    
    elif callback_query.data == "scramble:new_word":
        # Получаем новое слово и обновляем игру
        word, translation = await get_word_for_scramble(user_id, db_path=db_path)
        game = WordScrambleGame(word, translation)
        scramble_games[user_id] = game
        
        await callback_query.answer("Загадано новое слово!")
        
        # Отправляем обновленное состояние игры
        await callback_query.message.edit_text(
            game.get_status_message(),
            parse_mode="HTML"
        )
        
        # Обновляем клавиатуру
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("💡 Подсказка", callback_data="scramble:hint"),
            InlineKeyboardButton("🔄 Другое слово", callback_data="scramble:new_word")
        )
        keyboard.add(InlineKeyboardButton("❌ Выйти из игры", callback_data="game:exit"))
        
        await callback_query.message.answer(
            "Введите ваш ответ или воспользуйтесь подсказкой:",
            reply_markup=keyboard
        )
    
    elif callback_query.data == "game:exit":
        # Завершаем игру по запросу пользователя
        if user_id in scramble_games:
            game = scramble_games[user_id]
            
            await callback_query.answer("Игра завершена")
            
            # Показываем правильный ответ
            await callback_query.message.answer(
                f"Игра 'Расшифровка слов' завершена.\n\n"
                f"Загаданное слово: <b>{game.word}</b>\n"
                f"Перевод: <b>{game.translation}</b>",
                parse_mode="HTML"
            )
            
            # Предлагаем вернуться в меню
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🎮 Игры", callback_data="menu:games"))
            keyboard.add(InlineKeyboardButton("🏠 Главное меню", callback_data="menu:main"))
            
            await callback_query.message.answer(
                "Выберите действие:",
                reply_markup=keyboard
            )
            
            # Удаляем игру из словаря
            del scramble_games[user_id]
            
            # Сбрасываем состояние
            await state.finish()

async def start_match_game(message: types.Message, user_id: int, db_path: str, state: FSMContext):
    """
    Запускает игру "Поиск соответствий".
    
    Args:
        message: Сообщение пользователя.
        user_id: ID пользователя.
        db_path: Путь к файлу базы данных.
        state: Состояние FSM.
    """
    # Получаем пары слов для игры
    pairs = await get_pairs_for_word_match(user_id, count=5, db_path=db_path)
    
    # Создаем новую игру
    game = WordMatchGame(pairs)
    match_games[user_id] = game
    
    # Отправляем начальное состояние игры
    await message.answer(
        game.get_status_message(),
        parse_mode="HTML"
    )
    
    # Создаем клавиатуру с русскими и армянскими словами
    keyboard = get_match_game_keyboard(game)
    
    await message.answer(
        "Выберите пару слов, сначала на одном языке, затем на другом:",
        reply_markup=keyboard
    )
    
    # Устанавливаем состояние
    await GameStates.playing_wordmatch.set()

def get_match_game_keyboard(game: WordMatchGame) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для игры "Поиск соответствий".
    
    Args:
        game: Экземпляр игры.
        
    Returns:
        Инлайн-клавиатура с русскими и армянскими словами.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    # Получаем доступные слова
    russian_words = game.get_available_words('russian')
    armenian_words = game.get_available_words('armenian')
    
    # Добавляем заголовок для русских слов
    keyboard.add(InlineKeyboardButton("🇷🇺 Русские слова:", callback_data="match:noop"))
    
    # Добавляем русские слова
    for word in russian_words:
        keyboard.add(InlineKeyboardButton(word, callback_data=f"match:rus:{word}"))
    
    # Добавляем заголовок для армянских слов
    keyboard.add(InlineKeyboardButton("🇦🇲 Армянские слова:", callback_data="match:noop"))
    
    # Добавляем армянские слова
    for word in armenian_words:
        keyboard.add(InlineKeyboardButton(word, callback_data=f"match:arm:{word}"))
    
    # Добавляем кнопку выхода
    keyboard.add(InlineKeyboardButton("❌ Выйти из игры", callback_data="game:exit"))
    
    return keyboard

async def process_match_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор слова в игре "Поиск соответствий".
    
    Args:
        callback_query: Запрос обратного вызова.
        state: Состояние FSM.
    """
    user_id = callback_query.from_user.id
    
    # Проверяем, активна ли игра для пользователя
    if user_id not in match_games and not callback_query.data.startswith("game:"):
        await callback_query.answer("Игра не найдена. Начните новую игру.")
        await state.finish()
        return
    
    # Проверяем нажатие "noop" (заголовки)
    if callback_query.data == "match:noop":
        await callback_query.answer()
        return
    
    # Обрабатываем выбор слова
    if callback_query.data.startswith("match:"):
        parts = callback_query.data.split(":")
        if len(parts) == 3:
            language = parts[1]  # 'rus' или 'arm'
            word = parts[2]
            
            game = match_games[user_id]
            
            # Выбираем слово
            lang_full = 'russian' if language == 'rus' else 'armenian'
            result = game.select_word(word, lang_full)
            
            if not result:
                # Слово уже выбрано или сопоставлено
                await callback_query.answer("Это слово уже выбрано или сопоставлено")
                return
            
            # Показываем уведомление о выбранном слове
            if game.selected_word is None:
                # Найдено соответствие
                await callback_query.answer("Соответствие найдено!")
                
                # Проверяем, завершена ли игра
                if game.is_completed():
                    # Игра завершена - показываем результат
                    await callback_query.message.edit_text(
                        game.get_game_result(),
                        parse_mode="HTML"
                    )
                    
                    # Предлагаем сыграть еще раз
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(InlineKeyboardButton("🎮 Играть снова", callback_data="game:wordmatch"))
                    keyboard.add(InlineKeyboardButton("🎮 Другие игры", callback_data="menu:games"))
                    keyboard.add(InlineKeyboardButton("🏠 Главное меню", callback_data="menu:main"))
                    
                    await callback_query.message.answer(
                        "Выберите действие:",
                        reply_markup=keyboard
                    )
                    
                    # Удаляем игру из словаря
                    del match_games[user_id]
                    
                    # Сбрасываем состояние
                    await state.finish()
                else:
                    # Игра продолжается - обновляем клавиатуру
                    await callback_query.message.edit_text(
                        game.get_status_message(),
                        parse_mode="HTML"
                    )
                    
                    # Обновляем клавиатуру
                    keyboard = get_match_game_keyboard(game)
                    
                    await callback_query.message.answer(
                        "Выберите следующую пару слов:",
                        reply_markup=keyboard
                    )
            else:
                # Первое слово выбрано - ожидаем второе
                await callback_query.answer(f"Выбрано слово: {word}")
                
                # Обновляем текст сообщения
                await callback_query.message.edit_text(
                    game.get_status_message(),
                    parse_mode="HTML"
                )
    
    elif callback_query.data == "game:exit":
        # Завершаем игру по запросу пользователя
        if user_id in match_games:
            game = match_games[user_id]
            
            await callback_query.answer("Игра завершена")
            
            # Показываем правильные пары
            message = "Игра 'Поиск соответствий' завершена.\n\n<b>Правильные пары:</b>\n"
            for rus, arm in game.word_pairs:
                message += f"• {rus} - {arm}\n"
            
            await callback_query.message.answer(
                message,
                parse_mode="HTML"
            )
            
            # Предлагаем вернуться в меню
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🎮 Игры", callback_data="menu:games"))
            keyboard.add(InlineKeyboardButton("🏠 Главное меню", callback_data="menu:main"))
            
            await callback_query.message.answer(
                "Выберите действие:",
                reply_markup=keyboard
            )
            
            # Удаляем игру из словаря
            del match_games[user_id]
            
            # Сбрасываем состояние
            await state.finish()

async def show_game_stats(message: types.Message, user_id: int, db_path: str):
    """
    Показывает статистику игр пользователя.
    
    Args:
        message: Сообщение пользователя.
        user_id: ID пользователя.
        db_path: Путь к файлу базы данных.
    """
    # Заглушка для статистики игр
    # В реальной реализации здесь будет запрос к базе данных для получения статистики
    
    await message.answer(
        "📊 <b>Статистика игр</b>\n\n"
        "Функция статистики пока находится в разработке.\n\n"
        "Скоро здесь появится информация о вашем прогрессе, достижениях и результатах игр.",
        parse_mode="HTML"
    )
    
    # Предлагаем вернуться в меню игр
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🎮 Вернуться к играм", callback_data="menu:games"))
    
    await message.answer(
        "Выберите действие:",
        reply_markup=keyboard
    )

async def cmd_hangman(message: types.Message, state: FSMContext, config: Config = None):
    """
    Обработчик команды /hangman.
    
    Запускает игру "Виселица" напрямую.
    
    Args:
        message: Сообщение пользователя.
        state: Состояние FSM.
        config: Конфигурация бота.
    """
    user_id = message.from_user.id
    db_path = config.db_path if config else 'translations.db'
    
    await start_hangman_game(message, user_id, db_path, state)

async def cmd_scramble(message: types.Message, state: FSMContext, config: Config = None):
    """
    Обработчик команды /scramble.
    
    Запускает игру "Расшифровка слов" напрямую.
    
    Args:
        message: Сообщение пользователя.
        state: Состояние FSM.
        config: Конфигурация бота.
    """
    user_id = message.from_user.id
    db_path = config.db_path if config else 'translations.db'
    
    await start_scramble_game(message, user_id, db_path, state)

async def cmd_wordmatch(message: types.Message, state: FSMContext, config: Config = None):
    """
    Обработчик команды /wordmatch.
    
    Запускает игру "Поиск соответствий" напрямую.
    
    Args:
        message: Сообщение пользователя.
        state: Состояние FSM.
        config: Конфигурация бота.
    """
    user_id = message.from_user.id
    db_path = config.db_path if config else 'translations.db'
    
    await start_match_game(message, user_id, db_path, state)

def register_games_handlers(dp: Dispatcher, config: Config = None):
    """
    Регистрирует обработчики модуля игр.
    
    Args:
        dp: Диспетчер бота.
        config: Конфигурация бота.
    """
    # Регистрируем обработчики команд
    dp.register_message_handler(cmd_games, commands=["games"])
    dp.register_message_handler(lambda msg: cmd_hangman(msg, dp.current_state(), config), commands=["hangman"])
    dp.register_message_handler(lambda msg: cmd_scramble(msg, dp.current_state(), config), commands=["scramble"])
    dp.register_message_handler(lambda msg: cmd_wordmatch(msg, dp.current_state(), config), commands=["wordmatch"])
    
    # Регистрируем обработчики callback-запросов
    dp.register_callback_query_handler(
        lambda c: process_game_selection(c, dp.current_state(), config),
        lambda c: c.data.startswith("game:")
    )
    
    dp.register_callback_query_handler(
        lambda c: process_scramble_callback(c, dp.current_state(), config),
        lambda c: c.data.startswith("scramble:") or (c.data == "game:exit" and c.from_user.id in scramble_games),
        state=GameStates.playing_scramble
    )
    
    dp.register_callback_query_handler(
        process_hangman_callback,
        lambda c: c.data.startswith("letter:") or (c.data == "game:exit" and c.from_user.id in hangman_games),
        state=GameStates.playing_hangman
    )
    
    dp.register_callback_query_handler(
        process_match_callback,
        lambda c: c.data.startswith("match:") or (c.data == "game:exit" and c.from_user.id in match_games),
        state=GameStates.playing_wordmatch
    )
    
    # Регистрируем обработчики сообщений в играх
    dp.register_message_handler(
        process_hangman_letter,
        state=GameStates.playing_hangman,
        content_types=types.ContentTypes.TEXT
    )
    
    dp.register_message_handler(
        process_scramble_answer,
        state=GameStates.playing_scramble,
        content_types=types.ContentTypes.TEXT
    )
    
    logger.info("Обработчики модуля игр зарегистрированы")



class HangmanGame:
    """
    Класс для игры "Виселица".
    
    Attributes:
        word: Загаданное слово.
        translation: Перевод слова.
        guessed_letters: Множество угаданных букв.
        wrong_letters: Множество неправильно угаданных букв.
        max_attempts: Максимальное количество ошибок.
        attempts_left: Оставшееся количество попыток.
    """
    
    def __init__(self, word: str, translation: str, max_attempts: int = 6):
        """
        Инициализирует новую игру "Виселица".
        
        Args:
            word: Загаданное слово на русском.
            translation: Перевод слова на армянский.
            max_attempts: Максимальное количество ошибок.
        """
        self.word = word.lower()
        self.translation = translation
        self.guessed_letters: Set[str] = set()
        self.wrong_letters: Set[str] = set()
        self.max_attempts = max_attempts
        self.attempts_left = max_attempts
    
    def guess_letter(self, letter: str) -> bool:
        """
        Проверяет букву и обновляет состояние игры.
        
        Args:
            letter: Буква для проверки (в нижнем регистре).
            
        Returns:
            True, если буква присутствует в слове, иначе False.
        """
        if not letter or len(letter) != 1:
            return False
        
        letter = letter.lower()
        
        # Если буква уже была угадана или использована, считаем неправильным ходом
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False
        
        if letter in self.word:
            self.guessed_letters.add(letter)
            return True
        else:
            self.wrong_letters.add(letter)
            self.attempts_left -= 1
            return False
    
    def get_masked_word(self) -> str:
        """
        Возвращает слово с угаданными буквами и скрытыми неугаданными.
        
        Returns:
            Строка с угаданными и скрытыми буквами.
        """
        return ''.join([letter if letter in self.guessed_letters or letter.isspace() else '_' for letter in self.word])
    
    def get_status_message(self) -> str:
        """
        Формирует сообщение о текущем состоянии игры.
        
        Returns:
            Сообщение с информацией о текущем состоянии игры.
        """
        masked_word = self.get_masked_word()
        
        message = f"🎮 <b>Игра 'Виселица'</b>\n\n"
        message += f"Слово: <b>{' '.join(masked_word)}</b>\n\n"
        
        if self.wrong_letters:
            message += f"Неправильные буквы: <b>{', '.join(sorted(self.wrong_letters))}</b>\n"
        
        message += f"Осталось попыток: <b>{self.attempts_left}</b> из <b>{self.max_attempts}</b>\n\n"
        
        return message
    
    def is_game_over(self) -> bool:
        """
        Проверяет, завершена ли игра.
        
        Returns:
            True, если игра завершена (победа или поражение), иначе False.
        """
        return self.is_win() or self.attempts_left <= 0
    
    def is_win(self) -> bool:
        """
        Проверяет, выиграна ли игра.
        
        Returns:
            True, если все буквы в слове угаданы, иначе False.
        """
        for letter in self.word:
            if letter not in self.guessed_letters and letter.isalpha():
                return False
        return True
    
    def get_game_result(self) -> str:
        """
        Формирует сообщение с результатом игры.
        
        Returns:
            Сообщение с результатом игры.
        """
        if self.is_win():
            return (
                f"🎉 <b>Поздравляем! Вы победили!</b>\n\n"
                f"Загаданное слово: <b>{self.word}</b>\n"
                f"Перевод: <b>{self.translation}</b>\n\n"
                f"Вы использовали {self.max_attempts - self.attempts_left} неверных попыток."
            )
        else:
            return (
                f"😢 <b>Игра окончена!</b>\n\n"
                f"Загаданное слово: <b>{self.word}</b>\n"
                f"Перевод: <b>{self.translation}</b>\n\n"
                f"Не расстраивайтесь, попробуйте еще раз!"
            )


async def get_random_word_for_game(user_id: int, db_path: str = 'translations.db') -> Tuple[str, str]:
    """
    Получает случайное слово из базы данных для игры.
    
    Args:
        user_id: ID пользователя.
        db_path: Путь к файлу базы данных.
        
    Returns:
        Кортеж (слово, перевод).
    """
    from core.database import execute_query
    
    try:
        # Сначала пытаемся получить слова из карточек пользователя
        cards = await execute_query(
            """
            SELECT word, translation 
            FROM srs_cards 
            WHERE user_id = ?
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (user_id,),
            db_path,
            fetch=True
        )
        
        if cards and cards[0]:
            return cards[0]['word'], cards[0]['translation']
        
        # Если у пользователя нет карточек, берем из общего словаря
        words = await execute_query(
            """
            SELECT word, translation 
            FROM translation_dict
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (),
            db_path,
            fetch=True
        )
        
        if words and words[0]:
            return words[0]['word'], words[0]['translation']
        
        # Если в базе нет слов, возвращаем дефолтное
        return "армянский", "հայերեն"
        
    except Exception as e:
        logger.error(f"Ошибка при получении случайного слова: {e}")
        return "язык", "լեզու"