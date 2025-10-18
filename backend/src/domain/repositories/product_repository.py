"""Product repository interface."""
from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.product import Product
from .base_repository import IBaseRepository


class IProductRepository(IBaseRepository[Product]):
    """Product repository interface."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Product]:
        """Get product by name."""
        pass

    @abstractmethod
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products by name (partial match)."""
        pass

    @abstractmethod
    async def get_with_recipes(self, product_id: UUID) -> Optional[Product]:
        """Get product with all recipes loaded."""
        pass
