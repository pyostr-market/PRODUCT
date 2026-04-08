"""Value object для текста отзыва."""


class EmptyReviewTextError(ValueError):
    """Исключение для пустого текста отзыва."""


class ReviewText:
    """Value object для текста отзыва."""

    MAX_LENGTH = 5000

    def __init__(self, text: str | None):
        if text is not None:
            text = text.strip()
            if len(text) > self.MAX_LENGTH:
                raise ValueError(f"Review text must not exceed {self.MAX_LENGTH} characters, got {len(text)}")
        self._text = text

    @property
    def text(self) -> str | None:
        return self._text

    def __str__(self) -> str:
        return self._text or ""

    def __repr__(self) -> str:
        return f"ReviewText({self._text!r})"
