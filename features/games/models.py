"""
Модели игр для Armenian Learning Bot.
"""
import logging
import random
from typing import List, Dict, Tuple, Optional, Set

logger = logging.getLogger(__name__)

class HangmanGame:
    """
    Класс для игры "Виселица".
    
    Attributes:
        word: Загаданное слово.
        translation: Перевод слова.
        guessed_letters: Множество угаданных букв.
        wrong_letters: Множество неправильно угаданных букв.
        max_attempts: Максимальное количество ошибок.
        attempts_left: Оставшееся количество попыток.
    """
    
    def __init__(self, word: str, translation: str, max_attempts: int = 6):
        """
        Инициализирует новую игру "Виселица".
        
        Args:
            word: Загаданное слово на русском.
            translation: Перевод слова на армянский.
            max_attempts: Максимальное количество ошибок.
        """
        self.word = word.lower()
        self.translation = translation
        self.guessed_letters: Set[str] = set()
        self.wrong_letters: Set[str] = set()
        self.max_attempts = max_attempts
        self.attempts_left = max_attempts
    
    def guess_letter(self, letter: str) -> bool:
        """
        Проверяет букву и обновляет состояние игры.
        
        Args:
            letter: Буква для проверки (в нижнем регистре).
            
        Returns:
            True, если буква присутствует в слове, иначе False.
        """
        if not letter or len(letter) != 1:
            return False
        
        letter = letter.lower()
        
        # Если буква уже была угадана или использована, считаем неправильным ходом
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False
        
        if letter in self.word:
            self.guessed_letters.add(letter)
            return True
        else:
            self.wrong_letters.add(letter)
            self.attempts_left -= 1
            return False
    
    def get_masked_word(self) -> str:
        """
        Возвращает слово с угаданными буквами и скрытыми неугаданными.
        
        Returns:
            Строка с угаданными и скрытыми буквами.
        """
        return ''.join([letter if letter in self.guessed_letters or letter.isspace() else '_' for letter in self.word])
    
    def get_status_message(self) -> str:
        """
        Формирует сообщение о текущем состоянии игры.
        
        Returns:
            Сообщение с информацией о текущем состоянии игры.
        """
        masked_word = self.get_masked_word()
        
        message = f"🎮 <b>Игра 'Виселица'</b>\n\n"
        message += f"Слово: <b>{' '.join(masked_word)}</b>\n\n"
        
        if self.wrong_letters:
            message += f"Неправильные буквы: <b>{', '.join(sorted(self.wrong_letters))}</b>\n"
        
        message += f"Осталось попыток: <b>{self.attempts_left}</b> из <b>{self.max_attempts}</b>\n\n"
        
        # Добавляем графическое представление виселицы
        hangman_stages = [
            # 0 ошибок
            """
            --------
            |      
            |      
            |     
            |     
            |     
            ---------
            """,
            # 1 ошибка - голова
            """
            --------
            |      O
            |      
            |     
            |     
            |     
            ---------
            """,
            # 2 ошибки - голова и туловище
            """
            --------
            |      O
            |      |
            |     
            |     
            |     
            ---------
            """,
            # 3 ошибки - голова, туловище и одна рука
            """
            --------
            |      O
            |     /|
            |     
            |     
            |     
            ---------
            """,
            # 4 ошибки - голова, туловище и обе руки
            """
            --------
            |      O
            |     /|\\
            |     
            |     
            |     
            ---------
            """,
            # 5 ошибок - голова, туловище, обе руки и одна нога
            """
            --------
            |      O
            |     /|\\
            |     / 
            |     
            |     
            ---------
            """,
            # 6 ошибок - полностью нарисованная виселица
            """
            --------
            |      O
            |     /|\\
            |     / \\
            |     
            |     
            ---------
            """
        ]
        
        # Отображаем текущую стадию виселицы
        error_count = self.max_attempts - self.attempts_left
        if 0 <= error_count < len(hangman_stages):
            message += f"<pre>{hangman_stages[error_count]}</pre>\n"
        
        return message
    
    def is_game_over(self) -> bool:
        """
        Проверяет, завершена ли игра.
        
        Returns:
            True, если игра завершена (победа или поражение), иначе False.
        """
        return self.is_win() or self.attempts_left <= 0
    
    def is_win(self) -> bool:
        """
        Проверяет, выиграна ли игра.
        
        Returns:
            True, если все буквы в слове угаданы, иначе False.
        """
        for letter in self.word:
            if letter not in self.guessed_letters and letter.isalpha():
                return False
        return True
    
    def get_game_result(self) -> str:
        """
        Формирует сообщение с результатом игры.
        
        Returns:
            Сообщение с результатом игры.
        """
        if self.is_win():
            return (
                f"🎉 <b>Поздравляем! Вы победили!</b>\n\n"
                f"Загаданное слово: <b>{self.word}</b>\n"
                f"Перевод: <b>{self.translation}</b>\n\n"
                f"Вы использовали {self.max_attempts - self.attempts_left} неверных попыток."
            )
        else:
            return (
                f"😢 <b>Игра окончена!</b>\n\n"
                f"Загаданное слово: <b>{self.word}</b>\n"
                f"Перевод: <b>{self.translation}</b>\n\n"
                f"Не расстраивайтесь, попробуйте еще раз!"
            )

