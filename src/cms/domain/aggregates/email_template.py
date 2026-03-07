from dataclasses import dataclass
from typing import Optional

from src.cms.domain.events.base import DomainEvent
from src.cms.domain.events.cms_events import (
    EmailTemplateCreatedEvent,
    EmailTemplateUpdatedEvent,
)


@dataclass
class EmailTemplateAggregate:
    """
    Aggregate Root для email шаблона.

    Отвечает за:
    - Целостность данных шаблона
    - Публикацию доменных событий при изменениях
    """

    template_id: Optional[int]
    key: str
    subject: str
    body_html: str
    body_text: Optional[str] = None
    variables: Optional[list[str]] = None
    is_active: bool = True
    _events: list[DomainEvent] = None

    def __post_init__(self):
        if self._events is None:
            self._events = []
        if self.variables is None:
            self.variables = []

    @property
    def id(self) -> Optional[int]:
        return self.template_id

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
        subject: Optional[str] = None,
        body_html: Optional[str] = None,
        body_text: Optional[str] = None,
        variables: Optional[list[str]] = None,
    ):
        """Обновить данные шаблона."""
        if subject is not None:
            self.subject = subject
        if body_html is not None:
            self.body_html = body_html
        if body_text is not None:
            self.body_text = body_text
        if variables is not None:
            self.variables = variables

    def deactivate(self):
        """Деактивировать шаблон."""
        self.is_active = False

    def activate(self):
        """Активировать шаблон."""
        self.is_active = True

    def render(self, context: dict[str, str]) -> tuple[str, str, str]:
        """
        Рендеринг шаблона с подстановкой переменных.

        Returns:
            Кортеж (subject, body_html, body_text)
        """
        def replace_vars(text: str) -> str:
            if not text:
                return text
            for key, value in context.items():
                text = text.replace(f"{{{{{key}}}}}", value)
            return text

        return (
            replace_vars(self.subject),
            replace_vars(self.body_html),
            replace_vars(self.body_text) if self.body_text else "",
        )
