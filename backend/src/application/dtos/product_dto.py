"""Product DTOs."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ProductRecipeDTO(BaseModel):
    """Product recipe relationship."""

    recipe_id: UUID
    quantity: Decimal = Field(gt=0, default=Decimal("1"))


class ProductCreateDTO(BaseModel):
    """Request DTO for creating a product."""

    name: str = Field(min_length=1, max_length=255)
    image_url: str | None = Field(None, max_length=500)
    fixed_costs: Decimal = Field(ge=0, default=Decimal("0"))
    variable_costs_percentage: Decimal = Field(ge=0, le=100, default=Decimal("0"))
    profit_margin_percentage: Decimal = Field(ge=0, default=Decimal("0"))
    recipes: list[ProductRecipeDTO] = []


class ProductUpdateDTO(BaseModel):
    """Request DTO for updating a product."""

    name: str | None = Field(None, min_length=1, max_length=255)
    image_url: str | None = Field(None, max_length=500)
    fixed_costs: Decimal | None = Field(None, ge=0)
    variable_costs_percentage: Decimal | None = Field(None, ge=0, le=100)
    profit_margin_percentage: Decimal | None = Field(None, ge=0)
    recipes: list[ProductRecipeDTO] | None = None


class ProductRecipeResponseDTO(BaseModel):
    """Response DTO for product recipe."""

    recipe_id: UUID
    recipe_name: str | None = None
    quantity: Decimal

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProductResponseDTO(BaseModel):
    """Response DTO for product data."""

    id: UUID
    name: str
    image_url: str | None
    fixed_costs: Decimal
    variable_costs_percentage: Decimal
    profit_margin_percentage: Decimal
    recipes: list[ProductRecipeResponseDTO] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProductCostResponseDTO(BaseModel):
    """Response DTO for product with cost calculation."""

    id: UUID
    name: str
    recipe_costs: Decimal
    fixed_costs: Decimal
    variable_costs: Decimal
    profit_margin: Decimal
    total_cost: Decimal
    currency: str = "USD"
