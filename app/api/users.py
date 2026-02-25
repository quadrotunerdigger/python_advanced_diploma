"""API endpoints для работы с пользователями."""

import bcrypt
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.models.user import User
from app.schemas.base import ErrorResponse
from app.schemas.user import (
    UserProfile,
    UserProfileResponse,
    UserBase,
    UserCreate,
    UserCreateResponse,
)
from app.services.user_service import UserService


router = APIRouter()


@router.post(
    "/users",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового пользователя",
    description="Регистрация нового пользователя с уникальным именем и api-key.",
    responses={
        201: {"description": "Пользователь успешно создан"},
        400: {
            "model": ErrorResponse,
            "description": "Пользователь с таким именем уже существует",
        },
    },
)
async def create_user(
    user_data: UserCreate,
    session: DBSession,
) -> UserCreateResponse:
    """Создать нового пользователя."""
    # Проверка уникальности имени
    stmt = select(User).where(User.name == user_data.name)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "error_type": "UserExists",
                "error_message": "User with this name already exists",
            },
        )

    # Хешируем api_key с помощью bcrypt
    salt = bcrypt.gensalt()
    hashed_key = bcrypt.hashpw(user_data.api_key.encode('utf-8'), salt).decode('utf-8')

    # Создание пользователя с хешированным api_key
    new_user = User(
        name=user_data.name,
        api_key=hashed_key,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return UserCreateResponse(
        id=new_user.id,
        name=new_user.name,
    )


@router.get(
    "/users/me",
    response_model=UserProfileResponse,
    summary="Получить свой профиль",
    description="Получение информации о текущем пользователе, включая списки подписчиков и подписок.",
    responses={
        200: {"description": "Профиль пользователя"},
        401: {"model": ErrorResponse, "description": "Неверный api-key"},
    },
)
async def get_my_profile(
    current_user: CurrentUser,
) -> UserProfileResponse:
    """Получить профиль текущего пользователя."""
    return UserProfileResponse(
        user=UserProfile(
            id=current_user.id,
            name=current_user.name,
            followers=[
                UserBase(id=u.id, name=u.name)
                for u in current_user.followers
            ],
            following=[
                UserBase(id=u.id, name=u.name)
                for u in current_user.following
            ],
        )
    )


@router.get(
    "/users/{user_id}",
    response_model=UserProfileResponse,
    summary="Получить профиль пользователя",
    description="Получение информации о пользователе по его ID.",
    responses={
        200: {"description": "Профиль пользователя"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
    },
)
async def get_user_profile(
    user_id: int,
    session: DBSession,
) -> UserProfileResponse:
    """Получить профиль пользователя по ID."""
    user_service = UserService(session)

    user = await user_service.get_user_profile(user_id)

    return UserProfileResponse(
        user=UserProfile(
            id=user.id,
            name=user.name,
            followers=[
                UserBase(id=u.id, name=u.name)
                for u in user.followers
            ],
            following=[
                UserBase(id=u.id, name=u.name)
                for u in user.following
            ],
        )
    )