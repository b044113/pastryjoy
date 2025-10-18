"""Product mapper between database model and domain entity."""
from decimal import Decimal

from src.domain.entities.product import Product, ProductRecipe
from src.domain.value_objects.money import Money
from src.infrastructure.database.models.product import ProductModel, ProductRecipeModel


class ProductRecipeMapper:
    """Maps between ProductRecipeModel and ProductRecipe entity."""

    @staticmethod
    def to_entity(model: ProductRecipeModel) -> ProductRecipe:
        """Convert database model to domain entity."""
        return ProductRecipe(
            recipe_id=model.recipe_id,
            quantity=Decimal(str(model.quantity)),
        )

    @staticmethod
    def to_model(entity: ProductRecipe, product_id) -> ProductRecipeModel:
        """Convert domain entity to database model."""
        return ProductRecipeModel(
            product_id=product_id,
            recipe_id=entity.recipe_id,
            quantity=entity.quantity,
        )


class ProductMapper:
    """Maps between ProductModel and Product entity."""

    @staticmethod
    def to_entity(model: ProductModel) -> Product:
        """Convert database model to domain entity."""
        recipes = [ProductRecipeMapper.to_entity(rec) for rec in model.recipes]

        return Product(
            id=model.id,
            name=model.name,
            recipes=recipes,
            image_url=model.image_url,
            fixed_costs=Money(
                amount=Decimal(str(model.fixed_costs_amount)),
                currency=model.fixed_costs_currency,
            ),
            variable_costs_percentage=Decimal(str(model.variable_costs_percentage)),
            profit_margin_percentage=Decimal(str(model.profit_margin_percentage)),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Product) -> ProductModel:
        """Convert domain entity to database model."""
        model = ProductModel(
            id=entity.id,
            name=entity.name,
            image_url=entity.image_url,
            fixed_costs_amount=entity.fixed_costs.amount,
            fixed_costs_currency=entity.fixed_costs.currency,
            variable_costs_percentage=entity.variable_costs_percentage,
            profit_margin_percentage=entity.profit_margin_percentage,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

        # Add recipes
        model.recipes = [
            ProductRecipeMapper.to_model(rec, entity.id) for rec in entity.recipes
        ]

        return model
