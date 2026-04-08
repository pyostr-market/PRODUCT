"""API команды для модуля отзывов (create, update, delete)."""

from decimal import Decimal
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form

from src.catalog.review.api.schemas.review import (
    ReviewCreateSchema,
    ReviewReadSchema,
    ReviewUpdateSchema,
)
from src.catalog.review.application.dto.review import (
    ReviewCreateDTO,
    ReviewImageInputDTO,
    ReviewImageOperationDTO,
    ReviewUpdateDTO,
)
from src.catalog.review.composition import ReviewComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

review_commands_router = APIRouter(
    tags=["Отзывы"],
)


@review_commands_router.post(
    "",
    status_code=200,
    summary="Создать отзыв",
    description="""
    Создаёт новый отзыв для товара.

    Права:
    - Требуется авторизация (любой авторизованный пользователь)

    Сценарии:
    - Пользователь оставляет отзыв с рейтингом (1-5)
    - Опционально: текст отзыва и изображения
    - Один пользователь может оставить только один отзыв на товар
    """,
    response_description="Созданный отзыв в стандартной обёртке API",
    responses={
        200: {
            "description": "Отзыв успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "product_id": 100,
                            "user_id": 42,
                            "username": "Иван Петров",
                            "rating": "4.5",
                            "text": "Отличный товар!",
                            "images": [
                                {
                                    "upload_id": 10,
                                    "image_url": "https://cdn.example.com/reviews/img.jpg",
                                    "ordering": 0
                                }
                            ],
                        },
                    }
                }
            },
        },
        400: {"description": "Некорректные данные (рейтинг вне диапазона и т.д.)"},
        401: {"description": "Не авторизован"},
        409: {"description": "Пользователь уже оставлял отзыв на этот товар"},
    },
)
async def create(
    product_id: Annotated[int, Form(...)],
    rating: Annotated[Decimal, Form(..., ge=1, le=5)],
    text: Annotated[Optional[str], Form()] = None,
    images_json: Annotated[Optional[str], Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    import json

    images = []
    if images_json:
        payload = json.loads(images_json)
        for idx, item in enumerate(payload):
            images.append(
                ReviewImageInputDTO(
                    upload_id=item["upload_id"],
                    ordering=item.get("ordering", idx),
                )
            )

    commands = ReviewComposition.build_create_command(db)
    dto = await commands.execute(
        ReviewCreateDTO(
            product_id=product_id,
            rating=rating,
            text=text,
            images=images,
        ),
        user=user,
    )

    return api_response(ReviewReadSchema.model_validate(dto))


@review_commands_router.put(
    "/{review_id}",
    summary="Обновить отзыв",
    description="""
    Обновляет существующий отзыв.

    Права:
    - Только владелец отзыва

    Можно обновить:
    - Рейтинг (1-5)
    - Текст отзыва
    - Изображения (create/delete/pass)
    """,
    response_description="Обновлённый отзыв в стандартной обёртке API",
    responses={
        200: {
            "description": "Отзыв успешно обновлён",
        },
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав (не владелец)"},
        404: {"description": "Отзыв не найден"},
    },
)
async def update(
    review_id: int,
    rating: Annotated[Optional[Decimal], Form(ge=1, le=5)] = None,
    text: Annotated[Optional[str], Form()] = None,
    images_json: Annotated[Optional[str], Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    import json

    images = None
    if images_json:
        payload = json.loads(images_json)
        images = []
        for item in payload:
            images.append(
                ReviewImageOperationDTO(
                    action=item["action"],
                    upload_id=item.get("upload_id"),
                    ordering=item.get("ordering"),
                )
            )

    commands = ReviewComposition.build_update_command(db)
    dto = await commands.execute(
        review_id,
        ReviewUpdateDTO(
            rating=rating,
            text=text,
            images=images,
        ),
        user=user,
    )

    return api_response(ReviewReadSchema.model_validate(dto))


@review_commands_router.delete(
    "/{review_id}",
    summary="Удалить отзыв",
    description="""
    Удаляет отзыв по идентификатору.

    Права:
    - Только владелец отзыва
    """,
    response_description="Флаг успешного удаления",
    responses={
        200: {
            "description": "Отзыв успешно удалён",
            "content": {
                "application/json": {
                    "example": {"success": True, "data": {"deleted": True}}
                }
            },
        },
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав (не владелец)"},
        404: {"description": "Отзыв не найден"},
    },
)
async def delete(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ReviewComposition.build_delete_command(db)
    await commands.execute(review_id, user=user)
    return api_response({"deleted": True})
