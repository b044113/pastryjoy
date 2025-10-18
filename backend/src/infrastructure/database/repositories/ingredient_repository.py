"""Ingredient repository implementation."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ingredient import Ingredient
from src.domain.repositories.ingredient_repository import IIngredientRepository
from src.infrastructure.database.mappers.ingredient_mapper import IngredientMapper
from src.infrastructure.database.models.ingredient import IngredientModel


class IngredientRepository(IIngredientRepository):
    """SQLAlchemy implementation of ingredient repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self._session = session

    async def create(self, entity: Ingredient) -> Ingredient:
        """Create a new ingredient."""
        model = IngredientMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return IngredientMapper.to_entity(model)

    async def get_by_id(self, entity_id: UUID) -> Optional[Ingredient]:
        """Get ingredient by ID."""
        stmt = select(IngredientModel).where(IngredientModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return IngredientMapper.to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Ingredient]:
        """Get all ingredients with pagination."""
        stmt = select(IngredientModel).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [IngredientMapper.to_entity(model) for model in models]

    async def update(self, entity: Ingredient) -> Ingredient:
        """Update an existing ingredient."""
        stmt = select(IngredientModel).where(IngredientModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one()

        # Update fields
        model.name = entity.name
        model.unit = entity.unit.value
        model.updated_at = entity.updated_at

        await self._session.flush()
        await self._session.refresh(model)
        return IngredientMapper.to_entity(model)

    async def delete(self, entity_id: UUID) -> bool:
        """Delete an ingredient by ID."""
        stmt = select(IngredientModel).where(IngredientModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, entity_id: UUID) -> bool:
        """Check if ingredient exists."""
        stmt = select(IngredientModel.id).where(IngredientModel.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_name(self, name: str) -> Optional[Ingredient]:
        """Get ingredient by name."""
        stmt = select(IngredientModel).where(IngredientModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return IngredientMapper.to_entity(model) if model else None

    async def search_by_name(
        self, name: str, skip: int = 0, limit: int = 100
    ) -> List[Ingredient]:
        """Search ingredients by name (partial match)."""
        stmt = (
            select(IngredientModel)
            .where(IngredientModel.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [IngredientMapper.to_entity(model) for model in models]
