import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class SupplierCreatedEvent:
    """Событие: поставщик создан."""

    supplier_id: int
    name: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SupplierUpdatedEvent:
    """Событие: поставщик обновлен."""

    supplier_id: int
    changed_fields: dict
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SupplierDeletedEvent:
    """Событие: поставщик удален."""

    supplier_id: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SupplierNameChangedEvent:
    """Событие: имя поставщика изменено."""

    supplier_id: int
    old_name: str
    new_name: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SupplierContactEmailChangedEvent:
    """Событие: контактный email изменен."""

    supplier_id: int
    old_email: Optional[str]
    new_email: Optional[str]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SupplierPhoneChangedEvent:
    """Событие: телефон изменен."""

    supplier_id: int
    old_phone: Optional[str]
    new_phone: Optional[str]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
