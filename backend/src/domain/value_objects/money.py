"""Money value object."""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Represents a monetary value."""

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        """Validate money value."""
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if not self.currency:
            raise ValueError("Currency code is required")

    def __add__(self, other: "Money") -> "Money":
        """Add two money values."""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        """Subtract two money values."""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Subtraction would result in negative money")
        return Money(result, self.currency)

    def __mul__(self, multiplier: float | int | Decimal) -> "Money":
        """Multiply money by a number."""
        if not isinstance(multiplier, (int, float, Decimal)):
            raise TypeError("Can only multiply Money by a number")
        return Money(self.amount * Decimal(str(multiplier)), self.currency)

    def __rmul__(self, multiplier: float | int | Decimal) -> "Money":
        """Multiply money by a number (reverse)."""
        return self.__mul__(multiplier)

    def __truediv__(self, divisor: float | int | Decimal) -> "Money":
        """Divide money by a number."""
        if not isinstance(divisor, (int, float, Decimal)):
            raise TypeError("Can only divide Money by a number")
        if divisor == 0:
            raise ValueError("Cannot divide money by zero")
        return Money(self.amount / Decimal(str(divisor)), self.currency)

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.currency} {self.amount:.2f}"

    def __repr__(self) -> str:
        """Return representation."""
        return f"Money(amount={self.amount}, currency='{self.currency}')"
