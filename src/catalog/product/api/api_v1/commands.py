import json
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.schemas import (
    ProductImageOperationSchema,
    ProductReadSchema,
)
from src.catalog.product.application.dto.product import (
    ProductAttributeInputDTO,
    ProductCreateDTO,
    ProductImageInputDTO,
    ProductImageOperationDTO,
    ProductUpdateDTO,
)
from src.catalog.product.composition import ProductComposition
from src.catalog.product.domain.exceptions import ProductInvalidImage, ProductInvalidPayload
from src.core.api.normalizers import normalize_optional_fk
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

product_commands_router = APIRouter(
    tags=["Товары"],
)


def _is_image_bytes(data: bytes) -> bool:
    if not data:
        return False

    if data.startswith(b"\xff\xd8\xff"):
        return True
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return True
    if data.startswith(b"BM"):
        return True
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        return True
    return False


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default

    normalized = value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}


def _parse_attributes(attributes_json: str | None) -> list[ProductAttributeInputDTO]:
    if not attributes_json:
        return []

    try:
        payload = json.loads(attributes_json)
    except json.JSONDecodeError as exc:
        raise ProductInvalidPayload(details={"reason": "invalid_json", "error": str(exc)})

    if not isinstance(payload, list):
        raise ProductInvalidPayload(details={"reason": "attributes_must_be_list"})

    mapped = []
    for item in payload:
        if not isinstance(item, dict):
            raise ProductInvalidPayload(details={"reason": "attribute_item_must_be_object"})

        mapped.append(
            ProductAttributeInputDTO(
                name=str(item.get("name", "")).strip(),
                value=str(item.get("value", "")).strip(),
                is_filterable=bool(item.get("is_filterable", False)),
            )
        )

    return mapped


async def _build_images_dto(
    images: list[UploadFile] | None,
    image_is_main: list[str] | None,
) -> list[ProductImageInputDTO]:
    if not images:
        return []

    mapped: list[ProductImageInputDTO] = []

    for idx, image_file in enumerate(images):
        payload = await image_file.read()

        if image_file.content_type and not image_file.content_type.startswith("image/"):
            raise ProductInvalidImage(
                details={"filename": image_file.filename, "content_type": image_file.content_type}
            )

        if not _is_image_bytes(payload):
            raise ProductInvalidImage(
                details={"filename": image_file.filename, "reason": "unsupported_or_invalid_binary"}
            )

        is_main_value = image_is_main[idx] if image_is_main and idx < len(image_is_main) else None
        mapped.append(
            ProductImageInputDTO(
                image=payload,
                image_name=image_file.filename or "test.jpg",
                is_main=_to_bool(is_main_value, default=(idx == 0)),
            )
        )

    if mapped and not any(i.is_main for i in mapped):
        mapped[0].is_main = True

    return mapped


async def _build_image_operations_dto(
    images_json: str | None,
    new_images: list[UploadFile] | None,
    new_image_is_main: list[str] | None,
) -> list[ProductImageOperationDTO] | None:
    """
    Построение DTO для операций с изображениями при обновлении товара.

    images_json - JSON-список операций {action, image_id, is_main, ordering}
    new_images - новые файлы изображений для action=to_create
    """
    if not images_json and not new_images:
        return None

    operations: list[ProductImageOperationDTO] = []
    new_image_idx = 0  # Счётчик для файлов новых изображений

    if images_json:
        try:
            payload = json.loads(images_json)
        except json.JSONDecodeError as exc:
            raise ProductInvalidPayload(details={"reason": "invalid_images_json", "error": str(exc)})

        if not isinstance(payload, list):
            raise ProductInvalidPayload(details={"reason": "images_must_be_list"})

        for item in payload:
            if not isinstance(item, dict):
                raise ProductInvalidPayload(details={"reason": "image_operation_must_be_object"})

            action = item.get("action")
            if action not in ("to_create", "to_delete", "pass"):
                raise ProductInvalidPayload(details={"reason": "invalid_action", "action": action})

            op = ProductImageOperationDTO(
                action=action,  # type: ignore[arg-type]
                image_id=item.get("image_id"),
                is_main=_to_bool(str(item.get("is_main", "")), default=False),
                ordering=item.get("ordering"),
            )

            if action == "to_create":
                if new_images and new_image_idx < len(new_images):
                    image_file = new_images[new_image_idx]
                    image_payload = await image_file.read()

                    if image_file.content_type and not image_file.content_type.startswith("image/"):
                        raise ProductInvalidImage(
                            details={"filename": image_file.filename, "content_type": image_file.content_type}
                        )

                    if not _is_image_bytes(image_payload):
                        raise ProductInvalidImage(
                            details={"filename": image_file.filename, "reason": "unsupported_or_invalid_binary"}
                        )

                    op.image = image_payload
                    op.image_name = image_file.filename or "image.jpg"
                    is_main_value = (
                        new_image_is_main[new_image_idx]
                        if new_image_is_main and new_image_idx < len(new_image_is_main)
                        else None
                    )
                    op.is_main = _to_bool(is_main_value, default=False)
                    new_image_idx += 1
                else:
                    raise ProductInvalidPayload(details={"reason": "missing_image_file_for_to_create"})

            operations.append(op)

    return operations if operations else None


