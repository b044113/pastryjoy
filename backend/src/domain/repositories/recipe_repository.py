"""Recipe repository interface."""
from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.recipe import Recipe
from .base_repository import IBaseRepository


class IRecipeRepository(IBaseRepository[Recipe]):
    """Recipe repository interface."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Recipe]:
        """Get recipe by name."""
        pass

    @abstractmethod
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Recipe]:
        """Search recipes by name (partial match)."""
        pass

    @abstractmethod
    async def get_with_ingredients(self, recipe_id: UUID) -> Optional[Recipe]:
        """Get recipe with all ingredients loaded."""
        pass
