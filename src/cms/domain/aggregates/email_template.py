from typing import Optional

from src.cms.domain.events.base import DomainEvent
from src.cms.domain.events.cms_events import (
    EmailTemplateCreatedEvent,
    EmailTemplateUpdatedEvent,
)


class EmailTemplateAggregate:
    """
    Aggregate Root для email шаблона.

    Отвечает за:
    - Целостность данных шаблона
    - Публикацию доменных событий при изменениях
    """

    def __init__(
        self,
        template_id: Optional[int] = None,
        key: str = "",
        subject: str = "",
        body_html: str = "",
        body_text: Optional[str] = None,
        variables: Optional[list[str]] = None,
        is_active: bool = True,
    ):
        """
        Инициализировать email шаблон.
        
        Args:
            template_id: ID шаблона (None для новых)
            key: Ключ шаблона
            subject: Тема письма
            body_html: HTML тело
            body_text: Текстовое тело
            variables: Переменные шаблона
            is_active: Активен ли
        """
        self._template_id = template_id
        self._key = key
        self._subject = subject
        self._body_html = body_html
        self._body_text = body_text
        self._variables = variables if variables is not None else []
        self._is_active = is_active
        self._events: list[DomainEvent] = []

    @property
    def id(self) -> Optional[int]:
        return self._template_id

    @property
    def key(self) -> str:
        return self._key

    @property
    def subject(self) -> str:
        return self._subject

    @property
    def body_html(self) -> str:
        return self._body_html

    @property
    def body_text(self) -> Optional[str]:
        return self._body_text

    @property
    def variables(self) -> list[str]:
        return self._variables

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
        subject: Optional[str] = None,
        body_html: Optional[str] = None,
        body_text: Optional[str] = None,
        variables: Optional[list[str]] = None,
    ):
        """
        Обновить данные шаблона.
        
        Args:
            subject: Тема письма
            body_html: HTML тело
            body_text: Текстовое тело
            variables: Переменные шаблона
        """
        if subject is not None:
            self._subject = subject
        if body_html is not None:
            self._body_html = body_html
        if body_text is not None:
            self._body_text = body_text
        if variables is not None:
            self._variables = variables

    def deactivate(self):
        """Деактивировать шаблон."""
        self._is_active = False

    def activate(self):
        """Активировать шаблон."""
        self._is_active = True

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
            replace_vars(self._subject),
            replace_vars(self._body_html),
            replace_vars(self._body_text) if self._body_text else "",
        )

    def _set_id(self, template_id: int):
        """
        Установить ID (используется после создания).
        
        Args:
            template_id: ID шаблона
        """
        self._template_id = template_id