@product_commands_router.post(
    "",
    status_code=200,
    summary="Создать товар",
    description="""
    Создаёт новый товар, включая атрибуты и изображения.

    Права:
    - Требуется permission: `product:create`

    Сценарии:
    - Создание карточки товара при заведении ассортимента.
    - Импорт товаров с пользовательскими атрибутами.
    - Загрузка нескольких изображений с выбором главного.
    """,
    response_description="Созданный товар в стандартной обёртке API",
    responses={
        200: {
            "description": "Товар успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 3001,
                            "name": "Смартфон X",
                            "description": "Флагманская модель",
                            "price": "59990.00",
                            "category_id": 101,
                            "supplier_id": 210,
                            "product_type_id": 5,
                            "images": [
                                {
                                    "image_url": "https://cdn.example.com/product/smartphone-x-main.jpg",
                                    "is_main": True,
                                }
                            ],
                            "attributes": [
                                {"name": "RAM", "value": "8 GB", "is_filterable": True}
                            ],
                        },
                    }
                }
            },
        },
        400: {
            "description": "Некорректные данные товара (например, битый JSON атрибутов)",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "product_invalid_payload",
                            "message": "Некорректный payload товара",
                            "details": {"reason": "invalid_json"},
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("product:create"))],
)
async def create(
    name: Annotated[str, Form(...)],
    price: Annotated[Decimal, Form(...)],
    description: Annotated[str | None, Form()] = None,
    category_id: Annotated[int | None, Form()] = None,
    supplier_id: Annotated[int | None, Form()] = None,
    product_type_id: Annotated[int | None, Form()] = None,
    attributes_json: Annotated[str | None, Form()] = None,
    images: Annotated[list[UploadFile] | None, File()] = None,
    image_is_main: Annotated[list[str] | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    images_dto = await _build_images_dto(images, image_is_main)
    attributes_dto = _parse_attributes(attributes_json)

    commands = ProductComposition.build_create_command(db)
    dto = await commands.execute(
        ProductCreateDTO(
            name=name,
            description=description,
            price=price,
            category_id=normalize_optional_fk(category_id),
            supplier_id=normalize_optional_fk(supplier_id),
            product_type_id=normalize_optional_fk(product_type_id),
            images=images_dto,
            attributes=attributes_dto,
        ),
        user=user,
    )

    return api_response(ProductReadSchema.model_validate(dto))


@product_commands_router.put(
    "/{product_id}",
    summary="Обновить товар",
    description="""
    Частично обновляет товар по идентификатору.

    Права:
    - Требуется permission: `product:update`

    Работа с изображениями:
    - Изображения передаются через `images_json` (JSON-массив операций) + `images` (файлы для to_create).
    - Каждая операция имеет поле `action`: `to_create`, `to_delete`, `pass`.
    - `to_create` — загрузить новое изображение (требуется файл в `images`).
    - `to_delete` — удалить существующее изображение (требуется `image_id`).
    - `pass` — сохранить существующее изображение (требуется `image_id`).
    
    Пример `images_json`:
    ```json
    [
      {"action": "pass", "image_id": 123, "is_main": true},
      {"action": "to_delete", "image_id": 456},
      {"action": "to_create", "is_main": false}
    ]
    ```
    
    Сценарии:
    - Изменение цены и описания товара.
    - Добавление/удаление изображений товара.
    - Обновление или перезапись набора атрибутов.
    """,
    response_description="Обновлённый товар в стандартной обёртке API",
    responses={
        200: {
            "description": "Товар успешно обновлён",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 3001,
                            "name": "Смартфон X Pro",
                            "description": "Обновлённая модель",
                            "price": "64990.00",
                            "category_id": 101,
                            "supplier_id": 210,
                            "product_type_id": 5,
                            "images": [
                                {
                                    "image_url": "https://cdn.example.com/product/smartphone-x-pro-main.jpg",
                                    "is_main": True,
                                }
                            ],
                            "attributes": [
                                {"name": "RAM", "value": "12 GB", "is_filterable": True}
                            ],
                        },
                    }
                }
            },
        },
        400: {"description": "Некорректные входные данные"},
        404: {"description": "Товар не найден"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("product:update"))],
)
async def update(
    product_id: int,
    name: Annotated[str | None, Form()] = None,
    price: Annotated[Decimal | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    category_id: Annotated[int | None, Form()] = None,
    supplier_id: Annotated[int | None, Form()] = None,
    product_type_id: Annotated[int | None, Form()] = None,
    attributes_json: Annotated[str | None, Form()] = None,
    images_json: Annotated[str | None, Form()] = None,
    images: Annotated[list[UploadFile] | None, File()] = None,
    image_is_main: Annotated[list[str] | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    images_dto = None
    if images_json is not None or images is not None:
        images_dto = await _build_image_operations_dto(images_json, images, image_is_main)

    attributes_dto = None
    if attributes_json is not None:
        attributes_dto = _parse_attributes(attributes_json)

    commands = ProductComposition.build_update_command(db)
    dto = await commands.execute(
        product_id,
        ProductUpdateDTO(
            name=name,
            description=description,
            price=price,
            category_id=normalize_optional_fk(category_id),
            supplier_id=normalize_optional_fk(supplier_id),
            product_type_id=normalize_optional_fk(product_type_id),
            images=images_dto,
            attributes=attributes_dto,
        ),
        user=user,
    )

    return api_response(ProductReadSchema.model_validate(dto))


@product_commands_router.delete(
    "/{product_id}",
    summary="Удалить товар",
    description="""
    Удаляет товар по идентификатору.

    Права:
    - Требуется permission: `product:delete`

    Сценарии:
    - Удаление снятого с продажи товара.
    - Очистка тестовых или дубль-записей.
    """,
    response_description="Флаг успешного удаления",
    responses={
        200: {
            "description": "Товар успешно удалён",
            "content": {
                "application/json": {
                    "example": {"success": True, "data": {"deleted": True}}
                }
            },
        },
        404: {"description": "Товар не найден"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("product:delete"))],
)
async def delete(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ProductComposition.build_delete_command(db)
    await commands.execute(product_id, user=user)
    return api_response({"deleted": True})
