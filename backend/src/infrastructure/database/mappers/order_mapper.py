"""Order mapper between database model and domain entity."""
from decimal import Decimal

from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem
from src.domain.value_objects.money import Money
from src.infrastructure.database.models.order import OrderModel, OrderItemModel


class OrderItemMapper:
    """Maps between OrderItemModel and OrderItem entity."""

    @staticmethod
    def to_entity(model: OrderItemModel) -> OrderItem:
        """Convert database model to domain entity."""
        return OrderItem(
            id=model.id,
            order_id=model.order_id,
            product_id=model.product_id,
            quantity=Decimal(str(model.quantity)),
            unit_price=Money(
                amount=Decimal(str(model.unit_price_amount)),
                currency=model.unit_price_currency,
            ),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: OrderItem) -> OrderItemModel:
        """Convert domain entity to database model."""
        return OrderItemModel(
            id=entity.id,
            order_id=entity.order_id,
            product_id=entity.product_id,
            quantity=entity.quantity,
            unit_price_amount=entity.unit_price.amount,
            unit_price_currency=entity.unit_price.currency,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class OrderMapper:
    """Maps between OrderModel and Order entity."""

    @staticmethod
    def to_entity(model: OrderModel) -> Order:
        """Convert database model to domain entity."""
        items = [OrderItemMapper.to_entity(item) for item in model.items]

        return Order(
            id=model.id,
            customer_name=model.customer_name,
            customer_email=model.customer_email,
            items=items,
            status=OrderStatus(model.status),
            notes=model.notes or "",
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Order) -> OrderModel:
        """Convert domain entity to database model."""
        model = OrderModel(
            id=entity.id,
            customer_name=entity.customer_name,
            customer_email=entity.customer_email,
            status=entity.status.value,
            notes=entity.notes,
            created_by_user_id=entity.created_by_user_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

        # Add items
        model.items = [OrderItemMapper.to_model(item) for item in entity.items]

        return model
