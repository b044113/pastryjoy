"""Recipe database models."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..session import Base


class RecipeModel(Base):
    """Recipe database model."""

    __tablename__ = "recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ingredients = relationship("RecipeIngredientModel", back_populates="recipe", cascade="all, delete-orphan")
    product_recipes = relationship("ProductRecipeModel", back_populates="recipe")

    def __repr__(self) -> str:
        """String representation."""
        return f"<RecipeModel(id={self.id}, name={self.name})>"


class RecipeIngredientModel(Base):
    """Recipe ingredient association model."""

    __tablename__ = "recipe_ingredients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Numeric(10, 3), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipe = relationship("RecipeModel", back_populates="ingredients")
    ingredient = relationship("IngredientModel", back_populates="recipe_ingredients")

    def __repr__(self) -> str:
        """String representation."""
        return f"<RecipeIngredientModel(recipe_id={self.recipe_id}, ingredient_id={self.ingredient_id}, quantity={self.quantity})>"
