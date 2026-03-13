from typing import TYPE_CHECKING, Optional

from src.catalog.manufacturer.domain.events.base import DomainEvent
from src.catalog.manufacturer.domain.events.manufacturer_events import (
    ManufacturerDescriptionChangedEvent,
    ManufacturerNameChangedEvent,
)
from src.catalog.manufacturer.domain.exceptions import ManufacturerNameTooShort

if TYPE_CHECKING:
    from src.catalog.manufacturer.domain.aggregates.manufacturer import (
        ManufacturerAggregate,
    )


class ManufacturerImageAggregate:
    """Агрегат изображения производителя."""

    def __init__(
        self,
        upload_id: int,
        object_key: Optional[str] = None,
    ):
        self.upload_id = upload_id
        self.object_key = object_key


class ManufacturerAggregate:
    """
    Aggregate Root для Manufacturer.

    Отвечает за:
    - Согласованность данных производителя
    - Публикацию доменных событий при изменениях
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        manufacturer_id: Optional[int] = None,
        image: Optional[ManufacturerImageAggregate] = None,
    ):
        if not name or len(name.strip()) < 2:
            raise ManufacturerNameTooShort()

        self._id = manufacturer_id
        self._name = name.strip()
        self._description = description
        self._image = image
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
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def image(self) -> Optional[ManufacturerImageAggregate]:
        return self._image

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

    def rename(self, new_name: str):
        """Изменить имя производителя."""
        if not new_name or len(new_name.strip()) < 2:
            raise ManufacturerNameTooShort()

        old_name = self._name
        self._name = new_name.strip()
        self._record_event(ManufacturerNameChangedEvent(
            manufacturer_id=self._id,
            old_name=old_name,
            new_name=self._name,
        ))

    def change_description(self, description: Optional[str]):
        """Изменить описание производителя."""
        old_description = self._description
        self._description = description
        self._record_event(ManufacturerDescriptionChangedEvent(
            manufacturer_id=self._id,
            old_description=old_description,
            new_description=description,
        ))

    def set_image(self, image: ManufacturerImageAggregate):
        """Установить изображение производителя."""
        self._image = image

    def remove_image(self):
        """Удалить изображение производителя."""
        self._image = None

    # -----------------------------
    # Internal
    # -----------------------------

    def _set_id(self, manufacturer_id: int):
        self._id = manufacturer_id

    def update(
        self,
        name: Optional[str],
        description: Optional[str],
    ):
        """Обновить данные производителя."""
        if name is not None:
            self.rename(name)

        if description is not None:
            self.change_description(description)