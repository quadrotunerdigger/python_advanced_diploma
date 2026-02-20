"""Инициализация FastAPI приложения."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api import tweets, media, users, likes, follows
from app.db.database import engine
from app.models.base import Base


def create_app() -> FastAPI:
    """Фабрика приложения."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        version=settings.app_version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключение роутеров
    app.include_router(tweets.router, prefix="/api", tags=["tweets"])
    app.include_router(media.router, prefix="/api", tags=["media"])
    app.include_router(users.router, prefix="/api", tags=["users"])
    app.include_router(likes.router, prefix="/api", tags=["likes"])
    app.include_router(follows.router, prefix="/api", tags=["follows"])

    # Статические файлы для медиа
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

    @app.on_event("startup")
    async def startup():
        """Инициализация при запуске."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @app.get("/", include_in_schema=False)
    async def root():
        """Корневой endpoint."""
        return {"message": "Microblog API", "docs": "/api/docs"}

    return app


app = create_app()