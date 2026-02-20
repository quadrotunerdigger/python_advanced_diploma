"""Tests for follows API."""

import pytest
from httpx import AsyncClient

from app.models.user import User


class TestFollowUser:
    """Tests for POST /api/users/{id}/follow."""

    @pytest.mark.asyncio
    async def test_follow_user_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user_2: User,
    ):
        """Test following a user."""
        response = await client.post(
            f"/api/users/{test_user_2.id}/follow",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

    @pytest.mark.asyncio
    async def test_follow_user_already_following(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user_2: User,
    ):
        """Test following a user when already following."""
        # First follow
        await client.post(
            f"/api/users/{test_user_2.id}/follow",
            headers=auth_headers,
        )

        # Second follow
        response = await client.post(
            f"/api/users/{test_user_2.id}/follow",
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["result"] is False
        assert data["detail"]["error_type"] == "AlreadyExists"

    @pytest.mark.asyncio
    async def test_follow_self(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
    ):
        """Test following yourself."""
        response = await client.post(
            f"/api/users/{test_user.id}/follow",
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["result"] is False
        assert data["detail"]["error_type"] == "AlreadyExists"

    @pytest.mark.asyncio
    async def test_follow_nonexistent_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test following non-existent user."""
        response = await client.post(
            "/api/users/99999/follow",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["result"] is False
        assert data["detail"]["error_type"] == "UserNotFound"

    @pytest.mark.asyncio
    async def test_follow_without_auth(
        self,
        client: AsyncClient,
        test_user_2: User,
    ):
        """Test following without authentication."""
        response = await client.post(
            f"/api/users/{test_user_2.id}/follow",
        )

        assert response.status_code == 422  # Missing api-key header


class TestUnfollowUser:
    """Tests for DELETE /api/users/{id}/follow."""

    @pytest.mark.asyncio
    async def test_unfollow_user_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user_2: User,
    ):
        """Test unfollowing a user."""
        # First follow
        await client.post(
            f"/api/users/{test_user_2.id}/follow",
            headers=auth_headers,
        )

        # Then unfollow
        response = await client.delete(
            f"/api/users/{test_user_2.id}/follow",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

    @pytest.mark.asyncio
    async def test_unfollow_not_following(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user_2: User,
    ):
        """Test unfollowing when not following."""
        response = await client.delete(
            f"/api/users/{test_user_2.id}/follow",
            headers=auth_headers,
        )

        # Should succeed even if not following
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True

    @pytest.mark.asyncio
    async def test_unfollow_nonexistent_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test unfollowing non-existent user."""
        response = await client.delete(
            "/api/users/99999/follow",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["result"] is False

    @pytest.mark.asyncio
    async def test_unfollow_without_auth(
        self,
        client: AsyncClient,
        test_user_2: User,
    ):
        """Test unfollowing without authentication."""
        response = await client.delete(
            f"/api/users/{test_user_2.id}/follow",
        )

        assert response.status_code == 422  # Missing api-key header


class TestFollowIntegration:
    """Integration tests for follow functionality."""

    @pytest.mark.asyncio
    async def test_follow_updates_profile(
        self,
        client: AsyncClient,
        auth_headers: dict,
        auth_headers_2: dict,
        test_user: User,
        test_user_2: User,
    ):
        """Test that following updates user profiles."""
        # User 1 follows User 2
        await client.post(
            f"/api/users/{test_user_2.id}/follow",
            headers=auth_headers,
        )

        # Check User 1's profile (should have User 2 in following)
        response = await client.get(
            "/api/users/me",
            headers=auth_headers,
        )
        data = response.json()
        following_ids = [u["id"] for u in data["user"]["following"]]
        assert test_user_2.id in following_ids

        # Check User 2's profile (should have User 1 in followers)
        response = await client.get(
            f"/api/users/{test_user_2.id}",
        )
        data = response.json()
        follower_ids = [u["id"] for u in data["user"]["followers"]]
        assert test_user.id in follower_ids