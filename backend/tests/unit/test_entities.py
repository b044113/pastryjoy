"""Unit tests for domain entities."""
import pytest
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from src.domain.entities.order import Order, OrderStatus, OrderItem
from src.domain.entities.recipe import Recipe, RecipeIngredient
from src.domain.entities.product import Product, ProductRecipe
from src.domain.entities.user import User
from src.domain.value_objects.money import Money
from src.domain.value_objects.user_role import UserRole
from src.domain.value_objects.measurement_unit import MeasurementUnit


class TestOrderEntity:
    """Test Order entity business logic."""

    def test_order_creation_valid(self):
        """Test creating a valid order."""
        order = Order(
            customer_name="John Doe",
            customer_email="john@test.com",
            created_by_user_id=uuid4(),
        )
        assert order.customer_name == "John Doe"
        assert order.status == OrderStatus.PENDING

    def test_order_creation_missing_name(self):
        """Test creating order without customer name raises error."""
        with pytest.raises(ValueError, match="Customer name is required"):
            Order(
                customer_name="",
                customer_email="test@test.com",
                created_by_user_id=uuid4(),
            )

    def test_order_creation_missing_email(self):
        """Test creating order without customer email raises error."""
        with pytest.raises(ValueError, match="Customer email is required"):
            Order(
                customer_name="John",
                customer_email="",
                created_by_user_id=uuid4(),
            )

    def test_order_add_item(self):
        """Test adding item to order."""
        order = Order(
            customer_name="John",
            customer_email="john@test.com",
            created_by_user_id=uuid4(),
        )
        product_id = uuid4()
        order.add_item(product_id, Decimal("2"), Money(Decimal("10.00")))

        assert len(order.items) == 1
        assert order.items[0].product_id == product_id
        assert order.items[0].quantity == Decimal("2")

    def test_order_remove_item(self):
        """Test removing item from order."""
        order = Order(
            customer_name="John",
            customer_email="john@test.com",
            created_by_user_id=uuid4(),
        )
        product_id = uuid4()
        order.add_item(product_id, Decimal("2"), Money(Decimal("10.00")))
        item_id = order.items[0].id

        order.remove_item(item_id)
        assert len(order.items) == 0

    def test_order_calculate_total(self):
        """Test calculating order total."""
        order = Order(
            customer_name="John",
            customer_email="john@test.com",
            created_by_user_id=uuid4(),
        )
        order.add_item(uuid4(), Decimal("2"), Money(Decimal("10.00")))
        order.add_item(uuid4(), Decimal("1"), Money(Decimal("5.00")))

        total = order.calculate_total()
        assert total.amount == Decimal("25.00")

    def test_order_calculate_total_empty(self):
        """Test calculating total for empty order."""
        order = Order(
            customer_name="John",
            customer_email="john@test.com",
            created_by_user_id=uuid4(),
        )
        total = order.calculate_total()
        assert total.amount == Decimal("0")

    def test_order_confirm(self):
        """Test confirming an order."""
        order = Order(
            customer_name="John",
            customer_email="john@test.com",
            created_by_user_id=uuid4(),
        )
        order.add_item(uuid4(), Decimal("1"), Money(Decimal("10.00")))

        order.confirm()
        assert order.status == OrderStatus.CONFIRMED

    def test_order_confirm_without_items(self):
        """Test confirming order without items raises error."""
        order = Order(
            customer_name="John",
            customer_email="john@test.com",
            created_by_user_id=uuid4(),
        )

        with pytest.raises(ValueError, match="Cannot confirm order without items"):
            order.confirm()

    def test_order_confirm_non_pending(self):
        """Test confirming non-pending order raises error."""
        order = Order(
            customer_name="John",
            customer_email="john@test.com",
            created_by_user_id=uuid4(),
            status=OrderStatus.COMPLETED,
        )

        with pytest.raises(ValueError, match="Only pending orders can be confirmed"):
            order.confirm()

    def test_order_cancel(self):
        """Test canceling an order."""
        order = Order(
            customer_name="John",
            customer_email="john@test.com",
            created_by_user_id=uuid4(),
        )

        order.cancel()
        assert order.status == OrderStatus.CANCELLED

    def test_order_cancel_completed(self):
        """Test canceling completed order raises error."""
        order = Order(
            customer_name="John",
            customer_email="john@test.com",
            created_by_user_id=uuid4(),
            status=OrderStatus.COMPLETED,
        )

        with pytest.raises(ValueError, match="Cannot cancel completed orders"):
            order.cancel()

    def test_order_cancel_already_cancelled(self):
        """Test canceling already cancelled order raises error."""
        order = Order(
            customer_name="John",
            customer_email="john@test.com",
            created_by_user_id=uuid4(),
            status=OrderStatus.CANCELLED,
        )

        with pytest.raises(ValueError, match="Order is already cancelled"):
            order.cancel()


