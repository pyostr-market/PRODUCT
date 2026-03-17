import asyncio
from typing import TYPE_CHECKING, Optional

from src.catalog.category.domain.aggregates.category import CategoryAggregate
from src.catalog.category.domain.repository.category import CategoryRepository
from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.catalog.suppliers.domain.repository.supplier import SupplierRepository


class RelatedEntityLoader:
    """
    Сервис для загрузки связанных сущностей.

    Упрощает Command Handlers, инкапсулируя логику загрузки
    Category и Supplier.
    """

    def __init__(
        self,
        category_repository: CategoryRepository,
        supplier_repository: SupplierRepository,
    ):
        self.category_repository = category_repository
        self.supplier_repository = supplier_repository

    async def load_category(self, category_id: Optional[int]) -> Optional['CategoryAggregate']:
        """Загрузить CategoryAggregate по ID."""
        if not category_id:
            return None

        model = await self.category_repository.get(category_id)
        if not model:
            return None

        return CategoryAggregate(
            category_id=model.id,
            name=model.name,
            description=model.description,
            parent_id=model.parent_id,
            manufacturer_id=model.manufacturer_id,
            device_type_id=model.device_type_id,
        )

    async def load_supplier(self, supplier_id: Optional[int]) -> Optional['SupplierAggregate']:
        """Загрузить SupplierAggregate по ID."""
        if not supplier_id:
            return None

        model = await self.supplier_repository.get(supplier_id)
        if not model:
            return None

        return SupplierAggregate(
            supplier_id=model.id,
            name=model.name,
            contact_email=model.contact_email,
            phone=model.phone,
        )

    async def load_category_and_supplier(
        self,
        category_id: Optional[int],
        supplier_id: Optional[int],
    ) -> tuple[
        Optional['CategoryAggregate'],
        Optional['SupplierAggregate'],
    ]:
        """Загрузить все связанные сущности одним вызовом."""
        category, supplier = await asyncio.gather(
            self.load_category(category_id),
            self.load_supplier(supplier_id),
        )
        return category, supplier
