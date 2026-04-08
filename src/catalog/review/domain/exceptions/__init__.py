"""Исключения доменной модели отзывов."""

from src.core.exceptions.base import BaseServiceError


class ReviewNotFoundError(BaseServiceError):
    """Отзыв не найден."""

    def __init__(self, review_id: int):
        self.review_id = review_id
        super().__init__(
            message=f"Review with id {review_id} not found",
            code="review_not_found",
            status_code=404,
        )


class ProductNotFoundError(BaseServiceError):
    """Товар не найден."""

    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(
            message=f"Product with id {product_id} not found",
            code="product_not_found",
            status_code=404,
        )


class ReviewTextTooLongError(BaseServiceError):
    """Текст отзыва слишком длинный."""

    def __init__(self, max_length: int, actual_length: int):
        self.max_length = max_length
        self.actual_length = actual_length
        super().__init__(
            message=f"Review text must not exceed {max_length} characters, got {actual_length}",
            code="review_text_too_long",
            status_code=422,
        )


class InvalidRatingError(BaseServiceError):
    """Невалидный рейтинг."""

    def __init__(self, value: float):
        self.value = value
        super().__init__(
            message=f"Rating must be between 1 and 5, got {value}",
            code="invalid_rating",
            status_code=422,
        )


class ReviewNotOwnedError(BaseServiceError):
    """Пользователь не владеет отзывом."""

    def __init__(self, user_id: int, review_id: int):
        self.user_id = user_id
        self.review_id = review_id
        super().__init__(
            message=f"User {user_id} does not own review {review_id}",
            code="review_not_owned",
            status_code=403,
        )


class ReviewAlreadyExistsError(BaseServiceError):
    """Пользователь уже оставлял отзыв на этот товар."""

    def __init__(self, user_id: int, product_id: int):
        self.user_id = user_id
        self.product_id = product_id
        super().__init__(
            message=f"User {user_id} already has a review for product {product_id}",
            code="review_already_exists",
            status_code=409,
        )
