"""Ingredient repository interface."""
from abc import abstractmethod
from typing import List, Optional

from ..entities.ingredient import Ingredient
from .base_repository import IBaseRepository


class IIngredientRepository(IBaseRepository[Ingredient]):
    """Ingredient repository interface."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Ingredient]:
        """Get ingredient by name."""
        pass

    @abstractmethod
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Ingredient]:
        """Search ingredients by name (partial match)."""
        pass
