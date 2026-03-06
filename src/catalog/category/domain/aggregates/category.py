from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from src.catalog.category.domain.events.base import DomainEvent
from src.catalog.category.domain.events.category_events import (
    CategoryNameChangedEvent,
    CategoryDescriptionChangedEvent,
    CategoryParentChangedEvent,
    CategoryManufacturerChangedEvent,
    CategoryImageAddedEvent,
    CategoryImageRemovedEvent,
    CategoryImagesReplacedEvent,
)
from src.catalog.category.domain.exceptions import CategoryNameTooShort

if TYPE_CHECKING:
    from src.catalog.category.domain.aggregates.category import CategoryAggregate
    from src.catalog.manufacturer.domain.aggregates.manufacturer import (
        ManufacturerAggregate,
    )


@dataclass
class CategoryImageAggregate:
    upload_id: int  # ID из UploadHistory
    ordering: int
    object_key: str | None = None  # Ключ объекта в S3 (file_path из UploadHistory)


class CategoryAggregate:
    """
    Aggregate Root для Category.

    Отвечает за:
    - Согласованность данных категории
    - Публикацию доменных событий при изменениях
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        manufacturer_id: Optional[int] = None,
        images: Optional[list[CategoryImageAggregate]] = None,
        category_id: Optional[int] = None,
        parent: Optional['CategoryAggregate'] = None,
        manufacturer: Optional['ManufacturerAggregate'] = None,
    ):
        if not name or len(name.strip()) < 2:
            raise CategoryNameTooShort()

        self._id = category_id
        self._name = name.strip()
        self._description = description
        self._parent_id = parent_id
        self._manufacturer_id = manufacturer_id
        self._images = sorted(images or [], key=lambda i: i.ordering)
        self._parent = parent
        self._manufacturer = manufacturer
        self._events: list[DomainEvent] = []

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def parent_id(self) -> Optional[int]:
        return self._parent_id

    @property
    def manufacturer_id(self) -> Optional[int]:
        return self._manufacturer_id

    @property
    def images(self) -> list[CategoryImageAggregate]:
        return self._images

    @property
    def parent(self) -> Optional['CategoryAggregate']:
        return self._parent

    @property
    def manufacturer(self) -> Optional['ManufacturerAggregate']:
        return self._manufacturer

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

    def rename(self, new_name: str):
        if not new_name or len(new_name.strip()) < 2:
            raise CategoryNameTooShort()

        old_name = self._name
        self._name = new_name.strip()
        self._record_event(CategoryNameChangedEvent(
            category_id=self._id,
            old_name=old_name,
            new_name=self._name,
        ))

    def change_description(self, description: Optional[str]):
        old_description = self._description
        self._description = description
        self._record_event(CategoryDescriptionChangedEvent(
            category_id=self._id,
            old_description=old_description,
            new_description=description,
        ))

    def change_parent(self, parent_id: Optional[int]):
        old_parent_id = self._parent_id
        self._parent_id = parent_id
        self._record_event(CategoryParentChangedEvent(
            category_id=self._id,
            old_parent_id=old_parent_id,
            new_parent_id=parent_id,
        ))

    def change_manufacturer(self, manufacturer_id: Optional[int]):
        old_manufacturer_id = self._manufacturer_id
        self._manufacturer_id = manufacturer_id
        self._record_event(CategoryManufacturerChangedEvent(
            category_id=self._id,
            old_manufacturer_id=old_manufacturer_id,
            new_manufacturer_id=manufacturer_id,
        ))

    def add_image(self, image: CategoryImageAggregate):
        """Добавить изображение к категории."""
        self._images.append(image)
        self._record_event(CategoryImageAddedEvent(
            category_id=self._id,
            upload_id=image.upload_id,
            ordering=image.ordering,
        ))

    def remove_image_by_upload_id(self, upload_id: int):
        """Удалить изображение по upload_id."""
        for i, image in enumerate(self._images):
            if image.upload_id == upload_id:
                self._images.pop(i)
                self._record_event(CategoryImageRemovedEvent(
                    category_id=self._id,
                    upload_id=upload_id,
                ))
                break

    def replace_images(self, images: list[CategoryImageAggregate]):
        """Заменить все изображения."""
        old_image_ids = [img.upload_id for img in self._images]
        new_image_ids = [img.upload_id for img in images]
        
        self._images = sorted(images, key=lambda i: i.ordering)
        self._record_event(CategoryImagesReplacedEvent(
            category_id=self._id,
            old_image_ids=old_image_ids,
            new_image_ids=new_image_ids,
        ))

    def _set_id(self, category_id: int):
        self._id = category_id

    def update(
        self,
        name: Optional[str],
        description: Optional[str],
        parent_id: Optional[int],
        manufacturer_id: Optional[int],
    ):
        if name is not None:
            self.rename(name)

        if description is not None:
            self.change_description(description)

        if parent_id is not None:
            self.change_parent(parent_id)

        if manufacturer_id is not None:
            self.change_manufacturer(manufacturer_id)
