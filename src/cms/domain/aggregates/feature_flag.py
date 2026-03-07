from typing import Optional

from src.cms.domain.events.base import DomainEvent
from src.cms.domain.events.cms_events import FeatureFlagChangedEvent


class FeatureFlagAggregate:
    """
    Aggregate Root для feature flag.

    Отвечает за:
    - Целостность данных feature flag
    - Публикацию доменных событий при изменениях
    """

    def __init__(
        self,
        flag_id: Optional[int] = None,
        key: str = "",
        enabled: bool = False,
        description: Optional[str] = None,
    ):
        """
        Инициализировать feature flag.
        
        Args:
            flag_id: ID записи (None для новых)
            key: Ключ флага
            enabled: Включен ли
            description: Описание
        """
        self._flag_id = flag_id
        self._key = key
        self._enabled = enabled
        self._description = description
        self._events: list[DomainEvent] = []

    @property
    def id(self) -> Optional[int]:
        return self._flag_id

    @property
    def key(self) -> str:
        return self._key

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def description(self) -> Optional[str]:
        return self._description

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
        if not self._enabled:
            old_enabled = self._enabled
            self._enabled = True
            self._record_event(FeatureFlagChangedEvent(
                flag_id=self._flag_id or 0,
                key=self._key,
                old_enabled=old_enabled,
                new_enabled=True,
            ))

    def disable(self):
        """Выключить feature flag."""
        if self._enabled:
            old_enabled = self._enabled
            self._enabled = False
            self._record_event(FeatureFlagChangedEvent(
                flag_id=self._flag_id or 0,
                key=self._key,
                old_enabled=old_enabled,
                new_enabled=False,
            ))

    def toggle(self):
        """Переключить состояние feature flag."""
        if self._enabled:
            self.disable()
        else:
            self.enable()

    def update_description(self, description: str):
        """Обновить описание."""
        self._description = description

    def _set_id(self, flag_id: int):
        """
        Установить ID (используется после создания).
        
        Args:
            flag_id: ID записи
        """
        self._flag_id = flag_id
