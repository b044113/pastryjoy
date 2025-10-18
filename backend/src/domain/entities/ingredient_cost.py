"""Ingredient cost entity."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from ..value_objects.money import Money
from .base import BaseEntity

if TYPE_CHECKING:
    from .ingredient import Ingredient


@dataclass
class IngredientCost(BaseEntity):
    """Ingredient cost tracking."""

    ingredient_id: UUID = UUID(int=0)
    cost_per_unit: Money = Money(Decimal("0"))
    effective_date: datetime = datetime.utcnow()

    def __post_init__(self) -> None:
        """Validate ingredient cost data."""
        if self.cost_per_unit.amount < 0:
            raise ValueError("Cost per unit cannot be negative")
