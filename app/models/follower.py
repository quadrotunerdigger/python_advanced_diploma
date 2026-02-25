"""Модель подписок (Follower).

Примечание: Таблица подписок определена в модуле user.py как
связующая таблица many-to-many (followers_table).

Данный модуль предоставляет вспомогательные функции и типы
для работы с подписками.
"""

from typing import NamedTuple

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession


class FollowerRelation(NamedTuple):
    """Представление связи подписки."""

    follower_id: int  # Кто подписался
    followed_id: int  # На кого подписались


# Таблица подписок уже определена в user.py, но для удобства
# можно импортировать её и здесь
from app.models.user import followers_table


class FollowerManager:
    """Менеджер для работы с подписками."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_following(self, follower_id: int, followed_id: int) -> bool:
        """
        Проверить, подписан ли пользователь на другого.

        Args:
            follower_id: ID подписчика
            followed_id: ID пользователя, на которого проверяем подписку

        Returns:
            bool: True если подписан, False иначе
        """
        result = await self.session.execute(
            select(followers_table).where(
                and_(
                    followers_table.c.follower_id == follower_id,
                    followers_table.c.followed_id == followed_id,
                )
            )
        )
        return result.first() is not None

    async def get_followers_count(self, user_id: int) -> int:
        """
        Получить количество подписчиков пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            int: Количество подписчиков
        """
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count()).where(
                followers_table.c.followed_id == user_id
            )
        )
        return result.scalar() or 0

    async def get_following_count(self, user_id: int) -> int:
        """
        Получить количество подписок пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            int: Количество подписок
        """
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count()).where(
                followers_table.c.follower_id == user_id
            )
        )
        return result.scalar() or 0

    async def add_follow(self, follower_id: int, followed_id: int) -> bool:
        """
        Добавить подписку.

        Args:
            follower_id: ID подписчика
            followed_id: ID пользователя для подписки

        Returns:
            bool: True если подписка добавлена
        """
        if await self.is_following(follower_id, followed_id):
            return False

        await self.session.execute(
            followers_table.insert().values(
                follower_id=follower_id,
                followed_id=followed_id,
            )
        )
        return True

    async def remove_follow(self, follower_id: int, followed_id: int) -> bool:
        """
        Удалить подписку.

        Args:
            follower_id: ID подписчика
            followed_id: ID пользователя для отписки

        Returns:
            bool: True если подписка удалена
        """
        result = await self.session.execute(
            followers_table.delete().where(
                and_(
                    followers_table.c.follower_id == follower_id,
                    followers_table.c.followed_id == followed_id,
                )
            )
        )
        return result.rowcount > 0