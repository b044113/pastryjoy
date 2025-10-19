"""Integration tests for Product Repository."""
import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ingredient import Ingredient
from src.domain.entities.product import Product
from src.domain.entities.recipe import Recipe
from src.domain.value_objects.measurement_unit import MeasurementUnit
from src.domain.value_objects.money import Money
from src.infrastructure.database.repositories.product_repository import ProductRepository
from src.infrastructure.database.repositories.recipe_repository import RecipeRepository
from src.infrastructure.database.repositories.ingredient_repository import IngredientRepository


@pytest.mark.asyncio
class TestProductRepository:
    """Test Product Repository integration."""

    async def create_test_recipe(self, db_session: AsyncSession) -> Recipe:
        """Helper to create a test recipe."""
        # Create ingredient
        ing_repo = IngredientRepository(db_session)
        ingredient = Ingredient(name="Product Test Flour", unit=MeasurementUnit.KILOGRAM)
        created_ing = await ing_repo.create(ingredient)

        # Create recipe
        recipe_repo = RecipeRepository(db_session)
        recipe = Recipe(name="Product Test Recipe", instructions="Mix ingredients")
        recipe.add_ingredient(created_ing.id, Decimal("0.5"))
        return await recipe_repo.create(recipe)

    async def test_create_product(self, db_session: AsyncSession):
        """Test creating a product."""
        repo = ProductRepository(db_session)
        recipe = await self.create_test_recipe(db_session)

        product = Product(
            name="Test Bread",
            fixed_costs=Money(Decimal("5.00"), "USD"),
            variable_costs_percentage=Decimal("0.10"),
            profit_margin_percentage=Decimal("0.20"),
        )
        product.add_recipe(recipe.id, Decimal("1.0"))

        created = await repo.create(product)

        assert created.id is not None
        assert created.name == "Test Bread"
        assert created.fixed_costs.amount == Decimal("5.00")
        assert len(created.recipes) == 1

    async def test_get_by_id(self, db_session: AsyncSession):
        """Test getting product by ID."""
        repo = ProductRepository(db_session)
        recipe = await self.create_test_recipe(db_session)

        product = Product(
            name="Test Cake",
            fixed_costs=Money(Decimal("10.00"), "USD"),
        )
        product.add_recipe(recipe.id, Decimal("1.0"))
        created = await repo.create(product)

        found = await repo.get_by_id(created.id)

        assert found is not None
        assert found.id == created.id
        assert found.name == "Test Cake"

    async def test_get_by_name(self, db_session: AsyncSession):
        """Test getting product by name."""
        repo = ProductRepository(db_session)
        recipe = await self.create_test_recipe(db_session)

        product = Product(
            name="Unique Product Name",
            fixed_costs=Money(Decimal("15.00"), "USD"),
        )
        product.add_recipe(recipe.id, Decimal("1.0"))
        await repo.create(product)

        found = await repo.get_by_name("Unique Product Name")

        assert found is not None
        assert found.name == "Unique Product Name"

    async def test_get_all(self, db_session: AsyncSession):
        """Test getting all products."""
        repo = ProductRepository(db_session)
        recipe = await self.create_test_recipe(db_session)

        # Create multiple products
        for i in range(3):
            product = Product(
                name=f"Product {i}",
                fixed_costs=Money(Decimal("5.00"), "USD"),
            )
            product.add_recipe(recipe.id, Decimal("1.0"))
            await repo.create(product)

        products = await repo.get_all()

        assert len(products) >= 3

    async def test_update_product(self, db_session: AsyncSession):
        """Test updating a product."""
        repo = ProductRepository(db_session)
        recipe = await self.create_test_recipe(db_session)

        product = Product(
            name="Old Product Name",
            fixed_costs=Money(Decimal("5.00"), "USD"),
        )
        product.add_recipe(recipe.id, Decimal("1.0"))
        created = await repo.create(product)

        # Update name and cost
        created.name = "New Product Name"
        created.fixed_costs = Money(Decimal("8.00"), "USD")
        updated = await repo.update(created)

        assert updated.name == "New Product Name"
        assert updated.fixed_costs.amount == Decimal("8.00")

    async def test_delete_product(self, db_session: AsyncSession):
        """Test deleting a product."""
        repo = ProductRepository(db_session)
        recipe = await self.create_test_recipe(db_session)

        product = Product(
            name="To Delete Product",
            fixed_costs=Money(Decimal("5.00"), "USD"),
        )
        product.add_recipe(recipe.id, Decimal("1.0"))
        created = await repo.create(product)

        await repo.delete(created.id)

        found = await repo.get_by_id(created.id)
        assert found is None

    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        """Test getting product by non-existent ID."""
        from uuid import uuid4
        repo = ProductRepository(db_session)

        found = await repo.get_by_id(uuid4())

        assert found is None

    async def test_get_by_name_not_found(self, db_session: AsyncSession):
        """Test getting product by non-existent name."""
        repo = ProductRepository(db_session)

        found = await repo.get_by_name("NonExistentProduct")

        assert found is None

    async def test_product_with_multiple_recipes(self, db_session: AsyncSession):
        """Test creating product with multiple recipes."""
        repo = ProductRepository(db_session)
        recipe1 = await self.create_test_recipe(db_session)

        # Create second recipe
        ing_repo = IngredientRepository(db_session)
        ingredient2 = Ingredient(name="Sugar for Product", unit=MeasurementUnit.KILOGRAM)
        created_ing2 = await ing_repo.create(ingredient2)

        recipe_repo = RecipeRepository(db_session)
        recipe2 = Recipe(name="Sweet Recipe", instructions="Add sugar")
        recipe2.add_ingredient(created_ing2.id, Decimal("0.3"))
        recipe2 = await recipe_repo.create(recipe2)

        # Create product with multiple recipes
        product = Product(
            name="Complex Product",
            fixed_costs=Money(Decimal("12.00"), "USD"),
        )
        product.add_recipe(recipe1.id, Decimal("1.0"))
        product.add_recipe(recipe2.id, Decimal("0.5"))

        created = await repo.create(product)

        assert len(created.recipes) == 2

    async def test_product_cost_calculation(self, db_session: AsyncSession):
        """Test product with cost percentages."""
        repo = ProductRepository(db_session)
        recipe = await self.create_test_recipe(db_session)

        product = Product(
            name="Costed Product",
            fixed_costs=Money(Decimal("10.00"), "USD"),
            variable_costs_percentage=Decimal("0.15"),  # 15%
            profit_margin_percentage=Decimal("0.25"),   # 25%
        )
        product.add_recipe(recipe.id, Decimal("1.0"))

        created = await repo.create(product)

        assert created.variable_costs_percentage == Decimal("0.15")
        assert created.profit_margin_percentage == Decimal("0.25")

    async def test_update_product_recipes(self, db_session: AsyncSession):
        """Test updating product recipes - verifies bug fix for recipe persistence."""
        repo = ProductRepository(db_session)
        recipe1 = await self.create_test_recipe(db_session)

        # Create product with one recipe
        product = Product(
            name="Product to Update",
            fixed_costs=Money(Decimal("5.00"), "USD"),
        )
        product.add_recipe(recipe1.id, Decimal("1.0"))
        created = await repo.create(product)

        # Verify it has 1 recipe
        assert len(created.recipes) == 1
        assert created.recipes[0].quantity == Decimal("1.0")

        # Create second recipe
        ing_repo = IngredientRepository(db_session)
        ingredient2 = Ingredient(name="Chocolate for Update", unit=MeasurementUnit.KILOGRAM)
        created_ing2 = await ing_repo.create(ingredient2)

        recipe_repo = RecipeRepository(db_session)
        recipe2 = Recipe(name="Chocolate Recipe", instructions="Melt chocolate")
        recipe2.add_ingredient(created_ing2.id, Decimal("0.2"))
        recipe2 = await recipe_repo.create(recipe2)

        # Update product to add second recipe
        created.add_recipe(recipe2.id, Decimal("2.0"))
        updated = await repo.update(created)

        # Verify recipes were persisted (this was the bug)
        assert len(updated.recipes) == 2
        recipe_ids = [r.recipe_id for r in updated.recipes]
        assert recipe1.id in recipe_ids
        assert recipe2.id in recipe_ids

        # Verify quantities
        for recipe in updated.recipes:
            if recipe.recipe_id == recipe1.id:
                assert recipe.quantity == Decimal("1.0")
            elif recipe.recipe_id == recipe2.id:
                assert recipe.quantity == Decimal("2.0")

    async def test_update_product_remove_recipes(self, db_session: AsyncSession):
        """Test removing recipes from product during update."""
        repo = ProductRepository(db_session)
        recipe1 = await self.create_test_recipe(db_session)

        # Create second recipe
        ing_repo = IngredientRepository(db_session)
        ingredient2 = Ingredient(name="Sugar for Remove", unit=MeasurementUnit.KILOGRAM)
        created_ing2 = await ing_repo.create(ingredient2)

        recipe_repo = RecipeRepository(db_session)
        recipe2 = Recipe(name="Sugar Recipe", instructions="Add sugar")
        recipe2.add_ingredient(created_ing2.id, Decimal("0.3"))
        recipe2 = await recipe_repo.create(recipe2)

        # Create product with two recipes
        product = Product(
            name="Product with 2 Recipes",
            fixed_costs=Money(Decimal("10.00"), "USD"),
        )
        product.add_recipe(recipe1.id, Decimal("1.0"))
        product.add_recipe(recipe2.id, Decimal("0.5"))
        created = await repo.create(product)

        # Verify it has 2 recipes
        assert len(created.recipes) == 2

        # Remove one recipe
        created.recipes = [r for r in created.recipes if r.recipe_id == recipe1.id]
        updated = await repo.update(created)

        # Verify only one recipe remains
        assert len(updated.recipes) == 1
        assert updated.recipes[0].recipe_id == recipe1.id

    async def test_update_product_change_recipe_quantity(self, db_session: AsyncSession):
        """Test changing recipe quantities during product update."""
        repo = ProductRepository(db_session)
        recipe = await self.create_test_recipe(db_session)

        # Create product with recipe
        product = Product(
            name="Product with Recipe Qty",
            fixed_costs=Money(Decimal("7.00"), "USD"),
        )
        product.add_recipe(recipe.id, Decimal("1.0"))
        created = await repo.create(product)

        # Verify initial quantity
        assert created.recipes[0].quantity == Decimal("1.0")

        # Update quantity
        created.recipes[0].quantity = Decimal("3.5")
        updated = await repo.update(created)

        # Verify quantity was updated
        assert len(updated.recipes) == 1
        assert updated.recipes[0].quantity == Decimal("3.5")

        # Fetch again to verify persistence
        fetched = await repo.get_with_recipes(updated.id)
        assert fetched.recipes[0].quantity == Decimal("3.5")
