"""Unit tests for mappers."""
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.ingredient import Ingredient
from src.domain.entities.product import Product
from src.domain.entities.recipe import Recipe
from src.domain.entities.user import User
from src.domain.value_objects.measurement_unit import MeasurementUnit
from src.domain.value_objects.money import Money
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.mappers.ingredient_mapper import IngredientMapper
from src.infrastructure.database.mappers.product_mapper import ProductMapper
from src.infrastructure.database.mappers.recipe_mapper import RecipeMapper
from src.infrastructure.database.mappers.user_mapper import UserMapper
from src.infrastructure.database.models.ingredient import IngredientModel
from src.infrastructure.database.models.product import ProductModel
from src.infrastructure.database.models.recipe import RecipeModel
from src.infrastructure.database.models.user import UserModel


class TestUserMapper:
    """Test UserMapper."""

    def test_to_entity(self):
        """Test converting user model to entity."""
        test_id = uuid4()
        test_time = datetime.now()
        model = UserModel(
            id=test_id,
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpass",
            role="user",
            is_active=True,
            full_name="Test User",
            created_at=test_time,
            updated_at=test_time,
        )

        entity = UserMapper.to_entity(model)

        assert isinstance(entity, User)
        assert entity.id == test_id
        assert entity.email == "test@example.com"
        assert entity.username == "testuser"
        assert entity.role == UserRole.USER
        assert entity.is_active is True

    def test_to_model(self):
        """Test converting user entity to model."""
        test_id = uuid4()
        test_time = datetime.now()
        entity = User(
            id=test_id,
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpass",
            role=UserRole.ADMIN,
            is_active=True,
            full_name="Test User",
            created_at=test_time,
            updated_at=test_time,
        )

        model = UserMapper.to_model(entity)

        assert isinstance(model, UserModel)
        assert model.id == test_id
        assert model.email == "test@example.com"
        assert model.username == "testuser"
        assert model.role == "admin"


class TestIngredientMapper:
    """Test IngredientMapper."""

    def test_to_entity(self):
        """Test converting ingredient model to entity."""
        test_id = uuid4()
        test_time = datetime.now()
        model = IngredientModel(
            id=test_id,
            name="Flour",
            unit="kg",
            created_at=test_time,
            updated_at=test_time,
        )

        entity = IngredientMapper.to_entity(model)

        assert isinstance(entity, Ingredient)
        assert entity.id == test_id
        assert entity.name == "Flour"
        assert entity.unit == MeasurementUnit.KILOGRAM

    def test_to_model(self):
        """Test converting ingredient entity to model."""
        test_id = uuid4()
        test_time = datetime.now()
        entity = Ingredient(
            id=test_id,
            name="Sugar",
            unit=MeasurementUnit.GRAM,
            created_at=test_time,
            updated_at=test_time,
        )

        model = IngredientMapper.to_model(entity)

        assert isinstance(model, IngredientModel)
        assert model.id == test_id
        assert model.name == "Sugar"
        assert model.unit == "g"


class TestRecipeMapper:
    """Test RecipeMapper."""

    def test_to_entity(self):
        """Test converting recipe model to entity."""
        test_id = uuid4()
        test_time = datetime.now()
        model = RecipeModel(
            id=test_id,
            name="Bread",
            instructions="Mix and bake",
            created_at=test_time,
            updated_at=test_time,
        )
        # Mock the ingredients relationship as empty
        model.ingredients = []

        entity = RecipeMapper.to_entity(model)

        assert isinstance(entity, Recipe)
        assert entity.id == test_id
        assert entity.name == "Bread"
        assert entity.instructions == "Mix and bake"

    def test_to_model(self):
        """Test converting recipe entity to model."""
        test_id = uuid4()
        test_time = datetime.now()
        entity = Recipe(
            id=test_id,
            name="Cake",
            instructions="Bake at 180°C",
            created_at=test_time,
            updated_at=test_time,
        )

        model = RecipeMapper.to_model(entity)

        assert isinstance(model, RecipeModel)
        assert model.id == test_id
        assert model.name == "Cake"
        assert model.instructions == "Bake at 180°C"


class TestProductMapper:
    """Test ProductMapper."""

    def test_to_entity(self):
        """Test converting product model to entity."""
        test_id = uuid4()
        test_time = datetime.now()
        model = ProductModel(
            id=test_id,
            name="Bread Loaf",
            fixed_costs_amount=Decimal("5.99"),
            fixed_costs_currency="USD",
            variable_costs_percentage=Decimal("0.10"),
            profit_margin_percentage=Decimal("0.20"),
            created_at=test_time,
            updated_at=test_time,
        )
        # Mock the recipes relationship as empty
        model.recipes = []

        entity = ProductMapper.to_entity(model)

        assert isinstance(entity, Product)
        assert entity.id == test_id
        assert entity.name == "Bread Loaf"
        assert entity.fixed_costs.amount == Decimal("5.99")

    def test_to_model(self):
        """Test converting product entity to model."""
        test_id = uuid4()
        test_time = datetime.now()
        entity = Product(
            id=test_id,
            name="Croissant",
            fixed_costs=Money(Decimal("3.50"), "USD"),
            variable_costs_percentage=Decimal("0.15"),
            profit_margin_percentage=Decimal("0.25"),
            created_at=test_time,
            updated_at=test_time,
        )

        model = ProductMapper.to_model(entity)

        assert isinstance(model, ProductModel)
        assert model.id == test_id
        assert model.name == "Croissant"
        assert model.fixed_costs_amount == Decimal("3.50")
