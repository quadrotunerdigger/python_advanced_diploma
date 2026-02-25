"""Pydantic схемы для пользователей."""

from typing import List

from pydantic import Field

from app.schemas.base import BaseSchema, SuccessResponse


class UserBase(BaseSchema):
    """Базовая схема пользователя."""

    id: int
    name: str


class UserShort(BaseSchema):
    """Краткая информация о пользователе (для лайков)."""

    user_id: int = Field(alias="id")
    name: str

    @classmethod
    def from_user(cls, user) -> "UserShort":
        """Создать из модели User."""
        return cls(id=user.id, name=user.name)


class UserProfile(BaseSchema):
    """Полный профиль пользователя."""

    id: int
    name: str
    followers: List[UserBase] = []
    following: List[UserBase] = []


class UserProfileResponse(SuccessResponse):
    """Ответ с профилем пользователя."""

    user: UserProfile


class UserCreate(BaseSchema):
    """Схема для создания пользователя."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Имя пользователя",
        examples=["Юрий"],
    )
    api_key: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="API ключ пользователя",
        examples=["quadrotuner"],
    )


class UserCreateResponse(SuccessResponse):
    """Ответ при создании пользователя."""

    id: int = Field(..., description="ID созданного пользователя")
    name: str = Field(..., description="Имя пользователя")