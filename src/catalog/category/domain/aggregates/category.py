from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from src.catalog.category.domain.exceptions import CategoryNameTooShort
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)

if TYPE_CHECKING:
    from src.catalog.category.domain.aggregates.category import CategoryAggregate


@dataclass
class CategoryImageAggregate:
    upload_id: int  # ID из UploadHistory
    ordering: int
    object_key: str | None = None  # Ключ объекта в S3 (file_path из UploadHistory)


class CategoryAggregate:

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        manufacturer_id: Optional[int] = None,
        images: Optional[list[CategoryImageAggregate]] = None,
        category_id: Optional[int] = None,
        parent: Optional['CategoryAggregate'] = None,
        manufacturer: Optional[ManufacturerAggregate] = None,
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
    def manufacturer(self) -> Optional[ManufacturerAggregate]:
        return self._manufacturer

    def rename(self, new_name: str):
        if not new_name or len(new_name.strip()) < 2:
            raise CategoryNameTooShort()

        self._name = new_name.strip()

    def change_description(self, description: Optional[str]):
        self._description = description

    def change_parent(self, parent_id: Optional[int]):
        self._parent_id = parent_id

    def change_manufacturer(self, manufacturer_id: Optional[int]):
        self._manufacturer_id = manufacturer_id

    def replace_images(self, images: list[CategoryImageAggregate]):
        self._images = sorted(images, key=lambda i: i.ordering)

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
