from typing import List, Optional, Tuple

from sqlalchemy import and_, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.category.domain.aggregates.category import CategoryAggregate
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
from src.catalog.product.infrastructure.models.product import Product
from src.catalog.product.infrastructure.models.product_attribute import ProductAttribute
from src.catalog.product.infrastructure.models.product_attribute_value import (
    ProductAttributeValue,
)
from src.catalog.product.infrastructure.models.product_image import ProductImage
from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.core.services.images.storage import S3ImageStorageService


class SqlAlchemyProductReadRepository(ProductReadRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db
        self.image_storage = S3ImageStorageService.from_settings()

    def _to_read_dto(self, model: Product) -> ProductReadDTO:
        category_dto = None
        if model.category:
            category_dto = CategoryAggregate(
                category_id=model.category.id,
                name=model.category.name,
                description=model.category.description,
                parent_id=model.category.parent_id,
                manufacturer_id=model.category.manufacturer_id,
                device_type_id=model.category.device_type_id,
            )

        supplier_dto = None
        if model.supplier:
            supplier_dto = SupplierAggregate(
                supplier_id=model.supplier.id,
                name=model.supplier.name,
                contact_email=model.supplier.contact_email,
                phone=model.supplier.phone,
            )

        return ProductReadDTO(
            id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
            images=[
                ProductImageReadDTO(
                    image_key=image.upload.file_path,
                    image_url=self.image_storage.build_public_url(image.upload.file_path),
                    is_main=image.is_main,
                    ordering=image.ordering,
                    upload_id=image.upload_id,
                )
                for image in model.images
            ],
            attributes=[
                ProductAttributeReadDTO(
                    id=attribute_value.attribute.id,
                    name=attribute_value.attribute.name,
                    value=attribute_value.value,
                    is_filterable=attribute_value.attribute.is_filterable,
                )
                for attribute_value in model.attributes
            ],
            category=category_dto,
            supplier=supplier_dto,
        )

    async def get_by_id(self, product_id: int) -> Optional[ProductReadDTO]:
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images).selectinload(ProductImage.upload),
                selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute),
                selectinload(Product.category),
                selectinload(Product.supplier),
            )
            .where(Product.id == product_id)
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def get_by_name(self, name: str) -> Optional[ProductReadDTO]:
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images).selectinload(ProductImage.upload),
                selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute),
                selectinload(Product.category),
                selectinload(Product.supplier),
            )
            .where(Product.name == name)
        )

        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def filter(
        self,
        name: Optional[str],
        category_id: Optional[int],
        product_type_id: Optional[int],
        limit: int,
        offset: int,
        attributes: Optional[dict[str, str]] = None,
    ) -> Tuple[List[ProductReadDTO], int]:
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images).selectinload(ProductImage.upload),
                selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute),
                selectinload(Product.category),
                selectinload(Product.supplier),
            )
        )
        count_stmt = select(func.count()).select_from(Product)

        if name:
            stmt = stmt.where(Product.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(Product.name.ilike(f"%{name}%"))

        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
            count_stmt = count_stmt.where(Product.category_id == category_id)

        # product_type_id больше не используется (перенесён в категории)
        # Если передан, игнорируем или можно фильтровать через category.device_type_id

        # Фильтрация по атрибутам
        if attributes:
            for attr_name, attr_values in attributes.items():
                # Поддерживаем множественные значения для одного атрибута
                # Товар должен соответствовать хотя бы одному значению из списка
                stmt = stmt.where(
                    Product.attributes.any(
                        and_(
                            ProductAttributeValue.attribute.has(
                                ProductAttribute.name == attr_name
                            ),
                            ProductAttributeValue.value.in_(attr_values),
                        )
                    )
                )
                count_stmt = count_stmt.where(
                    Product.attributes.any(
                        and_(
                            ProductAttributeValue.attribute.has(
                                ProductAttribute.name == attr_name
                            ),
                            ProductAttributeValue.value.in_(attr_values),
                        )
                    )
                )

        stmt = stmt.order_by(Product.id).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = [self._to_read_dto(model) for model in result.scalars().all()]
        total = count_result.scalar() or 0

        return items, total

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
            # Получаем категорию и её device_type_id
            from src.catalog.product.infrastructure.models.product import Product as ProductModel
            from sqlalchemy import select
            
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
        sql = text("""
            SELECT
                p.id,
                p.name,
                p.price,
                p.category_id,
                c.name as category_name,
                c.device_type_id as category_device_type_id,
                p.supplier_id,
                s.name as supplier_name,
                COALESCE(
                    jsonb_agg(
                        jsonb_build_object(
                            'id', pa.id,
                            'name', pa.name,
                            'value', pav.value,
                            'is_filterable', pa.is_filterable
                        )
                    ) FILTER (WHERE pa.id IS NOT NULL),
                    '[]'
                ) as attributes
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN suppliers s ON s.id = p.supplier_id
            LEFT JOIN product_attribute_values pav ON pav.product_id = p.id
            LEFT JOIN product_attributes pa ON pa.id = pav.attribute_id
            GROUP BY
                p.id,
                c.name,
                c.device_type_id,
                s.name
            ORDER BY p.id
        """)

        result = await self.db.execute(sql)
        rows = result.mappings().all()

        return rows