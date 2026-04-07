from dataclasses import dataclass, field
from typing import Optional

from src.catalog.product.domain.exceptions import ProductTagAlreadyExists


# ==================== Domain Events ====================

@dataclass
class DomainEvent:
    """Base class for domain events."""
    pass


@dataclass
class ProductTagLinkedEvent(DomainEvent):
    product_id: int
    tag_id: int


@dataclass
class ProductTagUnlinkedEvent(DomainEvent):
    product_id: int
    tag_id: int


# ==================== Aggregate ====================

@dataclass
class ProductTagAggregate:
    """Доменный агрегат связи товара с тегом."""
    _id: int = 0
    _product_id: int = 0
    _tag_id: int = 0
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    @property
    def id(self) -> int:
        return self._id

    @property
    def product_id(self) -> int:
        return self._product_id

    @property
    def tag_id(self) -> int:
        return self._tag_id

    def __post_init__(self):
        """Валидация при создании."""
        if self._product_id <= 0:
            raise ValueError("product_id должен быть положительным числом")
        if self._tag_id <= 0:
            raise ValueError("tag_id должен быть положительным числом")

    def _record_event(self, event: DomainEvent) -> None:
        """Записать доменное событие."""
        self._events.append(event)

    def get_events(self) -> list[DomainEvent]:
        """Получить все доменные события и очистить список."""
        events = list(self._events)
        self._events.clear()
        return events

    def _set_id(self, link_id: int) -> None:
        """Установить ID (вызывается репозиторием после persist)."""
        object.__setattr__(self, '_id', link_id)

    @staticmethod
    def validate_not_exists(
        product_id: int,
        tag_id: int,
        already_exists: bool,
    ) -> None:
        """Проверить, что связь ещё не существует."""
        if already_exists:
            raise ProductTagAlreadyExists(
                details={
                    "product_id": product_id,
                    "tag_id": tag_id,
                }
            )
