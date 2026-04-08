"""API запросы для модуля отзывов (получение отзывов)."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.catalog.review.api.schemas.review import (
    ReviewListResponse,
    ReviewReadSchema,
)
from src.catalog.review.composition import ReviewComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

review_queries_router = APIRouter(
    tags=["Отзывы"],
)


@review_queries_router.get(
    "/{review_id}",
    summary="Получить отзыв по ID",
    description="""
    Возвращает один отзыв по его идентификатору.
    """,
    response_description="Отзыв в стандартной обёртке API",
    responses={
        200: {
            "description": "Отзыв найден",
        },
        404: {"description": "Отзыв не найден"},
    },
)
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
):
    queries = ReviewComposition.build_queries(db)
    dto = await queries.get_review(review_id)
    return api_response(ReviewReadSchema.model_validate(dto, from_attributes=True))


@review_queries_router.get(
    "/product/{product_id}",
    summary="Получить отзывы товара",
    description="""
    Возвращает список отзывов для конкретного товара с пагинацией.

    Также возвращает средний рейтинг товара.
    """,
    response_description="Список отзывов в стандартной обёртке API",
    responses={
        200: {
            "description": "Список отзывов",
        },
    },
)
async def get_reviews_by_product(
    product_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    queries = ReviewComposition.build_queries(db)
    dto = await queries.get_reviews_by_product(product_id, limit=limit, offset=offset)
    return api_response(ReviewListResponse.model_validate(dto, from_attributes=True))
