from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from src.catalog.product.domain.events.product_events import (
    DomainEvent,
    PriceChangedEvent,
    ProductAttributeAddedEvent,
    ProductAttributeRemovedEvent,
    ProductImageAddedEvent,
    ProductImageRemovedEvent,
    ProductNameChangedEvent,
)
from src.catalog.product.domain.value_objects import Money, ProductName

if TYPE_CHECKING:
    from src.catalog.category.domain.aggregates.category import CategoryAggregate
    from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate


class ProductImageOperation:
    """Операция с изображением для применения в агрегате."""
    
    def __init__(
        self,
        action: str,
        upload_id: int,
        is_main: Optional[bool] = None,
        ordering: Optional[int] = None,
        object_key: Optional[str] = None,
    ):
        self.action = action
        self.upload_id = upload_id
        self.is_main = is_main
        self.ordering = ordering
        self.object_key = object_key


@dataclass
class ProductImageAggregate:
    upload_id: int  # ID из UploadHistory
    is_main: bool = False
    ordering: int = 0
    object_key: Optional[str] = None  # Ключ объекта в хранилище


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
    """
    Aggregate Root для Product.

    Отвечает за:
    - Согласованность данных продукта
    - Публикацию доменных событий при изменениях
    """

    def __init__(
        self,
        name: str | ProductName,
        price: Decimal | Money,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        images: Optional[list[ProductImageAggregate]] = None,
        attributes: Optional[list[ProductAttributeAggregate]] = None,
        product_id: Optional[int] = None,
        category: Optional['CategoryAggregate'] = None,
        supplier: Optional['SupplierAggregate'] = None,
    ):
        # Используем Value Objects для name и price
        self._name_obj = name if isinstance(name, ProductName) else ProductName(name)
        self._price_obj = price if isinstance(price, Money) else Money.from_decimal(price)

        self._id = product_id
        self._description = description
        self._category_id = category_id
        self._supplier_id = supplier_id
        self._images = images or []
        self._attributes = attributes or []
        self._category = category
        self._supplier = supplier
        self._events: list[DomainEvent] = []
        self._normalize_images_main_flag()

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def name(self) -> str:
        return str(self._name_obj)

    @property
    def name_obj(self) -> ProductName:
        """Вернуть Value Object имени продукта."""
        return self._name_obj

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def price(self) -> Decimal:
        return self._price_obj.to_decimal()

    @property
    def price_obj(self) -> Money:
        """Вернуть Value Object цены."""
        return self._price_obj

    @property
    def category_id(self) -> Optional[int]:
        return self._category_id

    @property
    def supplier_id(self) -> Optional[int]:
        return self._supplier_id

    @property
    def images(self) -> list[ProductImageAggregate]:
        return self._images

    @property
    def attributes(self) -> list[ProductAttributeAggregate]:
        return self._attributes

    @property
    def category(self) -> Optional['CategoryAggregate']:
        return self._category

    @property
    def supplier(self) -> Optional['SupplierAggregate']:
        return self._supplier

    @property
    def images(self) -> list[ProductImageAggregate]:
        return self._images

    @property
    def attributes(self) -> list[ProductAttributeAggregate]:
        return self._attributes

    @property
    def category(self) -> Optional['CategoryAggregate']:
        return self._category

    @property
    def supplier(self) -> Optional['SupplierAggregate']:
        return self._supplier

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

    def rename(self, new_name: str | ProductName):
        """Изменить имя продукта."""
        old_name = self._name_obj
        new_name_obj = new_name if isinstance(new_name, ProductName) else ProductName(new_name)
        self._name_obj = new_name_obj
        self._record_event(ProductNameChangedEvent(
            product_id=self._id,
            old_name=str(old_name),
            new_name=str(new_name_obj),
        ))

    def change_description(self, description: Optional[str]):
        self._description = description

    def change_price(self, price: Decimal | Money):
        """Изменить цену продукта."""
        old_price = self._price_obj
        new_price_obj = price if isinstance(price, Money) else Money.from_decimal(price)
        self._price_obj = new_price_obj
        self._record_event(PriceChangedEvent(
            product_id=self._id,
            old_price=old_price.to_decimal(),
            new_price=new_price_obj.to_decimal(),
        ))

    def change_category(self, category_id: Optional[int]):
        self._category_id = category_id

    def change_supplier(self, supplier_id: Optional[int]):
        self._supplier_id = supplier_id

    def add_image(self, image: ProductImageAggregate):
        """Добавить изображение к продукту."""
        self._images.append(image)
        self._record_event(ProductImageAddedEvent(
            product_id=self._id,
            upload_id=image.upload_id,
            is_main=image.is_main,
            ordering=image.ordering,
        ))

    def remove_image_by_upload_id(self, upload_id: int):
        """Удалить изображение по upload_id."""
        for i, image in enumerate(self._images):
            if image.upload_id == upload_id:
                self._images.pop(i)
                self._record_event(ProductImageRemovedEvent(
                    product_id=self._id,
                    upload_id=upload_id,
                ))
                break

    def replace_images(self, images: list[ProductImageAggregate]):
        """Заменить все изображения."""
        self._images = images
        self._normalize_images_main_flag()

    def apply_image_operations(
        self,
        operations: list['ProductImageOperation'],
        existing_images: list[ProductImageAggregate],
    ) -> list[ProductImageAggregate]:
        """
        Применить операции с изображениями к текущему состоянию агрегата.
        
        Операции:
        - create: добавить новое изображение
        - update: обновить существующее изображение
        - delete: удалить изображение
        - pass: сохранить изображение (возможно с обновлением параметров)
        
        Возвращает финальный список изображений.
        """
        final_images: list[ProductImageAggregate] = []
        processed_upload_ids: set[int] = set()
        
        for op in operations:
            if op.upload_id in processed_upload_ids:
                continue  # Пропускаем дубликаты
            
            if op.action == "delete":
                # Удаляем изображение по upload_id
                self.remove_image_by_upload_id(op.upload_id)
                processed_upload_ids.add(op.upload_id)
                
            elif op.action == "pass":
                # Сохраняем существующее изображение
                for img in existing_images:
                    if img.upload_id == op.upload_id:
                        final_images.append(ProductImageAggregate(
                            upload_id=img.upload_id,
                            is_main=op.is_main if op.is_main is not None else img.is_main,
                            ordering=op.ordering if op.ordering is not None else img.ordering,
                            object_key=img.object_key,
                        ))
                        processed_upload_ids.add(op.upload_id)
                        break
                        
            elif op.action == "create":
                # Создаём новое изображение (будет добавлено отдельно)
                if op.upload_id is not None:
                    final_images.append(ProductImageAggregate(
                        upload_id=op.upload_id,
                        is_main=op.is_main if op.is_main is not None else False,
                        ordering=op.ordering if op.ordering is not None else 0,
                        object_key=op.object_key,
                    ))
                    processed_upload_ids.add(op.upload_id)
                    self.add_image(final_images[-1])
        
        # Нормализуем флаг is_main
        if final_images and not any(img.is_main for img in final_images):
            final_images[0].is_main = True
            
        return final_images

    def add_attribute(self, attribute: ProductAttributeAggregate):
        """Добавить атрибут к продукту."""
        self._attributes.append(attribute)
        self._record_event(ProductAttributeAddedEvent(
            product_id=self._id,
            attribute_name=attribute.name,
            attribute_value=attribute.value,
            is_filterable=attribute.is_filterable,
        ))

    def remove_attribute_by_name(self, name: str):
        """Удалить атрибут по имени."""
        for i, attribute in enumerate(self._attributes):
            if attribute.name == name:
                self._attributes.pop(i)
                self._record_event(ProductAttributeRemovedEvent(
                    product_id=self._id,
                    attribute_name=name,
                ))
                break

    def replace_attributes(self, attributes: list[ProductAttributeAggregate]):
        """Заменить все атрибуты."""
        self._attributes = attributes

    def update(
        self,
        name: Optional[str],
        description: Optional[str],
        price: Optional[Decimal],
        category_id: Optional[int],
        supplier_id: Optional[int],
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
