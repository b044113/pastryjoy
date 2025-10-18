"""Order entity."""
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List
from uuid import UUID

from ..value_objects.money import Money
from .base import BaseEntity
from .order_item import OrderItem


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Order(BaseEntity):
    """Order entity."""

    customer_name: str = ""
    customer_email: str = ""
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    notes: str = ""
    created_by_user_id: UUID = UUID(int=0)

    def __post_init__(self) -> None:
        """Validate order data."""
        if not self.customer_name:
            raise ValueError("Customer name is required")
        if not self.customer_email:
            raise ValueError("Customer email is required")

    def add_item(
        self,
        product_id: UUID,
        quantity: Decimal,
        unit_price: Money
    ) -> "Order":
        """Add an item to the order."""
        order_item = OrderItem(
            order_id=self.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price
        )
        self.items.append(order_item)
        return self

    def remove_item(self, item_id: UUID) -> "Order":
        """Remove an item from the order."""
        self.items = [item for item in self.items if item.id != item_id]
        return self

    def calculate_total(self) -> Money:
        """Calculate total order cost."""
        if not self.items:
            return Money(Decimal("0"))

        total = Money(Decimal("0"))
        for item in self.items:
            total = total + item.calculate_total()

        return total

    def confirm(self) -> "Order":
        """Confirm the order."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be confirmed")
        if not self.items:
            raise ValueError("Cannot confirm order without items")
        object.__setattr__(self, "status", OrderStatus.CONFIRMED)
        return self

    def cancel(self) -> "Order":
        """Cancel the order."""
        if self.status == OrderStatus.COMPLETED:
            raise ValueError("Cannot cancel completed orders")
        if self.status == OrderStatus.CANCELLED:
            raise ValueError("Order is already cancelled")
        object.__setattr__(self, "status", OrderStatus.CANCELLED)
        return self
