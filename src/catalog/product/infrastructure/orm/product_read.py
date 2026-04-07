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
    ProductSearchDTO,
    SearchSuggestionDTO,
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
from src.core.conf.settings import get_settings
from src.core.services.images.storage import S3ImageStorageService


class SqlAlchemyProductReadRepository(ProductReadRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db
        self.image_storage = S3ImageStorageService.from_settings()

    def _sort_filters(self, filters: list[FilterDTO]) -> list[FilterDTO]:
        """
        Сортировка фильтров.
        
        Алгоритм:
        1. Если имя атрибута есть в списке FILTER_SORT_ORDER - используем его позицию
        2. Если не указан - сортируем по алфавиту (default)
        
        Returns:
            Отсортированный список фильтров
        """
        settings = get_settings()
        sort_order = settings.filter_sort_order
        
        # Создаем словарь для быстрого поиска позиции
        order_map = {name: idx for idx, name in enumerate(sort_order)}
        max_order = len(sort_order)
        
        def sort_key(filter_dto: FilterDTO) -> tuple:
            # Если имя есть в списке порядка - возвращаем его позицию
            # Если нет - возвращаем max_order + имя (для алфавитной сортировки)
            if filter_dto.name in order_map:
                return (order_map[filter_dto.name], "")
            else:
                return (max_order, filter_dto.name.lower())
        
        return sorted(filters, key=sort_key)

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
                    is_groupable=attribute_value.attribute.is_groupable,
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
        sort_type: str = "default",
        product_ids: Optional[List[int]] = None,
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

        # product_type_id фильтрует товары через category.device_type_id
        # (с учётом наследования от родительских категорий)
        if product_type_id is not None:
            # Используем CTE для получения всех категорий с нужным device_type_id
            cte_stmt = text("""
                WITH RECURSIVE category_chain AS (
                    SELECT
                        c.id
                    FROM categories c
                    WHERE c.device_type_id = :product_type_id

                    UNION ALL

                    SELECT
                        c.id
                    FROM categories c
                    INNER JOIN category_chain cc ON c.parent_id = cc.id
                    WHERE c.device_type_id IS NULL
                )
                SELECT id FROM category_chain
            """)
            result = await self.db.execute(cte_stmt, {"product_type_id": product_type_id})
            category_ids = [row[0] for row in result.fetchall()]

            # Отладка
            print(f"filter: product_type_id={product_type_id}, category_ids={category_ids}")

            if category_ids:
                stmt = stmt.where(Product.category_id.in_(category_ids))
                count_stmt = count_stmt.where(Product.category_id.in_(category_ids))
            else:
                # Если категорий не найдено, возвращаем пустой результат
                stmt = stmt.where(Product.id == -1)
                count_stmt = count_stmt.where(Product.id == -1)

        # Фильтрация по списку ID товаров
        if product_ids:
            stmt = stmt.where(Product.id.in_(product_ids))
            count_stmt = count_stmt.where(Product.id.in_(product_ids))

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

        # Сортировка
        if sort_type == "price_asc":
            stmt = stmt.order_by(Product.price.asc(), Product.id)
        elif sort_type == "price_desc":
            stmt = stmt.order_by(Product.price.desc(), Product.id)
        else:  # default
            stmt = stmt.order_by(Product.id)

        stmt = stmt.limit(limit).offset(offset)

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
        1. Если указан product_type_id (device_type_id), используем его напрямую
        2. Если указана category_id:
           - Если у категории есть дочерние категории — берем атрибуты всех дочерних категорий (рекурсивно)
           - Если у категории нет дочерних категорий (конечная категория) — берем атрибуты только этой категории
        3. Получаем все filterable атрибуты и группируем уникальные значения
        """
        # Определяем device_type_id для фильтрации
        target_device_type_id = device_type_id
        target_category_id = None
        use_category_directly = False

        if category_id is not None:
            # Проверяем, есть ли у категории дочерние категории
            has_children_stmt = text("""
                SELECT EXISTS(
                    SELECT 1 FROM categories WHERE parent_id = :category_id
                ) as has_children
            """)
            result = await self.db.execute(has_children_stmt, {"category_id": category_id})
            row = result.fetchone()

            if row and not row.has_children:
                # У категории нет дочерних — это конечная категория
                # Используем только эту категорию напрямую
                target_category_id = category_id
                use_category_directly = True
            else:
                # У категории есть дочерние — это родительская категория
                # Нужно найти device_type_id и взять все дочерние категории
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
        if use_category_directly and target_category_id:
            # Режим: выбрана конечная категория (нет дочерних)
            # Берем атрибуты только товаров этой категории
            filter_stmt = text("""
                SELECT
                    pa.name as attribute_name,
                    pa.is_filterable,
                    pav.value as attribute_value,
                    COUNT(DISTINCT p.id) as product_count
                FROM product_attribute_values pav
                JOIN product_attributes pa ON pa.id = pav.attribute_id
                JOIN products p ON p.id = pav.product_id
                WHERE pa.is_filterable = true
                  AND p.category_id = :target_category_id
                GROUP BY pa.name, pa.is_filterable, pav.value
                ORDER BY pa.name, pav.value
            """)
            filter_params = {"target_category_id": target_category_id}
        elif target_device_type_id:
            # Режим: выбрана родительская категория или product_type_id
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
        else:
            # Нет ни category_id, ни device_type_id — возвращаем пустой результат
            return CatalogFiltersDTO(filters=[])
        
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

        # Сортируем фильтры
        sorted_filters = self._sort_filters(list(filters_dict.values()))

        return CatalogFiltersDTO(
            filters=sorted_filters
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

    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> ProductSearchDTO:
        """
        Полнотекстовый поиск товаров с подсказками следующих слов.
        
        Логика:
        1. Ищем товары по названию и атрибутам (ILIKE по частичному совпадению)
        2. Извлекаем следующиеие слова из названий найденных товаров
        3. Возвращаем товары + топ-5 подсказок
        """
        # Нормализуем поисковый запрос
        search_term = query.strip()
        if not search_term:
            return ProductSearchDTO(items=[], total=0, suggestions=[])

        # Запрос для поиска товаров
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images).selectinload(ProductImage.upload),
                selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute),
                selectinload(Product.category),
                selectinload(Product.supplier),
            )
            .where(
                # Поиск по названию товара
                Product.name.ilike(f"%{search_term}%")
                # Или поиск по атрибутам
                | Product.attributes.any(
                    ProductAttributeValue.value.ilike(f"%{search_term}%")
                )
            )
        )

        # Запрос для подсчета общего количества
        count_stmt = (
            select(func.count(Product.id))
            .where(
                Product.name.ilike(f"%{search_term}%")
                | Product.attributes.any(
                    ProductAttributeValue.value.ilike(f"%{search_term}%")
                )
            )
        )

        # Добавляем пагинацию
        stmt = stmt.order_by(Product.id).limit(limit).offset(offset)

        # Выполняем запросы
        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        products = result.scalars().all()
        total = count_result.scalar() or 0

        # Конвертируем в DTO
        items = [self._to_read_dto(product) for product in products]

        # Извлекаем следующиеие слова из названий товаров
        suggestions = self._extract_next_word_suggestions(products, search_term)

        return ProductSearchDTO(
            items=items,
            total=total,
            suggestions=suggestions,
        )

    def _extract_next_word_suggestions(
        self,
        products: list[Product],
        search_term: str,
    ) -> list[SearchSuggestionDTO]:
        """
        Извлекает следующиеие слова после введенного пользователем слова.
        
        Например, если пользователь ввел "iPhone", и есть товары:
        - "iPhone 15 Pro"
        - "iPhone 15"
        - "iPhone 16"
        - "iPhone Red"
        - "iPhone 17 Pro Max"
        
        Вернет: ["15", "16", "Red", "17", "Pro"]
        """
        import re
        from collections import Counter

        search_lower = search_term.lower()
        word_counter = Counter()

        for product in products:
            # Разбиваем название на слова
            name = product.name
            # Ищем поисковый запрос в названии (без учета регистра)
            match = re.search(re.escape(search_lower), name.lower())
            
            if match:
                # Получаем часть после поискового запроса
                after_search = name[match.end():].strip()
                
                # Берем первое слово после поискового запроса
                next_word_match = re.match(r'^(\S+)', after_search)
                if next_word_match:
                    next_word = next_word_match.group(1)
                    word_counter[next_word] += 1

        # Также ищем в атрибутах товаров
        # Собираем все атрибуты найденных товаров
        attribute_words = Counter()
        for product in products:
            for attr_value in product.attributes:
                value = attr_value.value
                # Ищем поисковый запрос в атрибуте
                match = re.search(re.escape(search_lower), value.lower())
                
                if match:
                    after_search = value[match.end():].strip()
                    next_word_match = re.match(r'^(\S+)', after_search)
                    if next_word_match:
                        next_word = next_word_match.group(1)
                        attribute_words[next_word] += 1

        # Объединяем счетчики, отдавая приоритет словам из названий
        for word, count in attribute_words.items():
            if word not in word_counter:
                word_counter[word] = count

        # Возвращаем топ-5 слов
        return [
            SearchSuggestionDTO(word=word, count=count)
            for word, count in word_counter.most_common(5)
        ]