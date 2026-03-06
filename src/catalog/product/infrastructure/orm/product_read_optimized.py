"""
Optimized Read Model для Product.

Использует raw SQL запросы с denormalized данными для высокой производительности.
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.application.dto.product import (
    ProductAttributeReadDTO,
    ProductImageReadDTO,
    ProductReadDTO,
)
from src.catalog.product.domain.aggregates.category import CategoryAggregate
from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.product.domain.repository.product_read import ProductReadRepositoryInterface
from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.core.services.images.storage import S3ImageStorageService


class OptimizedProductReadRepository(ProductReadRepositoryInterface):
    """
    Оптимизированная read model для Product.
    
    Использует:
    - Raw SQL запросы для производительности
    - Denormalized данные из основных таблиц
    - Эффективную пагинацию
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.image_storage = S3ImageStorageService.from_settings()

    async def get_by_id(self, product_id: int) -> Optional[ProductReadDTO]:
        query = text("""
            SELECT 
                p.id,
                p.name,
                p.description,
                p.price,
                p.category_id,
                p.supplier_id,
                p.product_type_id,
                -- Category data
                c.name as category_name,
                c.description as category_description,
                c.parent_id as category_parent_id,
                c.manufacturer_id as category_manufacturer_id,
                -- Supplier data
                s.name as supplier_name,
                s.contact_email as supplier_email,
                s.phone as supplier_phone,
                -- ProductType data
                pt.name as product_type_name,
                pt.parent_id as product_type_parent_id,
                pt_parent.name as product_type_parent_name,
                pt_parent.id as product_type_parent_id_val
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN suppliers s ON s.id = p.supplier_id
            LEFT JOIN product_types pt ON pt.id = p.product_type_id
            LEFT JOIN product_types pt_parent ON pt_parent.id = pt.parent_id
            WHERE p.id = :product_id
        """)
        
        result = await self.db.execute(query, {"product_id": product_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        # Загружаем изображения
        images = await self._load_images(product_id)
        
        # Загружаем атрибуты
        attributes = await self._load_attributes(product_id)
        
        # Собираем DTO
        return self._row_to_dto(row, images, attributes)

    async def get_by_name(self, name: str) -> Optional[ProductReadDTO]:
        query = text("""
            SELECT 
                p.id,
                p.name,
                p.description,
                p.price,
                p.category_id,
                p.supplier_id,
                p.product_type_id,
                c.name as category_name,
                c.description as category_description,
                c.parent_id as category_parent_id,
                c.manufacturer_id as category_manufacturer_id,
                s.name as supplier_name,
                s.contact_email as supplier_email,
                s.phone as supplier_phone,
                pt.name as product_type_name,
                pt.parent_id as product_type_parent_id,
                pt_parent.name as product_type_parent_name,
                pt_parent.id as product_type_parent_id_val
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN suppliers s ON s.id = p.supplier_id
            LEFT JOIN product_types pt ON pt.id = p.product_type_id
            LEFT JOIN product_types pt_parent ON pt_parent.id = pt.parent_id
            WHERE p.name = :name
        """)
        
        result = await self.db.execute(query, {"name": name})
        row = result.fetchone()
        
        if not row:
            return None
        
        images = await self._load_images(row.id)
        attributes = await self._load_attributes(row.id)
        
        return self._row_to_dto(row, images, attributes)

    async def filter(
        self,
        name: Optional[str],
        category_id: Optional[int],
        product_type_id: Optional[int],
        limit: int,
        offset: int,
        attributes: Optional[dict[str, str]] = None,
    ) -> Tuple[List[ProductReadDTO], int]:
        # Базовый запрос для подсчёта total
        count_query = text("""
            SELECT COUNT(*) 
            FROM products p
            WHERE 1=1
            """ + self._build_where_clause(name, category_id, product_type_id))
        
        count_params = self._build_params(name, category_id, product_type_id)
        count_result = await self.db.execute(text(count_query), count_params)
        total = count_result.scalar() or 0
        
        if total == 0:
            return [], 0
        
        # Основной запрос с пагинацией
        query = text(f"""
            SELECT 
                p.id,
                p.name,
                p.description,
                p.price,
                p.category_id,
                p.supplier_id,
                p.product_type_id,
                c.name as category_name,
                c.description as category_description,
                c.parent_id as category_parent_id,
                c.manufacturer_id as category_manufacturer_id,
                s.name as supplier_name,
                s.contact_email as supplier_email,
                s.phone as supplier_phone,
                pt.name as product_type_name,
                pt.parent_id as product_type_parent_id,
                pt_parent.name as product_type_parent_name,
                pt_parent.id as product_type_parent_id_val
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN suppliers s ON s.id = p.supplier_id
            LEFT JOIN product_types pt ON pt.id = p.product_type_id
            LEFT JOIN product_types pt_parent ON pt_parent.id = pt.parent_id
            WHERE 1=1
            {self._build_where_clause(name, category_id, product_type_id)}
            ORDER BY p.id
            LIMIT :limit OFFSET :offset
        """)
        
        params = self._build_params(name, category_id, product_type_id)
        params["limit"] = limit
        params["offset"] = offset
        
        result = await self.db.execute(text(query), params)
        rows = result.fetchall()
        
        # Параллельно загружаем изображения и атрибуты для всех продуктов
        products = []
        for row in rows:
            images, attributes = await asyncio.gather(
                self._load_images(row.id),
                self._load_attributes(row.id),
            )
            products.append(self._row_to_dto(row, images, attributes))
        
        return products, total

    def _build_where_clause(
        self,
        name: Optional[str],
        category_id: Optional[int],
        product_type_id: Optional[int],
    ) -> str:
        conditions = []
        if name:
            conditions.append("AND p.name ILIKE :name")
        if category_id:
            conditions.append("AND p.category_id = :category_id")
        if product_type_id:
            conditions.append("AND p.product_type_id = :product_type_id")
        return " ".join(conditions)

    def _build_params(
        self,
        name: Optional[str],
        category_id: Optional[int],
        product_type_id: Optional[int],
    ) -> dict[str, Any]:
        params = {}
        if name:
            params["name"] = f"%{name}%"
        if category_id:
            params["category_id"] = category_id
        if product_type_id:
            params["product_type_id"] = product_type_id
        return params

    async def _load_images(self, product_id: int) -> list[ProductImageReadDTO]:
        query = text("""
            SELECT 
                pi.upload_id,
                pi.is_main,
                pi.ordering,
                uh.file_path
            FROM product_images pi
            LEFT JOIN upload_history uh ON uh.id = pi.upload_id
            WHERE pi.product_id = :product_id
            ORDER BY pi.ordering, pi.id
        """)
        
        result = await self.db.execute(query, {"product_id": product_id})
        rows = result.fetchall()
        
        return [
            ProductImageReadDTO(
                upload_id=row.upload_id,
                image_key=row.file_path or "",
                image_url=self.image_storage.build_public_url(row.file_path or ""),
                is_main=row.is_main,
                ordering=row.ordering,
            )
            for row in rows
        ]

    async def _load_attributes(self, product_id: int) -> list[ProductAttributeReadDTO]:
        query = text("""
            SELECT 
                pa.id,
                pa.name,
                pav.value,
                pa.is_filterable
            FROM product_attribute_values pav
            JOIN product_attributes pa ON pa.id = pav.attribute_id
            WHERE pav.product_id = :product_id
            ORDER BY pa.name
        """)
        
        result = await self.db.execute(query, {"product_id": product_id})
        rows = result.fetchall()
        
        return [
            ProductAttributeReadDTO(
                id=row.id,
                name=row.name,
                value=row.value,
                is_filterable=row.is_filterable,
            )
            for row in rows
        ]

    def _row_to_dto(
        self,
        row,
        images: list[ProductImageReadDTO],
        attributes: list[ProductAttributeReadDTO],
    ) -> ProductReadDTO:
        category_dto = None
        if row.category_id:
            category_dto = CategoryAggregate(
                category_id=row.category_id,
                name=row.category_name,
                description=row.category_description,
                parent_id=row.category_parent_id,
                manufacturer_id=row.category_manufacturer_id,
            )
        
        supplier_dto = None
        if row.supplier_id:
            supplier_dto = SupplierAggregate(
                supplier_id=row.supplier_id,
                name=row.supplier_name,
                contact_email=row.supplier_email,
                phone=row.supplier_phone,
            )
        
        product_type_dto = None
        if row.product_type_id:
            parent_dto = None
            if row.product_type_parent_id_val:
                parent_dto = ProductTypeAggregate(
                    product_type_id=row.product_type_parent_id_val,
                    name=row.product_type_parent_name,
                    parent_id=None,
                )
            product_type_dto = ProductTypeAggregate(
                product_type_id=row.product_type_id,
                name=row.product_type_name,
                parent_id=row.product_type_parent_id,
                parent=parent_dto,
            )
        
        return ProductReadDTO(
            id=row.id,
            name=row.name,
            description=row.description,
            price=row.price,
            images=images,
            attributes=attributes,
            category=category_dto,
            supplier=supplier_dto,
            product_type=product_type_dto,
        )

    async def export_full_catalog(self):
        """Экспорт всего каталога — используется raw SQL для производительности."""
        query = text("""
            SELECT 
                p.id,
                p.name,
                p.description,
                p.price,
                p.category_id,
                p.supplier_id,
                p.product_type_id
            FROM products p
            ORDER BY p.id
        """)
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        return [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "price": float(row.price),
                "category_id": row.category_id,
                "supplier_id": row.supplier_id,
                "product_type_id": row.product_type_id,
            }
            for row in rows
        ]


# Импортируем asyncio в конце файла
import asyncio
