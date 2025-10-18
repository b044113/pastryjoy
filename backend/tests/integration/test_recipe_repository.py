"""Integration tests for Recipe Repository."""
import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ingredient import Ingredient
from src.domain.entities.recipe import Recipe
from src.domain.value_objects.measurement_unit import MeasurementUnit
from src.infrastructure.database.repositories.recipe_repository import RecipeRepository
from src.infrastructure.database.repositories.ingredient_repository import IngredientRepository


@pytest.mark.asyncio
class TestRecipeRepository:
    """Test Recipe Repository integration."""

    async def create_test_ingredient(self, db_session: AsyncSession, name: str) -> Ingredient:
        """Helper to create a test ingredient."""
        repo = IngredientRepository(db_session)
        ingredient = Ingredient(name=name, unit=MeasurementUnit.KILOGRAM)
        return await repo.create(ingredient)

    async def test_create_recipe(self, db_session: AsyncSession):
        """Test creating a recipe."""
        repo = RecipeRepository(db_session)
        ingredient = await self.create_test_ingredient(db_session, "Recipe Test Flour")

        recipe = Recipe(
            name="Test Bread Recipe",
            instructions="Mix flour and water, then bake",
        )
        recipe.add_ingredient(ingredient.id, Decimal("0.5"))

        created = await repo.create(recipe)

        assert created.id is not None
        assert created.name == "Test Bread Recipe"
        assert created.instructions == "Mix flour and water, then bake"
        assert len(created.ingredients) == 1

    async def test_get_by_id(self, db_session: AsyncSession):
        """Test getting recipe by ID."""
        repo = RecipeRepository(db_session)
        ingredient = await self.create_test_ingredient(db_session, "Get By ID Flour")

        recipe = Recipe(name="Cake Recipe", instructions="Bake at 180°C")
        recipe.add_ingredient(ingredient.id, Decimal("0.3"))
        created = await repo.create(recipe)

        found = await repo.get_by_id(created.id)

        assert found is not None
        assert found.id == created.id
        assert found.name == "Cake Recipe"

    async def test_get_by_name(self, db_session: AsyncSession):
        """Test getting recipe by name."""
        repo = RecipeRepository(db_session)
        ingredient = await self.create_test_ingredient(db_session, "By Name Flour")

        recipe = Recipe(name="Unique Recipe Name", instructions="Special instructions")
        recipe.add_ingredient(ingredient.id, Decimal("0.5"))
        await repo.create(recipe)

        found = await repo.get_by_name("Unique Recipe Name")

        assert found is not None
        assert found.name == "Unique Recipe Name"

    async def test_get_all(self, db_session: AsyncSession):
        """Test getting all recipes."""
        repo = RecipeRepository(db_session)
        ingredient = await self.create_test_ingredient(db_session, "GetAll Flour")

        # Create multiple recipes
        for i in range(3):
            recipe = Recipe(name=f"Recipe {i}", instructions=f"Instructions {i}")
            recipe.add_ingredient(ingredient.id, Decimal("0.5"))
            await repo.create(recipe)

        recipes = await repo.get_all()

        assert len(recipes) >= 3

    async def test_update_recipe(self, db_session: AsyncSession):
        """Test updating a recipe."""
        repo = RecipeRepository(db_session)
        ingredient = await self.create_test_ingredient(db_session, "Update Flour")

        recipe = Recipe(name="Original Recipe", instructions="Original instructions")
        recipe.add_ingredient(ingredient.id, Decimal("0.5"))
        created = await repo.create(recipe)

        # Update name and instructions
        created.name = "Updated Recipe"
        created.instructions = "Updated instructions"
        updated = await repo.update(created)

        assert updated.name == "Updated Recipe"
        assert updated.instructions == "Updated instructions"

    async def test_delete_recipe(self, db_session: AsyncSession):
        """Test deleting a recipe."""
        repo = RecipeRepository(db_session)
        ingredient = await self.create_test_ingredient(db_session, "Delete Flour")

        recipe = Recipe(name="To Delete Recipe", instructions="Will be deleted")
        recipe.add_ingredient(ingredient.id, Decimal("0.5"))
        created = await repo.create(recipe)

        await repo.delete(created.id)

        found = await repo.get_by_id(created.id)
        assert found is None

    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        """Test getting recipe by non-existent ID."""
        from uuid import uuid4
        repo = RecipeRepository(db_session)

        found = await repo.get_by_id(uuid4())

        assert found is None

    async def test_get_by_name_not_found(self, db_session: AsyncSession):
        """Test getting recipe by non-existent name."""
        repo = RecipeRepository(db_session)

        found = await repo.get_by_name("NonExistentRecipe")

        assert found is None

    async def test_recipe_with_multiple_ingredients(self, db_session: AsyncSession):
        """Test creating recipe with multiple ingredients."""
        repo = RecipeRepository(db_session)
        flour = await self.create_test_ingredient(db_session, "Multi Flour")
        sugar = await self.create_test_ingredient(db_session, "Multi Sugar")
        salt = await self.create_test_ingredient(db_session, "Multi Salt")

        recipe = Recipe(
            name="Complex Recipe",
            instructions="Use multiple ingredients",
        )
        recipe.add_ingredient(flour.id, Decimal("0.5"))
        recipe.add_ingredient(sugar.id, Decimal("0.2"))
        recipe.add_ingredient(salt.id, Decimal("0.01"))

        created = await repo.create(recipe)

        assert len(created.ingredients) == 3

    async def test_update_recipe_ingredients(self, db_session: AsyncSession):
        """Test updating recipe ingredients."""
        repo = RecipeRepository(db_session)
        flour = await self.create_test_ingredient(db_session, "Update Ing Flour")
        sugar = await self.create_test_ingredient(db_session, "Update Ing Sugar")

        recipe = Recipe(name="Recipe to Update", instructions="Instructions")
        recipe.add_ingredient(flour.id, Decimal("0.5"))
        created = await repo.create(recipe)

        # Update ingredient quantity
        created.update_ingredient_quantity(flour.id, Decimal("0.8"))
        # Add new ingredient
        created.add_ingredient(sugar.id, Decimal("0.3"))

        updated = await repo.update(created)

        assert len(updated.ingredients) == 2
        flour_ingredient = next(ing for ing in updated.ingredients if ing.ingredient_id == flour.id)
        assert flour_ingredient.quantity == Decimal("0.8")

    async def test_remove_recipe_ingredient(self, db_session: AsyncSession):
        """Test removing ingredient from recipe."""
        repo = RecipeRepository(db_session)
        flour = await self.create_test_ingredient(db_session, "Remove Flour")
        sugar = await self.create_test_ingredient(db_session, "Remove Sugar")

        recipe = Recipe(name="Recipe with Removable Ing", instructions="Instructions")
        recipe.add_ingredient(flour.id, Decimal("0.5"))
        recipe.add_ingredient(sugar.id, Decimal("0.2"))
        created = await repo.create(recipe)

        # Remove one ingredient
        created.remove_ingredient(sugar.id)
        updated = await repo.update(created)

        assert len(updated.ingredients) == 1
        assert updated.ingredients[0].ingredient_id == flour.id
