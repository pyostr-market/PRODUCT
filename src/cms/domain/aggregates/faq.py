from typing import Optional

from src.cms.domain.events.base import DomainEvent
from src.cms.domain.events.cms_events import (
    FaqCreatedEvent,
    FaqDeletedEvent,
    FaqUpdatedEvent,
)


class FaqAggregate:
    """
    Aggregate Root для FAQ.

    Отвечает за:
    - Целостность данных FAQ
    - Публикацию доменных событий при изменениях
    """

    def __init__(
        self,
        faq_id: Optional[int] = None,
        question: str = "",
        answer: str = "",
        category: Optional[str] = None,
        order: int = 0,
        is_active: bool = True,
    ):
        """
        Инициализировать FAQ агрегат.
        
        Args:
            faq_id: ID записи (None для новых)
            question: Вопрос
            answer: Ответ
            category: Категория
            order: Порядок отображения
            is_active: Активен ли
        """
        self._faq_id = faq_id
        self._question = question
        self._answer = answer
        self._category = category
        self._order = order
        self._is_active = is_active
        self._events: list[DomainEvent] = []

    @property
    def id(self) -> Optional[int]:
        return self._faq_id

    @property
    def question(self) -> str:
        return self._question

    @property
    def answer(self) -> str:
        return self._answer

    @property
    def category(self) -> Optional[str]:
        return self._category

    @property
    def order(self) -> int:
        return self._order

    @property
    def is_active(self) -> bool:
        return self._is_active

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
        """
        Обновить данные FAQ.
        
        Args:
            question: Новый вопрос
            answer: Новый ответ
            category: Новая категория
            order: Новый порядок
        """
        old_question = self._question

        if question is not None:
            self._question = question
        if answer is not None:
            self._answer = answer
        if category is not None:
            self._category = category
        if order is not None:
            self._order = order

        if old_question != self._question:
            self._record_event(FaqUpdatedEvent(
                faq_id=self._faq_id or 0,
                old_question=old_question,
                new_question=self._question,
            ))

    def deactivate(self):
        """Деактивировать FAQ."""
        self._is_active = False

    def activate(self):
        """Активировать FAQ."""
        self._is_active = True

    def change_order(self, new_order: int):
        """Изменить порядок отображения."""
        self._order = new_order

    def _set_id(self, faq_id: int):
        """
        Установить ID (используется после создания).
        
        Args:
            faq_id: ID записи
        """
        self._faq_id = faq_id
