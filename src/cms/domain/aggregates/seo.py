from typing import Optional

from src.cms.domain.events.base import DomainEvent
from src.cms.domain.events.cms_events import SeoUpdatedEvent


class SeoAggregate:
    """
    Aggregate Root для SEO данных.

    Отвечает за:
    - Целостность SEO данных
    - Публикацию доменных событий при изменениях
    """

    def __init__(
        self,
        seo_id: Optional[int] = None,
        page_slug: str = "",
        title: Optional[str] = None,
        description: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        og_image_id: Optional[int] = None,
    ):
        """
        Инициализировать SEO агрегат.
        
        Args:
            seo_id: ID записи (None для новых)
            page_slug: Slug страницы
            title: Meta title
            description: Meta description
            keywords: Meta keywords
            og_image_id: ID OG изображения
        """
        self._seo_id = seo_id
        self._page_slug = page_slug
        self._title = title
        self._description = description
        self._keywords = keywords if keywords is not None else []
        self._og_image_id = og_image_id
        self._events: list[DomainEvent] = []

    @property
    def id(self) -> Optional[int]:
        return self._seo_id

    @property
    def page_slug(self) -> str:
        return self._page_slug

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def keywords(self) -> list[str]:
        return self._keywords

    @property
    def og_image_id(self) -> Optional[int]:
        return self._og_image_id

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
        """
        Обновить SEO данные.
        
        Args:
            title: Meta title
            description: Meta description
            keywords: Meta keywords
            og_image_id: ID OG изображения
        """
        if title is not None:
            self._title = title
        if description is not None:
            self._description = description
        if keywords is not None:
            self._keywords = keywords
        if og_image_id is not None:
            self._og_image_id = og_image_id

        self._record_event(SeoUpdatedEvent(
            seo_id=self._seo_id or 0,
            page_slug=self._page_slug,
        ))

    def get_meta_tags(self) -> dict[str, str]:
        """
        Получить meta теги для фронтенда.

        Returns:
            Словарь с meta тегами
        """
        meta = {}

        if self._title:
            meta['title'] = self._title

        if self._description:
            meta['description'] = self._description

        if self._keywords:
            meta['keywords'] = ', '.join(self._keywords)

        return meta

    def get_og_data(self) -> dict[str, Optional[int]]:
        """
        Получить данные для Open Graph.

        Returns:
            Словарь с OG данными
        """
        return {
            'og_image_id': self._og_image_id,
        }

    def _set_id(self, seo_id: int):
        """
        Установить ID (используется после создания).
        
        Args:
            seo_id: ID записи
        """
        self._seo_id = seo_id
