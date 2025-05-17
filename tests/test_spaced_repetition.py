"""
Тесты для модуля интервального повторения.

Проверяет работу алгоритма SuperMemo-2 и функции для работы с карточками.
"""

import unittest
import asyncio
import os
import sys
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Добавляем корневую директорию проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from features.spaced_repetition.algorithm import SM2Algorithm, update_card_after_review, add_card_to_srs, get_cards_due_review


class TestSM2Algorithm(unittest.TestCase):
    """Тесты для алгоритма SuperMemo-2."""
    
    def setUp(self):
        """Подготовка к тестам."""
        self.algorithm = SM2Algorithm()
    
    def test_update_easiness(self):
        """Тест обновления фактора легкости."""
        # Проверяем увеличение фактора легкости при хорошем ответе
        easiness = 2.5
        new_easiness = self.algorithm._update_easiness(easiness, 5)
        self.assertGreater(new_easiness, easiness)
        
        # Проверяем уменьшение фактора легкости при плохом ответе
        new_easiness = self.algorithm._update_easiness(easiness, 0)
        self.assertLess(new_easiness, easiness)
        
        # Проверяем, что фактор легкости не опускается ниже 1.3
        new_easiness = self.algorithm._update_easiness(1.3, 0)
        self.assertGreaterEqual(new_easiness, 1.3)
    
    def test_calculate_interval(self):
        """Тест расчета интервала повторения."""
        # Проверяем первое повторение (всегда 1 день)
        interval = self.algorithm._calculate_interval(2.5, 1, 1)
        self.assertEqual(interval, 1)
        
        # Проверяем второе повторение (всегда 6 дней)
        interval = self.algorithm._calculate_interval(2.5, 1, 2)
        self.assertEqual(interval, 6)
        
        # Проверяем третье повторение (интервал * фактор легкости)
        interval = self.algorithm._calculate_interval(2.5, 6, 3)
        self.assertEqual(interval, 15)  # 6 * 2.5 = 15
    
    def test_process_response(self):
        """Тест обработки ответа пользователя."""
        # Начальные параметры
        easiness = 2.5
        interval = 1
        repetitions = 0
        
        # Проверяем хороший ответ (4)
        new_easiness, new_interval, new_repetitions, next_date = self.algorithm.process_response(
            4, easiness, interval, repetitions
        )
        
        # Проверяем, что фактор легкости не уменьшился
        self.assertGreaterEqual(new_easiness, easiness)
        
        # Проверяем, что счетчик повторений увеличился
        self.assertEqual(new_repetitions, repetitions + 1)
        
        # Проверяем, что интервал установлен на 1 день (для первого повторения)
        self.assertEqual(new_interval, 1)
        
        # Проверяем, что дата следующего повторения установлена
        self.assertIsInstance(next_date, datetime)
        self.assertGreater(next_date, datetime.now())
        
        # Проверяем плохой ответ (2)
        new_easiness, new_interval, new_repetitions, next_date = self.algorithm.process_response(
            2, easiness, interval, repetitions
        )
        
        # Проверяем, что фактор легкости уменьшился
        self.assertLess(new_easiness, easiness)
        
        # Проверяем, что счетчик повторений сброшен
        self.assertEqual(new_repetitions, 0)
        
        # Проверяем, что интервал сброшен до минимального
        self.assertEqual(new_interval, self.algorithm.min_interval)
    
    def test_get_estimated_retention(self):
        """Тест оценки вероятности удержания информации в памяти."""
        # Проверяем, что сразу после повторения вероятность близка к 1
        retention = self.algorithm.get_estimated_retention(0, 2.5)
        self.assertAlmostEqual(retention, 1.0, delta=0.1)
        
        # Проверяем, что через 10 дней вероятность значительно снижается
        retention = self.algorithm.get_estimated_retention(10, 2.5)
        self.assertLess(retention, 0.5)
        
        # Проверяем, что для легких карточек вероятность выше
        retention_easy = self.algorithm.get_estimated_retention(10, 3.0)
        retention_hard = self.algorithm.get_estimated_retention(10, 1.5)
        self.assertGreater(retention_easy, retention_hard)


class TestSRSDatabaseFunctions(unittest.TestCase):
    """Тесты для функций работы с базой данных SRS."""
    
    @patch('core.database.execute_query')
    def test_update_card_after_review(self, mock_execute_query):
        """Тест обновления карточки после повторения."""
        # Настройка мок-объекта
        mock_execute_query.side_effect = [
            [{'easiness': 2.5, 'interval': 1, 'repetitions': 0}],  # Первый вызов - получение данных карточки
            None  # Второй вызов - обновление карточки
        ]
        
        # Тестируем функцию
        result = asyncio.run(update_card_after_review(1, 4, 1234, 'test.db'))
        
        # Проверяем результат
        self.assertTrue(result)
        
        # Проверяем, что execute_query вызывался дважды
        self.assertEqual(mock_execute_query.call_count, 2)
    
    @patch('core.database.execute_query')
    def test_add_card_to_srs(self, mock_execute_query):
        """Тест добавления новой карточки в SRS."""
        # Настройка мок-объекта
        mock_execute_query.side_effect = [
            [],  # Первый вызов - проверка существования карточки
            None  # Второй вызов - добавление карточки
        ]
        
        # Тестируем функцию
        result = asyncio.run(add_card_to_srs(1234, 'тест', 'փորձարկում', 'test.db'))
        
        # Проверяем результат
        self.assertTrue(result)
        
        # Проверяем, что execute_query вызывался дважды
        self.assertEqual(mock_execute_query.call_count, 2)
    
    @patch('core.database.execute_query')
    def test_get_cards_due_review(self, mock_execute_query):
        """Тест получения карточек для повторения."""
        # Настройка мок-объекта
        mock_cards = [
            {'id': 1, 'word': 'тест', 'translation': 'փորձարկում', 'easiness': 2.5, 'interval': 1, 'repetitions': 0},
            {'id': 2, 'word': 'привет', 'translation': 'բարև', 'easiness': 2.3, 'interval': 3, 'repetitions': 1}
        ]
        mock_execute_query.return_value = mock_cards
        
        # Тестируем функцию
        cards = asyncio.run(get_cards_due_review(1234, 10, 'test.db'))
        
        # Проверяем результат
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards, mock_cards)
        
        # Проверяем, что execute_query вызывался
        mock_execute_query.assert_called_once()


if __name__ == '__main__':
    unittest.main()