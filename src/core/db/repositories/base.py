from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import delete as sql_delete, func, select, update as sql_update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db

    # ==============================
    # GET ONE
    # ==============================

    async def get(self, obj_id: int) -> T | None:
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ==============================
    # GET LIST
    # ==============================

    async def get_list(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[T]:
        stmt = (
            select(self.model)
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ==============================
    # FILTER
    # ==============================

    async def filter(self, *conditions: Any) -> Sequence[T]:
        stmt = select(self.model).where(*conditions)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ==============================
    # CREATE
    # ==============================

    async def create(self, data: dict) -> T:
        obj = self.model(**data)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    # ==============================
    # UPDATE (универсальный)
    # ==============================

    async def update(self, obj_id: int, data: dict) -> T | None:
        stmt = (
            sql_update(self.model)
            .where(self.model.id == obj_id)
            .values(**data)
            .execution_options(synchronize_session="fetch")
        )

        await self.db.execute(stmt)
        await self.db.commit()

        return await self.get(obj_id)

    # ==============================
    # DELETE (универсальный)
    # ==============================

    async def delete(self, obj_id: int) -> bool:
        stmt = sql_delete(self.model).where(self.model.id == obj_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    # ==============================
    # EXISTS
    # ==============================

    async def exists(self, obj_id: int) -> bool:
        stmt = select(func.count()).select_from(self.model).where(
            self.model.id == obj_id
        )
        result = await self.db.execute(stmt)
        return result.scalar() > 0

    # ==============================
    # COUNT
    # ==============================

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self.db.execute(stmt)
        return result.scalar()