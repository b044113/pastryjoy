"""Product entity."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from ..value_objects.money import Money
from .base import BaseEntity


@dataclass
class ProductRecipe:
    """Product recipe relationship with quantity."""

    recipe_id: UUID
    quantity: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        """Validate product recipe data."""
        if not isinstance(self.quantity, Decimal):
            object.__setattr__(self, "quantity", Decimal(str(self.quantity)))
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")


@dataclass
class Product(BaseEntity):
    """Product entity."""

    name: str = ""
    recipes: List[ProductRecipe] = field(default_factory=list)
    image_url: Optional[str] = None
    fixed_costs: Money = field(default_factory=lambda: Money(Decimal("0")))
    variable_costs_percentage: Decimal = Decimal("0")
    profit_margin_percentage: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        """Validate product data."""
        if not self.name:
            raise ValueError("Product name is required")
        if not self.name.strip():
            raise ValueError("Product name cannot be empty")
        if not isinstance(self.variable_costs_percentage, Decimal):
            object.__setattr__(
                self,
                "variable_costs_percentage",
                Decimal(str(self.variable_costs_percentage))
            )
        if not isinstance(self.profit_margin_percentage, Decimal):
            object.__setattr__(
                self,
                "profit_margin_percentage",
                Decimal(str(self.profit_margin_percentage))
            )
        if self.variable_costs_percentage < 0 or self.variable_costs_percentage > 100:
            raise ValueError("Variable costs percentage must be between 0 and 100")
        if self.profit_margin_percentage < 0:
            raise ValueError("Profit margin percentage cannot be negative")

    def add_recipe(self, recipe_id: UUID, quantity: Decimal = Decimal("1")) -> "Product":
        """Add a recipe to the product."""
        product_recipe = ProductRecipe(recipe_id=recipe_id, quantity=quantity)
        self.recipes.append(product_recipe)
        return self

    def remove_recipe(self, recipe_id: UUID) -> "Product":
        """Remove a recipe from the product."""
        self.recipes = [rec for rec in self.recipes if rec.recipe_id != recipe_id]
        return self

    def calculate_cost(self, recipe_costs: Dict[UUID, Money]) -> Money:
        """Calculate total product cost.

        Cost = (Recipe Costs + Fixed Costs) * (1 + Variable Costs %) * (1 + Profit Margin %)
        """
        if not self.recipes:
            base_cost = self.fixed_costs
        else:
            recipe_total = Money(Decimal("0"))
            for product_recipe in self.recipes:
                recipe_cost = recipe_costs.get(product_recipe.recipe_id)
                if recipe_cost:
                    recipe_total = recipe_total + (recipe_cost * product_recipe.quantity)

            base_cost = recipe_total + self.fixed_costs

        # Apply variable costs percentage
        variable_multiplier = Decimal("1") + (self.variable_costs_percentage / Decimal("100"))
        cost_with_variable = base_cost * variable_multiplier

        # Apply profit margin percentage
        profit_multiplier = Decimal("1") + (self.profit_margin_percentage / Decimal("100"))
        final_cost = cost_with_variable * profit_multiplier

        return final_cost
