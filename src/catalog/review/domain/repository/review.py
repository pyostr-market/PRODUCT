"""Интерфейс репозитория для отзывов."""

from abc import ABC, abstractmethod
from typing import Optional, Tuple

from src.catalog.review.domain.aggregates.review import ReviewAggregate


class ReviewRepository(ABC):
    """Абстрактный репозиторий для ReviewAggregate."""

    @abstractmethod
    async def get(self, review_id: int) -> Optional[ReviewAggregate]:
        """Получить отзыв по ID."""

    @abstractmethod
    async def get_by_product_id(
        self,
        product_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[list[ReviewAggregate], int]:
        """Получить список отзывов для товара с пагинацией."""

    @abstractmethod
    async def create(self, aggregate: ReviewAggregate) -> ReviewAggregate:
        """Создать отзыв."""

    @abstractmethod
    async def update(self, aggregate: ReviewAggregate) -> ReviewAggregate:
        """Обновить отзыв."""

    @abstractmethod
    async def delete(self, review_id: int) -> bool:
        """Удалить отзыв."""

    @abstractmethod
    async def get_average_rating_for_product(self, product_id: int) -> Optional[float]:
        """Получить средний рейтинг для товара."""

    @abstractmethod
    async def get_user_review_for_product(
        self,
        user_id: int,
        product_id: int,
    ) -> Optional[ReviewAggregate]:
        """Получить отзыв пользователя для конкретного товара."""
