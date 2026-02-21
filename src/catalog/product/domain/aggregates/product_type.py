from dataclasses import dataclass
from typing import Optional

from src.catalog.product.domain.exceptions import ProductTypeInvalidName


@dataclass
class ProductTypeAggregate:
    name: str
    parent_id: Optional[int] = None
    product_type_id: Optional[int] = None

    def __post_init__(self):
        if not self.name or len(self.name.strip()) < 2:
            raise ProductTypeInvalidName()
        self._name = self.name.strip()

    @property
    def id(self) -> Optional[int]:
        return self.product_type_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent_id(self) -> Optional[int]:
        return self._parent_id

    @parent_id.setter
    def parent_id(self, value: Optional[int]):
        self._parent_id = value

    def update(self, name: Optional[str], parent_id: Optional[int]):
        if name is not None:
            if not name or len(name.strip()) < 2:
                raise ProductTypeInvalidName()
            self._name = name.strip()
        if parent_id is not None:
            self._parent_id = parent_id

    def _set_id(self, product_type_id: int):
        self.product_type_id = product_type_id
