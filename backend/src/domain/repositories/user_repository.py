"""User repository interface."""
from abc import abstractmethod
from typing import Optional
from uuid import UUID

from ..entities.user import User
from ..value_objects.user_settings import UserSettings
from .base_repository import IBaseRepository


class IUserRepository(IBaseRepository[User]):
    """User repository interface."""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        pass

    @abstractmethod
    async def username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        pass

    @abstractmethod
    async def update_settings(self, user_id: UUID, settings: UserSettings) -> User:
        """Update user settings.

        Args:
            user_id: User ID
            settings: New user settings

        Returns:
            Updated user entity

        Raises:
            ValueError: If user not found
        """
        pass

    @abstractmethod
    async def get_settings(self, user_id: UUID) -> UserSettings:
        """Get user settings.

        Args:
            user_id: User ID

        Returns:
            User settings

        Raises:
            ValueError: If user not found
        """
        pass
