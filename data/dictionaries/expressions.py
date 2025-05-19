"""Collection of basic Armenian expressions."""

from typing import List, Tuple
import random

EXPRESSIONS: List[Tuple[str, str]] = [
    ("как дела?", "Ինչպես ես?"),
    ("доброе утро", "Բարի լույս"),
    ("спокойной ночи", "Բարի գիշեր"),
    ("большое спасибо", "Շնորհակալություն"),
    ("пожалуйста", "Խնդրում եմ"),
    ("до свидания", "Ցտեսություն"),
    ("меня зовут...", "Իմ անունը ... է"),
    ("очень приятно", "Շատ հաճելի է"),
    ("я не понимаю", "Ես չեմ հասկանում"),
    ("где находится туалет?", "Որտեղ է զուգարանը?"),
]


def get_random_expression() -> Tuple[str, str]:
    """Return a random expression and its translation."""
    return random.choice(EXPRESSIONS)
