from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class EventMessage:
    type: str
    method: str
    app: str
    data: Any
    entity: str
    entity_id: int | None = None
    version: int = 1
    event_id: str = field(default_factory=lambda: str(uuid4()))
    emitted_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "version": self.version,
            "type": self.type,
            "method": self.method,
            "app": self.app,
            "entity": self.entity,
            "entity_id": self.entity_id,
            "emitted_at": self.emitted_at,
            "data": self.data,
        }


def build_event(
    *,
    event_type: str,
    method: str,
    app: str,
    entity: str,
    entity_id: int | None,
    data: Any,
) -> dict[str, Any]:
    return EventMessage(
        type=event_type,
        method=method,
        app=app,
        entity=entity,
        entity_id=entity_id,
        data=data,
    ).to_dict()
