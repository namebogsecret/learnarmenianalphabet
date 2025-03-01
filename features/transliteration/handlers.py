"""
Обработчики сообщений для модуля транслитерации.

Содержит функции-обработчики для работы с сообщениями, 
связанными с транслитерацией русского текста на армянский.
"""

import logging
import re
from aiogram import Dispatcher, types
from config.config import Config
from core.database import add_or_update_user
from services.openai_service import get_completion, translate_with_openai
from features.transliteration.utils import process_text, process_unknown_word, add_translation

logger = logging.getLogger(__name__)

async def text_handler(message: types.Message, config: Config = None):
    """
    Основной обработчик текстовых сообщений.
    
    Обрабатывает входящие сообщения и отправляет транслитерированный и переведенный ответ.
    
    Args:
        message: Сообщение от пользователя.
        config: Конфигурация бота (опционально).
    """
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    question = message.text
    db_path = config.db_path if config else 'translations.db'
    
    # Логируем запрос
    logger.info(f"Received message from {username} ({user_id}): {question[:50]}...")
    
    try:
        # Обновляем статистику использования
        times = await add_or_update_user(user_id, username, db_path)
        
        # Обрабатываем запрос в зависимости от его типа
        if question.startswith('?'):
            # Запрос к OpenAI для получения ответа на вопрос
            clean_question = question[1:].strip()
            
            if not clean_question:
                await message.answer("Пожалуйста, введите вопрос после знака вопроса.")
                return
            
            # Получаем ответ от OpenAI
            openai_response = await get_completion(clean_question)
            
            # Проверяем, что ответ получен успешно
            if not openai_response or isinstance(openai_response, dict) and 'error' in openai_response:
                error_msg = openai_response.get('error', {}).get('message', 'Неизвестная ошибка') if isinstance(openai_response, dict) else 'Ошибка при получении ответа'
                await message.answer(f"Ошибка: {error_msg}")
                return
            
            # Транслитерируем ответ
            armenian_answer = await process_text(openai_response, db_path)
            
            # Отправляем оба ответа: оригинальный и транслитерированный
            await message.answer(f"{openai_response}\n\n{armenian_answer}")
        else:
            # Простая транслитерация текста
            response = await process_text(question, db_path)
            await message.answer(response)
    
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        await message.answer(f"Произошла ошибка при обработке сообщения. Пожалуйста, попробуйте позже.")

async def add_word_handler(message: types.Message, config: Config = None):
    """
    Обработчик команды /add_word.
    
    Добавляет новое слово и его перевод в словарь.
    
    Args:
        message: Сообщение от пользователя.
        config: Конфигурация бота (опционально).
    """
    db_path = config.db_path if config else 'translations.db'
    
    # Парсим аргументы команды
    args = message.get_args().split()
    
    if len(args) < 2:
        await message.answer(
            "Пожалуйста, укажите слово и перевод: /add_word <слово> <перевод>"
        )
        return
    
    word = args[0].lower()
    translation = args[1]
    
    # Добавляем слово в словарь
    success = await add_translation(word, translation, db_path)
    
    if success:
        await message.answer(f"Слово '{word}' успешно добавлено в словарь с переводом '{translation}'")
    else:
        await message.answer(f"Ошибка при добавлении слова '{word}' в словарь")

async def translate_handler(message: types.Message, config: Config = None):
    """
    Обработчик команды /translate.
    
    Переводит слово или фразу на армянский с помощью OpenAI.
    
    Args:
        message: Сообщение от пользователя.
        config: Конфигурация бота (опционально).
    """
    db_path = config.db_path if config else 'translations.db'
    
    # Получаем текст для перевода
    text = message.get_args()
    
    if not text:
        await message.answer(
            "Пожалуйста, укажите текст для перевода: /translate <текст>"
        )
        return
    
    # Переводим текст с помощью OpenAI
    translation = await translate_with_openai(text)
    
    if translation:
        # Пытаемся добавить слово в словарь, если это одно слово
        if len(text.split()) == 1:
            await add_translation(text.lower(), translation, db_path)
        
        await message.answer(f"Перевод: {translation}")
    else:
        await message.answer("Не удалось получить перевод. Пожалуйста, попробуйте позже.")

