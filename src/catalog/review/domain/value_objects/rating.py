"""Value object для рейтинга отзыва (1-5)."""

from decimal import Decimal


class InvalidRatingError(ValueError):
    """Исключение для невалидного рейтинга."""


class RatingValue:
    """Value object для рейтинга (1.0 - 5.0)."""

    MIN_RATING = Decimal("1.0")
    MAX_RATING = Decimal("5.0")

    def __init__(self, value: Decimal | float | int):
        decimal_value = Decimal(str(value))
        if decimal_value < self.MIN_RATING or decimal_value > self.MAX_RATING:
            raise InvalidRatingError(
                f"Rating must be between {self.MIN_RATING} and {self.MAX_RATING}, got {decimal_value}"
            )
        self._value = decimal_value

    @property
    def value(self) -> Decimal:
        return self._value

    def to_float(self) -> float:
        return float(self._value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RatingValue):
            return self._value == other._value
        if isinstance(other, (int, float, Decimal)):
            return self._value == Decimal(str(other))
        return NotImplemented

    def __repr__(self) -> str:
        return f"RatingValue({self._value})"

    def __str__(self) -> str:
        return str(self._value)
