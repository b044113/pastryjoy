"""Ingredient entity."""
from dataclasses import dataclass

from ..value_objects.measurement_unit import MeasurementUnit
from .base import BaseEntity


@dataclass
class Ingredient(BaseEntity):
    """Ingredient entity."""

    name: str = ""
    unit: MeasurementUnit = MeasurementUnit.GRAM

    def __post_init__(self) -> None:
        """Validate ingredient data."""
        if not self.name:
            raise ValueError("Ingredient name is required")
        if not self.name.strip():
            raise ValueError("Ingredient name cannot be empty")
