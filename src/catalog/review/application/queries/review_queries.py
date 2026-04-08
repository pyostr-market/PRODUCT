"""Запросы для получения отзывов."""

from decimal import Decimal
from typing import Optional

from src.catalog.review.application.dto.review import ReviewImageReadDTO, ReviewListDTO, ReviewReadDTO
from src.catalog.review.domain.aggregates.review import ReviewAggregate
from src.catalog.review.domain.exceptions import ReviewNotFoundError
from src.catalog.review.domain.repository.review import ReviewRepository
from src.core.services.images.storage import ImageStorageService


class ReviewQueries:

    def __init__(
        self,
        repository: ReviewRepository,
        image_storage: ImageStorageService,
    ):
        self.repository = repository
        self.image_storage = image_storage

    async def get_review(self, review_id: int) -> ReviewReadDTO:
        """Получить отзыв по ID."""
        aggregate = await self.repository.get(review_id)
        if not aggregate:
            raise ReviewNotFoundError(review_id)

        return self._to_read_dto(aggregate)

    async def get_reviews_by_product(
        self,
        product_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> ReviewListDTO:
        """Получить список отзывов для товара с пагинацией."""
        aggregates, total = await self.repository.get_by_product_id(
            product_id, limit=limit, offset=offset
        )

        average_rating = await self.repository.get_average_rating_for_product(product_id)

        items = [self._to_read_dto(agg) for agg in aggregates]

        return ReviewListDTO(
            items=items,
            total=total,
            average_rating=average_rating,
        )

    def _to_read_dto(self, aggregate: ReviewAggregate) -> ReviewReadDTO:
        """Преобразовать агрегат в DTO для чтения."""
        images = []
        for img in aggregate.images:
            image_url = None
            if img.object_key:
                image_url = self.image_storage.build_public_url(img.object_key)

            images.append(
                ReviewImageReadDTO(
                    upload_id=img.upload_id,
                    image_key=img.object_key or "",
                    image_url=image_url,
                    ordering=img.ordering,
                )
            )

        return ReviewReadDTO(
            id=aggregate.id,
            product_id=aggregate.product_id,
            user_id=aggregate.user_id,
            username=aggregate.username,
            rating=aggregate.rating,
            text=aggregate.text,
            images=images,
        )
