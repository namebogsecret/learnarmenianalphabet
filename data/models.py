"""
Модуль с моделями данных для бота.

Содержит классы данных для работы с переводами, пользователями и других сущностей.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any, Union


@dataclass
class TranslationEntry:
    """Модель для записи перевода."""
    word: str
    translation: str


@dataclass
class UnknownWordEntry:
    """Модель для неизвестного слова."""
    word: str
    count: int = 1


@dataclass
class UserEntry:
    """Модель данных пользователя."""
    user_id: int
    user_name: Optional[str] = None
    times: int = 0
    created_at: datetime = None
    last_active: datetime = None
    
    def __post_init__(self):
        """Устанавливает значения по умолчанию для дат при создании."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_active is None:
            self.last_active = datetime.now()


@dataclass
class LearningPathEntry:
    """Модель для пути обучения."""
    path_id: str
    name: str
    description: str
    levels: List[Dict[str, Any]]


@dataclass
class SRSCardEntry:
    """Модель для карточки в системе интервального повторения."""
    id: Optional[int]
    user_id: int
    word: str
    translation: str
    easiness: float = 2.5
    interval: int = 1
    repetitions: int = 0
    next_review: datetime = None
    last_review: datetime = None
    
    def __post_init__(self):
        """Устанавливает значения по умолчанию для дат при создании."""
        if self.next_review is None:
            self.next_review = datetime.now()
        if self.last_review is None:
            self.last_review = datetime.now()


@dataclass
class UserProgressEntry:
    """Модель для отслеживания прогресса пользователя."""
    user_id: int
    path: str
    level: int
    completed_words: List[str]
    completed_phrases: List[str]


@dataclass
class UserSettingsEntry:
    """Модель для пользовательских настроек."""
    user_id: int
    reminder_time: str = "09:00"
    difficulty_level: str = "normal"
    daily_goal: int = 5
    notification_enabled: bool = True
    game_sounds: bool = True
    theme: str = "default"
    custom_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        """Устанавливает значения по умолчанию для пользовательских настроек."""
        if self.custom_settings is None:
            self.custom_settings = {}


@dataclass
class CommunityContentEntry:
    """Модель для контента сообщества."""
    id: str
    user_id: int
    content_type: str
    russian_text: str
    armenian_text: str
    description: Optional[str] = None
    tags: Optional[str] = None
    upvotes: int = 0
    downvotes: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        """Устанавливает значения по умолчанию для дат при создании."""
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class UserCollectionEntry:
    """Модель для коллекции пользователя."""
    user_id: int
    collection_name: str
    content_ids: List[str]
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Устанавливает значения по умолчанию для дат при создании."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class UserActivityEntry:
    """Модель для записи активности пользователя."""
    user_id: int
    activity_type: str
    timestamp: datetime = None
    details: Optional[str] = None
    
    def __post_init__(self):
        """Устанавливает значения по умолчанию для дат при создании."""
        if self.timestamp is None:
            self.timestamp = datetime.now()