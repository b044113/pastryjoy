"""Recipe DTOs."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class RecipeIngredientDTO(BaseModel):
    """Recipe ingredient relationship."""

    ingredient_id: UUID
    quantity: Decimal = Field(gt=0)


class RecipeCreateDTO(BaseModel):
    """Request DTO for creating a recipe."""

    name: str = Field(min_length=1, max_length=255)
    instructions: str | None = None
    ingredients: list[RecipeIngredientDTO] = []


class RecipeUpdateDTO(BaseModel):
    """Request DTO for updating a recipe."""

    name: str | None = Field(None, min_length=1, max_length=255)
    instructions: str | None = None
    ingredients: list[RecipeIngredientDTO] | None = None


class RecipeIngredientResponseDTO(BaseModel):
    """Response DTO for recipe ingredient."""

    id: UUID
    ingredient_id: UUID
    ingredient_name: str | None = None
    quantity: Decimal

    class Config:
        """Pydantic config."""

        from_attributes = True


class RecipeResponseDTO(BaseModel):
    """Response DTO for recipe data."""

    id: UUID
    name: str
    instructions: str | None
    ingredients: list[RecipeIngredientResponseDTO] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class RecipeCostResponseDTO(BaseModel):
    """Response DTO for recipe with cost calculation."""

    id: UUID
    name: str
    total_cost: Decimal
    currency: str = "USD"
