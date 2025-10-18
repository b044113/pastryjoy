"""Ingredient DTOs."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class IngredientCreateDTO(BaseModel):
    """Request DTO for creating an ingredient."""

    name: str = Field(min_length=1, max_length=255)
    unit: str = Field(pattern="^(kg|g|l|ml|unit|tbsp|tsp|cup)$")


class IngredientUpdateDTO(BaseModel):
    """Request DTO for updating an ingredient."""

    name: str | None = Field(None, min_length=1, max_length=255)
    unit: str | None = Field(None, pattern="^(kg|g|l|ml|unit|tbsp|tsp|cup)$")


class IngredientResponseDTO(BaseModel):
    """Response DTO for ingredient data."""

    id: UUID
    name: str
    unit: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
