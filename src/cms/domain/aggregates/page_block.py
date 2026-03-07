from typing import TYPE_CHECKING, Any, Optional

from src.cms.domain.events.base import DomainEvent
from src.cms.domain.events.cms_events import (
    PageBlockDataChangedEvent,
    PageBlockReorderedEvent,
)
from src.cms.domain.value_objects.page_block_data import PageBlockData

if TYPE_CHECKING:
    from src.cms.domain.aggregates.page import PageAggregate


class PageBlockAggregate:
    """
    Aggregate для блока страницы.
    
    Является частью PageAggregate и не может существовать отдельно.
    
    Отвечает за:
    - Целостность данных блока
    - Публикацию доменных событий при изменениях
    """

    def __init__(
        self,
        block_id: Optional[int] = None,
        page_id: int = 0,
        block_type: str = "text",
        order: int = 0,
        data: Optional[dict[str, Any]] = None,
        is_active: bool = True,
    ):
        """
        Инициализировать блок страницы.
        
        Args:
            block_id: ID блока (None для новых блоков)
            page_id: ID родительской страницы
            block_type: Тип блока
            order: Порядок отображения
            data: Данные блока
            is_active: Активен ли блок
        """
        self._block_id = block_id
        self._page_id = page_id
        self._block_type = block_type
        self._order = order
        self._data = PageBlockData(data=data or {})
        self._is_active = is_active
        self._page: Optional['PageAggregate'] = None
        self._events: list[DomainEvent] = []

    @property
    def id(self) -> Optional[int]:
        return self._block_id

    @property
    def page_id(self) -> int:
        return self._page_id

    @property
    def block_type(self) -> str:
        return self._block_type

    @property
    def order(self) -> int:
        return self._order

    @property
    def data(self) -> PageBlockData:
        return self._data

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def page(self) -> Optional['PageAggregate']:
        return self._page

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
        """
        Изменить данные блока.
        
        Args:
            new_data: Новые данные блока
        """
        old_data = self._data.data.copy()
        self._data = PageBlockData(data=new_data)
        self._record_event(PageBlockDataChangedEvent(
            page_id=self._page_id,
            block_id=self._block_id or 0,
            old_data=old_data,
            new_data=new_data,
        ))

    def change_order(self, new_order: int):
        """
        Изменить порядок блока.
        
        Args:
            new_order: Новый порядок
        """
        self._order = new_order
        self._record_event(PageBlockReorderedEvent(
            page_id=self._page_id,
            block_id=self._block_id or 0,
            new_order=new_order,
        ))

    def deactivate(self):
        """Деактивировать блок."""
        self._is_active = False

    def activate(self):
        """Активировать блок."""
        self._is_active = True

    def set_page_context(self, page: 'PageAggregate', page_id: int):
        """
        Установить контекст родительской страницы.
        
        Используется агрегатом Page для связи с блоками.
        
        Args:
            page: Родительский агрегат Page
            page_id: ID страницы
        """
        self._page = page
        self._page_id = page_id

    def _set_id(self, block_id: int):
        """
        Установить ID блока (используется после создания).
        
        Args:
            block_id: ID блока
        """
        self._block_id = block_id

    def _set_page_id(self, page_id: int):
        """
        Установить ID страницы (используется после создания страницы).
        
        Args:
            page_id: ID страницы
        """
        self._page_id = page_id
