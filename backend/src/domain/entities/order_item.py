"""Order item entity."""
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from ..value_objects.money import Money
from .base import BaseEntity


@dataclass
class OrderItem(BaseEntity):
    """Order item entity."""

    order_id: UUID = UUID(int=0)
    product_id: UUID = UUID(int=0)
    quantity: Decimal = Decimal("1")
    unit_price: Money = Money(Decimal("0"))

    def __post_init__(self) -> None:
        """Validate order item data."""
        if not isinstance(self.quantity, Decimal):
            object.__setattr__(self, "quantity", Decimal(str(self.quantity)))
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")

    def calculate_total(self) -> Money:
        """Calculate total cost of this order item."""
        return self.unit_price * self.quantity
