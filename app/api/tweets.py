"""API endpoints для работы с твитами."""

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.base import SuccessResponse, TweetIdResponse, ErrorResponse
from app.schemas.tweet import TweetCreate, TweetResponse, TweetFeedResponse
from app.services.tweet_service import TweetService


router = APIRouter()


@router.post(
    "/tweets",
    response_model=TweetIdResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать твит",
    description="Создание нового твита. Опционально можно прикрепить изображения.",
    responses={
        201: {"description": "Твит успешно создан"},
        401: {"model": ErrorResponse, "description": "Неверный api-key"},
    },
)
async def create_tweet(
    tweet_data: TweetCreate,
    current_user: CurrentUser,
    session: DBSession,
) -> TweetIdResponse:
    """Создать новый твит."""
    tweet_service = TweetService(session)

    tweet = await tweet_service.create_tweet(
        content=tweet_data.tweet_data,
        author_id=current_user.id,
        media_ids=tweet_data.tweet_media_ids,
    )

    return TweetIdResponse(tweet_id=tweet.id)


@router.delete(
    "/tweets/{tweet_id}",
    response_model=SuccessResponse,
    summary="Удалить твит",
    description="Удаление твита. Пользователь может удалить только свой твит.",
    responses={
        200: {"description": "Твит успешно удалён"},
        401: {"model": ErrorResponse, "description": "Неверный api-key"},
        403: {"model": ErrorResponse, "description": "Нет прав на удаление"},
        404: {"model": ErrorResponse, "description": "Твит не найден"},
    },
)
async def delete_tweet(
    tweet_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> SuccessResponse:
    """Удалить твит."""
    tweet_service = TweetService(session)

    await tweet_service.delete_tweet(tweet_id, current_user.id)

    return SuccessResponse()


@router.get(
    "/tweets",
    response_model=TweetFeedResponse,
    summary="Получить ленту твитов",
    description="Получение ленты твитов от пользователей, на которых подписан текущий пользователь. "
                "Твиты отсортированы по популярности (количеству лайков) в порядке убывания.",
    responses={
        200: {"description": "Лента твитов"},
        401: {"model": ErrorResponse, "description": "Неверный api-key"},
    },
)
async def get_tweets_feed(
    current_user: CurrentUser,
    session: DBSession,
) -> TweetFeedResponse:
    """Получить ленту твитов."""
    tweet_service = TweetService(session)

    tweets = await tweet_service.get_feed_for_user(current_user)

    return TweetFeedResponse(
        tweets=[TweetResponse.from_tweet(tweet) for tweet in tweets]
    )