"""Unit tests for repository coverage."""
import pytest
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ingredient import Ingredient
from src.domain.entities.recipe import Recipe
from src.domain.entities.product import Product
from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.user import User
from src.domain.value_objects.measurement_unit import MeasurementUnit
from src.domain.value_objects.money import Money
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.repositories.ingredient_repository import IngredientRepository
from src.infrastructure.database.repositories.recipe_repository import RecipeRepository
from src.infrastructure.database.repositories.product_repository import ProductRepository
from src.infrastructure.database.repositories.order_repository import OrderRepository
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.security.auth import get_password_hash


@pytest.mark.asyncio
class TestIngredientRepositoryCoverage:
    """Test ingredient repository edge cases."""

    async def test_get_by_name(self, db_session: AsyncSession):
        """Test getting ingredient by name."""
        repo = IngredientRepository(db_session)

        # Create ingredient
        ingredient = Ingredient(name="Test Flour Coverage", unit=MeasurementUnit.KILOGRAM)
        created = await repo.create(ingredient)

        # Get by name
        found = await repo.get_by_name("Test Flour Coverage")
        assert found is not None
        assert found.id == created.id

    async def test_get_by_name_not_found(self, db_session: AsyncSession):
        """Test getting non-existent ingredient by name."""
        repo = IngredientRepository(db_session)
        found = await repo.get_by_name("NonExistent")
        assert found is None

    async def test_exists(self, db_session: AsyncSession):
        """Test checking if ingredient exists."""
        repo = IngredientRepository(db_session)

        # Create ingredient
        ingredient = Ingredient(name="Exists Test", unit=MeasurementUnit.KILOGRAM)
        created = await repo.create(ingredient)

        # Check exists
        assert await repo.exists(created.id) is True
        assert await repo.exists(uuid4()) is False


@pytest.mark.asyncio
class TestRecipeRepositoryCoverage:
    """Test recipe repository edge cases."""

    async def test_get_by_name(self, db_session: AsyncSession):
        """Test getting recipe by name."""
        repo = RecipeRepository(db_session)

        # Create recipe
        recipe = Recipe(name="Coverage Recipe", instructions="Test")
        created = await repo.create(recipe)

        # Get by name
        found = await repo.get_by_name("Coverage Recipe")
        assert found is not None
        assert found.id == created.id

    async def test_get_by_name_not_found(self, db_session: AsyncSession):
        """Test getting non-existent recipe by name."""
        repo = RecipeRepository(db_session)
        found = await repo.get_by_name("NonExistent")
        assert found is None

    async def test_exists(self, db_session: AsyncSession):
        """Test checking if recipe exists."""
        repo = RecipeRepository(db_session)

        recipe = Recipe(name="Exists Recipe Test", instructions="Test")
        created = await repo.create(recipe)

        assert await repo.exists(created.id) is True
        assert await repo.exists(uuid4()) is False

    async def test_get_with_ingredients_not_found(self, db_session: AsyncSession):
        """Test getting non-existent recipe with ingredients."""
        repo = RecipeRepository(db_session)
        found = await repo.get_with_ingredients(uuid4())
        assert found is None


@pytest.mark.asyncio
class TestProductRepositoryCoverage:
    """Test product repository edge cases."""

    async def test_get_by_name(self, db_session: AsyncSession):
        """Test getting product by name."""
        repo = ProductRepository(db_session)

        product = Product(
            name="Coverage Product",
            fixed_costs=Money(Decimal("5.00")),
        )
        created = await repo.create(product)

        found = await repo.get_by_name("Coverage Product")
        assert found is not None
        assert found.id == created.id

    async def test_get_by_name_not_found(self, db_session: AsyncSession):
        """Test getting non-existent product by name."""
        repo = ProductRepository(db_session)
        found = await repo.get_by_name("NonExistent")
        assert found is None

    async def test_exists(self, db_session: AsyncSession):
        """Test checking if product exists."""
        repo = ProductRepository(db_session)

        product = Product(name="Exists Product", fixed_costs=Money(Decimal("5.00")))
        created = await repo.create(product)

        assert await repo.exists(created.id) is True
        assert await repo.exists(uuid4()) is False


