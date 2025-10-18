"""Cost calculation domain service."""
from decimal import Decimal
from typing import Dict
from uuid import UUID

from ..entities.product import Product
from ..entities.recipe import Recipe
from ..repositories.ingredient_cost_repository import IIngredientCostRepository
from ..value_objects.money import Money


class CostCalculationService:
    """Service for calculating costs across the domain."""

    def __init__(self, ingredient_cost_repository: IIngredientCostRepository):
        """Initialize cost calculation service."""
        self._ingredient_cost_repo = ingredient_cost_repository

    async def calculate_recipe_cost(self, recipe: Recipe) -> Money:
        """Calculate the total cost of a recipe based on current ingredient costs."""
        if not recipe.ingredients:
            return Money(Decimal("0"))

        ingredient_costs: Dict[UUID, Money] = {}
        for recipe_ingredient in recipe.ingredients:
            cost = await self._ingredient_cost_repo.get_current_cost(
                recipe_ingredient.ingredient_id
            )
            if cost:
                ingredient_costs[recipe_ingredient.ingredient_id] = cost.cost_per_unit

        return recipe.calculate_cost(ingredient_costs)

    async def calculate_product_cost(
        self,
        product: Product,
        recipe_costs: Dict[UUID, Money]
    ) -> Money:
        """Calculate the total cost of a product including all markups."""
        return product.calculate_cost(recipe_costs)

    async def calculate_product_cost_with_recipe_lookup(
        self,
        product: Product,
        recipes: Dict[UUID, Recipe]
    ) -> Money:
        """Calculate product cost by looking up and calculating recipe costs."""
        recipe_costs: Dict[UUID, Money] = {}

        for product_recipe in product.recipes:
            recipe = recipes.get(product_recipe.recipe_id)
            if recipe:
                recipe_cost = await self.calculate_recipe_cost(recipe)
                recipe_costs[product_recipe.recipe_id] = recipe_cost

        return product.calculate_cost(recipe_costs)
