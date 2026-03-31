from dataclasses import dataclass, field
from typing import List, Optional

from src.catalog.product.domain.events.base import DomainEvent


@dataclass
class ProductRelationCreatedEvent(DomainEvent):
    """Событие: связь товара создана."""
    relation_id: int
    product_id: int
    related_product_id: int
    relation_type: str
    sort_order: int


@dataclass
class ProductRelationUpdatedEvent(DomainEvent):
    """Событие: связь товара обновлена."""
    relation_id: int
    changed_fields: dict


@dataclass
class ProductRelationDeletedEvent(DomainEvent):
    """Событие: связь товара удалена."""
    relation_id: int


@dataclass
class ProductRelationAggregate:
    """
    Aggregate Root для ProductRelation.

    Отвечает за:
    - Согласованность данных связи между товарами
    - Публикацию доменных событий при изменениях
    """

    def __init__(
        self,
        product_id: int,
        related_product_id: int,
        relation_type: str,
        sort_order: int = 0,
        relation_id: Optional[int] = None,
    ):
        self._validate_not_same_product(product_id, related_product_id)
        
        self._id = relation_id
        self._product_id = product_id
        self._related_product_id = related_product_id
        self._relation_type = relation_type
        self._sort_order = sort_order
        self._events: List[DomainEvent] = []

    @staticmethod
    def _validate_not_same_product(product_id: int, related_product_id: int):
        """Проверка: связь товара с самим собой не допускается."""
        if product_id == related_product_id:
            raise ValueError("Связь товара с самим собой не допускается")

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def product_id(self) -> int:
        return self._product_id

    @property
    def related_product_id(self) -> int:
        return self._related_product_id

    @property
    def relation_type(self) -> str:
        return self._relation_type

    @property
    def sort_order(self) -> int:
        return self._sort_order

    def get_events(self) -> List[DomainEvent]:
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

    def update(
        self,
        relation_type: Optional[str] = None,
        sort_order: Optional[int] = None,
    ):
        """Обновить параметры связи."""
        changed_fields = {}

        if relation_type is not None and relation_type != self._relation_type:
            old_value = self._relation_type
            self._relation_type = relation_type
            changed_fields["relation_type"] = {
                "old": old_value,
                "new": relation_type,
            }

        if sort_order is not None and sort_order != self._sort_order:
            old_value = self._sort_order
            self._sort_order = sort_order
            changed_fields["sort_order"] = {
                "old": old_value,
                "new": sort_order,
            }

        if changed_fields and self._id is not None:
            self._record_event(ProductRelationUpdatedEvent(
                relation_id=self._id,
                changed_fields=changed_fields,
            ))

    def _set_id(self, relation_id: int):
        """Установить ID связи (используется при создании)."""
        self._id = relation_id
