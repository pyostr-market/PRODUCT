from dataclasses import dataclass
from typing import Optional

from src.cms.domain.events.base import DomainEvent
from src.cms.domain.events.cms_events import FeatureFlagChangedEvent


@dataclass
class FeatureFlagAggregate:
    """
    Aggregate Root для feature flag.

    Отвечает за:
    - Целостность данных feature flag
    - Публикацию доменных событий при изменениях
    """

    flag_id: Optional[int]
    key: str
    enabled: bool
    description: Optional[str] = None
    _events: list[DomainEvent] = None

    def __post_init__(self):
        if self._events is None:
            self._events = []

    @property
    def id(self) -> Optional[int]:
        return self.flag_id

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

    def enable(self):
        """Включить feature flag."""
        if not self.enabled:
            old_enabled = self.enabled
            self.enabled = True
            self._record_event(FeatureFlagChangedEvent(
                flag_id=self.flag_id or 0,
                key=self.key,
                old_enabled=old_enabled,
                new_enabled=True,
            ))

    def disable(self):
        """Выключить feature flag."""
        if self.enabled:
            old_enabled = self.enabled
            self.enabled = False
            self._record_event(FeatureFlagChangedEvent(
                flag_id=self.flag_id or 0,
                key=self.key,
                old_enabled=old_enabled,
                new_enabled=False,
            ))

    def toggle(self):
        """Переключить состояние feature flag."""
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def update_description(self, description: str):
        """Обновить описание."""
        self.description = description
