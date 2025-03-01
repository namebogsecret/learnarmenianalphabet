import sys
from os.path import dirname, abspath
from os import getenv
from dotenv import load_dotenv
#from chatgpt_async import call_chatgpt
#from get_detailed_request import get_details
if getattr(sys, 'frozen', False):
    src_path = sys._MEIPASS
else:
    src_path = dirname(abspath(__file__))
sys.path.append(src_path)
import asyncio
import nest_asyncio
from handlers import text_handler
#from handlers_async_test import  gpt, gpt_chat,  handle_photos, voice_to_text,document_upload, voice_to_text_chat #, error_handler, bot_response_final, image_generator, rewrite,
#from utils_async import read_strings_from_file

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
#from aiogram.types import ParseMode
#from aiogram.utils import executor
 
#from update_messager_async import update_messager
#from db import create_connection
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text
from aiogram.types import Message
#from keyboard_handling import start_command_handler, handle_callback

#from aiogram.types import ParseMode
#from aiogram.utils import executor


async def send_startup_message(api_token, chat_id, text):
    bot = Bot(token=api_token)
    await bot.send_message(chat_id, text)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
nest_asyncio.apply()

async def my_telegram_bot(api="t_api") -> None:
    #strings_dict = await read_strings_from_file()
    load_dotenv()
    t_api = getenv("TELEGRAM_API")
    
    # await send_startup_message(t_api, "416177154", love)
    # await send_startup_message(t_api, "585870101", love)"""
    
    bot = Bot(token=t_api)
    dp = Dispatcher(bot)
    dp.middleware.setup(LoggingMiddleware())
    #dp.register_callback_query_handler(handle_callback)
    # Регистрация обработчика команды /start
    #dp.register_message_handler(start_command_handler, commands=["start"])
    #dp.add_handler(CallbackQueryHandler(handle_callback))

    # Register your async handlers here, for example:
    #dp.register_message_handler(gpt_chat, content_types=['text'])
    dp.register_message_handler(text_handler, lambda message: message.chat.type == 'private', content_types=['text'])
    # dp.register_message_handler(gpt_chat, lambda message: message.chat.type in ['group', 'supergroup'] and f'@vladimirgptweb_bot' in message.text.lower(), content_types=['text'])

    #dp.register_message_handler(handle_photos, content_types=['photo'])
    # dp.register_message_handler(handle_photos, lambda message: message.chat.type == 'private', content_types=['photo'])
    # dp.register_message_handler(handle_photos, lambda message: message.chat.type in ['group', 'supergroup'] and f'@vladimirgptweb_bot' in message.caption.lower(), content_types=['photo'])

    #dp.register_message_handler(voice_to_text, content_types=['voice'])
    # dp.register_message_handler(voice_to_text, lambda message: message.chat.type == 'private', content_types=['voice'])
    # dp.register_message_handler(voice_to_text_chat, lambda message: message.chat.type in ['group', 'supergroup'], content_types=['voice'])

    #dp.register_message_handler(document_upload, content_types=['document'])
    # dp.register_message_handler(document_upload, lambda message: message.chat.type == 'private', content_types=['document'])
    # dp.register_message_handler(document_upload, lambda message: message.chat.type in ['group', 'supergroup'] and f'@vladimirgptweb_bot' in message.text.lower(), content_types=['document'])
    try:
        await dp.start_polling()
    finally:
        await bot.close()


async def main():
    await my_telegram_bot("t_api_test")

if __name__ == "__main__":
    asyncio.run(main())
