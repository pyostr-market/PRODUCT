from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from src.catalog.product.domain.exceptions import ProductNameTooShort


@dataclass
class ProductImageAggregate:
    object_key: str
    is_main: bool = False
    image_id: Optional[int] = None  # ID изображения в БД (для существующих изображений)


class ProductAttributeAggregate:

    def __init__(
        self,
        name: str,
        value: str = "",
        is_filterable: bool = False,
        attribute_id: Optional[int] = None,
    ):
        self._id = attribute_id
        self._name = name
        self._value = value
        self._is_filterable = is_filterable

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_filterable(self) -> bool:
        return self._is_filterable

    def _set_id(self, attribute_id: int):
        self._id = attribute_id

    def update(self, name: Optional[str], value: Optional[str], is_filterable: Optional[bool]):
        if name is not None:
            self._name = name
        if value is not None:
            self._value = value
        if is_filterable is not None:
            self._is_filterable = is_filterable


class ProductAggregate:

    def __init__(
        self,
        name: str,
        price: Decimal,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        product_type_id: Optional[int] = None,
        images: Optional[list[ProductImageAggregate]] = None,
        attributes: Optional[list[ProductAttributeAggregate]] = None,
        product_id: Optional[int] = None,
    ):
        if not name or len(name.strip()) < 2:
            raise ProductNameTooShort()

        self._id = product_id
        self._name = name.strip()
        self._description = description
        self._price = Decimal(price)
        self._category_id = category_id
        self._supplier_id = supplier_id
        self._product_type_id = product_type_id
        self._images = images or []
        self._attributes = attributes or []
        self._normalize_images_main_flag()

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
    def price(self) -> Decimal:
        return self._price

    @property
    def category_id(self) -> Optional[int]:
        return self._category_id

    @property
    def supplier_id(self) -> Optional[int]:
        return self._supplier_id

    @property
    def product_type_id(self) -> Optional[int]:
        return self._product_type_id

    @property
    def images(self) -> list[ProductImageAggregate]:
        return self._images

    @property
    def attributes(self) -> list[ProductAttributeAggregate]:
        return self._attributes

    def rename(self, new_name: str):
        if not new_name or len(new_name.strip()) < 2:
            raise ProductNameTooShort()
        self._name = new_name.strip()

    def change_description(self, description: Optional[str]):
        self._description = description

    def change_price(self, price: Decimal):
        self._price = Decimal(price)

    def change_category(self, category_id: Optional[int]):
        self._category_id = category_id

    def change_supplier(self, supplier_id: Optional[int]):
        self._supplier_id = supplier_id

    def change_product_type(self, product_type_id: Optional[int]):
        self._product_type_id = product_type_id

    def replace_images(self, images: list[ProductImageAggregate]):
        self._images = images
        self._normalize_images_main_flag()

    def replace_attributes(self, attributes: list[ProductAttributeAggregate]):
        self._attributes = attributes

    def update(
        self,
        name: Optional[str],
        description: Optional[str],
        price: Optional[Decimal],
        category_id: Optional[int],
        supplier_id: Optional[int],
        product_type_id: Optional[int],
    ):
        if name is not None:
            self.rename(name)

        if description is not None:
            self.change_description(description)

        if price is not None:
            self.change_price(price)

        if category_id is not None:
            self.change_category(category_id)

        if supplier_id is not None:
            self.change_supplier(supplier_id)

        if product_type_id is not None:
            self.change_product_type(product_type_id)

    def _set_id(self, product_id: int):
        self._id = product_id

    def _normalize_images_main_flag(self):
        if not self._images:
            return

        if not any(image.is_main for image in self._images):
            self._images[0].is_main = True

        main_found = False
        for image in self._images:
            if image.is_main and not main_found:
                main_found = True
                continue
            if image.is_main and main_found:
                image.is_main = False
