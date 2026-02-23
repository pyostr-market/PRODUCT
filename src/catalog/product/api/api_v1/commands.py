import json
from decimal import Decimal
from pprint import pprint
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.schemas import (
    ProductImageActionSchema,
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


async def _parse_images_json(images_json: str | None) -> list[ProductImageInputDTO]:
    """
    Парсинг JSON массива изображений для создания товара.
    
    Формат images_json:
    ```json
    [
      {"image": <файл в base64>, "is_main": true, "ordering": 0},
      {"image": <файл в base64>, "is_main": false, "ordering": 1}
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

        # Получаем изображение (base64 строка или URL)
        image_data = item.get("image")
        if not image_data:
            raise ProductInvalidPayload(details={"reason": "missing_image", "index": idx})

        # Если это base64 строка, декодируем
        if isinstance(image_data, str) and image_data.startswith("data:"):
            # data:image/jpeg;base64,/9j/4AAQSkZJRg...
            try:
                import base64
                header, encoded = image_data.split(",", 1)
                payload_bytes = base64.b64decode(encoded)
            except Exception as exc:
                raise ProductInvalidImage(details={"reason": "invalid_base64", "index": idx, "error": str(exc)})
        else:
            raise ProductInvalidPayload(details={"reason": "image_must_be_base64", "index": idx})

        if not _is_image_bytes(payload_bytes):
            raise ProductInvalidImage(details={"filename": f"image_{idx}", "reason": "unsupported_or_invalid_binary"})

        is_main = _to_bool(str(item.get("is_main", "")), default=(idx == 0))
        ordering = item.get("ordering", idx)
        if isinstance(ordering, str):
            try:
                ordering = int(ordering)
            except ValueError:
                ordering = idx

        mapped.append(
            ProductImageInputDTO(
                image=payload_bytes,
                image_name=f"image_{idx}.jpg",
                is_main=is_main,
                ordering=ordering,
            )
        )

    if mapped and not any(i.is_main for i in mapped):
        mapped[0].is_main = True

    return mapped


async def _build_images_dto(
    images: list[UploadFile] | None,
    image_is_main: list[str] | None,
    image_ordering: list[str] | None,
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
        
        # Получаем ordering: если передан список, берём по индексу, иначе используем индекс
        if image_ordering and idx < len(image_ordering):
            try:
                ordering_value = int(image_ordering[idx])
            except (ValueError, TypeError):
                ordering_value = idx
        else:
            ordering_value = idx
            
        mapped.append(
            ProductImageInputDTO(
                image=payload,
                image_name=image_file.filename or "test.jpg",
                is_main=_to_bool(is_main_value, default=(idx == 0)),
                ordering=ordering_value,
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

    images_json - JSON-список операций {action, upload_id, is_main, ordering}
    new_images - загружаемые файлы изображений
    new_image_is_main - список значений is_main для загружаемых файлов
    """
    if not images_json and not new_images:
        return None

    operations: list[ProductImageOperationDTO] = []

    if images_json:
        try:
            payload = json.loads(images_json)
        except json.DecodeError as exc:
            raise ProductInvalidPayload(details={"reason": "invalid_images_json", "error": str(exc)})

        if not isinstance(payload, list):
            raise ProductInvalidPayload(details={"reason": "images_must_be_list"})

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

    # Обработка загружаемых файлов (для создания товара или быстрого добавления изображений)
    if new_images:
        for idx, image_file in enumerate(new_images):
            is_main_value = new_image_is_main[idx] if new_image_is_main and idx < len(new_image_is_main) else None
            operations.append(
                ProductImageOperationDTO(
                    action="create",
                    is_main=_to_bool(is_main_value, default=(idx == 0)),
                    ordering=idx,
                )
            )

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

    **Формат `images_json`** (массив изображений):
    ```json
    [
      {"image": <файл>, "is_main": true, "ordering": 0},
      {"image": <файл>, "is_main": false, "ordering": 1}
    ]
    ```
    
    Каждый элемент массива содержит:
    - `image`: файл изображения (UploadFile)
    - `is_main`: флаг главного изображения (true/false/1/0)
    - `ordering`: порядок сортировки (int)
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
    images_json: Annotated[str | None, Form()] = None,
    images: Annotated[list[UploadFile] | None, File()] = None,
    image_is_main: Annotated[list[str] | None, Form()] = None,
    image_ordering: Annotated[list[str] | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Парсим изображения: либо из JSON, либо из загружаемых файлов
    images_dto = None
    if images is not None:
        # Загрузка через form-data файлы
        images_dto = await _build_images_dto(images, image_is_main, image_ordering)
    elif images_json is not None:
        # Загрузка через JSON (base64)
        images_dto = await _parse_images_json(images_json)
    
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
            images=images_dto or [],
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
    pprint(images_json)
    pprint(images)
    pprint(image_is_main)
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
