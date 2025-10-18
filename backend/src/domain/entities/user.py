"""User entity."""
from dataclasses import dataclass, field
from typing import Optional

from ..value_objects.user_role import UserRole
from .base import BaseEntity


@dataclass
class User(BaseEntity):
    """User entity."""

    email: str = ""
    username: str = ""
    hashed_password: str = ""
    role: UserRole = field(default=UserRole.USER)
    is_active: bool = True
    full_name: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate user data."""
        if not self.email:
            raise ValueError("Email is required")
        if not self.username:
            raise ValueError("Username is required")
        if "@" not in self.email:
            raise ValueError("Invalid email format")

    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN

    def can_manage_products(self) -> bool:
        """Check if user can manage products."""
        return self.role.can_manage_products

    def can_manage_recipes(self) -> bool:
        """Check if user can manage recipes."""
        return self.role.can_manage_recipes

    def can_manage_ingredients(self) -> bool:
        """Check if user can manage ingredients."""
        return self.role.can_manage_ingredients

    def can_create_orders(self) -> bool:
        """Check if user can create orders."""
        return self.role.can_create_orders
