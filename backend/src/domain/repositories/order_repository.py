"""Order repository interface."""
from abc import abstractmethod
from typing import List
from uuid import UUID

from ..entities.order import Order, OrderStatus
from .base_repository import IBaseRepository


class IOrderRepository(IBaseRepository[Order]):
    """Order repository interface."""

    @abstractmethod
    async def get_by_customer_email(
        self, customer_email: str, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get orders by customer email."""
        pass

    @abstractmethod
    async def get_by_status(
        self, status: OrderStatus, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get orders by status."""
        pass

    @abstractmethod
    async def get_by_user_id(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get orders created by a specific user."""
        pass

    @abstractmethod
    async def get_with_items(self, order_id: UUID) -> Order:
        """Get order with all items loaded."""
        pass
