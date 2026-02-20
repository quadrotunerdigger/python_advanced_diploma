"""Сервис для работы с твитами."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tweet import Tweet
from app.models.media import Media
from app.models.user import User
from app.utils.exceptions import TweetNotFoundException, PermissionDeniedException


class TweetService:
    """Сервис для работы с твитами."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_tweet(
            self,
            content: str,
            author_id: int,
            media_ids: Optional[List[int]] = None,
    ) -> Tweet:
        """Создать новый твит."""
        tweet = Tweet(content=content, author_id=author_id)
        self.session.add(tweet)
        await self.session.flush()

        # Привязываем медиафайлы к твиту
        if media_ids:
            result = await self.session.execute(
                select(Media).where(Media.id.in_(media_ids))
            )
            media_files = result.scalars().all()
            for media in media_files:
                media.tweet_id = tweet.id

        await self.session.flush()
        await self.session.refresh(tweet)
        return tweet

    async def get_tweet_by_id(self, tweet_id: int) -> Tweet:
        """Получить твит по ID."""
        result = await self.session.execute(
            select(Tweet)
            .options(
                selectinload(Tweet.author),
                selectinload(Tweet.attachments),
                selectinload(Tweet.likes),
            )
            .where(Tweet.id == tweet_id)
        )
        tweet = result.scalar_one_or_none()
        if not tweet:
            raise TweetNotFoundException(tweet_id)
        return tweet

    async def delete_tweet(self, tweet_id: int, user_id: int) -> bool:
        """Удалить твит (только автор может удалить)."""
        tweet = await self.get_tweet_by_id(tweet_id)

        if tweet.author_id != user_id:
            raise PermissionDeniedException("Вы можете удалять только свои твиты")

        await self.session.delete(tweet)
        return True

    async def get_feed_for_user(self, user: User) -> List[Tweet]:
        """
        Получить ленту твитов для пользователя.

        Лента содержит твиты от пользователей, на которых подписан текущий пользователь,
        отсортированные по популярности (количеству лайков).
        """
        # Получаем ID пользователей, на которых подписан текущий пользователь
        following_ids = [u.id for u in user.following]

        if not following_ids:
            return []

        # Получаем твиты с подгрузкой связей
        result = await self.session.execute(
            select(Tweet)
            .options(
                selectinload(Tweet.author),
                selectinload(Tweet.attachments),
                selectinload(Tweet.likes),
            )
            .where(Tweet.author_id.in_(following_ids))
        )
        tweets = result.scalars().all()

        # Сортируем по количеству лайков (по убыванию)
        sorted_tweets = sorted(tweets, key=lambda t: len(t.likes), reverse=True)

        return sorted_tweets

    async def add_like(self, tweet_id: int, user: User) -> bool:
        """Добавить лайк к твиту."""
        tweet = await self.get_tweet_by_id(tweet_id)

        if user not in tweet.likes:
            tweet.likes.append(user)

        return True

    async def remove_like(self, tweet_id: int, user: User) -> bool:
        """Убрать лайк с твита."""
        tweet = await self.get_tweet_by_id(tweet_id)

        if user in tweet.likes:
            tweet.likes.remove(user)

        return True