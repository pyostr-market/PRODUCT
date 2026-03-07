from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from src.cms.domain.events.base import DomainEvent
from src.cms.domain.events.cms_events import (
    PageBlockAddedEvent,
    PageBlockRemovedEvent,
    PageCreatedEvent,
    PagePublishedEvent,
    PageSlugChangedEvent,
    PageTitleChangedEvent,
    PageUnpublishedEvent,
)
from src.cms.domain.value_objects.cms_value_objects import PageSlug, PageTitle

if TYPE_CHECKING:
    from src.cms.domain.aggregates.page_block import PageBlockAggregate


class PageAggregate:
    """
    Aggregate Root для страницы (Page).

    Отвечает за:
    - Согласованность данных страницы
    - Управление блоками страницы
    - Публикацию доменных событий при изменениях
    """

    def __init__(
        self,
        slug: str,
        title: str,
        is_published: bool = False,
        page_id: Optional[int] = None,
        blocks: Optional[list['PageBlockAggregate']] = None,
    ):
        # Валидация через value objects
        self._slug = PageSlug(slug).value
        self._title = PageTitle(title).value
        self._id = page_id
        self._is_published = is_published
        self._blocks: list['PageBlockAggregate'] = sorted(
            blocks or [],
            key=lambda b: b.order
        )
        self._events: list[DomainEvent] = []

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def title(self) -> str:
        return self._title

    @property
    def is_published(self) -> bool:
        return self._is_published

    @property
    def blocks(self) -> list['PageBlockAggregate']:
        return self._blocks

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

    def publish(self):
        """Опубликовать страницу."""
        if not self._is_published:
            self._is_published = True
            self._record_event(PagePublishedEvent(
                page_id=self._id or 0,
                slug=self._slug,
            ))

    def unpublish(self):
        """Скрыть страницу."""
        if self._is_published:
            self._is_published = False
            self._record_event(PageUnpublishedEvent(
                page_id=self._id or 0,
                slug=self._slug,
            ))

    def change_title(self, new_title: str):
        """Изменить заголовок страницы."""
        old_title = self._title
        self._title = PageTitle(new_title).value
        self._record_event(PageTitleChangedEvent(
            page_id=self._id or 0,
            old_title=old_title,
            new_title=self._title,
        ))

    def change_slug(self, new_slug: str):
        """Изменить slug страницы."""
        old_slug = self._slug
        self._slug = PageSlug(new_slug).value
        self._record_event(PageSlugChangedEvent(
            page_id=self._id or 0,
            old_slug=old_slug,
            new_slug=self._slug,
        ))

    def add_block(
        self,
        block_type: str,
        data: dict,
        order: Optional[int] = None,
        block_id: Optional[int] = None,
    ) -> 'PageBlockAggregate':
        """Добавить блок к странице."""
        from src.cms.domain.aggregates.page_block import PageBlockAggregate
        from src.cms.domain.value_objects.page_block_data import PageBlockData

        # Если порядок не указан, добавляем в конец
        if order is None:
            order = max((b.order for b in self._blocks), default=0) + 1

        block = PageBlockAggregate(
            block_id=block_id,
            page_id=self._id or 0,
            block_type=block_type,
            order=order,
            data=PageBlockData(data=data),
        )

        self._blocks.append(block)
        self._blocks.sort(key=lambda b: b.order)

        self._record_event(PageBlockAddedEvent(
            page_id=self._id or 0,
            block_id=block_id or 0,
            block_type=block_type,
            order=order,
        ))

        return block

    def remove_block(self, block_id: int):
        """Удалить блок из страницы."""
        for i, block in enumerate(self._blocks):
            if block.id == block_id:
                self._blocks.pop(i)
                self._record_event(PageBlockRemovedEvent(
                    page_id=self._id or 0,
                    block_id=block_id,
                ))
                break

    def get_block(self, block_id: int) -> Optional['PageBlockAggregate']:
        """Получить блок по ID."""
        for block in self._blocks:
            if block.id == block_id:
                return block
        return None

    def reorder_blocks(self, block_order: list[tuple[int, int]]):
        """
        Переупорядочить блоки.

        Args:
            block_order: Список кортежей (block_id, new_order)
        """
        for block_id, new_order in block_order:
            block = self.get_block(block_id)
            if block:
                block.change_order(new_order)

        self._blocks.sort(key=lambda b: b.order)

    def _set_id(self, page_id: int):
        """Установить ID страницы (используется после создания)."""
        self._id = page_id
        # Обновляем page_id у всех блоков
        for block in self._blocks:
            block.page_id = page_id
