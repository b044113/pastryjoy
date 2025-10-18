"""Recipe ingredient entity."""
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from .base import BaseEntity


@dataclass
class RecipeIngredient(BaseEntity):
    """Recipe ingredient relationship."""

    recipe_id: UUID = UUID(int=0)
    ingredient_id: UUID = UUID(int=0)
    quantity: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        """Validate recipe ingredient data."""
        if not isinstance(self.quantity, Decimal):
            object.__setattr__(self, "quantity", Decimal(str(self.quantity)))
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
