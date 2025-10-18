"""Recipe mapper between database model and domain entity."""
from decimal import Decimal

from src.domain.entities.recipe import Recipe
from src.domain.entities.recipe_ingredient import RecipeIngredient
from src.infrastructure.database.models.recipe import RecipeIngredientModel, RecipeModel


class RecipeIngredientMapper:
    """Maps between RecipeIngredientModel and RecipeIngredient entity."""

    @staticmethod
    def to_entity(model: RecipeIngredientModel) -> RecipeIngredient:
        """Convert database model to domain entity."""
        return RecipeIngredient(
            id=model.id,
            recipe_id=model.recipe_id,
            ingredient_id=model.ingredient_id,
            quantity=Decimal(str(model.quantity)),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: RecipeIngredient) -> RecipeIngredientModel:
        """Convert domain entity to database model."""
        return RecipeIngredientModel(
            id=entity.id,
            recipe_id=entity.recipe_id,
            ingredient_id=entity.ingredient_id,
            quantity=entity.quantity,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class RecipeMapper:
    """Maps between RecipeModel and Recipe entity."""

    @staticmethod
    def to_entity(model: RecipeModel) -> Recipe:
        """Convert database model to domain entity."""
        ingredients = [
            RecipeIngredientMapper.to_entity(ing) for ing in model.ingredients
        ]

        return Recipe(
            id=model.id,
            name=model.name,
            ingredients=ingredients,
            instructions=model.instructions,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Recipe) -> RecipeModel:
        """Convert domain entity to database model."""
        model = RecipeModel(
            id=entity.id,
            name=entity.name,
            instructions=entity.instructions,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

        # Add ingredients
        model.ingredients = [
            RecipeIngredientMapper.to_model(ing) for ing in entity.ingredients
        ]

        return model
