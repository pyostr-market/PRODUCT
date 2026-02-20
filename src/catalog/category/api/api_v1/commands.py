from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.api.schemas.schemas import CategoryReadSchema
from src.catalog.category.application.dto.category import (
    CategoryCreateDTO,
    CategoryImageInputDTO,
    CategoryUpdateDTO,
)
from src.catalog.category.composition import CategoryComposition
from src.catalog.category.domain.exceptions import (
    CategoryImagesOrderingMismatch,
    CategoryInvalidImage,
)
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

category_commands_router = APIRouter(tags=["Categories"])


def _normalize_optional_fk(value: int | None) -> int | None:
    if value is None or value <= 0:
        return None
    return value


def _is_image_bytes(data: bytes) -> bool:
    if not data:
        return False

    if data.startswith(b"\xff\xd8\xff"):
        return True  # JPEG
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return True  # PNG
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return True  # GIF
    if data.startswith(b"BM"):
        return True  # BMP
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        return True  # WEBP
    return False


async def _build_images_dto(
    images: list[UploadFile],
    orderings: list[int],
) -> list[CategoryImageInputDTO]:
    if len(images) != len(orderings):
        raise CategoryImagesOrderingMismatch(
            details={"images_count": len(images), "orderings_count": len(orderings)}
        )

    mapped: list[CategoryImageInputDTO] = []

    for image_file, ordering in zip(images, orderings):
        payload = await image_file.read()

        if image_file.content_type and not image_file.content_type.startswith("image/"):
            raise CategoryInvalidImage(
                details={"filename": image_file.filename, "content_type": image_file.content_type}
            )

        if not _is_image_bytes(payload):
            raise CategoryInvalidImage(
                details={"filename": image_file.filename, "reason": "unsupported_or_invalid_binary"}
            )

        mapped.append(
            CategoryImageInputDTO(
                image=payload,
                image_name=image_file.filename or "test.jpg",
                ordering=ordering,
            )
        )

    return mapped


@category_commands_router.post(
    "/",
    status_code=200,
    summary="Создать категорию",
    dependencies=[Depends(require_permissions("category:create"))],
)
async def create(
    name: Annotated[str, Form(...)],
    images: Annotated[list[UploadFile], File(...)],
    orderings: Annotated[list[int], Form(...)],
    description: Annotated[str | None, Form()] = None,
    parent_id: Annotated[int | None, Form()] = None,
    manufacturer_id: Annotated[int | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    images_dto = await _build_images_dto(images, orderings)
    commands = CategoryComposition.build_create_command(db)
    dto = await commands.execute(
        CategoryCreateDTO(
            name=name,
            description=description,
            parent_id=_normalize_optional_fk(parent_id),
            manufacturer_id=_normalize_optional_fk(manufacturer_id),
            images=images_dto,
        ),
        user=user,
    )
    return api_response(CategoryReadSchema.model_validate(dto))


@category_commands_router.put(
    "/{category_id}",
    summary="Обновить категорию",
    dependencies=[Depends(require_permissions("category:update"))],
)
async def update(
    category_id: int,
    name: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    parent_id: Annotated[int | None, Form()] = None,
    manufacturer_id: Annotated[int | None, Form()] = None,
    images: Annotated[list[UploadFile] | None, File()] = None,
    orderings: Annotated[list[int] | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if (images is None) != (orderings is None):
        raise CategoryImagesOrderingMismatch(
            msg="Для обновления изображений нужно передать и images, и orderings",
            details={"images_is_none": images is None, "orderings_is_none": orderings is None},
        )

    images_dto = None
    if images is not None and orderings is not None:
        images_dto = await _build_images_dto(images, orderings)

    commands = CategoryComposition.build_update_command(db)
    dto = await commands.execute(
        category_id,
        CategoryUpdateDTO(
            name=name,
            description=description,
            parent_id=_normalize_optional_fk(parent_id),
            manufacturer_id=_normalize_optional_fk(manufacturer_id),
            images=images_dto,
        ),
        user=user,
    )
    return api_response(CategoryReadSchema.model_validate(dto))


@category_commands_router.delete(
    "/{category_id}",
    summary="Удалить категорию",
    dependencies=[Depends(require_permissions("category:delete"))],
)
async def delete(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = CategoryComposition.build_delete_command(db)
    await commands.execute(category_id, user=user)
    return api_response({"deleted": True})
