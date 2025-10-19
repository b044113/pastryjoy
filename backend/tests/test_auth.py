"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.security.auth import get_password_hash
from tests.test_constants import TestCredentials


@pytest.mark.asyncio
class TestUserRegistration:
    """Test user registration endpoint."""

    async def test_register_new_user_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.TEST_EMAIL,
                "username": TestCredentials.TEST_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
                "full_name": "Test User",
            },
        )

        if response.status_code != 201:
            print(f"Error response: {response.text}")
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == TestCredentials.TEST_EMAIL
        assert data["username"] == TestCredentials.TEST_USERNAME
        assert data["full_name"] == "Test User"
        assert data["role"] == UserRole.USER.value
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_register_without_full_name(self, client: AsyncClient):
        """Test user registration without full name (optional field)."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.TEST_EMAIL_2,
                "username": TestCredentials.TEST_USERNAME_2,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == TestCredentials.TEST_EMAIL_2
        assert data["username"] == TestCredentials.TEST_USERNAME_2
        assert data["full_name"] is None

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registration with already registered email."""
        # First registration
        await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.DUPLICATE_EMAIL,
                "username": "user1",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        # Second registration with same email
        response = await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.DUPLICATE_EMAIL,
                "username": "user2",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    async def test_register_duplicate_username(self, client: AsyncClient):
        """Test registration with already taken username."""
        # First registration
        await client.post(
            "/api/auth/register",
            json={
                "email": "user1@example.com",
                "username": TestCredentials.DUPLICATE_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        # Second registration with same username
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "user2@example.com",
                "username": TestCredentials.DUPLICATE_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Username already taken"

    async def test_register_missing_required_fields(self, client: AsyncClient):
        """Test registration with missing required fields."""
        # Missing email
        response = await client.post(
            "/api/auth/register",
            json={
                "username": TestCredentials.TEST_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )
        assert response.status_code == 422  # Validation error

        # Missing username
        response = await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.TEST_EMAIL,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )
        assert response.status_code == 422

        # Missing password
        response = await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.TEST_EMAIL,
                "username": TestCredentials.TEST_USERNAME,
            },
        )
        assert response.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.INVALID_EMAIL,
                "username": TestCredentials.TEST_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        assert response.status_code == 422
        assert "email" in str(response.json()).lower()

    async def test_register_empty_password(self, client: AsyncClient):
        """Test registration with empty password."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.TEST_EMAIL,
                "username": TestCredentials.TEST_USERNAME,
                "password": "",
            },
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestUserLogin:
    """Test user login endpoint."""

    async def test_login_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful login."""
        # First, create a user
        await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.LOGIN_EMAIL,
                "username": TestCredentials.LOGIN_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        # Now login
        response = await client.post(
            "/api/auth/login",
            json={
                "username": TestCredentials.LOGIN_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] != ""
        assert "token_type" not in data or data.get("token_type") == "bearer"

    async def test_login_invalid_username(self, client: AsyncClient):
        """Test login with non-existent username."""
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    async def test_login_invalid_password(self, client: AsyncClient):
        """Test login with wrong password."""
        # First, create a user
        await client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "username": TestCredentials.TEST_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        # Try to login with wrong password
        response = await client.post(
            "/api/auth/login",
            json={
                "username": TestCredentials.TEST_USERNAME,
                "password": TestCredentials.WRONG_PASSWORD,
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    async def test_login_missing_fields(self, client: AsyncClient):
        """Test login with missing required fields."""
        # Missing username
        response = await client.post(
            "/api/auth/login",
            json={
                "password": TestCredentials.TEST_PASSWORD,
            },
        )
        assert response.status_code == 422

        # Missing password
        response = await client.post(
            "/api/auth/login",
            json={
                "username": TestCredentials.TEST_USERNAME,
            },
        )
        assert response.status_code == 422

    async def test_login_inactive_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test login with inactive user account."""
        # Create a user via registration
        await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.INACTIVE_EMAIL,
                "username": TestCredentials.INACTIVE_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        # Manually set user to inactive
        from src.infrastructure.database.models.user import UserModel
        from sqlalchemy import select

        result = await db_session.execute(
            select(UserModel).where(UserModel.username == TestCredentials.INACTIVE_USERNAME)
        )
        user_model = result.scalar_one()
        user_model.is_active = False
        await db_session.commit()

        # Try to login
        response = await client.post(
            "/api/auth/login",
            json={
                "username": TestCredentials.INACTIVE_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "User account is inactive"


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Test get current user endpoint."""

    async def test_get_current_user_with_valid_token(self, client: AsyncClient):
        """Test getting current user info with valid token."""
        # Register and login
        await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.CURRENT_EMAIL,
                "username": TestCredentials.CURRENT_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
                "full_name": "Current User",
            },
        )

        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": TestCredentials.CURRENT_USERNAME,
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
        assert data["email"] == "current@example.com"
        assert data["username"] == "currentuser"
        assert data["full_name"] == "Current User"
        assert data["role"] == UserRole.USER.value

    async def test_get_current_user_without_token(self, client: AsyncClient):
        """Test getting current user info without token."""
        response = await client.get("/api/auth/me")

        assert response.status_code == 401

    async def test_get_current_user_with_invalid_token(self, client: AsyncClient):
        """Test getting current user info with invalid token."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestAuthFlows:
    """Test complete authentication flows."""

    async def test_register_login_get_user_flow(self, client: AsyncClient):
        """Test complete flow: register -> login -> get user info."""
        # 1. Register
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": TestCredentials.FLOW_EMAIL,
                "username": TestCredentials.FLOW_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
                "full_name": "Flow User",
            },
        )
        assert register_response.status_code == 201
        user_data = register_response.json()

        # 2. Login
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": TestCredentials.FLOW_USERNAME,
                "password": TestCredentials.TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. Get user info
        me_response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        me_data = me_response.json()

        # Verify data consistency
        assert me_data["id"] == user_data["id"]
        assert me_data["email"] == user_data["email"]
        assert me_data["username"] == user_data["username"]
        assert me_data["full_name"] == user_data["full_name"]
