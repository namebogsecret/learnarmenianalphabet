"""
Тесты для модуля игр.

Проверяет функциональность различных игр для изучения армянского языка.
"""

import unittest
import asyncio
import os
import sys
import sqlite3
from unittest.mock import patch, MagicMock, AsyncMock

# Добавляем корневую директорию проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем модули после завершения их реализации
# from features.games.hangman import HangmanGame
# from features.games.word_scramble import WordScrambleGame
# from features.games.word_match import WordMatchGame


class TestHangmanGame(unittest.TestCase):
    """Тесты для игры 'Виселица'."""
    
    @unittest.skip("Модуль HangmanGame еще не реализован")
    def test_initialize_game(self):
        """Тест инициализации игры."""
        game = HangmanGame("тест", "փորձարկում")
        
        # Проверяем, что слово установлено
        self.assertEqual(game.word, "тест")
        
        # Проверяем, что перевод установлен
        self.assertEqual(game.translation, "փորձարկում")
        
        # Проверяем, что маска слова содержит нужное количество символов
        self.assertEqual(len(game.get_masked_word()), len(game.word))
        
        # Проверяем, что игра не завершена
        self.assertFalse(game.is_game_over())
    
    @unittest.skip("Модуль HangmanGame еще не реализован")
    def test_guess_letter(self):
        """Тест угадывания буквы."""
        game = HangmanGame("тест", "փորձարկում")
        
        # Угадываем правильную букву
        result = game.guess_letter("т")
        
        # Проверяем, что результат положительный
        self.assertTrue(result)
        
        # Проверяем, что маска обновилась
        masked_word = game.get_masked_word()
        self.assertEqual(masked_word[0], "т")
        
        # Угадываем неправильную букву
        result = game.guess_letter("ы")
        
        # Проверяем, что результат отрицательный
        self.assertFalse(result)
        
        # Проверяем, что счетчик попыток уменьшился
        self.assertEqual(game.attempts_left, game.max_attempts - 1)
    
    @unittest.skip("Модуль HangmanGame еще не реализован")
    def test_game_over_conditions(self):
        """Тест условий завершения игры."""
        game = HangmanGame("тест", "փորձարկում")
        
        # Угадываем все буквы
        game.guess_letter("т")
        game.guess_letter("е")
        game.guess_letter("с")
        
        # Проверяем, что игра завершена с победой
        self.assertTrue(game.is_game_over())
        self.assertTrue(game.is_win())
        
        # Создаем новую игру
        game = HangmanGame("тест", "փորձարկում")
        
        # Угадываем неправильные буквы до исчерпания попыток
        for _ in range(game.max_attempts):
            game.guess_letter("ы")
        
        # Проверяем, что игра завершена с поражением
        self.assertTrue(game.is_game_over())
        self.assertFalse(game.is_win())


class TestWordScrambleGame(unittest.TestCase):
    """Тесты для игры 'Расшифровка слов'."""
    
    @unittest.skip("Модуль WordScrambleGame еще не реализован")
    def test_scramble_word(self):
        """Тест перемешивания букв в слове."""
        word = "тест"
        game = WordScrambleGame(word, "փորձարկում")
        
        # Проверяем, что перемешанное слово отличается от исходного
        self.assertNotEqual(game.scrambled_word, word)
        
        # Проверяем, что перемешанное слово содержит те же буквы
        self.assertEqual(sorted(game.scrambled_word), sorted(word))
    
    @unittest.skip("Модуль WordScrambleGame еще не реализован")
    def test_check_answer(self):
        """Тест проверки ответа пользователя."""
        game = WordScrambleGame("тест", "փորձարկում")
        
        # Проверяем правильный ответ
        self.assertTrue(game.check_answer("тест"))
        
        # Проверяем неправильный ответ
        self.assertFalse(game.check_answer("неверно"))
        
        # Проверяем с учетом регистра
        self.assertTrue(game.check_answer("Тест"))


class TestWordMatchGame(unittest.TestCase):
    """Тесты для игры 'Поиск соответствий'."""
    
    @unittest.skip("Модуль WordMatchGame еще не реализован")
    def test_initialize_game(self):
        """Тест инициализации игры."""
        # Создаем список слов с переводами
        word_pairs = [
            ("один", "մեկ"),
            ("два", "երկու"),
            ("три", "երեք"),
            ("четыре", "չորս")
        ]
        
        game = WordMatchGame(word_pairs)
        
        # Проверяем, что все пары добавлены
        self.assertEqual(len(game.word_pairs), len(word_pairs))
        
        # Проверяем, что списки слов и переводов имеют одинаковую длину
        self.assertEqual(len(game.russian_words), len(game.armenian_words))
    
    @unittest.skip("Модуль WordMatchGame еще не реализован")
    def test_check_match(self):
        """Тест проверки соответствия слов."""
        word_pairs = [
            ("один", "մեկ"),
            ("два", "երկու"),
            ("три", "երեք"),
            ("четыре", "չորս")
        ]
        
        game = WordMatchGame(word_pairs)
        
        # Проверяем правильное соответствие
        self.assertTrue(game.check_match("один", "մեկ"))
        
        # Проверяем неправильное соответствие
        self.assertFalse(game.check_match("один", "երկու"))
    
    @unittest.skip("Модуль WordMatchGame еще не реализован")
    def test_game_completion(self):
        """Тест завершения игры."""
        word_pairs = [
            ("один", "մեկ"),
            ("два", "երկու")
        ]
        
        game = WordMatchGame(word_pairs)
        
        # Находим все соответствия
        game.check_match("один", "մեկ")
        game.check_match("два", "երկու")
        
        # Проверяем, что игра завершена
        self.assertTrue(game.is_completed())
        
        # Проверяем, что все пары найдены
        self.assertEqual(len(game.matched_pairs), len(word_pairs))


# Добавляем тесты для вспомогательных функций игр

class TestGameUtils(unittest.TestCase):
    """Тесты для вспомогательных функций игр."""
    
    @patch('core.database.execute_query')
    async def test_get_random_words(self, mock_execute_query):
        """Тест получения случайных слов из базы данных."""
        # Реализация будет добавлена после создания соответствующей функции
        pass
    
    @patch('features.games.utils.get_random_words')
    async def test_generate_game_data(self, mock_get_random_words):
        """Тест генерации данных для игр."""
        # Реализация будет добавлена после создания соответствующей функции
        pass


if __name__ == '__main__':
    # Запускаем асинхронные тесты
    loop = asyncio.get_event_loop()
    unittest.main()