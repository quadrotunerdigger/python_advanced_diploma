"""Tests for likes API."""

import pytest
from httpx import AsyncClient

from app.models.user import User
from app.models.tweet import Tweet


class TestAddLike:
    """Tests for POST /api/tweets/{id}/likes."""

    @pytest.mark.asyncio
    async def test_add_like_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_tweet: Tweet,
    ):
        """Test adding like to tweet."""
        response = await client.post(
            f"/api/tweets/{test_tweet.id}/likes",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

    @pytest.mark.asyncio
    async def test_add_like_twice(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_tweet: Tweet,
    ):
        """Test adding like twice (should be idempotent)."""
        # First like
        await client.post(
            f"/api/tweets/{test_tweet.id}/likes",
            headers=auth_headers,
        )

        # Second like
        response = await client.post(
            f"/api/tweets/{test_tweet.id}/likes",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

    @pytest.mark.asyncio
    async def test_add_like_nonexistent_tweet(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test adding like to non-existent tweet."""
        response = await client.post(
            "/api/tweets/99999/likes",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["result"] is False
        assert data["detail"]["error_type"] == "TweetNotFound"

    @pytest.mark.asyncio
    async def test_add_like_without_auth(
        self,
        client: AsyncClient,
        test_tweet: Tweet,
    ):
        """Test adding like without authentication."""
        response = await client.post(
            f"/api/tweets/{test_tweet.id}/likes",
        )

        assert response.status_code == 422  # Missing api-key header


class TestRemoveLike:
    """Tests for DELETE /api/tweets/{id}/likes."""

    @pytest.mark.asyncio
    async def test_remove_like_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_tweet: Tweet,
    ):
        """Test removing like from tweet."""
        # First add like
        await client.post(
            f"/api/tweets/{test_tweet.id}/likes",
            headers=auth_headers,
        )

        # Then remove it
        response = await client.delete(
            f"/api/tweets/{test_tweet.id}/likes",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

    @pytest.mark.asyncio
    async def test_remove_like_not_liked(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_tweet: Tweet,
    ):
        """Test removing like from not liked tweet."""
        response = await client.delete(
            f"/api/tweets/{test_tweet.id}/likes",
            headers=auth_headers,
        )

        # Should succeed even if not liked
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

    @pytest.mark.asyncio
    async def test_remove_like_nonexistent_tweet(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test removing like from non-existent tweet."""
        response = await client.delete(
            "/api/tweets/99999/likes",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["result"] is False

    @pytest.mark.asyncio
    async def test_remove_like_without_auth(
        self,
        client: AsyncClient,
        test_tweet: Tweet,
    ):
        """Test removing like without authentication."""
        response = await client.delete(
            f"/api/tweets/{test_tweet.id}/likes",
        )

        assert response.status_code == 422  # Missing api-key header