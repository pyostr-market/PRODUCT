"""SQLAlchemy реализация репозитория для отзывов."""

from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.review.domain.aggregates.review import ReviewAggregate
from src.catalog.review.domain.aggregates.review_image import ReviewImageAggregate
from src.catalog.review.domain.exceptions import ReviewNotFoundError
from src.catalog.review.domain.repository.review import ReviewRepository
from src.catalog.review.infrastructure.models.review import Review
from src.catalog.review.infrastructure.models.review_image import ReviewImage
from src.uploads.infrastructure.models.upload_history import UploadHistory


class SqlAlchemyReviewRepository(ReviewRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, review_id: int) -> Optional[ReviewAggregate]:
        stmt = (
            select(Review)
            .options(
                selectinload(Review.images).selectinload(ReviewImage.upload),
            )
            .where(Review.id == review_id)
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    async def get_by_product_id(
        self,
        product_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[list[ReviewAggregate], int]:
        # Счётчик
        count_stmt = (
            select(func.count(Review.id))
            .where(Review.product_id == product_id)
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Данные
        stmt = (
            select(Review)
            .options(
                selectinload(Review.images).selectinload(ReviewImage.upload),
            )
            .where(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        aggregates = [self._to_aggregate(m) for m in models]
        return aggregates, total

    async def create(self, aggregate: ReviewAggregate) -> ReviewAggregate:
        model = Review(
            product_id=aggregate.product_id,
            user_id=aggregate.user_id,
            username=aggregate.username,
            rating=aggregate.rating,
            text=aggregate.text,
        )
        self.db.add(model)
        await self.db.flush()

        for image in aggregate.images:
            image_model = ReviewImage(
                review_id=model.id,
                upload_id=image.upload_id,
                ordering=image.ordering,
            )
            self.db.add(image_model)

        await self.db.flush()

        aggregate._set_id(model.id)
        return aggregate

    async def update(self, aggregate: ReviewAggregate) -> ReviewAggregate:
        model = await self.db.get(Review, aggregate.id)
        if not model:
            raise ReviewNotFoundError(aggregate.id)

        model.rating = aggregate.rating
        model.text = aggregate.text

        # Удаляем все изображения и создаём заново
        # (или можно делать более тонкую синхронизацию)
        # Для простоты — полная замена
        existing_upload_ids = {img.upload_id for img in model.images}
        new_upload_ids = {img.upload_id for img in aggregate.images}

        # Удаляем те, которых больше нет
        for img in list(model.images):
            if img.upload_id not in new_upload_ids:
                self.db.delete(img)

        # Добавляем новые
        existing_ids_set = {img.upload_id for img in model.images}
        for image in aggregate.images:
            if image.upload_id not in existing_ids_set:
                image_model = ReviewImage(
                    review_id=model.id,
                    upload_id=image.upload_id,
                    ordering=image.ordering,
                )
                self.db.add(image_model)

        await self.db.flush()
        return aggregate

    async def delete(self, review_id: int) -> bool:
        model = await self.db.get(Review, review_id)
        if not model:
            return False
        await self.db.delete(model)
        await self.db.flush()
        return True

    async def get_average_rating_for_product(self, product_id: int) -> Optional[float]:
        """Получить средний рейтинг для товара."""
        stmt = (
            select(func.avg(Review.rating))
            .where(Review.product_id == product_id)
        )
        result = await self.db.execute(stmt)
        avg_value = result.scalar()

        if avg_value is None:
            return None

        return float(avg_value)

    async def get_user_review_for_product(
        self,
        user_id: int,
        product_id: int,
    ) -> Optional[ReviewAggregate]:
        """Получить отзыв пользователя для конкретного товара."""
        stmt = (
            select(Review)
            .options(
                selectinload(Review.images).selectinload(ReviewImage.upload),
            )
            .where(
                Review.product_id == product_id,
                Review.user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    # -----------------------------
    # Mapping
    # -----------------------------

    def _to_aggregate(self, model: Review) -> ReviewAggregate:
        """Преобразовать ORM-модель в доменный агрегат."""
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

        aggregate = ReviewAggregate(
            product_id=model.product_id,
            user_id=model.user_id,
            username=model.username,
            rating=model.rating,
            text=model.text,
            images=images,
            review_id=model.id,
        )
        return aggregate
