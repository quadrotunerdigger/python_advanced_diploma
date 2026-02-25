"""Tests for users API."""

import pytest
from httpx import AsyncClient

from app.models.user import User


class TestGetMyProfile:
    """Tests for GET /api/users/me."""

    @pytest.mark.asyncio
    async def test_get_my_profile_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
    ):
        """Test getting own profile."""
        response = await client.get(
            "/api/users/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True
        assert "user" in data
        assert data["user"]["id"] == test_user.id
        assert data["user"]["name"] == test_user.name
        assert "followers" in data["user"]
        assert "following" in data["user"]

    @pytest.mark.asyncio
    async def test_get_my_profile_without_auth(
        self,
        client: AsyncClient,
    ):
        """Test getting profile without authentication."""
        response = await client.get("/api/users/me")

        assert response.status_code == 422  # Missing api-key header

    @pytest.mark.asyncio
    async def test_get_my_profile_invalid_api_key(
        self,
        client: AsyncClient,
    ):
        """Test getting profile with invalid API key."""
        response = await client.get(
            "/api/users/me",
            headers={"api-key": "invalid_key"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["result"] is False


class TestGetUserProfile:
    """Tests for GET /api/users/{id}."""

    @pytest.mark.asyncio
    async def test_get_user_profile_success(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test getting user profile by ID."""
        response = await client.get(f"/api/users/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True
        assert "user" in data
        assert data["user"]["id"] == test_user.id
        assert data["user"]["name"] == test_user.name

    @pytest.mark.asyncio
    async def test_get_user_profile_not_found(
        self,
        client: AsyncClient,
    ):
        """Test getting non-existent user profile."""
        response = await client.get("/api/users/99999")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["result"] is False
        assert data["detail"]["error_type"] == "UserNotFound"

    @pytest.mark.asyncio
    async def test_get_user_profile_with_followers(
        self,
        client: AsyncClient,
        async_session,
        test_user: User,
        test_user_2: User,
    ):
        """Test getting user profile with followers."""
        # Add follower relationship
        test_user_2.following.append(test_user)
        await async_session.commit()

        response = await client.get(f"/api/users/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True
        assert len(data["user"]["followers"]) == 1
        assert data["user"]["followers"][0]["id"] == test_user_2.id