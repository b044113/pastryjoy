"""Order repository implementation."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.order import Order, OrderStatus
from src.domain.repositories.order_repository import IOrderRepository
from src.infrastructure.database.mappers.order_mapper import OrderMapper
from src.infrastructure.database.models.order import OrderModel


class OrderRepository(IOrderRepository):
    """SQLAlchemy implementation of order repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self._session = session

    async def create(self, entity: Order) -> Order:
        """Create a new order."""
        model = OrderMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, ["items"])
        return OrderMapper.to_entity(model)

    async def get_by_id(self, entity_id: UUID) -> Optional[Order]:
        """Get order by ID."""
        stmt = (
            select(OrderModel)
            .where(OrderModel.id == entity_id)
            .options(selectinload(OrderModel.items))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return OrderMapper.to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders with pagination."""
        stmt = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [OrderMapper.to_entity(model) for model in models]

    async def get_with_items(self, order_id: UUID) -> Optional[Order]:
        """Get order with all items loaded."""
        stmt = (
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(selectinload(OrderModel.items))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return OrderMapper.to_entity(model) if model else None

    async def update(self, entity: Order) -> Order:
        """Update an existing order."""
        stmt = (
            select(OrderModel)
            .where(OrderModel.id == entity.id)
            .options(selectinload(OrderModel.items))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one()

        # Update fields
        model.customer_name = entity.customer_name
        model.customer_email = entity.customer_email
        model.status = entity.status.value
        model.notes = entity.notes
        model.updated_at = entity.updated_at

        await self._session.flush()
        await self._session.refresh(model, ["items"])
        return OrderMapper.to_entity(model)

    async def delete(self, entity_id: UUID) -> bool:
        """Delete an order by ID."""
        stmt = select(OrderModel).where(OrderModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, entity_id: UUID) -> bool:
        """Check if order exists."""
        stmt = select(OrderModel.id).where(OrderModel.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_customer_email(
        self, email: str, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get orders by customer email."""
        stmt = (
            select(OrderModel)
            .where(OrderModel.customer_email == email)
            .options(selectinload(OrderModel.items))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [OrderMapper.to_entity(model) for model in models]

    async def get_by_status(
        self, status: OrderStatus, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get orders by status."""
        stmt = (
            select(OrderModel)
            .where(OrderModel.status == status.value)
            .options(selectinload(OrderModel.items))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [OrderMapper.to_entity(model) for model in models]

    async def get_by_user_id(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get orders created by specific user."""
        stmt = (
            select(OrderModel)
            .where(OrderModel.created_by_user_id == user_id)
            .options(selectinload(OrderModel.items))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [OrderMapper.to_entity(model) for model in models]
