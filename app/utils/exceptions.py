"""Кастомные исключения приложения."""

from typing import Optional

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Базовое исключение приложения."""

    def __init__(
        self,
        error_type: str,
        error_message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.error_type = error_type
        self.error_message = error_message
        super().__init__(
            status_code=status_code,
            detail={
                "result": False,
                "error_type": error_type,
                "error_message": error_message,
            },
        )


class UserNotFoundException(AppException):
    """Пользователь не найден."""

    def __init__(self, user_id: Optional[int] = None):
        message = f"Пользователь с id={user_id} не найден" if user_id else "Пользователь не найден"
        super().__init__(
            error_type="UserNotFound",
            error_message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class TweetNotFoundException(AppException):
    """Твит не найден."""

    def __init__(self, tweet_id: int):
        super().__init__(
            error_type="TweetNotFound",
            error_message=f"Твит с id={tweet_id} не найден",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class MediaNotFoundException(AppException):
    """Медиафайл не найден."""

    def __init__(self, media_id: int):
        super().__init__(
            error_type="MediaNotFound",
            error_message=f"Медиафайл с id={media_id} не найден",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class PermissionDeniedException(AppException):
    """Нет прав на выполнение операции."""

    def __init__(self, message: str = "Нет прав на выполнение операции"):
        super().__init__(
            error_type="PermissionDenied",
            error_message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class InvalidApiKeyException(AppException):
    """Неверный API ключ."""

    def __init__(self):
        super().__init__(
            error_type="InvalidApiKey",
            error_message="Неверный или отсутствующий api-key",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidFileException(AppException):
    """Недопустимый файл."""

    def __init__(self, message: str = "Недопустимый формат файла"):
        super().__init__(
            error_type="InvalidFile",
            error_message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class AlreadyExistsException(AppException):
    """Объект уже существует."""

    def __init__(self, message: str):
        super().__init__(
            error_type="AlreadyExists",
            error_message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )