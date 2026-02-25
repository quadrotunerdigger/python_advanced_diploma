"""Базовые Pydantic схемы."""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовая схема с общими настройками."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class SuccessResponse(BaseModel):
    """Схема успешного ответа."""

    result: bool = True


class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой."""

    result: bool = False
    error_type: str
    error_message: str


class TweetIdResponse(SuccessResponse):
    """Ответ с ID созданного твита."""

    tweet_id: int


class MediaIdResponse(SuccessResponse):
    """Ответ с ID загруженного медиафайла."""

    media_id: int