"""Pydantic схемы для медиафайлов."""

from app.schemas.base import BaseSchema, SuccessResponse


class MediaResponse(BaseSchema):
    """Схема медиафайла."""

    id: int
    filename: str
    url: str


class MediaUploadResponse(SuccessResponse):
    """Ответ при загрузке медиафайла."""

    media_id: int