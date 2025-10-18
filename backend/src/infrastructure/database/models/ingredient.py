"""Ingredient database model."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..session import Base


class IngredientModel(Base):
    """Ingredient database model."""

    __tablename__ = "ingredients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    unit = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    costs = relationship("IngredientCostModel", back_populates="ingredient", cascade="all, delete-orphan")
    recipe_ingredients = relationship("RecipeIngredientModel", back_populates="ingredient")

    def __repr__(self) -> str:
        """String representation."""
        return f"<IngredientModel(id={self.id}, name={self.name}, unit={self.unit})>"
