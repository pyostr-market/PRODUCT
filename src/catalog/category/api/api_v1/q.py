from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.api.schemas.schemas import (
    CategoryListResponse,
    CategoryReadSchema,
)
from src.catalog.category.composition import CategoryComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

category_q_router = APIRouter(tags=["Categories"])


@category_q_router.get("/{category_id}", summary="Получить категорию по ID")
async def get_by_id(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    queries = CategoryComposition.build_queries(db)
    dto = await queries.get_by_id(category_id)
    return api_response(CategoryReadSchema.model_validate(dto))


@category_q_router.get("/", summary="Получить список категорий")
async def filter_categories(
    name: str | None = Query(None, description="Фильтр по имени"),
    limit: int = Query(10, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = CategoryComposition.build_queries(db)
    items, total = await queries.filter(name, limit, offset)

    return api_response(
        CategoryListResponse(
            total=total,
            items=[CategoryReadSchema.model_validate(i) for i in items],
        )
    )
