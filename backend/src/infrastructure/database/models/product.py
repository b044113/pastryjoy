"""Product database models."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..session import Base


class ProductModel(Base):
    """Product database model."""

    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    image_url = Column(String(500), nullable=True)
    fixed_costs_amount = Column(Numeric(10, 2), nullable=False, default=0)
    fixed_costs_currency = Column(String(3), nullable=False, default="USD")
    variable_costs_percentage = Column(Numeric(5, 2), nullable=False, default=0)
    profit_margin_percentage = Column(Numeric(5, 2), nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipes = relationship("ProductRecipeModel", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItemModel", back_populates="product")

    def __repr__(self) -> str:
        """String representation."""
        return f"<ProductModel(id={self.id}, name={self.name})>"


class ProductRecipeModel(Base):
    """Product recipe association model."""

    __tablename__ = "product_recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Numeric(10, 3), nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("ProductModel", back_populates="recipes")
    recipe = relationship("RecipeModel", back_populates="product_recipes")

    def __repr__(self) -> str:
        """String representation."""
        return f"<ProductRecipeModel(product_id={self.product_id}, recipe_id={self.recipe_id}, quantity={self.quantity})>"
