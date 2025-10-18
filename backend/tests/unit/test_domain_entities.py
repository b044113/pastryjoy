"""Unit tests for domain entities."""
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.ingredient import Ingredient
from src.domain.entities.user import User
from src.domain.value_objects.measurement_unit import MeasurementUnit
from src.domain.value_objects.user_role import UserRole


class TestUser:
    """Test User entity."""

    def test_create_user(self):
        """Test creating a user entity."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123",
            role=UserRole.USER,
            is_active=True,
            full_name="Test User",
            created_at=datetime.now(),
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert user.full_name == "Test User"

    def test_user_is_admin(self):
        """Test checking if user is admin."""
        admin = User(
            id=uuid4(),
            email="admin@example.com",
            username="admin",
            hashed_password="hash",
            role=UserRole.ADMIN,
        )
        regular_user = User(
            id=uuid4(),
            email="user@example.com",
            username="user",
            hashed_password="hash",
            role=UserRole.USER,
        )

        assert admin.is_admin() is True
        assert regular_user.is_admin() is False

    def test_user_validation_no_email(self):
        """Test user validation fails without email."""
        with pytest.raises(ValueError, match="Email is required"):
            User(
                id=uuid4(),
                email="",
                username="testuser",
                hashed_password="hash",
                role=UserRole.USER,
            )

    def test_user_validation_no_username(self):
        """Test user validation fails without username."""
        with pytest.raises(ValueError, match="Username is required"):
            User(
                id=uuid4(),
                email="test@example.com",
                username="",
                hashed_password="hash",
                role=UserRole.USER,
            )

    def test_user_validation_invalid_email(self):
        """Test user validation fails with invalid email."""
        with pytest.raises(ValueError, match="Invalid email format"):
            User(
                id=uuid4(),
                email="notanemail",
                username="testuser",
                hashed_password="hash",
                role=UserRole.USER,
            )

    def test_user_can_manage_products(self):
        """Test admin can manage products."""
        admin = User(
            id=uuid4(),
            email="admin@example.com",
            username="admin",
            hashed_password="hash",
            role=UserRole.ADMIN,
        )

        assert admin.can_manage_products() is True

    def test_user_can_create_orders(self):
        """Test user can create orders."""
        user = User(
            id=uuid4(),
            email="user@example.com",
            username="user",
            hashed_password="hash",
            role=UserRole.USER,
        )

        assert user.can_create_orders() is True


class TestIngredient:
    """Test Ingredient entity."""

    def test_create_ingredient(self):
        """Test creating an ingredient."""
        ingredient = Ingredient(
            id=uuid4(),
            name="Flour",
            unit=MeasurementUnit.KILOGRAM
        )

        assert ingredient.name == "Flour"
        assert ingredient.unit == MeasurementUnit.KILOGRAM

    def test_ingredient_validation_no_name(self):
        """Test ingredient validation fails without name."""
        with pytest.raises(ValueError, match="Ingredient name is required"):
            Ingredient(
                id=uuid4(),
                name="",
                unit=MeasurementUnit.KILOGRAM
            )

    def test_ingredient_validation_empty_name(self):
        """Test ingredient validation fails with empty name."""
        with pytest.raises(ValueError, match="Ingredient name cannot be empty"):
            Ingredient(
                id=uuid4(),
                name="   ",
                unit=MeasurementUnit.KILOGRAM
            )

    def test_ingredient_with_different_units(self):
        """Test creating ingredients with different units."""
        flour = Ingredient(id=uuid4(), name="Flour", unit=MeasurementUnit.KILOGRAM)
        salt = Ingredient(id=uuid4(), name="Salt", unit=MeasurementUnit.GRAM)
        milk = Ingredient(id=uuid4(), name="Milk", unit=MeasurementUnit.LITER)

        assert flour.unit == MeasurementUnit.KILOGRAM
        assert salt.unit == MeasurementUnit.GRAM
        assert milk.unit == MeasurementUnit.LITER

    def test_ingredient_equality_different_id(self):
        """Test ingredient inequality with different ID."""
        ing1 = Ingredient(id=uuid4(), name="Sugar", unit=MeasurementUnit.KILOGRAM)
        ing2 = Ingredient(id=uuid4(), name="Salt", unit=MeasurementUnit.GRAM)

        assert ing1 != ing2
