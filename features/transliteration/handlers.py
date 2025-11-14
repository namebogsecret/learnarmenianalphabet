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
from services.openai_service import get_completion
from services.translation import get_translation, translate_and_save
from features.transliteration.utils import process_text, process_unknown_word, add_translation

logger = logging.getLogger(__name__)

async def text_handler(message: types.Message, config: Config = None):
    """
    Main handler for text messages.
    
    Processes incoming messages and sends transliterated and translated responses.
    """
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    question = message.text
    db_path = config.db_path if config else 'translations.db'
    
    # Log the request
    logger.info(f"Received message from {username} ({user_id}): {question[:50]}...")
    
    try:
        # Update usage statistics
        times = await add_or_update_user(user_id, username, db_path)
        
        # Process the request based on its type
        if question.startswith('?'):
            # OpenAI request for answering a question
            clean_question = question[1:].strip()
            
            if not clean_question:
                await message.answer("Please enter a question after the question mark.")
                return
            
            # Show typing action
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            
            # Get response from OpenAI
            try:
                from services.openai_service import get_completion
                openai_response = await get_completion(clean_question)
                
                # Transliterate the response
                await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
                armenian_answer = await process_text(openai_response, db_path)
                
                # Send both responses: original and transliterated
                await message.answer(f"{openai_response}\n\n{armenian_answer}")
            except Exception as e:
                logger.error(f"Error getting OpenAI response: {e}")
                await message.answer(f"Error getting response: {str(e)}")
        else:
            # Simple text transliteration
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            response = await process_text(question, db_path)
            await message.answer(response)
    
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        await message.answer(f"An error occurred while processing your message. Please try again later.")

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
    args = message.get_args().split(None, 1)

    if len(args) < 2:
        await message.answer(
            "Пожалуйста, укажите слово и перевод: /add_word <слово> <перевод>"
        )
        return

    word = args[0].strip().lower()
    translation = args[1].strip()

    # Валидация входных данных
    if not word or len(word) > 100:
        await message.answer(
            "Слово должно содержать от 1 до 100 символов."
        )
        return

    if not translation or len(translation) > 200:
        await message.answer(
            "Перевод должен содержать от 1 до 200 символов."
        )
        return

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

    # Show typing action
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Переводим текст
    try:
        translation = await translate_and_save(text, db_path)

        if translation:
            await message.answer(f"Перевод: {translation}")
        else:
            await message.answer("Не удалось получить перевод. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await message.answer(f"Ошибка при переводе: {str(e)}")

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
• /word слово - получить перевод слова из словаря
• /translate текст - перевести слово или фразу на армянский
• /add\_word слово перевод - добавить новое слово в словарь

*Дополнительные команды:*
• /help - показать эту справку
• /settings - настройки бота

Бот автоматически запоминает неизвестные слова и добавляет их в словарь после нескольких использований.
    """
    
    try:
        await message.answer(help_text, parse_mode="MarkdownV2")
    except Exception as e:
        # If MarkdownV2 fails, try HTML
        html_help_text = help_text.replace('*', '<b>').replace('_', '<i>')
        html_help_text = html_help_text.replace('</i>', '</i>').replace('</b>', '</b>')
        try:
            await message.answer(html_help_text, parse_mode="HTML")
        except Exception as e:
            # If all formatting fails, send plain text
            await message.answer(help_text.replace('*', '').replace('_', ''), parse_mode=None)

async def start_handler(message: types.Message):
    """
    Obrabotchik komandy /start.
    
    Otobrazhayet privetstvennoe soobshcheniye i kratkuyu instruktsiyu.
    
    Args:
        message: Soobshcheniye ot pol'zovatelya.
    """
    user_name = message.from_user.first_name
    
    welcome_text = f"""
👋 Privet, {user_name}!

Dobro pozhalovat' v Armenian Learning Bot! 🇦🇲

Ya pomogu vam izuchat' armyanskiy yazyk cherez transliteratsiyu i perevod.

*Kak menya ispol'zovat':*
- Otprav'te lyuboy tekst na russkom, chtoby poluchit' ego transliteratsiyu
- Ispol'zuyte ? pered voprosom, chtoby poluchit' otvet ot II
- Ispol'zuyte komandu /help dlya polucheniya polnoy spravki

Udachi v izuchenii armyanskogo yazyka! 🚀
    """
    
    await message.answer(welcome_text, parse_mode="Markdown")

def register_transliteration_handlers(dp: Dispatcher, config: Config = None):
    """
    Registriruet obrabotchiki modulya transliteratsii.
    
    Args:
        dp: Dispetcher bota.
        config: Konfiguratsiya bota (optsional'no).
    """
    # Obrabotchiki komand
    dp.register_message_handler(start_handler, commands=["start"])
    dp.register_message_handler(help_handler, commands=["help"])
    dp.register_message_handler(word_handler, commands=["word"])
    dp.register_message_handler(translate_handler, commands=["translate"])
    dp.register_message_handler(add_word_handler, commands=["add_word"])
    
    # Osnovnoy obrabotchik teksta (s chastichnym primeneniyem config)
    dp.register_message_handler(
        lambda message: text_handler(message, config),
        lambda message: message.chat.type == 'private' and message.text is not None,
        content_types=['text']
    )
    
    logger.info("Obrabotchiki modulya transliteratsii zaregistrirovany")