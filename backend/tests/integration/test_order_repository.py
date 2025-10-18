"""Integration tests for Order Repository."""
import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ingredient import Ingredient
from src.domain.entities.order import Order
from src.domain.entities.product import Product
from src.domain.entities.recipe import Recipe
from src.domain.entities.user import User
from src.domain.value_objects.measurement_unit import MeasurementUnit
from src.domain.value_objects.money import Money
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.repositories.order_repository import OrderRepository
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.repositories.product_repository import ProductRepository
from src.infrastructure.database.repositories.recipe_repository import RecipeRepository
from src.infrastructure.database.repositories.ingredient_repository import IngredientRepository
from src.infrastructure.security.auth import get_password_hash


@pytest.mark.asyncio
class TestOrderRepository:
    """Test Order Repository integration."""

    async def create_test_user(self, db_session: AsyncSession) -> User:
        """Helper to create a test user."""
        user_repo = UserRepository(db_session)
        user = User(
            email="orderuser@test.com",
            username="orderuser",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            full_name="Order User",
        )
        return await user_repo.create(user)

    async def create_test_product(self, db_session: AsyncSession) -> Product:
        """Helper to create a test product."""
        # Create ingredient
        ing_repo = IngredientRepository(db_session)
        ingredient = Ingredient(name="Test Flour", unit=MeasurementUnit.KILOGRAM)
        created_ing = await ing_repo.create(ingredient)

        # Create recipe
        recipe_repo = RecipeRepository(db_session)
        recipe = Recipe(name="Test Recipe", instructions="Mix ingredients")
        recipe.add_ingredient(created_ing.id, Decimal("0.5"))
        created_recipe = await recipe_repo.create(recipe)

        # Create product
        product_repo = ProductRepository(db_session)
        product = Product(
            name="Test Product",
            fixed_costs=Money(Decimal("5.00"), "USD"),
            variable_costs_percentage=Decimal("0.10"),
            profit_margin_percentage=Decimal("0.20"),
        )
        product.add_recipe(created_recipe.id, Decimal("1.0"))
        return await product_repo.create(product)

    async def test_create_order(self, db_session: AsyncSession):
        """Test creating an order."""
        repo = OrderRepository(db_session)
        user = await self.create_test_user(db_session)
        product = await self.create_test_product(db_session)

        order = Order(
            customer_name="John Doe",
            customer_email="john@test.com",
            customer_phone="555-1234",
            created_by=user.id,
            status="pending",
        )
        order.add_item(product.id, 2, Money(Decimal("10.00"), "USD"))

        created = await repo.create(order)

        assert created.id is not None
        assert created.customer_name == "John Doe"
        assert created.status == "pending"
        assert len(created.items) == 1

    async def test_get_by_id(self, db_session: AsyncSession):
        """Test getting order by ID."""
        repo = OrderRepository(db_session)
        user = await self.create_test_user(db_session)
        product = await self.create_test_product(db_session)

        order = Order(
            customer_name="Jane Doe",
            created_by=user.id,
            status="pending",
        )
        order.add_item(product.id, 1, Money(Decimal("10.00"), "USD"))
        created = await repo.create(order)

        found = await repo.get_by_id(created.id)

        assert found is not None
        assert found.id == created.id
        assert found.customer_name == "Jane Doe"

    async def test_get_all(self, db_session: AsyncSession):
        """Test getting all orders."""
        repo = OrderRepository(db_session)
        user = await self.create_test_user(db_session)
        product = await self.create_test_product(db_session)

        # Create multiple orders
        for i in range(3):
            order = Order(
                customer_name=f"Customer {i}",
                created_by=user.id,
                status="pending",
            )
            order.add_item(product.id, 1, Money(Decimal("10.00"), "USD"))
            await repo.create(order)

        orders = await repo.get_all()

        assert len(orders) >= 3

    async def test_get_by_user(self, db_session: AsyncSession):
        """Test getting orders by user ID."""
        repo = OrderRepository(db_session)
        user_repo = UserRepository(db_session)

        user1 = await self.create_test_user(db_session)
        user2 = User(
            email="user2@test.com",
            username="user2",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        user2 = await user_repo.create(user2)

        product = await self.create_test_product(db_session)

        # Create order for user1
        order1 = Order(
            customer_name="User1 Order",
            created_by=user1.id,
            status="pending",
        )
        order1.add_item(product.id, 1, Money(Decimal("10.00"), "USD"))
        await repo.create(order1)

        # Create order for user2
        order2 = Order(
            customer_name="User2 Order",
            created_by=user2.id,
            status="pending",
        )
        order2.add_item(product.id, 1, Money(Decimal("10.00"), "USD"))
        await repo.create(order2)

        # Get orders for user1
        user1_orders = await repo.get_by_user_id(user1.id)

        assert len(user1_orders) >= 1
        assert all(order.created_by == user1.id for order in user1_orders)

    async def test_update_order(self, db_session: AsyncSession):
        """Test updating an order."""
        repo = OrderRepository(db_session)
        user = await self.create_test_user(db_session)
        product = await self.create_test_product(db_session)

        order = Order(
            customer_name="Original Name",
            created_by=user.id,
            status="pending",
        )
        order.add_item(product.id, 1, Money(Decimal("10.00"), "USD"))
        created = await repo.create(order)

        # Update status
        created.update_status("completed")
        updated = await repo.update(created)

        assert updated.status == "completed"

    async def test_delete_order(self, db_session: AsyncSession):
        """Test deleting an order."""
        repo = OrderRepository(db_session)
        user = await self.create_test_user(db_session)
        product = await self.create_test_product(db_session)

        order = Order(
            customer_name="To Delete",
            created_by=user.id,
            status="pending",
        )
        order.add_item(product.id, 1, Money(Decimal("10.00"), "USD"))
        created = await repo.create(order)

        await repo.delete(created.id)

        found = await repo.get_by_id(created.id)
        assert found is None

    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        """Test getting order by non-existent ID."""
        from uuid import uuid4
        repo = OrderRepository(db_session)

        found = await repo.get_by_id(uuid4())

        assert found is None

    async def test_order_with_multiple_items(self, db_session: AsyncSession):
        """Test creating order with multiple items."""
        repo = OrderRepository(db_session)
        user = await self.create_test_user(db_session)
        product1 = await self.create_test_product(db_session)

        # Create second product
        product_repo = ProductRepository(db_session)
        product2 = Product(
            name="Test Product 2",
            fixed_costs=Money(Decimal("8.00"), "USD"),
        )
        product2 = await product_repo.create(product2)

        order = Order(
            customer_name="Multi Item Order",
            created_by=user.id,
            status="pending",
        )
        order.add_item(product1.id, 2, Money(Decimal("10.00"), "USD"))
        order.add_item(product2.id, 1, Money(Decimal("8.00"), "USD"))

        created = await repo.create(order)

        assert len(created.items) == 2
        assert created.calculate_total().amount == Decimal("28.00")
