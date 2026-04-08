"""Команда обновления отзыва."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.catalog.review.application.dto.review import (
    ReviewAuditDTO,
    ReviewImageOperationDTO,
    ReviewImageReadDTO,
    ReviewReadDTO,
    ReviewUpdateDTO,
)
from src.catalog.review.domain.aggregates.review import ReviewAggregate
from src.catalog.review.domain.aggregates.review_image import ReviewImageAggregate
from src.catalog.review.domain.exceptions import ReviewNotFoundError
from src.catalog.review.domain.repository.review import ReviewRepository
from src.catalog.review.domain.repository.review_audit import ReviewAuditRepository
from src.catalog.review.infrastructure.models.review import Review
from src.catalog.review.infrastructure.models.review_image import ReviewImage
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus
from src.core.services.images.storage import S3ImageStorageService
from src.uploads.domain.repository.upload_history import UploadHistoryRepository


class UpdateReviewCommand:

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

    async def execute(
        self,
        review_id: int,
        dto: ReviewUpdateDTO,
        user: User,
    ) -> ReviewReadDTO:
        async with self.uow:
            session = self.uow.session

            # Загружаем отзыв через UOW session
            stmt = (
                select(Review)
                .options(
                    selectinload(Review.images).selectinload(ReviewImage.upload),
                )
                .where(Review.id == review_id)
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if not model:
                raise ReviewNotFoundError(review_id)

            # Проверяем права владения
            aggregate = self._to_aggregate(model)
            aggregate.check_ownership(user.id)

            old_data = self._capture_state(aggregate)

            # Применяем изменения
            aggregate.update(rating=dto.rating, text=dto.text)

            if dto.images is not None:
                await self._apply_image_operations(aggregate, dto.images)

            # Сохраняем изменения
            model.rating = aggregate.rating
            model.text = aggregate.text

            # Синхронизируем изображения
            new_upload_ids = {img.upload_id for img in aggregate.images}
            for img in list(model.images):
                if img.upload_id not in new_upload_ids:
                    session.delete(img)

            existing_ids = {img.upload_id for img in model.images}
            for image in aggregate.images:
                if image.upload_id not in existing_ids:
                    session.add(ReviewImage(
                        review_id=model.id,
                        upload_id=image.upload_id,
                        ordering=image.ordering,
                    ))

            await session.flush()

            new_data = self._capture_state(aggregate)

            if old_data != new_data:
                await self.audit_repository.log(
                    ReviewAuditDTO(
                        review_id=aggregate.id,
                        action="update",
                        old_data=old_data,
                        new_data=new_data,
                        user_id=user.id,
                        fio=user.fio,
                    )
                )

            # Обновляем рейтинг товара
            await self._update_product_rating(aggregate.product_id)

        return self._to_read_dto(aggregate)

    async def _apply_image_operations(
        self,
        aggregate: ReviewAggregate,
        operations: list[ReviewImageOperationDTO],
    ):
        for op in operations:
            if op.action == "delete" and op.upload_id:
                aggregate.remove_image_by_upload_id(op.upload_id)
            elif op.action == "create" and op.upload_id:
                upload_record = await self.upload_history_repository.get(op.upload_id)
                if not upload_record:
                    raise ValueError(f"Upload with id {op.upload_id} not found")
                aggregate.add_image(
                    ReviewImageAggregate(
                        upload_id=upload_record.upload_id,
                        ordering=op.ordering if op.ordering is not None else len(aggregate.images),
                        object_key=upload_record.file_path,
                    )
                )

    def _capture_state(self, aggregate: ReviewAggregate) -> dict[str, Any]:
        return {
            "product_id": aggregate.product_id,
            "user_id": aggregate.user_id,
            "username": aggregate.username,
            "rating": str(aggregate.rating),
            "text": aggregate.text,
            "image_upload_ids": [img.upload_id for img in aggregate.images],
        }

    def _to_read_dto(self, aggregate: ReviewAggregate) -> ReviewReadDTO:
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
        from sqlalchemy import update, func
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

    def _to_aggregate(self, model: Review) -> ReviewAggregate:
        images = []
        for img in model.images:
            object_key = img.upload.file_path if img.upload else None
            images.append(
                ReviewImageAggregate(
                    upload_id=img.upload_id,
                    ordering=img.ordering,
                    object_key=object_key,
                )
            )
        return ReviewAggregate(
            product_id=model.product_id,
            user_id=model.user_id,
            username=model.username,
            rating=model.rating,
            text=model.text,
            images=images,
            review_id=model.id,
        )
