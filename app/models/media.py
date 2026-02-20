"""Модель медиафайла."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.tweet import Tweet


class Media(Base):
    """Модель медиафайла (изображения)."""

    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    tweet_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tweets.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Связь с твитом
    tweet: Mapped[Optional["Tweet"]] = relationship(
        "Tweet",
        back_populates="attachments",
    )

    @property
    def url(self) -> str:
        """URL для доступа к файлу."""
        return f"/media/{self.filename}"

    def __repr__(self) -> str:
        """Строковое представление объекта."""
        return f"<Media(id={self.id}, filename='{self.filename}')>"