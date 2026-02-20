from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.suppliers.api.schemas.schemas import SupplierListResponse, SupplierReadSchema
from src.catalog.suppliers.composition import SupplierComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

supplier_q_router = APIRouter(tags=["Suppliers"])


@supplier_q_router.get("/{supplier_id}", summary="Получить поставщика по ID")
async def get_by_id(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
):
    queries = SupplierComposition.build_queries(db)
    dto = await queries.get_by_id(supplier_id)
    return api_response(SupplierReadSchema.model_validate(dto))


@supplier_q_router.get("/", summary="Получить список поставщиков")
async def filter_suppliers(
    name: str | None = Query(None, description="Фильтр по имени"),
    limit: int = Query(10, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = SupplierComposition.build_queries(db)
    items, total = await queries.filter(name, limit, offset)

    return api_response(
        SupplierListResponse(
            total=total,
            items=[SupplierReadSchema.model_validate(i) for i in items],
        )
    )
