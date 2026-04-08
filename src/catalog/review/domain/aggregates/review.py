"""Aggregate Root для отзыва товара."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from src.catalog.review.domain.aggregates.review_image import ReviewImageAggregate
from src.catalog.review.domain.events.base import DomainEvent
from src.catalog.review.domain.events.review_events import (
    ReviewCreatedEvent,
    ReviewDeletedEvent,
    ReviewUpdatedEvent,
)
from src.catalog.review.domain.exceptions import (
    InvalidRatingError,
    ReviewNotOwnedError,
    ReviewTextTooLongError,
)
from src.catalog.review.domain.value_objects.rating import RatingValue
from src.catalog.review.domain.value_objects.review_text import ReviewText


@dataclass
class ReviewAggregate:
    """
    Aggregate Root для Review.

    Отвечает за:
    - Согласованность данных отзыва
    - Валидацию рейтинга (1-5) и текста
    - Публикацию доменных событий при изменениях
    - Проверку прав владельца при редактировании/удалении
    """

    MAX_TEXT_LENGTH = 5000

    def __init__(
        self,
        product_id: int,
        user_id: int,
        username: str,
        rating: Decimal | float | int,
        text: Optional[str] = None,
        images: Optional[list[ReviewImageAggregate]] = None,
        review_id: Optional[int] = None,
    ):
        self._id = review_id
        self._product_id = product_id
        self._user_id = user_id
        self._username = username.strip()
        self._rating_obj = self._validate_and_create_rating(rating)
        self._text_obj = ReviewText(text)
        self._images = images or []
        self._events: list[DomainEvent] = []

    # -----------------------------
    # Identity
    # -----------------------------

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def product_id(self) -> int:
        return self._product_id

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    # -----------------------------
    # State
    # -----------------------------

    @property
    def rating(self) -> Decimal:
        return self._rating_obj.value

    @property
    def rating_obj(self) -> RatingValue:
        return self._rating_obj

    @property
    def text(self) -> Optional[str]:
        return self._text_obj.text

    @property
    def images(self) -> list[ReviewImageAggregate]:
        return self._images

    # -----------------------------
    # Events
    # -----------------------------

    def get_events(self) -> list[DomainEvent]:
        """Вернуть все накопленные события и очистить очередь."""
        events = self._events.copy()
        self._events.clear()
        return events

    def clear_events(self):
        """Очистить очередь событий."""
        self._events.clear()

    def _record_event(self, event: DomainEvent):
        """Записать доменное событие."""
        self._events.append(event)

    # -----------------------------
    # Behavior
    # -----------------------------

    def update_rating(self, new_rating: Decimal | float | int):
        """Изменить рейтинг отзыва."""
        old_rating = self._rating_obj.value
        self._rating_obj = self._validate_and_create_rating(new_rating)
        self._record_event(ReviewUpdatedEvent(
            review_id=self._id,
            product_id=self._product_id,
            user_id=self._user_id,
            old_rating=old_rating,
            new_rating=self._rating_obj.value,
            old_text=self._text_obj.text,
            new_text=self._text_obj.text,
        ))

    def update_text(self, new_text: Optional[str]):
        """Изменить текст отзыва."""
        old_text = self._text_obj.text
        self._text_obj = ReviewText(new_text)
        self._record_event(ReviewUpdatedEvent(
            review_id=self._id,
            product_id=self._product_id,
            user_id=self._user_id,
            old_rating=self._rating_obj.value,
            new_rating=self._rating_obj.value,
            old_text=old_text,
            new_text=self._text_obj.text,
        ))

    def update(
        self,
        rating: Optional[Decimal | float | int] = None,
        text: Optional[str] = None,
    ):
        """Обновить данные отзыва."""
        if rating is not None:
            self.update_rating(rating)
        if text is not None:
            self.update_text(text)

    def set_images(self, images: list[ReviewImageAggregate]):
        """Заменить все изображения отзыва."""
        self._images = images

    def add_image(self, image: ReviewImageAggregate):
        """Добавить изображение к отзыву."""
        self._images.append(image)

    def remove_image_by_upload_id(self, upload_id: int):
        """Удалить изображение по upload_id."""
        for i, image in enumerate(self._images):
            if image.upload_id == upload_id:
                self._images.pop(i)
                break

    # -----------------------------
    # Ownership check
    # -----------------------------

    def check_ownership(self, user_id: int):
        """Проверить, что пользователь владеет отзывом."""
        if self._user_id != user_id:
            raise ReviewNotOwnedError(user_id=user_id, review_id=self._id)

    # -----------------------------
    # Internal
    # -----------------------------

    def _set_id(self, review_id: int):
        self._id = review_id

    def _validate_and_create_rating(self, rating: Decimal | float | int) -> RatingValue:
        """Валидировать и создать RatingValue."""
        try:
            return RatingValue(rating)
        except ValueError:
            raise InvalidRatingError(value=float(rating))

    def _capture_state(self) -> dict:
        """Зафиксировать текущее состояние агрегата."""
        return {
            "product_id": self._product_id,
            "user_id": self._user_id,
            "username": self._username,
            "rating": str(self._rating_obj.value),
            "text": self._text_obj.text,
            "image_upload_ids": [img.upload_id for img in self._images],
        }
