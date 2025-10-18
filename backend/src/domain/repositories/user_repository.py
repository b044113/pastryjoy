"""User repository interface."""
from abc import abstractmethod
from typing import Optional

from ..entities.user import User
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
