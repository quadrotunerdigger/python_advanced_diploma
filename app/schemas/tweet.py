"""Pydantic схемы для твитов."""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, SuccessResponse
from app.schemas.user import UserShort


class TweetCreate(BaseModel):
    """Схема создания твита."""

    tweet_data: str = Field(..., min_length=1, max_length=1000)
    tweet_media_ids: Optional[List[int]] = None


class TweetAuthor(BaseSchema):
    """Автор твита."""

    id: int
    name: str


class TweetResponse(BaseSchema):
    """Схема твита в ответе."""

    id: int
    content: str
    attachments: List[str] = []  # Список URL изображений
    author: TweetAuthor
    likes: List[UserShort] = []

    @classmethod
    def from_tweet(cls, tweet) -> "TweetResponse":
        """Создать из модели Tweet."""
        return cls(
            id=tweet.id,
            content=tweet.content,
            attachments=[media.url for media in tweet.attachments],
            author=TweetAuthor(id=tweet.author.id, name=tweet.author.name),
            likes=[
                UserShort(id=user.id, name=user.name)
                for user in tweet.likes
            ],
        )


class TweetFeedResponse(SuccessResponse):
    """Ответ с лентой твитов."""

    tweets: List[TweetResponse]