"""Tests for user settings API endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import TestCredentials


@pytest.mark.asyncio
class TestUserSettingsEndpoints:
    """Test user settings API endpoints."""

    async def test_get_settings_returns_settings_when_authenticated(
        self, client: AsyncClient
    ):
        """Test GET /api/users/me/settings returns settings for authenticated user."""
        # Register and login
        await client.post(
            "/api/auth/register",
            json={
                "email": "settings1@example.com",
                "username": "settings1",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "settings1",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        token = login_response.json()["access_token"]

        # Get settings
        response = await client.get(
            "/api/users/me/settings",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "preferred_language" in data
        assert data["preferred_language"] == "en"  # Default language

    async def test_get_settings_returns_401_without_auth(self, client: AsyncClient):
        """Test GET /api/users/me/settings returns 401 without authentication."""
        response = await client.get("/api/users/me/settings")

        assert response.status_code == 401

    async def test_patch_settings_updates_settings_successfully(
        self, client: AsyncClient
    ):
        """Test PATCH /api/users/me/settings updates settings successfully."""
        # Register and login
        await client.post(
            "/api/auth/register",
            json={
                "email": "settings2@example.com",
                "username": "settings2",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "settings2",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        token = login_response.json()["access_token"]

        # Update settings
        response = await client.patch(
            "/api/users/me/settings",
            headers={"Authorization": f"Bearer {token}"},
            json={"preferred_language": "es"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["preferred_language"] == "es"

        # Verify settings were updated by getting them again
        get_response = await client.get(
            "/api/users/me/settings",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_response.status_code == 200
        assert get_response.json()["preferred_language"] == "es"

    async def test_patch_settings_validates_language(self, client: AsyncClient):
        """Test PATCH /api/users/me/settings validates language (only en/es allowed)."""
        # Register and login
        await client.post(
            "/api/auth/register",
            json={
                "email": "settings3@example.com",
                "username": "settings3",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "settings3",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        token = login_response.json()["access_token"]

        # Try to update with invalid language
        response = await client.patch(
            "/api/users/me/settings",
            headers={"Authorization": f"Bearer {token}"},
            json={"preferred_language": "fr"},  # French not supported
        )

        # Pydantic validation returns 422
        assert response.status_code == 422
        # Check that the error is about preferred_language validation
        error_detail = str(response.json()["detail"]).lower()
        assert "preferred_language" in error_detail or "language" in error_detail

    async def test_patch_settings_returns_401_without_auth(self, client: AsyncClient):
        """Test PATCH /api/users/me/settings returns 401 without authentication."""
        response = await client.patch(
            "/api/users/me/settings",
            json={"preferred_language": "es"},
        )

        assert response.status_code == 401

    async def test_auth_me_includes_settings_in_response(self, client: AsyncClient):
        """Test /api/auth/me includes settings in response."""
        # Register and login
        await client.post(
            "/api/auth/register",
            json={
                "email": "settings4@example.com",
                "username": "settings4",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "settings4",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        token = login_response.json()["access_token"]

        # Get current user info
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "settings" in data
        assert "preferred_language" in data["settings"]
        assert data["settings"]["preferred_language"] == "en"

    async def test_settings_update_persists_across_sessions(self, client: AsyncClient):
        """Test that settings updates persist across login sessions."""
        # Register
        await client.post(
            "/api/auth/register",
            json={
                "email": "settings5@example.com",
                "username": "settings5",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        # First login
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "settings5",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )
        token1 = login_response.json()["access_token"]

        # Update settings
        await client.patch(
            "/api/users/me/settings",
            headers={"Authorization": f"Bearer {token1}"},
            json={"preferred_language": "es"},
        )

        # Second login (new token)
        login_response2 = await client.post(
            "/api/auth/login",
            json={
                "username": "settings5",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )
        token2 = login_response2.json()["access_token"]

        # Get settings with new token
        response = await client.get(
            "/api/users/me/settings",
            headers={"Authorization": f"Bearer {token2}"},
        )

        assert response.status_code == 200
        assert response.json()["preferred_language"] == "es"

    async def test_patch_settings_with_missing_field(self, client: AsyncClient):
        """Test PATCH /api/users/me/settings with missing required field."""
        # Register and login
        await client.post(
            "/api/auth/register",
            json={
                "email": "settings6@example.com",
                "username": "settings6",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "settings6",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        token = login_response.json()["access_token"]

        # Try to update with missing field
        response = await client.patch(
            "/api/users/me/settings",
            headers={"Authorization": f"Bearer {token}"},
            json={},  # No preferred_language
        )

        assert response.status_code == 422  # Validation error

    async def test_patch_settings_with_invalid_json(self, client: AsyncClient):
        """Test PATCH /api/users/me/settings with invalid JSON structure."""
        # Register and login
        await client.post(
            "/api/auth/register",
            json={
                "email": "settings7@example.com",
                "username": "settings7",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "settings7",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        token = login_response.json()["access_token"]

        # Try to update with wrong type
        response = await client.patch(
            "/api/users/me/settings",
            headers={"Authorization": f"Bearer {token}"},
            json={"preferred_language": 123},  # Should be string
        )

        assert response.status_code == 422  # Validation error
