"""Unit tests for value objects."""
from decimal import Decimal

import pytest

from src.domain.value_objects.measurement_unit import MeasurementUnit
from src.domain.value_objects.money import Money
from src.domain.value_objects.user_role import UserRole


class TestMoney:
    """Test Money value object."""

    def test_create_money(self):
        """Test creating money value object."""
        money = Money(Decimal("10.50"), "USD")

        assert money.amount == Decimal("10.50")
        assert money.currency == "USD"

    def test_money_add(self):
        """Test adding two money values."""
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("5.50"), "USD")

        result = money1 + money2

        assert result.amount == Decimal("15.50")
        assert result.currency == "USD"

    def test_money_subtract(self):
        """Test subtracting two money values."""
        money1 = Money(Decimal("20.00"), "USD")
        money2 = Money(Decimal("7.50"), "USD")

        result = money1 - money2

        assert result.amount == Decimal("12.50")
        assert result.currency == "USD"

    def test_money_multiply(self):
        """Test multiplying money by a number."""
        money = Money(Decimal("5.00"), "USD")

        result = money * 3

        assert result.amount == Decimal("15.00")
        assert result.currency == "USD"

    def test_money_multiply_decimal(self):
        """Test multiplying money by a decimal."""
        money = Money(Decimal("10.00"), "USD")

        result = money * Decimal("1.5")

        assert result.amount == Decimal("15.00")
        assert result.currency == "USD"

    def test_money_divide(self):
        """Test dividing money by a number."""
        money = Money(Decimal("10.00"), "USD")

        result = money / 2

        assert result.amount == Decimal("5.00")
        assert result.currency == "USD"

    def test_money_equality(self):
        """Test money equality."""
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("10.00"), "USD")
        money3 = Money(Decimal("10.00"), "EUR")
        money4 = Money(Decimal("5.00"), "USD")

        assert money1 == money2
        assert money1 != money3  # Different currency
        assert money1 != money4  # Different amount

    def test_money_add_different_currency_raises_error(self):
        """Test adding money with different currencies raises error."""
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("5.00"), "EUR")

        with pytest.raises(ValueError, match="Cannot add money with different currencies"):
            money1 + money2

    def test_money_subtract_different_currency_raises_error(self):
        """Test subtracting money with different currencies raises error."""
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("5.00"), "EUR")

        with pytest.raises(ValueError, match="Cannot subtract money with different currencies"):
            money1 - money2

    def test_money_subtract_resulting_negative_raises_error(self):
        """Test subtracting resulting in negative raises error."""
        money1 = Money(Decimal("5.00"), "USD")
        money2 = Money(Decimal("10.00"), "USD")

        with pytest.raises(ValueError, match="Subtraction would result in negative money"):
            money1 - money2

    def test_money_negative_amount_raises_error(self):
        """Test creating money with negative amount raises error."""
        with pytest.raises(ValueError, match="Money amount cannot be negative"):
            Money(Decimal("-10.00"), "USD")

    def test_money_string_representation(self):
        """Test money string representation."""
        money = Money(Decimal("10.50"), "USD")

        assert str(money) == "USD 10.50"

    def test_money_repr(self):
        """Test money repr."""
        money = Money(Decimal("10.50"), "USD")

        assert repr(money) == "Money(amount=10.50, currency='USD')"

    def test_money_divide_by_zero_raises_error(self):
        """Test dividing money by zero raises error."""
        money = Money(Decimal("10.00"), "USD")

        with pytest.raises(ValueError, match="Cannot divide money by zero"):
            money / 0


class TestMeasurementUnit:
    """Test MeasurementUnit value object."""

    def test_measurement_units_exist(self):
        """Test that all measurement units are defined."""
        assert MeasurementUnit.KILOGRAM == "kg"
        assert MeasurementUnit.GRAM == "g"
        assert MeasurementUnit.LITER == "l"
        assert MeasurementUnit.MILLILITER == "ml"
        assert MeasurementUnit.UNIT == "unit"
        assert MeasurementUnit.TABLESPOON == "tbsp"
        assert MeasurementUnit.TEASPOON == "tsp"
        assert MeasurementUnit.CUP == "cup"

    def test_measurement_unit_to_string(self):
        """Test converting measurement unit to string."""
        assert str(MeasurementUnit.KILOGRAM) == "kg"
        assert str(MeasurementUnit.LITER) == "l"
        assert str(MeasurementUnit.GRAM) == "g"

    def test_measurement_unit_from_string(self):
        """Test getting measurement unit from string."""
        unit = MeasurementUnit("kg")
        assert unit == MeasurementUnit.KILOGRAM

        unit2 = MeasurementUnit("l")
        assert unit2 == MeasurementUnit.LITER

    def test_measurement_unit_invalid_raises_error(self):
        """Test invalid measurement unit raises error."""
        with pytest.raises(ValueError):
            MeasurementUnit("invalid_unit")

    def test_measurement_unit_equality(self):
        """Test measurement unit equality."""
        unit1 = MeasurementUnit.KILOGRAM
        unit2 = MeasurementUnit("kg")
        unit3 = MeasurementUnit.GRAM

        assert unit1 == unit2
        assert unit1 != unit3


class TestUserRole:
    """Test UserRole value object."""

    def test_user_roles_exist(self):
        """Test that all user roles are defined."""
        assert UserRole.ADMIN == "admin"
        assert UserRole.USER == "user"

    def test_user_role_to_string(self):
        """Test converting user role to string."""
        assert str(UserRole.ADMIN) == "admin"
        assert str(UserRole.USER) == "user"

    def test_user_role_from_string(self):
        """Test getting user role from string."""
        role = UserRole("admin")
        assert role == UserRole.ADMIN

        role2 = UserRole("user")
        assert role2 == UserRole.USER

    def test_user_role_invalid_raises_error(self):
        """Test invalid user role raises error."""
        with pytest.raises(ValueError):
            UserRole("superuser")

    def test_admin_can_manage_products(self):
        """Test admin can manage products."""
        assert UserRole.ADMIN.can_manage_products is True
        assert UserRole.USER.can_manage_products is False

    def test_admin_can_manage_recipes(self):
        """Test admin can manage recipes."""
        assert UserRole.ADMIN.can_manage_recipes is True
        assert UserRole.USER.can_manage_recipes is False

    def test_admin_can_manage_ingredients(self):
        """Test admin can manage ingredients."""
        assert UserRole.ADMIN.can_manage_ingredients is True
        assert UserRole.USER.can_manage_ingredients is False

    def test_both_roles_can_create_orders(self):
        """Test both roles can create orders."""
        assert UserRole.ADMIN.can_create_orders is True
        assert UserRole.USER.can_create_orders is True

    def test_admin_can_manage_users(self):
        """Test only admin can manage users."""
        assert UserRole.ADMIN.can_manage_users is True
        assert UserRole.USER.can_manage_users is False

    def test_user_role_equality(self):
        """Test user role equality."""
        role1 = UserRole.ADMIN
        role2 = UserRole("admin")
        role3 = UserRole.USER

        assert role1 == role2
        assert role1 != role3
