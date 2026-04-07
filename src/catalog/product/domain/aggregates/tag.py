from dataclasses import dataclass, field
from typing import Optional

from src.catalog.product.domain.exceptions import TagInvalidName, TagNameTooShort


# ==================== Domain Events ====================

@dataclass
class DomainEvent:
    """Base class for domain events."""
    pass


@dataclass
class TagCreatedEvent(DomainEvent):
    tag_id: int
    name: str
    description: Optional[str]
    color: Optional[str]


@dataclass
class TagUpdatedEvent(DomainEvent):
    tag_id: int
    old_name: str
    new_name: str
    old_description: Optional[str]
    new_description: Optional[str]
    old_color: Optional[str]
    new_color: Optional[str]


@dataclass
class TagDeletedEvent(DomainEvent):
    tag_id: int
    name: str


# ==================== Aggregate ====================

@dataclass
class TagAggregate:
    """Доменный агрегат тега."""
    _tag_id: int = 0
    _name: str = ""
    _description: Optional[str] = None
    _color: Optional[str] = None
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    @property
    def tag_id(self) -> int:
        return self._tag_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def color(self) -> Optional[str]:
        return self._color

    def __post_init__(self):
        """Валидация при создании."""
        if self._name:
            self._validate_name(self._name)

    @staticmethod
    def _validate_name(name: str) -> None:
        """Проверить корректность имени тега."""
        if not name or len(name.strip()) < 2:
            raise TagNameTooShort()
        if len(name) > 100:
            raise TagInvalidName(details={"reason": "name_too_long", "max_length": 100})

    def _record_event(self, event: DomainEvent) -> None:
        """Записать доменное событие."""
        self._events.append(event)

    def get_events(self) -> list[DomainEvent]:
        """Получить все доменные события и очистить список."""
        events = list(self._events)
        self._events.clear()
        return events

    def _set_id(self, tag_id: int) -> None:
        """Установить ID (вызывается репозиторием после persist)."""
        object.__setattr__(self, '_tag_id', tag_id)

    # ==================== Business Methods ====================

    def rename(self, new_name: str) -> None:
        """Переименовать тег."""
        self._validate_name(new_name)
        old_name = self._name
        self._name = new_name.strip()
        self._record_event(TagUpdatedEvent(
            tag_id=self._tag_id,
            old_name=old_name,
            new_name=self._name,
            old_description=self._description,
            new_description=self._description,
            old_color=self._color,
            new_color=self._color,
        ))

    def change_description(self, new_description: Optional[str]) -> None:
        """Изменить описание тега."""
        if new_description and len(new_description) > 500:
            raise TagInvalidName(details={"reason": "description_too_long", "max_length": 500})
        old_description = self._description
        self._description = new_description
        self._record_event(TagUpdatedEvent(
            tag_id=self._tag_id,
            old_name=self._name,
            new_name=self._name,
            old_description=old_description,
            new_description=self._description,
            old_color=self._color,
            new_color=self._color,
        ))

    def change_color(self, new_color: Optional[str]) -> None:
        """Изменить цвет тега."""
        if new_color and len(new_color) > 7:
            raise TagInvalidName(details={"reason": "color_too_long", "max_length": 7})
        old_color = self._color
        self._color = new_color
        self._record_event(TagUpdatedEvent(
            tag_id=self._tag_id,
            old_name=self._name,
            new_name=self._name,
            old_description=self._description,
            new_description=self._description,
            old_color=old_color,
            new_color=self._color,
        ))

    def update(self, name: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None) -> None:
        """Batch-обновование тегов через фасад."""
        if name is not None:
            self.rename(name)
        if description is not None:
            self.change_description(description)
        if color is not None:
            self.change_color(color)