async def word_handler(message: types.Message, config: Config = None):
    """
    Обработчик команды /word.
    
    Возвращает перевод слова из словаря.
    
    Args:
        message: Сообщение от пользователя.
        config: Конфигурация бота (опционально).
    """
    db_path = config.db_path if config else 'translations.db'
    
    # Получаем слово для перевода
    word = message.get_args().lower()
    
    if not word:
        await message.answer(
            "Пожалуйста, укажите слово для перевода: /word <слово>"
        )
        return
    
    # Получаем перевод из базы данных
    from core.database import get_translation
    
    translation = await get_translation(word, db_path)
    
    if translation:
        await message.answer(f"Слово: {word}\nПеревод: {translation}")
    else:
        await message.answer(
            f"Перевод для слова '{word}' не найден в словаре. "
            f"Вы можете добавить его с помощью команды: "
            f"/add_word {word} <перевод>"
        )

async def help_handler(message: types.Message):
    """
    Обработчик команды /help.
    
    Отображает справку по использованию бота.
    
    Args:
        message: Сообщение от пользователя.
    """
    help_text = """
🇦🇲 *Armenian Learning Bot* 🇦🇲

Этот бот поможет вам изучать армянский язык через транслитерацию и перевод.

*Основные команды:*
• Отправьте любой текст на русском, чтобы получить его транслитерацию
• Отправьте сообщение, начинающееся с ?, чтобы задать вопрос боту (например: ?как дела?)
• /word <слово> - получить перевод слова из словаря
• /translate <текст> - перевести слово или фразу на армянский
• /add_word <слово> <перевод> - добавить новое слово в словарь

*Дополнительные команды:*
• /help - показать эту справку
• /settings - настройки бота

Бот автоматически запоминает неизвестные слова и добавляет их в словарь после нескольких использований.
    """
    
    await message.answer(help_text, parse_mode="Markdown")

async def start_handler(message: types.Message):
    """
    Обработчик команды /start.
    
    Отображает приветственное сообщение и краткую инструкцию.
    
    Args:
        message: Сообщение от пользователя.
    """
    user_name = message.from_user.first_name
    
    welcome_text = f"""
👋 Привет, {user_name}!

Добро пожаловать в Armenian Learning Bot! 🇦🇲

Я помогу вам изучать армянский язык через транслитерацию и перевод.

*Как меня использовать:*
• Отправьте любой текст на русском, чтобы получить его транслитерацию
• Используйте ? перед вопросом, чтобы получить ответ от ИИ
• Используйте команду /help для получения полной справки

Удачи в изучении армянского языка! 🚀
    """
    
    await message.answer(welcome_text, parse_mode="Markdown")

def register_transliteration_handlers(dp: Dispatcher, config: Config = None):
    """
    Регистрирует обработчики модуля транслитерации.
    
    Args:
        dp: Диспетчер бота.
        config: Конфигурация бота (опционально).
    """
    # Обработчики команд
    dp.register_message_handler(start_handler, commands=["start"])
    dp.register_message_handler(help_handler, commands=["help"])
    dp.register_message_handler(word_handler, commands=["word"], 
                             lambda message: bool(message.get_args()))
    dp.register_message_handler(translate_handler, commands=["translate"], 
                              lambda message: bool(message.get_args()))
    dp.register_message_handler(add_word_handler, commands=["add_word"], 
                             lambda message: len(message.get_args().split()) >= 2)
    
    # Основной обработчик текста (с частичным применением config)
    dp.register_message_handler(
        lambda message: text_handler(message, config),
        lambda message: message.chat.type == 'private',
        content_types=['text']
    )
    
    logger.info("Обработчики модуля транслитерации зарегистрированы")