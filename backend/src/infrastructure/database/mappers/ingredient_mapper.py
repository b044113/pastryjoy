"""Ingredient mapper between database model and domain entity."""
from decimal import Decimal

from src.domain.entities.ingredient import Ingredient
from src.domain.entities.ingredient_cost import IngredientCost
from src.domain.value_objects.measurement_unit import MeasurementUnit
from src.domain.value_objects.money import Money
from src.infrastructure.database.models.ingredient import IngredientModel
from src.infrastructure.database.models.ingredient_cost import IngredientCostModel


class IngredientMapper:
    """Maps between IngredientModel and Ingredient entity."""

    @staticmethod
    def to_entity(model: IngredientModel) -> Ingredient:
        """Convert database model to domain entity."""
        return Ingredient(
            id=model.id,
            name=model.name,
            unit=MeasurementUnit(model.unit),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Ingredient) -> IngredientModel:
        """Convert domain entity to database model."""
        return IngredientModel(
            id=entity.id,
            name=entity.name,
            unit=entity.unit.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class IngredientCostMapper:
    """Maps between IngredientCostModel and IngredientCost entity."""

    @staticmethod
    def to_entity(model: IngredientCostModel) -> IngredientCost:
        """Convert database model to domain entity."""
        return IngredientCost(
            id=model.id,
            ingredient_id=model.ingredient_id,
            cost_per_unit=Money(
                amount=Decimal(str(model.cost_amount)),
                currency=model.cost_currency
            ),
            effective_date=model.effective_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: IngredientCost) -> IngredientCostModel:
        """Convert domain entity to database model."""
        return IngredientCostModel(
            id=entity.id,
            ingredient_id=entity.ingredient_id,
            cost_amount=entity.cost_per_unit.amount,
            cost_currency=entity.cost_per_unit.currency,
            effective_date=entity.effective_date,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