@pytest.mark.asyncio
class TestOrderRepositoryCoverage:
    """Test order repository edge cases."""

    async def create_user(self, db_session: AsyncSession) -> User:
        """Helper to create user."""
        user_repo = UserRepository(db_session)
        user = User(
            email=f"ordercover{uuid4().hex[:8]}@test.com",
            username=f"ordercover{uuid4().hex[:8]}",
            hashed_password=get_password_hash("pass123"),
            role=UserRole.USER,
        )
        return await user_repo.create(user)

    async def test_get_with_items_not_found(self, db_session: AsyncSession):
        """Test getting non-existent order with items."""
        repo = OrderRepository(db_session)
        found = await repo.get_with_items(uuid4())
        assert found is None

    async def test_exists(self, db_session: AsyncSession):
        """Test checking if order exists."""
        repo = OrderRepository(db_session)
        user = await self.create_user(db_session)

        order = Order(
            customer_name="Exists Test",
            customer_email="exists@test.com",
            created_by_user_id=user.id,
        )
        created = await repo.create(order)

        assert await repo.exists(created.id) is True
        assert await repo.exists(uuid4()) is False

    async def test_get_by_customer_email(self, db_session: AsyncSession):
        """Test getting orders by customer email."""
        repo = OrderRepository(db_session)
        user = await self.create_user(db_session)

        email = f"customer{uuid4().hex[:8]}@test.com"
        order = Order(
            customer_name="Test Customer",
            customer_email=email,
            created_by_user_id=user.id,
        )
        await repo.create(order)

        orders = await repo.get_by_customer_email(email)
        assert len(orders) >= 1

    async def test_get_by_status(self, db_session: AsyncSession):
        """Test getting orders by status."""
        repo = OrderRepository(db_session)
        user = await self.create_user(db_session)

        order = Order(
            customer_name="Status Test",
            customer_email="status@test.com",
            created_by_user_id=user.id,
            status=OrderStatus.PENDING,
        )
        await repo.create(order)

        orders = await repo.get_by_status(OrderStatus.PENDING)
        assert len(orders) >= 1


@pytest.mark.asyncio
class TestUserRepositoryCoverage:
    """Test user repository edge cases."""

    async def test_get_by_email(self, db_session: AsyncSession):
        """Test getting user by email."""
        repo = UserRepository(db_session)

        email = f"usercover{uuid4().hex[:8]}@test.com"
        user = User(
            email=email,
            username=f"usercover{uuid4().hex[:8]}",
            hashed_password=get_password_hash("pass123"),
            role=UserRole.USER,
        )
        created = await repo.create(user)

        found = await repo.get_by_email(email)
        assert found is not None
        assert found.id == created.id

    async def test_get_by_email_not_found(self, db_session: AsyncSession):
        """Test getting non-existent user by email."""
        repo = UserRepository(db_session)
        found = await repo.get_by_email("nonexistent@test.com")
        assert found is None

    async def test_get_by_username(self, db_session: AsyncSession):
        """Test getting user by username."""
        repo = UserRepository(db_session)

        username = f"usernamecover{uuid4().hex[:8]}"
        user = User(
            email=f"{username}@test.com",
            username=username,
            hashed_password=get_password_hash("pass123"),
            role=UserRole.USER,
        )
        created = await repo.create(user)

        found = await repo.get_by_username(username)
        assert found is not None
        assert found.id == created.id

    async def test_get_by_username_not_found(self, db_session: AsyncSession):
        """Test getting non-existent user by username."""
        repo = UserRepository(db_session)
        found = await repo.get_by_username("nonexistent")
        assert found is None

    async def test_exists(self, db_session: AsyncSession):
        """Test checking if user exists."""
        repo = UserRepository(db_session)

        user = User(
            email=f"exists{uuid4().hex[:8]}@test.com",
            username=f"exists{uuid4().hex[:8]}",
            hashed_password=get_password_hash("pass123"),
            role=UserRole.USER,
        )
        created = await repo.create(user)

        assert await repo.exists(created.id) is True
        assert await repo.exists(uuid4()) is False
