from dataclasses import dataclass
from typing import Optional

from src.cms.domain.events.base import DomainEvent
from src.cms.domain.events.cms_events import SeoUpdatedEvent


@dataclass
class SeoAggregate:
    """
    Aggregate Root для SEO данных.

    Отвечает за:
    - Целостность SEO данных
    - Публикацию доменных событий при изменениях
    """

    seo_id: Optional[int]
    page_slug: str
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[list[str]] = None
    og_image_id: Optional[int] = None
    _events: list[DomainEvent] = None

    def __post_init__(self):
        if self._events is None:
            self._events = []
        if self.keywords is None:
            self.keywords = []

    @property
    def id(self) -> Optional[int]:
        return self.seo_id

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

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        og_image_id: Optional[int] = None,
    ):
        """Обновить SEO данные."""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if keywords is not None:
            self.keywords = keywords
        if og_image_id is not None:
            self.og_image_id = og_image_id

        self._record_event(SeoUpdatedEvent(
            seo_id=self.seo_id or 0,
            page_slug=self.page_slug,
        ))

    def get_meta_tags(self) -> dict[str, str]:
        """
        Получить meta теги для фронтенда.

        Returns:
            Словарь с meta тегами
        """
        meta = {}

        if self.title:
            meta['title'] = self.title

        if self.description:
            meta['description'] = self.description

        if self.keywords:
            meta['keywords'] = ', '.join(self.keywords)

        return meta

    def get_og_data(self) -> dict[str, Optional[int]]:
        """
        Получить данные для Open Graph.

        Returns:
            Словарь с OG данными
        """
        return {
            'og_image_id': self.og_image_id,
        }
