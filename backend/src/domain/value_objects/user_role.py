"""User role value object."""
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""

    ADMIN = "admin"
    USER = "user"

    def __str__(self) -> str:
        """Return string representation."""
        return self.value

    @property
    def can_manage_products(self) -> bool:
        """Check if role can manage products."""
        return self == UserRole.ADMIN

    @property
    def can_manage_recipes(self) -> bool:
        """Check if role can manage recipes."""
        return self == UserRole.ADMIN

    @property
    def can_manage_ingredients(self) -> bool:
        """Check if role can manage ingredients."""
        return self == UserRole.ADMIN

    @property
    def can_create_orders(self) -> bool:
        """Check if role can create orders."""
        return True  # Both admin and user can create orders

    @property
    def can_manage_users(self) -> bool:
        """Check if role can manage users."""
        return self == UserRole.ADMIN
