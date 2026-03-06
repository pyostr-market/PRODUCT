from typing import Optional

from src.catalog.category.domain.aggregates.category import CategoryAggregate
from src.catalog.category.domain.repository.category import CategoryRepository
from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.product.domain.repository.product_type import ProductTypeRepository
from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.catalog.suppliers.domain.repository.supplier import SupplierRepository


class RelatedEntityLoader:
    """
    Сервис для загрузки связанных сущностей.
    
    Упрощает Command Handlers, инкапсулируя логику загрузки
    Category, Supplier и ProductType.
    """

    def __init__(
        self,
        category_repository: CategoryRepository,
        supplier_repository: SupplierRepository,
        product_type_repository: ProductTypeRepository,
    ):
        self.category_repository = category_repository
        self.supplier_repository = supplier_repository
        self.product_type_repository = product_type_repository

    async def load_category(self, category_id: Optional[int]) -> Optional[CategoryAggregate]:
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
        )

    async def load_supplier(self, supplier_id: Optional[int]) -> Optional[SupplierAggregate]:
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

    async def load_product_type(self, product_type_id: Optional[int]) -> Optional[ProductTypeAggregate]:
        """Загрузить ProductTypeAggregate по ID с родителем."""
        if not product_type_id:
            return None
        
        model = await self.product_type_repository.get_with_parent(product_type_id)
        if not model:
            return None
        
        return ProductTypeAggregate(
            product_type_id=model.id,
            name=model.name,
            parent_id=model.parent_id,
            parent=model.parent,
        )

    async def load_all(
        self,
        category_id: Optional[int],
        supplier_id: Optional[int],
        product_type_id: Optional[int],
    ) -> tuple[
        Optional[CategoryAggregate],
        Optional[SupplierAggregate],
        Optional[ProductTypeAggregate],
    ]:
        """Загрузить все связанные сущности одним вызовом."""
        category, supplier, product_type = await asyncio.gather(
            self.load_category(category_id),
            self.load_supplier(supplier_id),
            self.load_product_type(product_type_id),
        )
        return category, supplier, product_type


# Импортируем asyncio в конце файла для избежания проблем с порядком импорта
import asyncio
