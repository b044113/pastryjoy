"""Ingredient cost DTOs."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class IngredientCostCreateDTO(BaseModel):
    """Request DTO for adding ingredient cost."""

    cost_amount: Decimal = Field(gt=0)
    cost_currency: str = Field(default="USD", max_length=3)
    effective_date: datetime | None = None


class IngredientCostResponseDTO(BaseModel):
    """Response DTO for ingredient cost data."""

    id: UUID
    ingredient_id: UUID
    cost_amount: Decimal
    cost_currency: str
    effective_date: datetime
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
