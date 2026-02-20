"""Модель лайков (Like).

Примечание: Таблица лайков определена в модуле tweet.py как
связующая таблица many-to-many (likes_table).

Данный модуль предоставляет вспомогательные функции и типы
для работы с лайками.
"""

from typing import NamedTuple, List

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession


class LikeRelation(NamedTuple):
    """Представление связи лайка."""

    user_id: int  # Кто поставил лайк
    tweet_id: int  # Какому твиту


# Импортируем таблицу лайков из tweet.py
from app.models.tweet import likes_table


class LikeManager:
    """Менеджер для работы с лайками."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_liked(self, user_id: int, tweet_id: int) -> bool:
        """
        Проверить, лайкнул ли пользователь твит.

        Args:
            user_id: ID пользователя
            tweet_id: ID твита

        Returns:
            bool: True если лайкнул, False иначе
        """
        result = await self.session.execute(
            select(likes_table).where(
                and_(
                    likes_table.c.user_id == user_id,
                    likes_table.c.tweet_id == tweet_id,
                )
            )
        )
        return result.first() is not None

    async def get_likes_count(self, tweet_id: int) -> int:
        """
        Получить количество лайков у твита.

        Args:
            tweet_id: ID твита

        Returns:
            int: Количество лайков
        """
        result = await self.session.execute(
            select(func.count()).where(
                likes_table.c.tweet_id == tweet_id
            )
        )
        return result.scalar() or 0

    async def get_user_likes_count(self, user_id: int) -> int:
        """
        Получить количество лайков, поставленных пользователем.

        Args:
            user_id: ID пользователя

        Returns:
            int: Количество поставленных лайков
        """
        result = await self.session.execute(
            select(func.count()).where(
                likes_table.c.user_id == user_id
            )
        )
        return result.scalar() or 0

    async def add_like(self, user_id: int, tweet_id: int) -> bool:
        """
        Добавить лайк.

        Args:
            user_id: ID пользователя
            tweet_id: ID твита

        Returns:
            bool: True если лайк добавлен
        """
        if await self.is_liked(user_id, tweet_id):
            return False

        await self.session.execute(
            likes_table.insert().values(
                user_id=user_id,
                tweet_id=tweet_id,
            )
        )
        return True

    async def remove_like(self, user_id: int, tweet_id: int) -> bool:
        """
        Удалить лайк.

        Args:
            user_id: ID пользователя
            tweet_id: ID твита

        Returns:
            bool: True если лайк удалён
        """
        result = await self.session.execute(
            likes_table.delete().where(
                and_(
                    likes_table.c.user_id == user_id,
                    likes_table.c.tweet_id == tweet_id,
                )
            )
        )
        return result.rowcount > 0

    async def get_liked_tweet_ids(self, user_id: int) -> List[int]:
        """
        Получить список ID твитов, которые лайкнул пользователь.

        Args:
            user_id: ID пользователя

        Returns:
            List[int]: Список ID твитов
        """
        result = await self.session.execute(
            select(likes_table.c.tweet_id).where(
                likes_table.c.user_id == user_id
            )
        )
        return [row[0] for row in result.fetchall()]

    async def get_users_who_liked(self, tweet_id: int) -> List[int]:
        """
        Получить список ID пользователей, которые лайкнули твит.

        Args:
            tweet_id: ID твита

        Returns:
            List[int]: Список ID пользователей
        """
        result = await self.session.execute(
            select(likes_table.c.user_id).where(
                likes_table.c.tweet_id == tweet_id
            )
        )
        return [row[0] for row in result.fetchall()]