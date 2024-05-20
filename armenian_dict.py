import sqlite3
import random
from myopenai import get_armenian_translation

async def transliterate_to_armenian(text):
    # Подключение к базе данных SQLite
    conn = sqlite3.connect('translations.db')
    cursor = conn.cursor()
    max_count = 10

    # Словарь для транслитерации букв
    transliteration_map = {
        'А': ['Ա', 'Ը'], 'Б': ['Բ'], 'В': ['Վ'], 'Г': ['Գ'], 'Д': ['Դ'], 'Е': ['Ե', 'Է'], 'Ё': ['Յո'], 'Ж': ['Ժ'], 'З': ['Զ'],
        'И': ['Ի'], 'Й': ['Յ'], 'К': ['Կ'], 'Л': ['Լ'], 'М': ['Մ'], 'Н': ['Ն'], 'О': ['Ո'], 'П': ['Պ'], 'Р': ['Ռ'],
        'С': ['Ս'], 'Т': ['Տ'], 'У': ['Ու'], 'Ф': ['Ֆ'], 'Х': ['Խ', 'Հ'], 'Ц': ['Ց'], 'Ч': ['Չ'], 'Ш': ['Շ'], 'Щ': ['Շ'],
        'Ъ': [''], 'Ы': ['Ը'], 'Ь': [''], 'Э': ['Է'], 'Ю': ['Յու'], 'Я': ['Յա'], 'а': ['ա', 'ը'], 'б': ['բ'], 'в': ['վ'],
        'г': ['գ'], 'д': ['դ'], 'е': ['ե', 'է'], 'ё': ['յո'], 'ж': ['ժ'], 'з': ['զ'], 'и': ['ի'], 'й': ['յ'], 'к': ['կ'],
        'л': ['լ'], 'м': ['մ'], 'н': ['ն'], 'о': ['ո'], 'п': ['պ'], 'р': ['ռ'], 'с': ['ս'], 'т': ['տ'], 'у': ['ու'],
        'ф': ['ֆ'], 'х': ['խ', 'հ'], 'ц': ['ց'], 'ч': ['չ'], 'ш': ['շ'], 'щ': ['շ'], 'ъ': [''], 'ы': ['ը'], 'ь': [''],
        'э': ['է'], 'ю': ['յու'], 'я': ['յա']
    }

    async def transliterate_to_armenian(text):
        transliterated_text = ''.join(random.choice(transliteration_map.get(char, [char])) for char in text)
        return transliterated_text

    # Функция для перевода и транслитерации текста
    async def translate_and_transliterate(text):
        words = text.split()
        result = []
        for word in words:
            transliterated_word = await transliterate_to_armenian(word)
            cursor.execute('SELECT translation FROM translation_dict WHERE word=?', (word.lower(),))
            row = cursor.fetchone()
            if row:
                transliterated_word += f" ({row[0]})"
            else:
                cursor.execute('SELECT count FROM unknown_words WHERE word=?', (word.lower(),))
                row = cursor.fetchone()
                if row:
                    cursor.execute('UPDATE unknown_words SET count = count + 1 WHERE word = ?', (word.lower(),))
                    # Получение обновленного значения count
                    cursor.execute('SELECT count FROM unknown_words WHERE word = ?', (word.lower(),))
                    count = cursor.fetchone()[0]
                    if count >= max_count:
                        # Удаление слова из таблицы unknown_words
                        cursor.execute('DELETE FROM unknown_words WHERE word = ?', (word.lower(),))
                        # Добавление слова в таблицу translation_dict
                        translation = await get_armenian_translation(word)
                        print(f"Перевод слова '{word}': {translation}")
                        cursor.execute('INSERT INTO translation_dict (word, translation) VALUES (?, ?)', (word.lower(), translation))
                        transliterated_word += f" ({translation})"
                else:
                    cursor.execute('INSERT INTO unknown_words (word, count) VALUES (?, ?)', (word.lower(), 1))
            result.append(transliterated_word)
        conn.commit()
        return ' '.join(result)

    # Пример использования
    russian_text = text
    armenian_text = await translate_and_transliterate(russian_text)
    print(russian_text)
    print(armenian_text)

    # Закрытие соединения с базой данных
    conn.close()
    return armenian_text

if __name__ == '__main__':
    text = "Привет, мир!"
    transliterate_to_armenian(text)