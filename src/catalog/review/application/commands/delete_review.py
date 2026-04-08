"""Команда удаления отзыва."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.catalog.review.application.dto.review import ReviewAuditDTO
from src.catalog.review.domain.exceptions import ReviewNotFoundError
from src.catalog.review.domain.repository.review import ReviewRepository
from src.catalog.review.domain.repository.review_audit import ReviewAuditRepository
from src.catalog.review.infrastructure.models.review import Review
from src.catalog.review.infrastructure.models.review_image import ReviewImage
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus


class DeleteReviewCommand:

    def __init__(
        self,
        repository: ReviewRepository,
        audit_repository: ReviewAuditRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, review_id: int, user: User) -> bool:
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

            # Сначала записываем audit лог (до удаления, чтобы FK был валиден)
            await self.audit_repository.log(
                ReviewAuditDTO(
                    review_id=review_id,
                    action="delete",
                    old_data=old_data,
                    new_data=None,
                    user_id=user.id,
                    fio=user.fio,
                )
            )

            # Затем удаляем отзыв
            await session.delete(model)
            await session.flush()

            # Обновляем рейтинг товара (может стать None если отзывов больше нет)
            await self._update_product_rating(aggregate.product_id)

        return True

    def _capture_state(self, aggregate) -> dict:
        """Зафиксировать состояние перед удалением."""
        return {
            "product_id": aggregate.product_id,
            "user_id": aggregate.user_id,
            "username": aggregate.username,
            "rating": str(aggregate.rating),
            "text": aggregate.text,
            "image_upload_ids": [img.upload_id for img in aggregate.images],
        }

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

    def _to_aggregate(self, model: Review):
        from src.catalog.review.domain.aggregates.review import ReviewAggregate
        from src.catalog.review.domain.aggregates.review_image import ReviewImageAggregate

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
