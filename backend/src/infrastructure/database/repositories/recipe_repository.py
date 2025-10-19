"""Recipe repository implementation."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.recipe import Recipe
from src.domain.repositories.recipe_repository import IRecipeRepository
from src.infrastructure.database.mappers.recipe_mapper import RecipeMapper
from src.infrastructure.database.models.recipe import RecipeModel, RecipeIngredientModel


class RecipeRepository(IRecipeRepository):
    """SQLAlchemy implementation of recipe repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self._session = session

    async def create(self, entity: Recipe) -> Recipe:
        """Create a new recipe."""
        model = RecipeMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()

        # Reload with ingredients and their ingredient data
        stmt = (
            select(RecipeModel)
            .where(RecipeModel.id == model.id)
            .options(selectinload(RecipeModel.ingredients).selectinload(RecipeIngredientModel.ingredient))
        )
        result = await self._session.execute(stmt)
        refreshed_model = result.scalar_one()
        return RecipeMapper.to_entity(refreshed_model)

    async def get_by_id(self, entity_id: UUID) -> Optional[Recipe]:
        """Get recipe by ID."""
        stmt = (
            select(RecipeModel)
            .where(RecipeModel.id == entity_id)
            .options(selectinload(RecipeModel.ingredients).selectinload(RecipeIngredientModel.ingredient))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return RecipeMapper.to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Recipe]:
        """Get all recipes with pagination."""
        stmt = (
            select(RecipeModel)
            .options(selectinload(RecipeModel.ingredients).selectinload(RecipeIngredientModel.ingredient))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [RecipeMapper.to_entity(model) for model in models]

    async def get_with_ingredients(self, recipe_id: UUID) -> Optional[Recipe]:
        """Get recipe with all ingredients loaded."""
        stmt = (
            select(RecipeModel)
            .where(RecipeModel.id == recipe_id)
            .options(selectinload(RecipeModel.ingredients).selectinload(RecipeIngredientModel.ingredient))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return RecipeMapper.to_entity(model) if model else None

    async def update(self, entity: Recipe) -> Recipe:
        """Update an existing recipe."""
        stmt = (
            select(RecipeModel)
            .where(RecipeModel.id == entity.id)
            .options(selectinload(RecipeModel.ingredients).selectinload(RecipeIngredientModel.ingredient))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one()

        # Update fields
        model.name = entity.name
        model.instructions = entity.instructions
        model.updated_at = entity.updated_at

        await self._session.flush()

        # Reload with ingredients and their ingredient data
        stmt_refresh = (
            select(RecipeModel)
            .where(RecipeModel.id == entity.id)
            .options(selectinload(RecipeModel.ingredients).selectinload(RecipeIngredientModel.ingredient))
        )
        result_refresh = await self._session.execute(stmt_refresh)
        refreshed_model = result_refresh.scalar_one()
        return RecipeMapper.to_entity(refreshed_model)

    async def delete(self, entity_id: UUID) -> bool:
        """Delete a recipe by ID."""
        stmt = select(RecipeModel).where(RecipeModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, entity_id: UUID) -> bool:
        """Check if recipe exists."""
        stmt = select(RecipeModel.id).where(RecipeModel.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_name(self, name: str) -> Optional[Recipe]:
        """Get recipe by name."""
        stmt = (
            select(RecipeModel)
            .where(RecipeModel.name == name)
            .options(selectinload(RecipeModel.ingredients).selectinload(RecipeIngredientModel.ingredient))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return RecipeMapper.to_entity(model) if model else None

    async def search_by_name(
        self, name: str, skip: int = 0, limit: int = 100
    ) -> List[Recipe]:
        """Search recipes by name (partial match)."""
        stmt = (
            select(RecipeModel)
            .where(RecipeModel.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [RecipeMapper.to_entity(model) for model in models]
