"""Ingredient cost database model."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..session import Base


class IngredientCostModel(Base):
    """Ingredient cost database model."""

    __tablename__ = "ingredient_costs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True)
    cost_amount = Column(Numeric(10, 2), nullable=False)
    cost_currency = Column(String(3), nullable=False, default="USD")
    effective_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ingredient = relationship("IngredientModel", back_populates="costs")

    def __repr__(self) -> str:
        """String representation."""
        return f"<IngredientCostModel(id={self.id}, ingredient_id={self.ingredient_id}, cost={self.cost_amount})>"
