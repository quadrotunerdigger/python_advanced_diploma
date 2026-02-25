"""Зависимости для API endpoints."""

from typing import Annotated

from fastapi import Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.models.user import User
from app.services.user_service import UserService
from app.utils.exceptions import InvalidApiKeyException


async def get_current_user(
        api_key: Annotated[str, Header(alias="api-key")],
        session: AsyncSession = Depends(get_session),
) -> User:
    """
    Получить текущего пользователя по api-key из заголовка.

    Args:
        api_key: API ключ из заголовка запроса
        session: Сессия базы данных

    Returns:
        User: Текущий пользователь

    Raises:
        InvalidApiKeyException: Если пользователь не найден
    """
    user_service = UserService(session)
    user = await user_service.get_user_by_api_key(api_key)

    if not user:
        raise InvalidApiKeyException()

    return user


# Типизированная зависимость для удобства
CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_session)]