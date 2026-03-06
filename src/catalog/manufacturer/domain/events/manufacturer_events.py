from dataclasses import dataclass
from typing import Any, Optional

from src.catalog.manufacturer.domain.events.base import DomainEvent


@dataclass
class ManufacturerCreatedEvent(DomainEvent):
    """Событие: производитель создан."""

    manufacturer_id: int
    name: str
    description: Optional[str]


@dataclass
class ManufacturerUpdatedEvent(DomainEvent):
    """Событие: производитель обновлен."""

    manufacturer_id: int
    changed_fields: dict[str, Any]


@dataclass
class ManufacturerDeletedEvent(DomainEvent):
    """Событие: производитель удален."""

    manufacturer_id: int


@dataclass
class ManufacturerNameChangedEvent(DomainEvent):
    """Событие: имя производителя изменено."""

    manufacturer_id: int
    old_name: str
    new_name: str


@dataclass
class ManufacturerDescriptionChangedEvent(DomainEvent):
    """Событие: описание производителя изменено."""

    manufacturer_id: int
    old_description: Optional[str]
    new_description: Optional[str]
