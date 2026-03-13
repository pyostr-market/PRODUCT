from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.category.domain.aggregates.category import (
    CategoryAggregate,
    CategoryImageAggregate,
)
from src.catalog.category.domain.exceptions import (
    CategoryCircularDependency,
    CategoryNotFound,
)
from src.catalog.category.domain.repository.category import CategoryRepository
from src.catalog.category.infrastructure.models.categories import Category
from src.catalog.category.infrastructure.models.category_image import CategoryImage
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.catalog.manufacturer.infrastructure.models.manufacturer import Manufacturer


class SqlAlchemyCategoryRepository(CategoryRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _has_cycle(self, category_id: int, new_parent_id: Optional[int]) -> bool:
        """
        Проверить, создаст ли установка new_parent_id циклическую зависимость.

        Возвращает True, если new_parent_id является потомком category_id
        (т.е. установка создаст цикл).
        """
        if new_parent_id is None:
            return False

        # Если пытаемся установить родителя равным самой категории — это цикл
        if new_parent_id == category_id:
            return True

        # Проверяем, является ли new_parent_id потомком category_id
        # (т.е. category_id находится в цепочке родителей new_parent_id)
        current_id = new_parent_id
        visited = set()

        while current_id is not None:
            if current_id in visited:
                # Обнаружен цикл в существующих данных
                return True
            visited.add(current_id)

            if current_id == category_id:
                # category_id является родителем new_parent_id — будет цикл
                return True

            # Получаем родителя текущей категории
            stmt = select(Category.parent_id).where(Category.id == current_id)
            result = await self.db.execute(stmt)
            parent_id = result.scalar_one_or_none()
            current_id = parent_id

        return False

    async def get(self, category_id: int) -> Optional[CategoryAggregate]:
        stmt = (
            select(Category)
            .options(
                selectinload(Category.images).selectinload(CategoryImage.upload),
                selectinload(Category.parent),
                selectinload(Category.manufacturer),
            )
            .where(Category.id == category_id)
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    async def create(self, aggregate: CategoryAggregate) -> CategoryAggregate:
        model = Category(
            name=aggregate.name,
            description=aggregate.description,
            parent_id=aggregate.parent_id,
            manufacturer_id=aggregate.manufacturer_id,
        )

        self.db.add(model)
        await self.db.flush()

        # Сохраняем изображение, если есть
        if aggregate.image:
            image_model = CategoryImage(
                category_id=model.id,
                upload_id=aggregate.image.upload_id,
            )
            self.db.add(image_model)

        await self.db.flush()

        aggregate._set_id(model.id)
        return aggregate

    async def delete(self, category_id: int) -> bool:
        model = await self.db.get(Category, category_id)
        if not model:
            return False

        # При удалении категории записи из category_images удаляются (CASCADE),
        # но файлы в S3 остаются
        await self.db.delete(model)
        return True

    async def update(self, aggregate: CategoryAggregate) -> CategoryAggregate:
        # Проверяем на циклическую зависимость перед обновлением parent_id
        if aggregate.parent_id is not None:
            if await self._has_cycle(aggregate.id, aggregate.parent_id):
                raise CategoryCircularDependency()

        # Сначала удаляем объект из сессии, чтобы SQLAlchemy не синхронизировал
        # старое состояние parent_id при flush()
        existing = await self.db.get(Category, aggregate.id)
        if existing is not None:
            self.db.expunge(existing)

        # Обновляем parent_id через raw SQL, чтобы полностью обойти
        # SQLAlchemy unit of work и избежать CircularDependencyError
        from sqlalchemy import text
        await self.db.execute(
            text("UPDATE categories SET parent_id = :parent_id WHERE id = :id"),
            {"parent_id": aggregate.parent_id, "id": aggregate.id}
        )

        # Загружаем модель заново БЕЗ relationship на parent для обновления остальных полей
        stmt = (
            select(Category)
            .options(
                selectinload(Category.images).selectinload(CategoryImage.upload),
            )
            .where(Category.id == aggregate.id)
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise CategoryNotFound()

        # Обновляем простые атрибуты
        model.name = aggregate.name
        model.description = aggregate.description
        model.manufacturer_id = aggregate.manufacturer_id

        # Обновляем изображение
        if aggregate.image:
            if model.images:
                # Обновляем существующее
                model.images[0].upload_id = aggregate.image.upload_id
            else:
                # Создаём новое
                image_model = CategoryImage(
                    category_id=model.id,
                    upload_id=aggregate.image.upload_id,
                )
                self.db.add(image_model)
        elif model.images and not aggregate.image:
            # Удаляем изображение
            await self.db.delete(model.images[0])

        await self.db.flush()
        return aggregate

    def _to_aggregate(self, model: Category) -> CategoryAggregate:
        parent = None
        if model.parent:
            parent = CategoryAggregate(
                category_id=model.parent.id,
                name=model.parent.name,
                description=model.parent.description,
                parent_id=model.parent.parent_id,
                manufacturer_id=model.parent.manufacturer_id,
            )

        manufacturer = None
        if model.manufacturer:
            manufacturer = ManufacturerAggregate(
                manufacturer_id=model.manufacturer.id,
                name=model.manufacturer.name,
                description=model.manufacturer.description,
            )

        image = None
        if model.images:
            img = model.images[0]
            image = CategoryImageAggregate(
                upload_id=img.upload_id,
                object_key=img.upload.file_path if img.upload else None,
            )

        return CategoryAggregate(
            category_id=model.id,
            name=model.name,
            description=model.description,
            parent_id=model.parent_id,
            manufacturer_id=model.manufacturer_id,
            image=image,
            parent=parent,
            manufacturer=manufacturer,
        )
