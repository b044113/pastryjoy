"""Recipe entity."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from ..value_objects.money import Money
from .base import BaseEntity
from .recipe_ingredient import RecipeIngredient


@dataclass
class Recipe(BaseEntity):
    """Recipe entity."""

    name: str = ""
    ingredients: List[RecipeIngredient] = field(default_factory=list)
    instructions: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate recipe data."""
        if not self.name:
            raise ValueError("Recipe name is required")
        if not self.name.strip():
            raise ValueError("Recipe name cannot be empty")

    def add_ingredient(
        self, ingredient_id: UUID, quantity: Decimal
    ) -> "Recipe":
        """Add an ingredient to the recipe."""
        recipe_ingredient = RecipeIngredient(
            recipe_id=self.id,
            ingredient_id=ingredient_id,
            quantity=quantity
        )
        self.ingredients.append(recipe_ingredient)
        return self

    def update_ingredient_quantity(self, ingredient_id: UUID, quantity: Decimal) -> "Recipe":
        """Update the quantity of an existing ingredient in the recipe."""
        for ingredient in self.ingredients:
            if ingredient.ingredient_id == ingredient_id:
                ingredient.quantity = quantity
                return self
        raise ValueError(f"Ingredient {ingredient_id} not found in recipe")

    def remove_ingredient(self, ingredient_id: UUID) -> "Recipe":
        """Remove an ingredient from the recipe."""
        self.ingredients = [
            ing for ing in self.ingredients
            if ing.ingredient_id != ingredient_id
        ]
        return self

    def calculate_cost(
        self,
        ingredient_costs: dict[UUID, Money]
    ) -> Money:
        """Calculate total cost of recipe based on ingredient costs."""
        if not self.ingredients:
            return Money(Decimal("0"))

        total = Money(Decimal("0"))
        for recipe_ingredient in self.ingredients:
            ingredient_cost = ingredient_costs.get(recipe_ingredient.ingredient_id)
            if ingredient_cost:
                total = total + (ingredient_cost * recipe_ingredient.quantity)

        return total
