"""Tests for tweets API."""

import pytest
from httpx import AsyncClient

from app.models.user import User
from app.models.tweet import Tweet


class TestCreateTweet:
    """Tests for POST /api/tweets."""

    @pytest.mark.asyncio
    async def test_create_tweet_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test successful tweet creation."""
        response = await client.post(
            "/api/tweets",
            json={"tweet_data": "Hello, World!"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["result"] is True
        assert "tweet_id" in data
        assert isinstance(data["tweet_id"], int)

    @pytest.mark.asyncio
    async def test_create_tweet_with_media_ids(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test tweet creation with media IDs."""
        response = await client.post(
            "/api/tweets",
            json={
                "tweet_data": "Tweet with images",
                "tweet_media_ids": [1, 2],
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["result"] is True

    @pytest.mark.asyncio
    async def test_create_tweet_without_auth(
        self,
        client: AsyncClient,
    ):
        """Test tweet creation without authentication."""
        response = await client.post(
            "/api/tweets",
            json={"tweet_data": "Hello!"},
        )

        assert response.status_code == 422  # Missing api-key header

    @pytest.mark.asyncio
    async def test_create_tweet_invalid_api_key(
        self,
        client: AsyncClient,
    ):
        """Test tweet creation with invalid API key."""
        response = await client.post(
            "/api/tweets",
            json={"tweet_data": "Hello!"},
            headers={"api-key": "invalid_key"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["result"] is False
        assert data["detail"]["error_type"] == "InvalidApiKey"

    @pytest.mark.asyncio
    async def test_create_tweet_empty_content(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test tweet creation with empty content."""
        response = await client.post(
            "/api/tweets",
            json={"tweet_data": ""},
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error


class TestDeleteTweet:
    """Tests for DELETE /api/tweets/{id}."""

    @pytest.mark.asyncio
    async def test_delete_own_tweet(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_tweet: Tweet,
    ):
        """Test deleting own tweet."""
        response = await client.delete(
            f"/api/tweets/{test_tweet.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

    @pytest.mark.asyncio
    async def test_delete_other_user_tweet(
        self,
        client: AsyncClient,
        auth_headers_2: dict,
        test_tweet: Tweet,
    ):
        """Test deleting another user's tweet."""
        response = await client.delete(
            f"/api/tweets/{test_tweet.id}",
            headers=auth_headers_2,
        )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["result"] is False
        assert data["detail"]["error_type"] == "PermissionDenied"

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tweet(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test deleting non-existent tweet."""
        response = await client.delete(
            "/api/tweets/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["result"] is False
        assert data["detail"]["error_type"] == "TweetNotFound"


class TestGetTweetsFeed:
    """Tests for GET /api/tweets."""

    @pytest.mark.asyncio
    async def test_get_feed_empty(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test getting empty feed."""
        response = await client.get(
            "/api/tweets",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True
        assert data["tweets"] == []

    @pytest.mark.asyncio
    async def test_get_feed_without_auth(
        self,
        client: AsyncClient,
    ):
        """Test getting feed without authentication."""
        response = await client.get("/api/tweets")

        assert response.status_code == 422  # Missing api-key header