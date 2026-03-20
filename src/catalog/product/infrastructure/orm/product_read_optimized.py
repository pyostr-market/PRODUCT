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
    CatalogFiltersDTO,
    FilterDTO,
    FilterOptionDTO,
)
from src.catalog.product.domain.repository.product_read import (
    ProductReadRepositoryInterface,
)
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
                -- Category data
                c.name as category_name,
                c.description as category_description,
                c.parent_id as category_parent_id,
                c.manufacturer_id as category_manufacturer_id,
                c.device_type_id as category_device_type_id,
                -- Supplier data
                s.name as supplier_name,
                s.contact_email as supplier_email,
                s.phone as supplier_phone
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN suppliers s ON s.id = p.supplier_id
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
                c.name as category_name,
                c.description as category_description,
                c.parent_id as category_parent_id,
                c.manufacturer_id as category_manufacturer_id,
                c.device_type_id as category_device_type_id,
                s.name as supplier_name,
                s.contact_email as supplier_email,
                s.phone as supplier_phone
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN suppliers s ON s.id = p.supplier_id
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
        attributes: Optional[dict[str, list[str]]] = None,
    ) -> Tuple[List[ProductReadDTO], int]:
        # Базовый запрос для подсчёта total
        count_query = text("""
            SELECT COUNT(*)
            FROM products p
            WHERE 1=1
            """ + self._build_where_clause(name, category_id, attributes))

        count_params = self._build_params(name, category_id, attributes)
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
                c.name as category_name,
                c.description as category_description,
                c.parent_id as category_parent_id,
                c.manufacturer_id as category_manufacturer_id,
                c.device_type_id as category_device_type_id,
                s.name as supplier_name,
                s.contact_email as supplier_email,
                s.phone as supplier_phone
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN suppliers s ON s.id = p.supplier_id
            WHERE 1=1
            {self._build_where_clause(name, category_id, attributes)}
            ORDER BY p.id
            LIMIT :limit OFFSET :offset
        """)

        params = self._build_params(name, category_id, attributes)
        params["limit"] = limit
        params["offset"] = offset

        result = await self.db.execute(text(query), params)
        rows = result.fetchall()

        # Параллельно загружаем изображения и атрибуты для всех продуктов
        import asyncio
        products = []
        for row in rows:
            images, attributes_data = await asyncio.gather(
                self._load_images(row.id),
                self._load_attributes(row.id),
            )
            products.append(self._row_to_dto(row, images, attributes_data))

        return products, total

    def _build_where_clause(
        self,
        name: Optional[str],
        category_id: Optional[int],
        attributes: Optional[dict[str, list[str]]] = None,
    ) -> str:
        conditions = []
        if name:
            conditions.append("AND p.name ILIKE :name")
        if category_id:
            conditions.append("AND p.category_id = :category_id")
        
        # Добавляем условия для атрибутов
        if attributes:
            for attr_name in attributes.keys():
                conditions.append(f"AND EXISTS (")
                conditions.append(f"    SELECT 1 FROM product_attribute_values pav ")
                conditions.append(f"    JOIN product_attributes pa ON pa.id = pav.attribute_id ")
                conditions.append(f"    WHERE pav.product_id = p.id ")
                conditions.append(f"    AND pa.name = :attr_{attr_name}_name ")
                conditions.append(f"    AND pav.value = ANY(:attr_{attr_name}_values)")
                conditions.append(f")")
        
        return " ".join(conditions)

    def _build_params(
        self,
        name: Optional[str],
        category_id: Optional[int],
        attributes: Optional[dict[str, list[str]]] = None,
    ) -> dict[str, Any]:
        params = {}
        if name:
            params["name"] = f"%{name}%"
        if category_id:
            params["category_id"] = category_id
        
        # Добавляем параметры для атрибутов
        if attributes:
            for attr_name, attr_values in attributes.items():
                # Создаем безопасное имя параметра
                safe_name = attr_name.replace(" ", "_").replace("-", "_")
                params[f"attr_{safe_name}_name"] = attr_name
                params[f"attr_{safe_name}_values"] = attr_values
        
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
        from src.catalog.category.domain.aggregates.category import CategoryAggregate
        from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate

        category_dto = None
        if row.category_id:
            category_dto = CategoryAggregate(
                category_id=row.category_id,
                name=row.category_name,
                description=row.category_description,
                parent_id=row.category_parent_id,
                manufacturer_id=row.category_manufacturer_id,
                device_type_id=row.category_device_type_id,
            )

        supplier_dto = None
        if row.supplier_id:
            supplier_dto = SupplierAggregate(
                supplier_id=row.supplier_id,
                name=row.supplier_name,
                contact_email=row.supplier_email,
                phone=row.supplier_phone,
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
        )

    async def get_catalog_filters(
        self,
        category_id: Optional[int] = None,
        device_type_id: Optional[int] = None,
    ) -> CatalogFiltersDTO:
        """
        Получить фильтры для каталога.
        
        Логика:
        1. Если указана category_id, проверяем её device_type_id
        2. Если у категории нет device_type_id, смотрим на родительскую категорию
        3. Получаем все filterable атрибуты для этого device_type
        4. Группируем уникальные значения атрибутов и возвращаем в ответе
        """
        # Определяем device_type_id для фильтрации
        target_device_type_id = device_type_id

        if category_id is not None:
            # Запрос для получения device_type_id из категории (с учётом наследования)
            category_stmt = text("""
                WITH RECURSIVE category_chain AS (
                    SELECT id, parent_id, device_type_id
                    FROM categories
                    WHERE id = :category_id
                    UNION ALL
                    SELECT c.id, c.parent_id, c.device_type_id
                    FROM categories c
                    INNER JOIN category_chain cc ON c.id = cc.parent_id
                    WHERE cc.device_type_id IS NULL
                )
                SELECT device_type_id
                FROM category_chain
                WHERE device_type_id IS NOT NULL
                LIMIT 1
            """)

            result = await self.db.execute(category_stmt, {"category_id": category_id})
            row = result.fetchone()

            if row and row.device_type_id:
                target_device_type_id = row.device_type_id
        
        # Формируем запрос для получения атрибутов
        # Используем CTE для получения всех категорий с нужным effective device_type_id
        filter_stmt = text("""
            WITH RECURSIVE category_chain AS (
                -- Находим все категории, у которых effective device_type_id = target
                SELECT 
                    c.id,
                    c.device_type_id,
                    c.device_type_id as effective_device_type_id
                FROM categories c
                WHERE c.device_type_id = :target_device_type_id
                
                UNION ALL
                
                -- Добавляем дочерние категории, которые наследуют device_type_id
                SELECT 
                    c.id,
                    c.device_type_id,
                    cc.effective_device_type_id
                FROM categories c
                INNER JOIN category_chain cc ON c.parent_id = cc.id
                WHERE c.device_type_id IS NULL
            )
            SELECT
                pa.name as attribute_name,
                pa.is_filterable,
                pav.value as attribute_value,
                COUNT(DISTINCT p.id) as product_count
            FROM product_attribute_values pav
            JOIN product_attributes pa ON pa.id = pav.attribute_id
            JOIN products p ON p.id = pav.product_id
            JOIN category_chain cc ON cc.id = p.category_id
            WHERE pa.is_filterable = true
            GROUP BY pa.name, pa.is_filterable, pav.value
            ORDER BY pa.name, pav.value
        """)

        filter_params = {"target_device_type_id": target_device_type_id}
        
        result = await self.db.execute(filter_stmt, filter_params)
        rows = result.fetchall()
        
        # Группируем результаты по атрибутам
        filters_dict = {}
        for row in rows:
            attr_name = row.attribute_name
            if attr_name not in filters_dict:
                filters_dict[attr_name] = FilterDTO(
                    name=attr_name,
                    is_filterable=row.is_filterable,
                    options=[]
                )
            filters_dict[attr_name].options.append(
                FilterOptionDTO(
                    value=row.attribute_value,
                    count=row.product_count
                )
            )
        
        return CatalogFiltersDTO(
            filters=list(filters_dict.values())
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
                p.supplier_id
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
            }
            for row in rows
        ]
