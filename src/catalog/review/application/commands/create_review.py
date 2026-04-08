"""Команда создания отзыва."""

from decimal import Decimal
from typing import Any

from src.catalog.review.application.dto.review import (
    ReviewCreateDTO,
    ReviewImageReadDTO,
    ReviewReadDTO,
)
from src.catalog.review.application.dto.review import ReviewAuditDTO
from src.catalog.review.domain.aggregates.review import ReviewAggregate
from src.catalog.review.domain.aggregates.review_image import ReviewImageAggregate
from src.catalog.review.domain.exceptions import ReviewAlreadyExistsError
from src.catalog.review.domain.repository.review import ReviewRepository
from src.catalog.review.domain.repository.review_audit import ReviewAuditRepository
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus
from src.core.services.images.storage import S3ImageStorageService
from src.uploads.domain.repository.upload_history import UploadHistoryRepository


class CreateReviewCommand:

    def __init__(
        self,
        repository: ReviewRepository,
        audit_repository: ReviewAuditRepository,
        uow: UnitOfWork,
        image_storage: S3ImageStorageService,
        event_bus: AsyncEventBus,
        upload_history_repository: UploadHistoryRepository,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.image_storage = image_storage
        self.event_bus = event_bus
        self.upload_history_repository = upload_history_repository

    async def execute(self, dto: ReviewCreateDTO, user: User) -> ReviewReadDTO:
        # Валидируем upload_id изображений (вне UOW — только чтение)
        mapped_images = await self._map_images(dto.images)

        async with self.uow:
            session = self.uow.session

            # Проверяем, что пользователь ещё не оставлял отзыв на этот товар
            existing = await self.repository.get_user_review_for_product(user.id, dto.product_id)
            if existing:
                raise ReviewAlreadyExistsError(user_id=user.id, product_id=dto.product_id)

            aggregate = ReviewAggregate(
                product_id=dto.product_id,
                user_id=user.id,
                username=user.fio or f"user_{user.id}",
                rating=dto.rating,
                text=dto.text,
                images=mapped_images,
            )

            await self.repository.create(aggregate)

            new_data = self._capture_state(aggregate)

            await self.audit_repository.log(
                ReviewAuditDTO(
                    review_id=aggregate.id,
                    action="create",
                    old_data=None,
                    new_data=new_data,
                    user_id=user.id,
                    fio=user.fio,
                )
            )

            # Обновляем рейтинг товара
            await self._update_product_rating(aggregate.product_id)

        return self._to_read_dto(aggregate)

    async def _map_images(
        self,
        images: list,
    ) -> list[ReviewImageAggregate]:
        """Валидировать и замапить изображения."""
        mapped = []
        for idx, image in enumerate(images):
            upload_record = await self.upload_history_repository.get(image.upload_id)
            if not upload_record:
                raise ValueError(f"Upload with id {image.upload_id} not found")

            mapped.append(
                ReviewImageAggregate(
                    upload_id=upload_record.upload_id,
                    ordering=image.ordering if image.ordering else idx,
                    object_key=upload_record.file_path,
                )
            )
        return mapped

    def _capture_state(self, aggregate: ReviewAggregate) -> dict[str, Any]:
        """Зафиксировать текущее состояние агрегата."""
        return {
            "product_id": aggregate.product_id,
            "user_id": aggregate.user_id,
            "username": aggregate.username,
            "rating": str(aggregate.rating),
            "text": aggregate.text,
            "image_upload_ids": [img.upload_id for img in aggregate.images],
        }

    def _to_read_dto(self, aggregate: ReviewAggregate) -> ReviewReadDTO:
        """Преобразовать агрегат в DTO для чтения."""
        return ReviewReadDTO(
            id=aggregate.id,
            product_id=aggregate.product_id,
            user_id=aggregate.user_id,
            username=aggregate.username,
            rating=aggregate.rating,
            text=aggregate.text,
            images=[
                ReviewImageReadDTO(
                    upload_id=img.upload_id,
                    image_key=img.object_key or "",
                    image_url=None,
                    ordering=img.ordering,
                )
                for img in aggregate.images
            ],
        )

    async def _update_product_rating(self, product_id: int):
        """Обновить рейтинг товара на основе среднего рейтинга отзывов."""
        from sqlalchemy import update, func, select
        from src.catalog.product.infrastructure.models.product import Product
        from src.catalog.review.infrastructure.models.review import Review

        avg_stmt = (
            select(func.avg(Review.rating))
            .where(Review.product_id == product_id)
        )
        result = await self.uow.session.execute(avg_stmt)
        avg_rating = result.scalar()

        stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(rating=avg_rating)
        )
        await self.uow.session.execute(stmt)
