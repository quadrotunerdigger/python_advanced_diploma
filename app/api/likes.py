"""API endpoints для работы с лайками."""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession
from app.schemas.base import SuccessResponse, ErrorResponse
from app.services.tweet_service import TweetService


router = APIRouter()


@router.post(
    "/tweets/{tweet_id}/likes",
    response_model=SuccessResponse,
    summary="Поставить лайк",
    description="Поставить отметку 'Нравится' на твит.",
    responses={
        200: {"description": "Лайк успешно добавлен"},
        401: {"model": ErrorResponse, "description": "Неверный api-key"},
        404: {"model": ErrorResponse, "description": "Твит не найден"},
    },
)
async def add_like(
    tweet_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> SuccessResponse:
    """Поставить лайк на твит."""
    tweet_service = TweetService(session)

    await tweet_service.add_like(tweet_id, current_user)

    return SuccessResponse()


@router.delete(
    "/tweets/{tweet_id}/likes",
    response_model=SuccessResponse,
    summary="Убрать лайк",
    description="Убрать отметку 'Нравится' с твита.",
    responses={
        200: {"description": "Лайк успешно удалён"},
        401: {"model": ErrorResponse, "description": "Неверный api-key"},
        404: {"model": ErrorResponse, "description": "Твит не найден"},
    },
)
async def remove_like(
    tweet_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> SuccessResponse:
    """Убрать лайк с твита."""
    tweet_service = TweetService(session)

    await tweet_service.remove_like(tweet_id, current_user)

    return SuccessResponse()