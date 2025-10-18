"""Ingredient cost repository interface."""
from abc import abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ..entities.ingredient_cost import IngredientCost
from .base_repository import IBaseRepository


class IIngredientCostRepository(IBaseRepository[IngredientCost]):
    """Ingredient cost repository interface."""

    @abstractmethod
    async def get_by_ingredient_id(
        self, ingredient_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[IngredientCost]:
        """Get all costs for a specific ingredient."""
        pass

    @abstractmethod
    async def get_current_cost(self, ingredient_id: UUID) -> Optional[IngredientCost]:
        """Get the most recent (current) cost for an ingredient."""
        pass

    @abstractmethod
    async def get_cost_at_date(
        self, ingredient_id: UUID, date: datetime
    ) -> Optional[IngredientCost]:
        """Get the cost for an ingredient at a specific date."""
        pass
