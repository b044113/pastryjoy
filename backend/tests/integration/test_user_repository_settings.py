"""Integration tests for User Repository settings methods."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole
from src.domain.value_objects.user_settings import UserSettings
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.security.auth import get_password_hash


@pytest.mark.asyncio
class TestUserRepositorySettings:
    """Test User Repository settings integration."""

    async def test_update_settings_successfully_updates_language(
        self, db_session: AsyncSession
    ):
        """Test updating user settings successfully updates language."""
        repo = UserRepository(db_session)

        # Create a user
        user = User(
            email="settings@test.com",
            username="settingsuser",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        created_user = await repo.create(user)

        # Update settings
        new_settings = UserSettings(preferred_language="es")
        updated_user = await repo.update_settings(created_user.id, new_settings)

        assert updated_user.settings.preferred_language == "es"
        assert updated_user.id == created_user.id

    async def test_update_settings_with_nonexistent_user_raises_error(
        self, db_session: AsyncSession
    ):
        """Test updating settings for non-existent user raises ValueError."""
        repo = UserRepository(db_session)

        # Try to update settings for non-existent user
        new_settings = UserSettings(preferred_language="es")
        with pytest.raises(ValueError, match="User with id 99999 not found"):
            await repo.update_settings(99999, new_settings)

    async def test_get_settings_returns_correct_settings(self, db_session: AsyncSession):
        """Test getting user settings returns correct settings."""
        repo = UserRepository(db_session)

        # Create a user with specific settings
        user = User(
            email="getsettings@test.com",
            username="getsettingsuser",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            settings=UserSettings(preferred_language="es"),
        )
        created_user = await repo.create(user)

        # Get settings
        settings = await repo.get_settings(created_user.id)

        assert settings.preferred_language == "es"

    async def test_get_settings_with_nonexistent_user_raises_error(
        self, db_session: AsyncSession
    ):
        """Test getting settings for non-existent user raises ValueError."""
        repo = UserRepository(db_session)

        # Try to get settings for non-existent user
        with pytest.raises(ValueError, match="User with id 99999 not found"):
            await repo.get_settings(99999)

    async def test_settings_persist_after_update(self, db_session: AsyncSession):
        """Test that settings persist correctly after update."""
        repo = UserRepository(db_session)

        # Create a user
        user = User(
            email="persist@test.com",
            username="persistuser",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        created_user = await repo.create(user)

        # Update settings to Spanish
        new_settings = UserSettings(preferred_language="es")
        await repo.update_settings(created_user.id, new_settings)

        # Get user again to verify persistence
        found_user = await repo.get_by_id(created_user.id)
        assert found_user is not None
        assert found_user.settings.preferred_language == "es"

        # Update settings to English
        english_settings = UserSettings(preferred_language="en")
        await repo.update_settings(created_user.id, english_settings)

        # Get user again to verify second update
        found_user_2 = await repo.get_by_id(created_user.id)
        assert found_user_2 is not None
        assert found_user_2.settings.preferred_language == "en"

    async def test_multiple_users_have_independent_settings(
        self, db_session: AsyncSession
    ):
        """Test that multiple users can have independent settings."""
        repo = UserRepository(db_session)

        # Create first user with English settings
        user1 = User(
            email="user1@test.com",
            username="user1settings",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            settings=UserSettings(preferred_language="en"),
        )
        created_user1 = await repo.create(user1)

        # Create second user with Spanish settings
        user2 = User(
            email="user2@test.com",
            username="user2settings",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            settings=UserSettings(preferred_language="es"),
        )
        created_user2 = await repo.create(user2)

        # Verify both users have correct settings
        settings1 = await repo.get_settings(created_user1.id)
        settings2 = await repo.get_settings(created_user2.id)

        assert settings1.preferred_language == "en"
        assert settings2.preferred_language == "es"

    async def test_default_settings_on_user_creation(self, db_session: AsyncSession):
        """Test that users get default settings on creation."""
        repo = UserRepository(db_session)

        # Create a user without specifying settings
        user = User(
            email="default@test.com",
            username="defaultuser",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        created_user = await repo.create(user)

        # Get settings
        settings = await repo.get_settings(created_user.id)

        # Should have default language (English)
        assert settings.preferred_language == "en"
