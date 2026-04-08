"""Доменные события для модуля отзывов."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from src.catalog.review.domain.events.base import DomainEvent


@dataclass
class ReviewCreatedEvent(DomainEvent):
    """Событие: отзыв создан."""

    review_id: int
    product_id: int
    user_id: int
    username: str
    rating: Decimal
    text: Optional[str]
    image_upload_ids: list[int]


@dataclass
class ReviewUpdatedEvent(DomainEvent):
    """Событие: отзыв обновлён."""

    review_id: int
    product_id: int
    user_id: int
    old_rating: Optional[Decimal]
    new_rating: Optional[Decimal]
    old_text: Optional[str]
    new_text: Optional[str]


@dataclass
class ReviewDeletedEvent(DomainEvent):
    """Событие: отзыв удалён."""

    review_id: int
    product_id: int
    user_id: int
