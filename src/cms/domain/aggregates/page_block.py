from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from src.cms.domain.events.base import DomainEvent
from src.cms.domain.events.cms_events import (
    PageBlockAddedEvent,
    PageBlockDataChangedEvent,
    PageBlockRemovedEvent,
    PageBlockReorderedEvent,
)
from src.cms.domain.value_objects.page_block_data import PageBlockData

if TYPE_CHECKING:
    from src.cms.domain.aggregates.page import PageAggregate


@dataclass
class PageBlockAggregate:
    """
    Aggregate для блока страницы.

    Отвечает за:
    - Целостность данных блока
    - Публикацию доменных событий при изменениях
    """

    block_id: Optional[int] = field(default=None)
    page_id: int = field(default=0)
    block_type: str = field(default="text")
    order: int = field(default=0)
    data: PageBlockData = field(default_factory=lambda: PageBlockData(data={}))
    _is_active: bool = field(default=True)
    page: Optional['PageAggregate'] = field(default=None)
    _events: list[DomainEvent] = field(default_factory=list)

    @property
    def id(self) -> Optional[int]:
        return self.block_id

    @property
    def type(self) -> str:
        return self.block_type

    @property
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool):
        self._is_active = value

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

    def change_data(self, new_data: dict[str, Any]):
        """Изменить данные блока."""
        old_data = self.data.data.copy()
        self.data = PageBlockData(data=new_data)
        self._record_event(PageBlockDataChangedEvent(
            page_id=self.page_id,
            block_id=self.block_id or 0,
            old_data=old_data,
            new_data=new_data,
        ))

    def change_order(self, new_order: int):
        """Изменить порядок блока."""
        self.order = new_order
        self._record_event(PageBlockReorderedEvent(
            page_id=self.page_id,
            block_id=self.block_id or 0,
            new_order=new_order,
        ))

    def deactivate(self):
        """Деактивировать блок."""
        self.is_active = False

    def activate(self):
        """Активировать блок."""
        self.is_active = True
