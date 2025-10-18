"""Integration tests for User Repository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.security.auth import get_password_hash


@pytest.mark.asyncio
class TestUserRepository:
    """Test User Repository integration."""

    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user."""
        repo = UserRepository(db_session)

        user = User(
            email="newuser@test.com",
            username="newuser",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            full_name="New User",
        )

        created_user = await repo.create(user)

        assert created_user.id is not None
        assert created_user.email == "newuser@test.com"
        assert created_user.username == "newuser"

    async def test_get_by_id(self, db_session: AsyncSession):
        """Test getting user by ID."""
        repo = UserRepository(db_session)

        # Create a user first
        user = User(
            email="test@test.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        created = await repo.create(user)

        # Get by ID
        found_user = await repo.get_by_id(created.id)

        assert found_user is not None
        assert found_user.id == created.id
        assert found_user.email == "test@test.com"

    async def test_get_by_email(self, db_session: AsyncSession):
        """Test getting user by email."""
        repo = UserRepository(db_session)

        user = User(
            email="email@test.com",
            username="emailuser",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        await repo.create(user)

        found_user = await repo.get_by_email("email@test.com")

        assert found_user is not None
        assert found_user.email == "email@test.com"

    async def test_get_by_username(self, db_session: AsyncSession):
        """Test getting user by username."""
        repo = UserRepository(db_session)

        user = User(
            email="username@test.com",
            username="usernametest",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        await repo.create(user)

        found_user = await repo.get_by_username("usernametest")

        assert found_user is not None
        assert found_user.username == "usernametest"

    async def test_get_all(self, db_session: AsyncSession):
        """Test getting all users."""
        repo = UserRepository(db_session)

        # Create multiple users
        for i in range(3):
            user = User(
                email=f"user{i}@test.com",
                username=f"user{i}",
                hashed_password=get_password_hash("password123"),
                role=UserRole.USER,
            )
            await repo.create(user)

        users = await repo.get_all()

        assert len(users) >= 3

    async def test_update_user(self, db_session: AsyncSession):
        """Test updating a user."""
        repo = UserRepository(db_session)

        user = User(
            email="update@test.com",
            username="updateuser",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            full_name="Original Name",
        )
        created = await repo.create(user)

        # Update full name
        created.full_name = "Updated Name"
        updated = await repo.update(created)

        assert updated.full_name == "Updated Name"

    async def test_delete_user(self, db_session: AsyncSession):
        """Test deleting a user."""
        repo = UserRepository(db_session)

        user = User(
            email="delete@test.com",
            username="deleteuser",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        created = await repo.create(user)

        # Delete
        await repo.delete(created.id)

        # Verify deleted
        found = await repo.get_by_id(created.id)
        assert found is None
