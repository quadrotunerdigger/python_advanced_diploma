"""Конфигурация приложения."""

from pathlib import Path
from functools import lru_cache
from typing import Set

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # База данных
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/microblog"
    database_echo: bool = False

    # Приложение
    app_title: str = "Microblog API"
    app_description: str = "Корпоративный сервис микроблогов"
    app_version: str = "1.0.0"
    debug: bool = False

    # Загрузка файлов
    max_file_size: int = 5 * 1024 * 1024  # 5 MB
    allowed_extensions_str: str = "jpg,jpeg,png,gif,webp"

    @computed_field
    @property
    def allowed_extensions(self) -> Set[str]:
        """Множество разрешённых расширений."""
        return set(ext.strip() for ext in self.allowed_extensions_str.split(","))

    @computed_field
    @property
    def base_dir(self) -> Path:
        """Базовая директория проекта."""
        return Path(__file__).resolve().parent.parent

    @computed_field
    @property
    def static_dir(self) -> Path:
        """Директория статических файлов."""
        return self.base_dir / "static"

    @computed_field
    @property
    def media_dir(self) -> Path:
        """Директория медиафайлов."""
        return self.static_dir / "media"


@lru_cache
def get_settings() -> Settings:
    """Получить настройки приложения (кэшированные)."""
    return Settings()