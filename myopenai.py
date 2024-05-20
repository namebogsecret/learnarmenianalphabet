from os import getenv
import base64
import requests
from dotenv import load_dotenv
import asyncio
import httpx

class OpenAI:
    def __init__(self):
        load_dotenv()
        self.api_key = getenv("OPENAI_API_KEY")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    async def answer(self, question, temperature=0.9, model="gpt-4o"):
        if not question:
            return {"error": {"message": "Необходимо ввести вопрос или загрузить изображение.", "type": "InputError"}}

        messages = [{
            "role": "user",
            "content": [{"type": "text", "text": question}]
        }]

        if not any(message.get('type') == 'image_url' for message in messages[0]['content']):
            model = "gpt-4o"
        print(f" myo {model}")

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 3000,
            "temperature": temperature
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post("https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload, timeout=240)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as http_err:
                return {"error": {"message": f"HTTP ошибка: {http_err}", "type": "HTTPError"}}
            except httpx.RequestError as req_err:
                return {"error": {"message": f"Ошибка запроса: {req_err}", "type": "RequestError"}}

    async def handle_response(self, response):
        """Обрабатывает успешный ответ от API."""
        if 'error' in response:
            return await self.handle_error(response['error'])
        else:
            # Извлекаем и возвращаем полезную часть ответа
            try:
                return response['choices'][0]['message']['content']
            except (IndexError, KeyError):
                return "Ошибка в структуре ответа API."

    async def handle_error(self, error_info):

        """Обрабатывает ошибки, возвращая информативное сообщение."""
        error_message = error_info.get('message', 'Неизвестная ошибка.')
        error_type = error_info.get('type', 'Неизвестный тип ошибки.')
        return f"Ошибка: {error_message} Тип ошибки: {error_type}"

async def get_armenian_translation(word):
    analyzer = OpenAI()
    question = f"Переведи на армянский язык слово '{word}'. не пиши предисловие послесловие точек кавычек итд, только слово перевода"

    response = await analyzer.answer(question, temperature=0.1, model="gpt-3.5-turbo-0125")
    result = await analyzer.handle_response(response)  # handle_response не является асинхронной

    print(result)
    return result

async def main():
    await get_armenian_translation("дудушка")

# Запуск асинхронной функции main
if __name__ == "__main__":
    asyncio.run(main())