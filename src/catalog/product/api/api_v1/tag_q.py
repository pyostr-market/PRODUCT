"""Query endpoints для тегов (чтение, без проверки прав)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.schemas import (
    TagReadSchema,
    TagListResponse,
    ProductTagReadSchema,
    ProductTagListResponse,
)
from src.catalog.product.application.queries.tag_queries import TagQueries
from src.catalog.product.composition import ProductComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

tag_q_router = APIRouter(
    prefix="/tags",
    tags=["Теги товаров"],
)


def _build_tag_queries(db: AsyncSession) -> TagQueries:
    return ProductComposition.build_tag_queries(db)


@tag_q_router.get(
    "",
    summary="Получить все теги",
    response_model=TagListResponse,
)
async def get_all_tags(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить список всех тегов с пагинацией.

    Не требует проверки прав — доступно авторизованным и публичным клиентам.
    """
    queries = _build_tag_queries(db)
    tags, total = await queries.get_all_tags(limit=limit, offset=offset)
    return api_response(
        TagListResponse(
            total=total,
            items=[TagReadSchema.model_validate(tag) for tag in tags],
        )
    )


@tag_q_router.get(
    "/{tag_id}",
    summary="Получить тег по ID",
    response_model=TagReadSchema,
)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить тег по ID.

    Не требует проверки прав — доступно авторизованным и публичным клиентам.
    """
    from fastapi import HTTPException

    queries = _build_tag_queries(db)
    tag = await queries.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Тег не найден")
    return api_response(TagReadSchema.model_validate(tag))


@tag_q_router.get(
    "/product-tags/{product_id}",
    summary="Получить все теги товара",
    response_model=ProductTagListResponse,
)
async def get_product_tags(
    product_id: int,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить все теги, связанные с товаром.

    Не требует проверки прав — доступно авторизованным и публичным клиентам.
    """
    queries = _build_tag_queries(db)
    product_tags, total = await queries.get_product_tags(
        product_id=product_id, limit=limit, offset=offset
    )

    return api_response(
        ProductTagListResponse(
            total=total,
            items=[
                ProductTagReadSchema(
                    id=pt.id,
                    product_id=pt.product_id,
                    tag_id=pt.tag_id,
                    tag=TagReadSchema(
                        tag_id=pt.tag.tag_id,
                        name=pt.tag.name,
                        description=pt.tag.description,
                    ),
                )
                for pt in product_tags
            ],
        )
    )
