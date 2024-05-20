import asyncio
import sqlite3

async def add_or_update_user(user) -> int:
    conn = sqlite3.connect('translations.db')
    cursor = conn.cursor()
    if user:
        #создание таблицы учета пользователй если не существует user_id  - аутоинкрементный идентификатор пользователя
        cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, user_name TEXT, times INTEGER)')
        #проверка наличия пользователя в базе
        cursor.execute('SELECT user_id FROM users WHERE user_name = ?', (user,))
        row = cursor.fetchone()

        if row:
            #обновление количества запросов пользователя
            cursor.execute('UPDATE users SET times = times + 1 WHERE user_name = ?', (user,))
            #get times
            cursor.execute('SELECT times FROM users WHERE user_name = ?', (user,))
            times = cursor.fetchone()
            conn.commit()
            conn.close()
            return times[0]
        else:
            #добавление нового пользователя
            cursor.execute('INSERT INTO users (user_name, times) VALUES (?, ?)', (user, 1))
            conn.commit()
            conn.close()
            return 1

if __name__ == "__main__":
    # Пример использования
    user = "Vladimir"
    #asyncio.run(main())
    asyncio.run(add_or_update_user(user))
    print(f"Пользователь {user} добавлен или обновлен.")