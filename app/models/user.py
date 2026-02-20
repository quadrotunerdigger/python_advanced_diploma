"""Модель пользователя."""

from typing import TYPE_CHECKING, List

from sqlalchemy import String, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.tweet import Tweet


# Таблица подписок (many-to-many для фолловеров)
followers_table = Table(
    "followers",
    Base.metadata,
    Column(
        "follower_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "followed_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    api_key: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )

    # Связь с твитами
    tweets: Mapped[List["Tweet"]] = relationship(
        "Tweet",
        back_populates="author",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Подписки: на кого подписан пользователь
    following: Mapped[List["User"]] = relationship(
        "User",
        secondary=followers_table,
        primaryjoin=id == followers_table.c.follower_id,
        secondaryjoin=id == followers_table.c.followed_id,
        backref="followers",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Строковое представление объекта."""
        return f"<User(id={self.id}, name='{self.name}')>"