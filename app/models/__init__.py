"""Экспорт всех моделей."""

from app.models.base import Base, TimestampMixin
from app.models.user import User, followers_table
from app.models.tweet import Tweet, likes_table
from app.models.media import Media

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Tweet",
    "Media",
    "followers_table",
    "likes_table",
]