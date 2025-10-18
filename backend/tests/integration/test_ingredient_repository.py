"""Integration tests for Ingredient Repository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ingredient import Ingredient
from src.domain.value_objects.measurement_unit import MeasurementUnit
from src.infrastructure.database.repositories.ingredient_repository import IngredientRepository


@pytest.mark.asyncio
class TestIngredientRepository:
    """Test Ingredient Repository integration."""

    async def test_create_ingredient(self, db_session: AsyncSession):
        """Test creating an ingredient."""
        repo = IngredientRepository(db_session)

        ingredient = Ingredient(
            name="Test Flour",
            unit=MeasurementUnit.KILOGRAM,
        )

        created = await repo.create(ingredient)

        assert created.id is not None
        assert created.name == "Test Flour"
        assert created.unit == MeasurementUnit.KILOGRAM

    async def test_get_by_id(self, db_session: AsyncSession):
        """Test getting ingredient by ID."""
        repo = IngredientRepository(db_session)

        ingredient = Ingredient(name="Sugar", unit=MeasurementUnit.GRAM)
        created = await repo.create(ingredient)

        found = await repo.get_by_id(created.id)

        assert found is not None
        assert found.id == created.id
        assert found.name == "Sugar"

    async def test_get_by_name(self, db_session: AsyncSession):
        """Test getting ingredient by name."""
        repo = IngredientRepository(db_session)

        ingredient = Ingredient(name="Salt", unit=MeasurementUnit.GRAM)
        await repo.create(ingredient)

        found = await repo.get_by_name("Salt")

        assert found is not None
        assert found.name == "Salt"

    async def test_get_all(self, db_session: AsyncSession):
        """Test getting all ingredients."""
        repo = IngredientRepository(db_session)

        # Create multiple ingredients
        for i, name in enumerate(["Flour", "Sugar", "Salt"]):
            ingredient = Ingredient(name=f"{name}_{i}", unit=MeasurementUnit.KILOGRAM)
            await repo.create(ingredient)

        ingredients = await repo.get_all()

        assert len(ingredients) >= 3

    async def test_update_ingredient(self, db_session: AsyncSession):
        """Test updating an ingredient."""
        repo = IngredientRepository(db_session)

        ingredient = Ingredient(name="Old Name", unit=MeasurementUnit.KILOGRAM)
        created = await repo.create(ingredient)

        created.name = "New Name"
        updated = await repo.update(created)

        assert updated.name == "New Name"

    async def test_delete_ingredient(self, db_session: AsyncSession):
        """Test deleting an ingredient."""
        repo = IngredientRepository(db_session)

        ingredient = Ingredient(name="To Delete", unit=MeasurementUnit.KILOGRAM)
        created = await repo.create(ingredient)

        await repo.delete(created.id)

        found = await repo.get_by_id(created.id)
        assert found is None

    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        """Test getting ingredient by non-existent ID."""
        from uuid import uuid4
        repo = IngredientRepository(db_session)

        found = await repo.get_by_id(uuid4())

        assert found is None

    async def test_get_by_name_not_found(self, db_session: AsyncSession):
        """Test getting ingredient by non-existent name."""
        repo = IngredientRepository(db_session)

        found = await repo.get_by_name("NonExistentIngredient")

        assert found is None
