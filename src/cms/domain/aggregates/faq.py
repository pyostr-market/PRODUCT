from dataclasses import dataclass
from typing import Optional

from src.cms.domain.events.base import DomainEvent
from src.cms.domain.events.cms_events import (
    FaqCreatedEvent,
    FaqDeletedEvent,
    FaqUpdatedEvent,
)


@dataclass
class FaqAggregate:
    """
    Aggregate Root для FAQ.

    Отвечает за:
    - Целостность данных FAQ
    - Публикацию доменных событий при изменениях
    """

    faq_id: Optional[int]
    question: str
    answer: str
    category: Optional[str] = None
    order: int = 0
    is_active: bool = True
    _events: list[DomainEvent] = None

    def __post_init__(self):
        if self._events is None:
            self._events = []

    @property
    def id(self) -> Optional[int]:
        return self.faq_id

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
        question: Optional[str] = None,
        answer: Optional[str] = None,
        category: Optional[str] = None,
        order: Optional[int] = None,
    ):
        """Обновить данные FAQ."""
        old_question = self.question

        if question is not None:
            self.question = question
        if answer is not None:
            self.answer = answer
        if category is not None:
            self.category = category
        if order is not None:
            self.order = order

        if old_question != self.question:
            self._record_event(FaqUpdatedEvent(
                faq_id=self.faq_id or 0,
                old_question=old_question,
                new_question=self.question,
            ))

    def deactivate(self):
        """Деактивировать FAQ."""
        self.is_active = False

    def activate(self):
        """Активировать FAQ."""
        self.is_active = True

    def change_order(self, new_order: int):
        """Изменить порядок отображения."""
        self.order = new_order
