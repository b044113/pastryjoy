"""Order database models."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..session import Base


class OrderModel(Base):
    """Order database model."""

    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    notes = Column(Text, nullable=True)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<OrderModel(id={self.id}, customer={self.customer_name}, status={self.status})>"


class OrderItemModel(Base):
    """Order item database model."""

    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False)
    unit_price_amount = Column(Numeric(10, 2), nullable=False)
    unit_price_currency = Column(String(3), nullable=False, default="USD")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order = relationship("OrderModel", back_populates="items")
    product = relationship("ProductModel", back_populates="order_items")

    def __repr__(self) -> str:
        """String representation."""
        return f"<OrderItemModel(id={self.id}, order_id={self.order_id}, product_id={self.product_id})>"
