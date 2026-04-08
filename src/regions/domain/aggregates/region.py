from typing import Optional

from src.regions.domain.events.base import DomainEvent
from src.regions.domain.events.region_events import (
    RegionNameChangedEvent,
    RegionParentChangedEvent,
)
from src.regions.domain.value_objects import RegionName


class RegionAggregate:
    """
    Aggregate Root для Region.

    Отвечает за:
    - Согласованность данных региона
    - Публикацию доменных событий при изменениях
    - Поддержание иерархии (родительский регион)
    """

    def __init__(
        self,
        name: str | RegionName,
        parent_id: Optional[int] = None,
        region_id: Optional[int] = None,
    ):
        # Используем Value Objects
        self._name_obj = name if isinstance(name, RegionName) else RegionName(name)

        self._id = region_id
        self._parent_id = parent_id
        self._events: list[DomainEvent] = []

    # -----------------------------
    # Identity
    # -----------------------------

    @property
    def id(self) -> Optional[int]:
        return self._id

    # -----------------------------
    # State
    # -----------------------------

    @property
    def name(self) -> str:
        return str(self._name_obj)

    @property
    def name_obj(self) -> RegionName:
        """Вернуть Value Object имени региона."""
        return self._name_obj

    @property
    def parent_id(self) -> Optional[int]:
        return self._parent_id

    # -----------------------------
    # Events
    # -----------------------------

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

    # -----------------------------
    # Behavior
    # -----------------------------

    def rename(self, new_name: str | RegionName):
        """Изменить имя региона."""
        old_name = self._name_obj
        new_name_obj = new_name if isinstance(new_name, RegionName) else RegionName(new_name)
        self._name_obj = new_name_obj
        self._record_event(RegionNameChangedEvent(
            region_id=self._id,
            old_name=str(old_name),
            new_name=str(new_name_obj),
        ))

    def change_parent(self, parent_id: Optional[int]):
        """Изменить родительский регион."""
        old_parent_id = self._parent_id
        self._parent_id = parent_id
        self._record_event(RegionParentChangedEvent(
            region_id=self._id,
            old_parent_id=old_parent_id,
            new_parent_id=parent_id,
        ))

    # -----------------------------
    # Internal
    # -----------------------------

    def _set_id(self, region_id: int):
        self._id = region_id

    def update(
        self,
        name: Optional[str],
        parent_id: Optional[int],
    ):
        """Обновить данные региона."""
        if name is not None:
            self.rename(name)

        if parent_id is not None:
            self.change_parent(parent_id)
