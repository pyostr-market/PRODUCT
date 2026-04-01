from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.product.application.dto.product_relation import ProductRelationListItemDTO
from src.catalog.product.domain.repository.product_relation import ProductRelationRepository
from src.catalog.product.infrastructure.models.product import Product
from src.catalog.product.infrastructure.models.product_image import ProductImage
from src.catalog.product.infrastructure.models.product_relation import ProductRelation
from src.core.services.images import ImageStorageService


@dataclass
class ProductRelationsResult:
    """Результат получения списка связей."""
    items: List[ProductRelationListItemDTO]
    total: int
    page: int
    limit: int


class ProductRelationQueries:
    """Queries для получения связей и рекомендаций товаров."""

    def __init__(
        self,
        repository: ProductRelationRepository,
        db: AsyncSession,
        image_storage: ImageStorageService,
    ):
        self.repository = repository
        self.db = db
        self.image_storage = image_storage

    async def get_relations(
        self,
        product_id: int,
        relation_type: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> ProductRelationsResult:
        """
        Получить список связей товара с пагинацией.

        Args:
            product_id: ID товара
            relation_type: Опциональный фильтр по типу связи
            page: Номер страницы (1-based)
            limit: Количество элементов на странице

        Returns:
            ProductRelationsResult с элементами и пагинацией
        """
        # Базовый запрос для подсчёта общего количества
        count_stmt = select(func.count()).select_from(ProductRelation).where(
            ProductRelation.product_id == product_id
        )

        if relation_type:
            count_stmt = count_stmt.where(ProductRelation.relation_type == relation_type)

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        # Запрос для получения данных с пагинацией
        offset = (page - 1) * limit

        stmt = (
            select(ProductRelation)
            .where(ProductRelation.product_id == product_id)
            .order_by(ProductRelation.sort_order, ProductRelation.id)
        )

        if relation_type:
            stmt = stmt.where(ProductRelation.relation_type == relation_type)

        stmt = stmt.offset(offset).limit(limit)

        result = await self.db.execute(stmt)
        relations = result.scalars().all()

        # Получаем связанные товары с изображениями
        related_product_ids = [r.related_product_id for r in relations]

        products_stmt = (
            select(Product)
            .where(Product.id.in_(related_product_ids))
            .options(selectinload(Product.images).selectinload(ProductImage.upload))
        )
        products_result = await self.db.execute(products_stmt)
        products_map = {p.id: p for p in products_result.scalars().all()}

        # Формируем результат
        items = []
        for relation in relations:
            product = products_map.get(relation.related_product_id)
            if product:
                # Формируем список изображений с URL
                images_data = []
                for img in sorted(product.images, key=lambda x: x.ordering):
                    images_data.append({
                        "upload_id": img.upload_id,
                        "image_url": self.image_storage.build_public_url(img.upload.file_path) if img.upload else "",
                        "is_main": img.is_main,
                        "ordering": img.ordering,
                    })

                items.append(ProductRelationListItemDTO(
                    relation_id=relation.id,  # ID связи для удаления
                    id=product.id,
                    name=product.name,
                    price=float(product.price),
                    description=product.description,
                    relation_type=relation.relation_type,
                    sort_order=relation.sort_order,
                    images=images_data if images_data else [],
                ))

        return ProductRelationsResult(
            items=items,
            total=total,
            page=page,
            limit=limit,
        )

    async def get_recommendations(
        self,
        product_id: int,
        relation_type: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> ProductRelationsResult:
        """
        Получить рекомендации для товара.

        Это алиас для get_relations, но с более семантически правильным названием
        для публичного API.

        Args:
            product_id: ID товара
            relation_type: Опциональный фильтр по типу рекомендации
            page: Номер страницы (1-based)
            limit: Количество элементов на странице

        Returns:
            ProductRelationsResult с рекомендациями и пагинацией
        """
        return await self.get_relations(
            product_id=product_id,
            relation_type=relation_type,
            page=page,
            limit=limit,
        )
