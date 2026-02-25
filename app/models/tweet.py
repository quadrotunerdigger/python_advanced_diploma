"""Модель твита."""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Text, Integer, ForeignKey, Table, Column, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.media import Media


# Таблица лайков (many-to-many)
likes_table = Table(
    "likes",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tweet_id",
        Integer,
        ForeignKey("tweets.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Tweet(Base):
    """Модель твита."""

    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Связь с автором
    author: Mapped["User"] = relationship(
        "User",
        back_populates="tweets",
        lazy="selectin",
    )

    # Связь с медиафайлами
    attachments: Mapped[List["Media"]] = relationship(
        "Media",
        back_populates="tweet",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Лайки (many-to-many с пользователями)
    likes: Mapped[List["User"]] = relationship(
        "User",
        secondary=likes_table,
        lazy="selectin",
    )

    @property
    def likes_count(self) -> int:
        """Количество лайков."""
        return len(self.likes)

    def __repr__(self) -> str:
        """Строковое представление объекта."""
        return f"<Tweet(id={self.id}, author_id={self.author_id})>"