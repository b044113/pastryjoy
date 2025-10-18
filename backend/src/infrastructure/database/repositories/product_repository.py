"""Product repository implementation."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.product import Product
from src.domain.repositories.product_repository import IProductRepository
from src.infrastructure.database.mappers.product_mapper import ProductMapper
from src.infrastructure.database.models.product import ProductModel


class ProductRepository(IProductRepository):
    """SQLAlchemy implementation of product repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self._session = session

    async def create(self, entity: Product) -> Product:
        """Create a new product."""
        model = ProductMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, ["recipes"])
        return ProductMapper.to_entity(model)

    async def get_by_id(self, entity_id: UUID) -> Optional[Product]:
        """Get product by ID."""
        stmt = select(ProductModel).where(ProductModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ProductMapper.to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products with pagination."""
        stmt = select(ProductModel).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [ProductMapper.to_entity(model) for model in models]

    async def get_with_recipes(self, product_id: UUID) -> Optional[Product]:
        """Get product with all recipes loaded."""
        stmt = (
            select(ProductModel)
            .where(ProductModel.id == product_id)
            .options(selectinload(ProductModel.recipes))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ProductMapper.to_entity(model) if model else None

    async def update(self, entity: Product) -> Product:
        """Update an existing product."""
        stmt = select(ProductModel).where(ProductModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one()

        # Update fields
        model.name = entity.name
        model.image_url = entity.image_url
        model.fixed_costs_amount = entity.fixed_costs.amount
        model.fixed_costs_currency = entity.fixed_costs.currency
        model.variable_costs_percentage = entity.variable_costs_percentage
        model.profit_margin_percentage = entity.profit_margin_percentage
        model.updated_at = entity.updated_at

        await self._session.flush()
        await self._session.refresh(model)
        return ProductMapper.to_entity(model)

    async def delete(self, entity_id: UUID) -> bool:
        """Delete a product by ID."""
        stmt = select(ProductModel).where(ProductModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, entity_id: UUID) -> bool:
        """Check if product exists."""
        stmt = select(ProductModel.id).where(ProductModel.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_name(self, name: str) -> Optional[Product]:
        """Get product by name."""
        stmt = select(ProductModel).where(ProductModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return ProductMapper.to_entity(model) if model else None

    async def search_by_name(
        self, name: str, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """Search products by name (partial match)."""
        stmt = (
            select(ProductModel)
            .where(ProductModel.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [ProductMapper.to_entity(model) for model in models]
