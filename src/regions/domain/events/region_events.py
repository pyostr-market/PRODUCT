import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class RegionCreatedEvent:
    """Событие: регион создан."""

    region_id: int
    name: str
    parent_id: Optional[int] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RegionUpdatedEvent:
    """Событие: регион обновлен."""

    region_id: int
    changed_fields: dict
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RegionDeletedEvent:
    """Событие: регион удален."""

    region_id: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RegionNameChangedEvent:
    """Событие: имя региона изменено."""

    region_id: int
    old_name: str
    new_name: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RegionParentChangedEvent:
    """Событие: родительский регион изменен."""

    region_id: int
    old_parent_id: Optional[int]
    new_parent_id: Optional[int]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
