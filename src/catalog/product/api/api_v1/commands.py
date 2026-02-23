import json
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.schemas import ProductReadSchema
from src.catalog.product.application.dto.product import (
    ProductAttributeInputDTO,
    ProductCreateDTO,
    ProductImageInputDTO,
    ProductImageOperationDTO,
    ProductUpdateDTO,
)
from src.catalog.product.composition import ProductComposition
from src.catalog.product.domain.exceptions import ProductInvalidPayload
from src.core.api.normalizers import normalize_optional_fk
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

product_commands_router = APIRouter(
    tags=["Товары"],
)


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


async def _parse_images_json(images_json: str | None) -> list[ProductImageInputDTO]:
    """
    Парсинг JSON массива изображений для создания товара.

    Формат images_json:
    ```json
    [
      {"upload_id": 1, "is_main": true, "ordering": 0},
      {"upload_id": 2, "is_main": false, "ordering": 1}
    ]
    ```
    """
    if not images_json:
        return []

    try:
        payload = json.loads(images_json)
    except json.JSONDecodeError as exc:
        raise ProductInvalidPayload(details={"reason": "invalid_images_json", "error": str(exc)})

    if not isinstance(payload, list):
        raise ProductInvalidPayload(details={"reason": "images_must_be_list"})

    mapped = []
    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ProductInvalidPayload(details={"reason": "image_item_must_be_object"})

        upload_id = item.get("upload_id")
        if not upload_id:
            raise ProductInvalidPayload(details={"reason": "missing_upload_id", "index": idx})

        try:
            upload_id = int(upload_id)
        except (ValueError, TypeError):
            raise ProductInvalidPayload(details={"reason": "upload_id_must_be_int", "index": idx})

        is_main = _to_bool(str(item.get("is_main", "")), default=(idx == 0))
        ordering = item.get("ordering", idx)
        if isinstance(ordering, str):
            try:
                ordering = int(ordering)
            except ValueError:
                ordering = idx

        mapped.append(
            ProductImageInputDTO(
                upload_id=upload_id,
                is_main=is_main,
                ordering=ordering,
            )
        )

    if mapped and not any(i.is_main for i in mapped):
        mapped[0].is_main = True

    return mapped


async def _build_image_operations_dto(
    images_json: str | None,
) -> list[ProductImageOperationDTO] | None:
    """
    Построение DTO для операций с изображениями при обновлении товара.

    images_json - JSON-список операций {action, upload_id, is_main, ordering}
    """
    if not images_json:
        return None

    try:
        payload = json.loads(images_json)
    except json.DecodeError as exc:
        raise ProductInvalidPayload(details={"reason": "invalid_images_json", "error": str(exc)})

    if not isinstance(payload, list):
        raise ProductInvalidPayload(details={"reason": "images_must_be_list"})

    operations: list[ProductImageOperationDTO] = []

    for item in payload:
        if not isinstance(item, dict):
            raise ProductInvalidPayload(details={"reason": "image_operation_must_be_object"})

        action = item.get("action")
        # Поддерживаем как новые (create, delete, pass), так и старые (to_create, to_delete, pass) названия
        if action not in ("create", "delete", "pass", "to_create", "to_delete"):
            raise ProductInvalidPayload(details={"reason": "invalid_action", "action": action})

        # Нормализуем action
        if action == "to_create":
            action = "create"
        elif action == "to_delete":
            action = "delete"

        op = ProductImageOperationDTO(
            action=action,  # type: ignore[arg-type]
            upload_id=item.get("upload_id"),
            image_url=item.get("image_url"),
            is_main=item.get("is_main", False),
            ordering=item.get("ordering"),
        )

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

    **Формат `images_json`** (массив объектов с upload_id):
    ```json
    [
      {"upload_id": 1, "is_main": true, "ordering": 0},
      {"upload_id": 2, "is_main": false, "ordering": 1}
    ]
    ```

    Каждый элемент массива содержит:
    - `upload_id`: ID предварительно загруженного изображения через UploadHistory
    - `is_main`: флаг главного изображения (true/false)
    - `ordering`: порядок сортировки (int)

    **Формат `attributes_json`** (массив атрибутов):
    ```json
    [
      {"name": "RAM", "value": "8 GB", "is_filterable": true},
      {"name": "Цвет", "value": "Черный", "is_filterable": true}
    ]
    ```
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
                                    "upload_id": 1,
                                    "image_url": "https://cdn.example.com/product/smartphone-x-main.jpg",
                                    "is_main": True,
                                    "ordering": 0
                                }
                            ],
                            "attributes": [
                                {"id": 10, "name": "RAM", "value": "8 GB", "is_filterable": True}
                            ],
                            "category": {
                                "id": 101,
                                "name": "Смартфоны",
                                "description": "Мобильные устройства"
                            },
                            "supplier": {
                                "id": 210,
                                "name": "ООО Поставка Плюс",
                                "contact_email": "sales@supply-plus.example",
                                "phone": "+7-999-123-45-67"
                            },
                            "product_type": {
                                "id": 5,
                                "name": "Смартфоны",
                                "parent_id": None
                            }
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
    images_json: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    images_dto = await _parse_images_json(images_json) if images_json else []
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
    - Изображения передаются через `images_json` (JSON-массив операций).
    - Каждая операция имеет поле `action`: `create`, `update`, `delete`, `pass` (или устаревшие `to_create`, `to_delete`).
    - `create` — добавить изображение (требуется `upload_id`).
    - `update` — обновить изображение (требуется `upload_id`).
    - `delete` — удалить изображение (требуется `upload_id`).
    - `pass` — сохранить существующее изображение (требуется `upload_id`).

    Пример `images_json`:
    ```json
    [
      {"action": "pass", "upload_id": 123, "is_main": true, "ordering": 0},
      {"action": "update", "upload_id": 124, "is_main": false, "ordering": 1},
      {"action": "delete", "upload_id": 456},
      {"action": "create", "upload_id": 789, "is_main": true, "ordering": 2}
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
                                    "upload_id": 1,
                                    "image_url": "https://cdn.example.com/product/smartphone-x-pro-main.jpg",
                                    "is_main": True,
                                    "ordering": 0
                                }
                            ],
                            "attributes": [
                                {"id": 10, "name": "RAM", "value": "12 GB", "is_filterable": True}
                            ],
                            "category": {
                                "id": 101,
                                "name": "Смартфоны",
                                "description": "Мобильные устройства"
                            },
                            "supplier": {
                                "id": 210,
                                "name": "ООО Поставка Плюс",
                                "contact_email": "sales@supply-plus.example",
                                "phone": "+7-999-123-45-67"
                            },
                            "product_type": {
                                "id": 5,
                                "name": "Смартфоны",
                                "parent_id": None
                            }
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
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    images_dto = await _build_image_operations_dto(images_json) if images_json else None

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
