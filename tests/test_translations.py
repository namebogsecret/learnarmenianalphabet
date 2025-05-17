"""
Тесты для модуля транслитерации и переводов.

Проверяет функциональность транслитерации русского текста на армянский 
и работу со словарем переводов.
"""

import unittest
import asyncio
import os
import sys
import sqlite3
from unittest.mock import patch, MagicMock

# Добавляем корневую директорию проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.dictionaries.transliteration import transliterate_text, transliterate_char
from data.dictionaries.armenian_dict import get_armenian_translation
from features.transliteration.utils import process_text, process_unknown_word, add_translation
from core.database import get_translation, add_translation as db_add_translation


class TestTransliteration(unittest.TestCase):
    """Тесты для функций транслитерации."""
    
    def test_transliterate_char(self):
        """Тест транслитерации отдельных символов."""
        # Проверяем транслитерацию гласных
        self.assertIn(transliterate_char('а'), ['ա', 'ը'])
        self.assertIn(transliterate_char('е'), ['ե', 'է'])
        
        # Проверяем транслитерацию согласных
        self.assertEqual(transliterate_char('б'), 'բ')
        self.assertEqual(transliterate_char('в'), 'վ')
        
        # Проверяем символы, которых нет в карте транслитерации
        self.assertEqual(transliterate_char('1'), '1')
        self.assertEqual(transliterate_char(' '), ' ')
        self.assertEqual(transliterate_char('.'), '.')
    
    def test_transliterate_text(self):
        """Тест транслитерации текста."""
        # Проверяем транслитерацию простого текста
        result = transliterate_text('привет')
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Проверяем, что длина текста примерно сохраняется
        text = 'привет, мир!'
        result = transliterate_text(text)
        # Допускаем небольшое отклонение в длине из-за особенностей армянского алфавита
        self.assertLessEqual(abs(len(result) - len(text)), 5)
        
        # Проверяем сохранение пробелов и знаков препинания
        text = 'привет, как дела?'
        result = transliterate_text(text)
        self.assertEqual(result.count(' '), text.count(' '))
        self.assertEqual(result.count(','), text.count(','))
        self.assertEqual(result.count('?'), text.count('?'))


class TestTranslations(unittest.TestCase):
    """Тесты для функций работы с переводами."""
    
    @classmethod
    def setUpClass(cls):
        """Создает тестовую базу данных перед запуском тестов."""
        # Создаем тестовую базу данных в памяти
        cls.db_conn = sqlite3.connect(':memory:')
        cls.db_cursor = cls.db_conn.cursor()
        
        # Создаем необходимые таблицы
        cls.db_cursor.execute('''
            CREATE TABLE translation_dict (
                word TEXT PRIMARY KEY,
                translation TEXT
            )
        ''')
        
        cls.db_cursor.execute('''
            CREATE TABLE unknown_words (
                word TEXT PRIMARY KEY,
                count INTEGER DEFAULT 1
            )
        ''')
        
        # Добавляем тестовые данные
        test_data = [
            ('привет', 'բարև'),
            ('мир', 'աշխարհ'),
            ('армянский', 'հայերեն')
        ]
        cls.db_cursor.executemany(
            'INSERT INTO translation_dict (word, translation) VALUES (?, ?)',
            test_data
        )
        cls.db_conn.commit()
    
    @classmethod
    def tearDownClass(cls):
        """Закрывает соединение с базой данных после выполнения тестов."""
        cls.db_conn.close()
    
    @patch('data.dictionaries.armenian_dict.TRANSLATION_DICT', {
        'привет': 'բարև',
        'мир': 'աշխարհ',
        'армянский': 'հայերեն'
    })
    def test_get_armenian_translation(self):
        """Тест получения перевода из словаря."""
        # Проверяем существующие переводы
        self.assertEqual(get_armenian_translation('привет'), 'բարև')
        self.assertEqual(get_armenian_translation('мир'), 'աշխարհ')
        
        # Проверяем регистр
        self.assertEqual(get_armenian_translation('Привет'), 'բարև')
        self.assertEqual(get_armenian_translation('МИР'), 'աշխարհ')
        
        # Проверяем отсутствующий перевод
        self.assertIsNone(get_armenian_translation('неизвестное_слово'))
    
    @patch('core.database.execute_query')
    def test_get_translation_from_db(self, mock_execute_query):
        """Тест получения перевода из базы данных."""
        mock_execute_query.return_value = [{'translation': 'բարև'}]
        
        # Тестируем функцию
        result = asyncio.run(get_translation('привет', 'test.db'))
        
        # Проверяем результат
        self.assertEqual(result, 'բարև')
        
        # Проверяем вызовы функций
        mock_execute_query.assert_called_once()


class TestTransliterationUtils(unittest.TestCase):
    """Тесты для утилит транслитерации."""
    
    @patch('features.transliteration.utils.transliterate_text')
    @patch('features.transliteration.utils.get_translation')
    @patch('features.transliteration.utils.process_unknown_word')
    def test_process_text(self, mock_process_unknown, mock_get_translation, mock_transliterate):
        """Тест обработки текста с транслитерацией и переводом."""
        # Настраиваем мок-объекты
        mock_transliterate.side_effect = lambda word: f"t_{word}"
        mock_get_translation.side_effect = lambda word, db: 'перевод' if word == 'известное' else None
        
        # Тестируем функцию
        result = asyncio.run(process_text('известное слово', 'test.db'))
        
        # Проверяем результат
        self.assertIn('t_известное (перевод)', result)
        self.assertIn('t_слово', result)
        
        # Проверяем вызовы функций
        mock_transliterate.assert_any_call('известное')
        mock_transliterate.assert_any_call('слово')
        mock_get_translation.assert_any_call('известное', 'test.db')
        mock_get_translation.assert_any_call('слово', 'test.db')
        mock_process_unknown.assert_called_once()


if __name__ == '__main__':
    unittest.main()
