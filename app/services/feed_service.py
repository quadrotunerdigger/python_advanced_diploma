"""Сервис для формирования ленты твитов."""

from typing import List

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tweet import Tweet, likes_table
from app.models.user import User


class FeedService:
    """Сервис для формирования ленты твитов."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_feed_for_user(self, user: User) -> List[Tweet]:
        """
        Получить ленту твитов для пользователя.

        Лента содержит твиты от пользователей, на которых подписан
        текущий пользователь, отсортированные по популярности
        (количеству лайков) в порядке убывания.

        Args:
            user: Текущий пользователь

        Returns:
            List[Tweet]: Список твитов для ленты
        """
        # Получаем ID пользователей, на которых подписан текущий пользователь
        following_ids = [u.id for u in user.following]

        if not following_ids:
            return []

        # Подзапрос для подсчёта лайков
        likes_count_subquery = (
            select(
                likes_table.c.tweet_id,
                func.count(likes_table.c.user_id).label("likes_count")
            )
            .group_by(likes_table.c.tweet_id)
            .subquery()
        )

        # Основной запрос с сортировкой по количеству лайков
        result = await self.session.execute(
            select(Tweet)
            .options(
                selectinload(Tweet.author),
                selectinload(Tweet.attachments),
                selectinload(Tweet.likes),
            )
            .outerjoin(
                likes_count_subquery,
                Tweet.id == likes_count_subquery.c.tweet_id
            )
            .where(Tweet.author_id.in_(following_ids))
            .order_by(
                desc(func.coalesce(likes_count_subquery.c.likes_count, 0)),
                desc(Tweet.created_at)
            )
        )

        return list(result.scalars().all())

    async def get_popular_tweets(self, limit: int = 50) -> List[Tweet]:
        """
        Получить популярные твиты (для главной страницы без авторизации).

        Args:
            limit: Максимальное количество твитов

        Returns:
            List[Tweet]: Список популярных твитов
        """
        likes_count_subquery = (
            select(
                likes_table.c.tweet_id,
                func.count(likes_table.c.user_id).label("likes_count")
            )
            .group_by(likes_table.c.tweet_id)
            .subquery()
        )

        result = await self.session.execute(
            select(Tweet)
            .options(
                selectinload(Tweet.author),
                selectinload(Tweet.attachments),
                selectinload(Tweet.likes),
            )
            .outerjoin(
                likes_count_subquery,
                Tweet.id == likes_count_subquery.c.tweet_id
            )
            .order_by(
                desc(func.coalesce(likes_count_subquery.c.likes_count, 0)),
                desc(Tweet.created_at)
            )
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_user_tweets(self, user_id: int) -> List[Tweet]:
        """
        Получить все твиты конкретного пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            List[Tweet]: Список твитов пользователя
        """
        result = await self.session.execute(
            select(Tweet)
            .options(
                selectinload(Tweet.author),
                selectinload(Tweet.attachments),
                selectinload(Tweet.likes),
            )
            .where(Tweet.author_id == user_id)
            .order_by(desc(Tweet.created_at))
        )

        return list(result.scalars().all())