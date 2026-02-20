from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.suppliers.api.schemas.schemas import (
    SupplierCreateSchema,
    SupplierReadSchema,
    SupplierUpdateSchema,
)
from src.catalog.suppliers.application.dto.supplier import (
    SupplierCreateDTO,
    SupplierUpdateDTO,
)
from src.catalog.suppliers.composition import SupplierComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

supplier_commands_router = APIRouter(tags=["Suppliers"])


@supplier_commands_router.post(
    "/",
    status_code=200,
    summary="Создать поставщика",
    dependencies=[Depends(require_permissions("supplier:create"))],
)
async def create(
    payload: SupplierCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = SupplierComposition.build_create_command(db)
    dto = await commands.execute(SupplierCreateDTO(**payload.model_dump()), user=user)
    return api_response(SupplierReadSchema.model_validate(dto))


@supplier_commands_router.put(
    "/{supplier_id}",
    summary="Обновить поставщика",
    dependencies=[Depends(require_permissions("supplier:update"))],
)
async def update(
    supplier_id: int,
    payload: SupplierUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = SupplierComposition.build_update_command(db)
    dto = await commands.execute(supplier_id, SupplierUpdateDTO(**payload.model_dump()), user=user)
    return api_response(SupplierReadSchema.model_validate(dto))


@supplier_commands_router.delete(
    "/{supplier_id}",
    summary="Удалить поставщика",
    dependencies=[Depends(require_permissions("supplier:delete"))],
)
async def delete(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = SupplierComposition.build_delete_command(db)
    await commands.execute(supplier_id, user=user)
    return api_response({"deleted": True})
