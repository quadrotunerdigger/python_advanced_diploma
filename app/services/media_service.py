"""Сервис для работы с медиафайлами."""

import uuid
import aiofiles

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.media import Media
from app.utils.exceptions import InvalidFileException, MediaNotFoundException


class MediaService:
    """Сервис для работы с медиафайлами."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.settings = get_settings()

    def _validate_file(self, file: UploadFile) -> str:
        """Валидация загружаемого файла."""
        if not file.filename:
            raise InvalidFileException("Имя файла не указано")

        # Получаем расширение файла
        extension = file.filename.rsplit(".", 1)[-1].lower()

        if extension not in self.settings.allowed_extensions:
            raise InvalidFileException(
                f"Недопустимый формат файла. Разрешены: {', '.join(self.settings.allowed_extensions)}"
            )

        return extension

    def _generate_filename(self, extension: str) -> str:
        """Генерация уникального имени файла."""
        return f"{uuid.uuid4()}.{extension}"

    async def upload_file(self, file: UploadFile) -> Media:
        """Загрузить медиафайл."""
        extension = self._validate_file(file)
        filename = self._generate_filename(extension)
        file_path = self.settings.media_dir / filename

        # Создаём директорию, если не существует
        self.settings.media_dir.mkdir(parents=True, exist_ok=True)

        # Сохраняем файл
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()

            # Проверяем размер файла
            if len(content) > self.settings.max_file_size:
                raise InvalidFileException(
                    f"Размер файла превышает максимально допустимый ({self.settings.max_file_size // 1024 // 1024} MB)"
                )

            await out_file.write(content)

        # Создаём запись в БД
        media = Media(filename=filename)
        self.session.add(media)
        await self.session.flush()
        await self.session.refresh(media)

        return media

    async def get_media_by_id(self, media_id: int) -> Media:
        """Получить медиафайл по ID."""
        result = await self.session.execute(
            select(Media).where(Media.id == media_id)
        )
        media = result.scalar_one_or_none()

        if not media:
            raise MediaNotFoundException(media_id)

        return media

    async def delete_file(self, media_id: int) -> bool:
        """Удалить медиафайл."""
        media = await self.get_media_by_id(media_id)

        # Удаляем физический файл
        file_path = self.settings.media_dir / media.filename
        if file_path.exists():
            file_path.unlink()

        # Удаляем запись из БД
        await self.session.delete(media)

        return True