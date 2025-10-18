"""Order DTOs."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class OrderItemDTO(BaseModel):
    """Order item."""

    product_id: UUID
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


class OrderCreateDTO(BaseModel):
    """Request DTO for creating an order."""

    customer_name: str = Field(min_length=1, max_length=255)
    customer_email: EmailStr
    notes: str = ""
    items: list[OrderItemDTO] = Field(min_items=1)


class OrderUpdateStatusDTO(BaseModel):
    """Request DTO for updating order status."""

    status: str = Field(pattern="^(pending|confirmed|in_progress|completed|cancelled)$")


class OrderItemResponseDTO(BaseModel):
    """Response DTO for order item."""

    id: UUID
    product_id: UUID
    product_name: str | None = None
    quantity: Decimal
    unit_price: Decimal
    total: Decimal

    class Config:
        """Pydantic config."""

        from_attributes = True


class OrderResponseDTO(BaseModel):
    """Response DTO for order data."""

    id: UUID
    customer_name: str
    customer_email: str
    status: str
    notes: str
    items: list[OrderItemResponseDTO] = []
    total: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