class TestRecipeEntity:
    """Test Recipe entity business logic."""

    def test_recipe_creation(self):
        """Test creating a recipe."""
        recipe = Recipe(name="Test Recipe", instructions="Mix well")
        assert recipe.name == "Test Recipe"
        assert recipe.instructions == "Mix well"
        assert len(recipe.ingredients) == 0

    def test_recipe_creation_empty_name(self):
        """Test creating recipe with empty name raises error."""
        with pytest.raises(ValueError, match="Recipe name is required"):
            Recipe(name="", instructions="Test")

    def test_recipe_add_ingredient(self):
        """Test adding ingredient to recipe."""
        recipe = Recipe(name="Test", instructions="Mix")
        ingredient_id = uuid4()

        recipe.add_ingredient(ingredient_id, Decimal("0.5"))
        assert len(recipe.ingredients) == 1
        assert recipe.ingredients[0].ingredient_id == ingredient_id
        assert recipe.ingredients[0].quantity == Decimal("0.5")

    def test_recipe_update_ingredient_quantity(self):
        """Test updating ingredient quantity."""
        recipe = Recipe(name="Test", instructions="Mix")
        ingredient_id = uuid4()
        recipe.add_ingredient(ingredient_id, Decimal("0.5"))

        recipe.update_ingredient_quantity(ingredient_id, Decimal("0.8"))
        assert recipe.ingredients[0].quantity == Decimal("0.8")

    def test_recipe_update_ingredient_quantity_not_found(self):
        """Test updating quantity for non-existent ingredient raises error."""
        recipe = Recipe(name="Test", instructions="Mix")
        ingredient_id = uuid4()

        with pytest.raises(ValueError, match="Ingredient .* not found in recipe"):
            recipe.update_ingredient_quantity(ingredient_id, Decimal("0.8"))

    def test_recipe_remove_ingredient(self):
        """Test removing ingredient from recipe."""
        recipe = Recipe(name="Test", instructions="Mix")
        ingredient_id = uuid4()
        recipe.add_ingredient(ingredient_id, Decimal("0.5"))

        recipe.remove_ingredient(ingredient_id)
        assert len(recipe.ingredients) == 0


class TestProductEntity:
    """Test Product entity business logic."""

    def test_product_creation(self):
        """Test creating a product."""
        product = Product(
            name="Test Product",
            fixed_costs=Money(Decimal("5.00")),
            variable_costs_percentage=Decimal("0.10"),
            profit_margin_percentage=Decimal("0.20"),
        )
        assert product.name == "Test Product"
        assert len(product.recipes) == 0

    def test_product_creation_empty_name(self):
        """Test creating product with empty name raises error."""
        with pytest.raises(ValueError, match="Product name is required"):
            Product(name="", fixed_costs=Money(Decimal("5.00")))

    def test_product_add_recipe(self):
        """Test adding recipe to product."""
        product = Product(name="Test", fixed_costs=Money(Decimal("5.00")))
        recipe_id = uuid4()

        product.add_recipe(recipe_id, Decimal("1.0"))
        assert len(product.recipes) == 1
        assert product.recipes[0].recipe_id == recipe_id

    def test_product_remove_recipe(self):
        """Test removing recipe from product."""
        product = Product(name="Test", fixed_costs=Money(Decimal("5.00")))
        recipe_id = uuid4()
        product.add_recipe(recipe_id, Decimal("1.0"))

        product.remove_recipe(recipe_id)
        assert len(product.recipes) == 0


class TestUserEntity:
    """Test User entity business logic."""

    def test_user_is_admin(self):
        """Test checking if user is admin."""
        admin = User(
            email="admin@test.com",
            username="admin",
            hashed_password="hashed",
            role=UserRole.ADMIN,
        )
        assert admin.is_admin() is True

        user = User(
            email="user@test.com",
            username="user",
            hashed_password="hashed",
            role=UserRole.USER,
        )
        assert user.is_admin() is False


class TestOrderItemEntity:
    """Test OrderItem entity."""

    def test_order_item_calculate_total(self):
        """Test calculating item total."""
        item = OrderItem(
            order_id=uuid4(),
            product_id=uuid4(),
            quantity=Decimal("3"),
            unit_price=Money(Decimal("10.00")),
        )
        total = item.calculate_total()
        assert total.amount == Decimal("30.00")


class TestMoneyValueObject:
    """Test Money value object."""

    def test_money_creation(self):
        """Test creating money value object."""
        money = Money(Decimal("10.50"), "USD")
        assert money.amount == Decimal("10.50")
        assert money.currency == "USD"

    def test_money_default_currency(self):
        """Test default currency."""
        money = Money(Decimal("10.50"))
        assert money.currency == "USD"

    def test_money_addition(self):
        """Test adding money."""
        money1 = Money(Decimal("10.00"))
        money2 = Money(Decimal("5.00"))
        result = money1 + money2
        assert result.amount == Decimal("15.00")

    def test_money_subtraction(self):
        """Test subtracting money."""
        money1 = Money(Decimal("10.00"))
        money2 = Money(Decimal("3.00"))
        result = money1 - money2
        assert result.amount == Decimal("7.00")

    def test_money_multiplication(self):
        """Test multiplying money."""
        money = Money(Decimal("10.00"))
        result = money * Decimal("2.5")
        assert result.amount == Decimal("25.00")

    def test_money_equality(self):
        """Test money equality."""
        money1 = Money(Decimal("10.00"))
        money2 = Money(Decimal("10.00"))
        assert money1 == money2
