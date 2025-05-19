"""Functions to provide random words and common expressions."""

from typing import Tuple
import random

from data.dictionaries.armenian_dict import TRANSLATION_DICT
from data.dictionaries import expressions


def get_random_word() -> Tuple[str, str]:
    """Return a random Russian word and its Armenian translation."""
    word, translation = random.choice(list(TRANSLATION_DICT.items()))
    return word, translation


def get_random_expression() -> Tuple[str, str]:
    """Return a random expression and its Armenian translation."""
    return expressions.get_random_expression()
