"""Measurement unit value object."""
from enum import Enum


class MeasurementUnit(str, Enum):
    """Units of measurement for ingredients."""

    KILOGRAM = "kg"
    GRAM = "g"
    LITER = "l"
    MILLILITER = "ml"
    UNIT = "unit"
    TABLESPOON = "tbsp"
    TEASPOON = "tsp"
    CUP = "cup"

    def __str__(self) -> str:
        """Return string representation."""
        return self.value
