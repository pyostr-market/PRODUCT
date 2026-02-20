from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.schemas import ProductListResponse, ProductReadSchema
from src.catalog.product.composition import ProductComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

product_q_router = APIRouter(tags=["Products"])


@product_q_router.get("/related/variants", summary="Получить связанные товары")
async def related_products(
    product_id: int | None = Query(None),
    name: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    queries = ProductComposition.build_queries(db)
    items = await queries.related(product_id=product_id, name=name)

    return api_response(
        ProductListResponse(
            total=len(items),
            items=[ProductReadSchema.model_validate(item) for item in items],
        )
    )


@product_q_router.get("/{product_id}", summary="Получить товар по ID")
async def get_by_id(product_id: int, db: AsyncSession = Depends(get_db)):
    queries = ProductComposition.build_queries(db)
    dto = await queries.get_by_id(product_id)
    return api_response(ProductReadSchema.model_validate(dto))


@product_q_router.get("/", summary="Получить список товаров")
async def filter_products(
    name: str | None = Query(None),
    category_id: int | None = Query(None),
    product_type_id: int | None = Query(None),
    limit: int = Query(10, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = ProductComposition.build_queries(db)
    items, total = await queries.filter(
        name=name,
        category_id=category_id,
        product_type_id=product_type_id,
        limit=limit,
        offset=offset,
    )

    return api_response(
        ProductListResponse(
            total=total,
            items=[ProductReadSchema.model_validate(item) for item in items],
        )
    )
