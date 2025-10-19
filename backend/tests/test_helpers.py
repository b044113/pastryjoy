"""Test helper functions."""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.security.auth import get_password_hash
from tests.test_constants import TestCredentials


async def create_test_user(
    session: AsyncSession,
    email: str = TestCredentials.TEST_EMAIL,
    username: str = TestCredentials.TEST_USERNAME,
    password: str = TestCredentials.TEST_PASSWORD,
    role: UserRole = UserRole.USER,
    full_name: str | None = "Test User",
) -> UserModel:
    """Create a test user directly in the database.

    Args:
        session: Database session
        email: User email
        username: Username
        password: Plain text password (will be hashed)
        role: User role
        full_name: Full name

    Returns:
        Created user model
    """
    user = UserModel(
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        role=role.value,
        full_name=full_name,
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_auth_token(
    client: AsyncClient,
    username: str = TestCredentials.TEST_USERNAME,
    password: str = TestCredentials.TEST_PASSWORD,
) -> str:
    """Get authentication token for a user.

    Args:
        client: Test client
        username: Username
        password: Password

    Returns:
        JWT access token
    """
    response = await client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    return response.json()["access_token"]


async def create_admin_and_get_token(
    client: AsyncClient,
    session: AsyncSession,
    email: str = TestCredentials.ADMIN_EMAIL,
    username: str = TestCredentials.ADMIN_USERNAME,
    password: str = TestCredentials.ADMIN_PASSWORD,
) -> str:
    """Create an admin user and get auth token.

    Args:
        client: Test client
        session: Database session
        email: Admin email
        username: Admin username
        password: Admin password

    Returns:
        JWT access token
    """
    await create_test_user(
        session=session,
        email=email,
        username=username,
        password=password,
        role=UserRole.ADMIN,
        full_name="Admin User",
    )
    return await get_auth_token(client, username, password)
