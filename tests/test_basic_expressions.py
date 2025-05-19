import unittest

from data.dictionaries import EXPRESSIONS
from features.basic_expressions import get_random_word, get_random_expression
from data.dictionaries.armenian_dict import TRANSLATION_DICT


class TestBasicExpressions(unittest.TestCase):
    def test_get_random_word(self):
        word, translation = get_random_word()
        self.assertIn(word, TRANSLATION_DICT)
        self.assertEqual(translation, TRANSLATION_DICT[word])

    def test_get_random_expression(self):
        expr, translation = get_random_expression()
        self.assertIn((expr, translation), EXPRESSIONS)


if __name__ == "__main__":
    unittest.main()