class WordScrambleGame:
    """
    Класс для игры "Расшифровка слов".
    
    Attributes:
        word: Исходное слово.
        translation: Перевод слова.
        scrambled_word: Перемешанное слово.
        hints_left: Количество оставшихся подсказок.
        attempts: Количество попыток.
    """
    
    def __init__(self, word: str, translation: str, max_hints: int = 2):
        """
        Инициализирует новую игру "Расшифровка слов".
        
        Args:
            word: Исходное слово.
            translation: Перевод слова.
            max_hints: Максимальное количество подсказок.
        """
        self.word = word.lower()
        self.translation = translation
        self.scrambled_word = self._scramble_word()
        self.hints_left = max_hints
        self.attempts = 0
    
    def _scramble_word(self) -> str:
        """
        Перемешивает буквы в слове.
        
        Returns:
            Перемешанное слово.
        """
        # Разбиваем слово на символы
        chars = list(self.word)
        
        # Проверяем, чтобы перемешанное слово не совпадало с исходным
        scrambled = ''.join(chars)
        while scrambled == self.word and len(chars) > 1:
            random.shuffle(chars)
            scrambled = ''.join(chars)
        
        return scrambled
    
    def check_answer(self, answer: str) -> bool:
        """
        Проверяет ответ пользователя.
        
        Args:
            answer: Ответ пользователя.
            
        Returns:
            True, если ответ правильный, иначе False.
        """
        self.attempts += 1
        return answer.lower() == self.word.lower()
    
    def get_hint(self) -> str:
        """
        Предоставляет подсказку - раскрывает часть слова.
        
        Returns:
            Подсказка или сообщение о том, что подсказок не осталось.
        """
        if self.hints_left <= 0:
            return "У вас не осталось подсказок."
        
        self.hints_left -= 1
        
        # Генерируем подсказку, раскрывая часть слова
        revealed_count = min(len(self.word) // 2, self.hints_left + 1)
        positions = random.sample(range(len(self.word)), revealed_count)
        
        hint = []
        for i, char in enumerate(self.word):
            if i in positions:
                hint.append(char)
            else:
                hint.append("_")
        
        return f"Подсказка: {''.join(hint)}"
    
    def get_status_message(self) -> str:
        """
        Формирует сообщение о текущем состоянии игры.
        
        Returns:
            Сообщение с информацией о текущем состоянии игры.
        """
        message = (
            f"🎮 <b>Игра 'Расшифровка слов'</b>\n\n"
            f"Соберите правильное слово из букв: <b>{' '.join(self.scrambled_word)}</b>\n\n"
            f"Перевод: <b>{self.translation}</b>\n\n"
            f"Количество попыток: <b>{self.attempts}</b>\n"
            f"Доступно подсказок: <b>{self.hints_left}</b>\n\n"
            f"Введите ваш ответ или нажмите кнопку 'Подсказка'."
        )
        
        return message

class WordMatchGame:
    """
    Класс для игры "Поиск соответствий".
    
    Attributes:
        word_pairs: Пары слов (русское - армянское).
        russian_words: Список русских слов.
        armenian_words: Список армянских слов.
        matched_pairs: Множество найденных пар.
        attempts: Количество попыток.
        selected_word: Текущее выбранное слово.
    """
    
    def __init__(self, word_pairs: List[Tuple[str, str]], shuffle: bool = True):
        """
        Инициализирует новую игру "Поиск соответствий".
        
        Args:
            word_pairs: Список пар слов в формате [(русское, армянское), ...].
            shuffle: Перемешивать ли слова.
        """
        self.word_pairs = word_pairs
        self.russian_words = [pair[0] for pair in word_pairs]
        self.armenian_words = [pair[1] for pair in word_pairs]
        
        if shuffle:
            random.shuffle(self.russian_words)
            random.shuffle(self.armenian_words)
        
        self.matched_pairs: Set[Tuple[str, str]] = set()
        self.attempts = 0
        self.selected_word: Optional[str] = None
        self.selected_language: Optional[str] = None
    
    def select_word(self, word: str, language: str) -> bool:
        """
        Выбирает слово для сопоставления.
        
        Args:
            word: Выбранное слово.
            language: Язык слова ('russian' или 'armenian').
            
        Returns:
            True, если слово успешно выбрано, иначе False.
        """
        # Проверяем, что слово еще не сопоставлено
        for rus, arm in self.matched_pairs:
            if (language == 'russian' and rus == word) or (language == 'armenian' and arm == word):
                return False
        
        # Если это первое выбранное слово
        if self.selected_word is None:
            self.selected_word = word
            self.selected_language = language
            return True
        
        # Если это второе выбранное слово, проверяем соответствие
        self.attempts += 1
        
        # Если выбраны слова на одном языке, сбрасываем выбор
        if self.selected_language == language:
            self.selected_word = word
            self.selected_language = language
            return True
        
        # Получаем пару для проверки
        russian_word = word if language == 'russian' else self.selected_word
        armenian_word = word if language == 'armenian' else self.selected_word
        
        # Проверяем соответствие
        for rus, arm in self.word_pairs:
            if rus == russian_word and arm == armenian_word:
                self.matched_pairs.add((rus, arm))
                self.selected_word = None
                self.selected_language = None
                return True
        
        # Если соответствие не найдено, сбрасываем выбор
        self.selected_word = None
        self.selected_language = None
        return False
    
    def check_match(self, russian_word: str, armenian_word: str) -> bool:
        """
        Проверяет соответствие между русским и армянским словами.
        
        Args:
            russian_word: Русское слово.
            armenian_word: Армянское слово.
            
        Returns:
            True, если слова образуют пару, иначе False.
        """
        for rus, arm in self.word_pairs:
            if rus == russian_word and arm == armenian_word:
                return True
        return False
    
    def is_completed(self) -> bool:
        """
        Проверяет, завершена ли игра.
        
        Returns:
            True, если все пары найдены, иначе False.
        """
        return len(self.matched_pairs) == len(self.word_pairs)
    
    def get_available_words(self, language: str) -> List[str]:
        """
        Возвращает список доступных слов на указанном языке.
        
        Args:
            language: Язык ('russian' или 'armenian').
            
        Returns:
            Список слов, которые еще не сопоставлены.
        """
        if language == 'russian':
            all_words = self.russian_words
        else:
            all_words = self.armenian_words
        
        # Исключаем сопоставленные слова
        matched_words = set()
        for rus, arm in self.matched_pairs:
            if language == 'russian':
                matched_words.add(rus)
            else:
                matched_words.add(arm)
        
        return [word for word in all_words if word not in matched_words]
    
    def get_status_message(self) -> str:
        """
        Формирует сообщение о текущем состоянии игры.
        
        Returns:
            Сообщение с информацией о текущем состоянии игры.
        """
        message = (
            f"🎮 <b>Игра 'Поиск соответствий'</b>\n\n"
            f"Найдено пар: <b>{len(self.matched_pairs)}/{len(self.word_pairs)}</b>\n"
            f"Попыток: <b>{self.attempts}</b>\n\n"
        )
        
        if self.selected_word:
            message += f"Выбрано слово: <b>{self.selected_word}</b>\n\n"
        
        message += "Выберите соответствующие пары русских и армянских слов.\n\n"
        
        # Добавляем найденные пары
        if self.matched_pairs:
            message += "<b>Найденные пары:</b>\n"
            for rus, arm in self.matched_pairs:
                message += f"• {rus} - {arm}\n"
        
        return message
    
    def get_game_result(self) -> str:
        """
        Формирует сообщение с результатом игры.
        
        Returns:
            Сообщение с результатом игры.
        """
        message = (
            f"🎉 <b>Игра завершена!</b>\n\n"
            f"Вы нашли все {len(self.word_pairs)} пар слов за {self.attempts} попыток!\n\n"
            f"<b>Правильные пары:</b>\n"
        )
        
        for rus, arm in self.word_pairs:
            message += f"• {rus} - {arm}\n"
        
        message += "\nХотите сыграть еще раз?"
        
        return message