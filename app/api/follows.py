"""API endpoints для работы с подписками."""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession
from app.schemas.base import SuccessResponse, ErrorResponse
from app.services.user_service import UserService


router = APIRouter()


@router.post(
    "/users/{user_id}/follow",
    response_model=SuccessResponse,
    summary="Подписаться на пользователя",
    description="Подписаться на другого пользователя для получения его твитов в ленте.",
    responses={
        200: {"description": "Подписка успешно оформлена"},
        400: {"model": ErrorResponse, "description": "Уже подписаны или попытка подписаться на себя"},
        401: {"model": ErrorResponse, "description": "Неверный api-key"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
    },
)
async def follow_user(
    user_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> SuccessResponse:
    """Подписаться на пользователя."""
    user_service = UserService(session)

    await user_service.follow_user(current_user, user_id)

    return SuccessResponse()


@router.delete(
    "/users/{user_id}/follow",
    response_model=SuccessResponse,
    summary="Отписаться от пользователя",
    description="Отписаться от пользователя. Его твиты больше не будут появляться в ленте.",
    responses={
        200: {"description": "Подписка успешно отменена"},
        401: {"model": ErrorResponse, "description": "Неверный api-key"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
    },
)
async def unfollow_user(
    user_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> SuccessResponse:
    """Отписаться от пользователя."""
    user_service = UserService(session)

    await user_service.unfollow_user(current_user, user_id)

    return SuccessResponse()