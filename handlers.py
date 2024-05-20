
from os import getenv
from aiogram import types
from dotenv import load_dotenv
from armenian_dict import transliterate_to_armenian
from myopenai import OpenAI
from log_users import add_or_update_user

async def not_allowed(message: types.Message):
    await message.answer(f"Test 5 queries are expired. Please contact the bot owner for more. @bots_admin_Vladimir")

async def text_handler(message: types.Message):
    load_dotenv()
    users_string = getenv("USERS")
    ALLOWED_USERS = users_string.split(",") if users_string else []
    times = await add_or_update_user(message.from_user.id)
    if str(message.from_user.id) not in ALLOWED_USERS:
        if times == 1:
            await message.answer(f"You have 5 test queries. For more contact the bot owner. @bots_admin_Vladimir")
        elif times > 5:
            await not_allowed(message)
            return
    if message.text:
        if message.text.startswith('?'):
            openai = OpenAI()
            answer = await openai.answer(message.text[1:])
            answer = await openai.handle_response(answer)
            armenian_answer = await transliterate_to_armenian(answer)
            await message.answer(f"{answer}\n\n{armenian_answer}")
            return
        question = message.text
        response = await transliterate_to_armenian(question)
        await message.answer(response)
