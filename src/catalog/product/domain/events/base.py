import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class DomainEvent:
    """Базовый класс доменного события."""
    
    event_id: str = field(init=False)
    occurred_on: datetime = field(init=False)
    event_type: str = field(init=False)
    aggregate_id: Any = field(init=False)
    
    def __post_init__(self):
        object.__setattr__(self, 'event_id', str(uuid.uuid4()))
        object.__setattr__(self, 'occurred_on', datetime.now(timezone.utc))
        object.__setattr__(self, 'event_type', self.__class__.__name__)
