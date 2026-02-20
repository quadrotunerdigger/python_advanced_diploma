"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator

import bcrypt
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app import create_app
from app.db.database import get_session
from app.models.base import Base
from app.models.media import Media
from app.models.tweet import Tweet
from app.models.user import User

# Тестовая база данных (SQLite в памяти)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create async engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for tests."""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(async_engine, async_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    app = create_app()

    # Override database session
    async def override_get_session():
        yield async_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def test_user(async_session: AsyncSession) -> User:
    """Create test user with hashed api_key."""
    # Хешируем api_key
    salt = bcrypt.gensalt()
    hashed_key = bcrypt.hashpw(b"test_api_key", salt).decode("utf-8")

    user = User(
        id=1,
        name="Test User",
        api_key=hashed_key,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_user_2(async_session: AsyncSession) -> User:
    """Create second test user with hashed api_key."""
    # Хешируем api_key
    salt = bcrypt.gensalt()
    hashed_key = bcrypt.hashpw(b"test_api_key_2", salt).decode("utf-8")

    user = User(
        id=2,
        name="Second User",
        api_key=hashed_key,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_tweet(async_session: AsyncSession, test_user: User) -> Tweet:
    """Create test tweet."""
    tweet = Tweet(
        id=1,
        content="Test tweet content",
        author_id=test_user.id,
    )
    async_session.add(tweet)
    await async_session.commit()
    await async_session.refresh(tweet)
    return tweet


@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_user: User) -> dict:
    """Return authorization headers for test user."""
    return {"api-key": "test_api_key"}


@pytest_asyncio.fixture(scope="function")
async def auth_headers_2(test_user_2: User) -> dict:
    """Return authorization headers for second test user."""
    return {"api-key": "test_api_key_2"}