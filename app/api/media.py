"""API endpoints для работы с медиафайлами."""

from fastapi import APIRouter, UploadFile, File, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.base import MediaIdResponse, ErrorResponse
from app.services.media_service import MediaService


router = APIRouter()


@router.post(
    "/medias",
    response_model=MediaIdResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить изображение",
    description="Загрузка изображения для последующего прикрепления к твиту. "
                "Поддерживаемые форматы: jpg, jpeg, png, gif, webp.",
    responses={
        201: {"description": "Файл успешно загружен"},
        400: {"model": ErrorResponse, "description": "Недопустимый формат файла"},
        401: {"model": ErrorResponse, "description": "Неверный api-key"},
    },
)
async def upload_media(
    current_user: CurrentUser,
    session: DBSession,
    file: UploadFile = File(..., description="Изображение для загрузки"),
) -> MediaIdResponse:
    """Загрузить медиафайл."""
    media_service = MediaService(session)

    media = await media_service.upload_file(file)

    return MediaIdResponse(media_id=media.id)