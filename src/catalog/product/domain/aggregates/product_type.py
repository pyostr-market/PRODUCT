from dataclasses import dataclass, field
from typing import Optional

from src.catalog.product.domain.aggregates.product_type_image import ProductTypeImageAggregate
from src.catalog.product.domain.exceptions import ProductTypeInvalidName


@dataclass
class ProductTypeAggregate:
    _name: str = field(init=False)
    _parent_id: Optional[int] = field(init=False, default=None)
    _image: Optional[ProductTypeImageAggregate] = field(init=False, default=None)
    name: str
    parent_id: Optional[int] = None
    product_type_id: Optional[int] = None
    parent: Optional["ProductTypeAggregate"] = None

    def __post_init__(self):
        if not self.name or len(self.name.strip()) < 2:
            raise ProductTypeInvalidName()
        self._name = self.name.strip()
        self._parent_id = self.parent_id
        # Обрабатываем image, если передан
        if hasattr(self, 'image') and self.image is not None:
            self._image = self.image

    @property
    def id(self) -> Optional[int]:
        return self.product_type_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or len(value.strip()) < 2:
            raise ProductTypeInvalidName()
        self._name = value.strip()

    @property
    def parent_id(self) -> Optional[int]:
        return self._parent_id

    @parent_id.setter
    def parent_id(self, value: Optional[int]):
        self._parent_id = value

    @property
    def image(self) -> Optional[ProductTypeImageAggregate]:
        return self._image

    @image.setter
    def image(self, value: Optional[ProductTypeImageAggregate]):
        self._image = value

    def update(self, name: Optional[str], parent_id: Optional[int]):
        if name is not None:
            if not name or len(name.strip()) < 2:
                raise ProductTypeInvalidName()
            self._name = name.strip()
        if parent_id is not None:
            self._parent_id = parent_id

    def set_image(self, image: ProductTypeImageAggregate):
        """Установить изображение типа продукта."""
        self._image = image

    def remove_image(self):
        """Удалить изображение типа продукта."""
        self._image = None

    def _set_id(self, product_type_id: int):
        self.product_type_id = product_type_id
