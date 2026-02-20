"""Сервис для работы с пользователями."""

from typing import Optional

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.utils.exceptions import AlreadyExistsException, UserNotFoundException


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _verify_api_key(self, plain_key: str, stored_key: str) -> bool:
        """
        Проверить api_key (поддерживает оба формата).

        Сначала пробует bcrypt (хешированный),
        если не подходит - проверяет plain text (для фронтенда).
        """
        # Проверка 1: Bcrypt (начинается с $2b$ или $2a$)
        if stored_key.startswith("$2"):
            try:
                return bcrypt.checkpw(
                    plain_key.encode("utf-8"), stored_key.encode("utf-8")
                )
            except (ValueError, AttributeError):
                return False

        # Проверка 2: Plain text (для совместимости с фронтендом)
        return plain_key == stored_key

    async def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """
        Получить пользователя по API ключу.

        Поддерживает как хешированные (bcrypt), так и plain text ключи.
        """
        # Получаем всех пользователей
        result = await self.session.execute(
            select(User).options(
                selectinload(User.following),
                selectinload(User.followers),
            )
        )
        users = result.scalars().all()

        # Проверяем каждого пользователя
        for user in users:
            if self._verify_api_key(api_key, user.api_key):
                return user

        return None

    async def get_user_by_id(self, user_id: int) -> User:
        """Получить пользователя по ID."""
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.following),
                selectinload(User.followers),
            )
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFoundException(user_id)

        return user

    async def follow_user(self, follower: User, followed_id: int) -> bool:
        """Подписаться на пользователя."""
        if follower.id == followed_id:
            raise AlreadyExistsException("Нельзя подписаться на самого себя")

        followed = await self.get_user_by_id(followed_id)

        if followed in follower.following:
            raise AlreadyExistsException("Вы уже подписаны на этого пользователя")

        follower.following.append(followed)
        return True

    async def unfollow_user(self, follower: User, followed_id: int) -> bool:
        """Отписаться от пользователя."""
        followed = await self.get_user_by_id(followed_id)

        if followed in follower.following:
            follower.following.remove(followed)

        return True

    async def get_user_profile(self, user_id: int) -> User:
        """Получить профиль пользователя с подписками."""
        return await self.get_user_by_id(user_id)