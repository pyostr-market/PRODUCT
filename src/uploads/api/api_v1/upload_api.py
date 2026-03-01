from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user
from src.core.auth.schemas.user import User
from src.core.db.database import get_db
from src.uploads.api.schemas.schemas import (
    UploadHistoryReadSchema,
    UploadResponseSchema,
)
from src.uploads.application.upload_service import UploadService
from src.uploads.composition import UploadsComposition

upload_router = APIRouter(
    tags=["Загрузка файлов"],
)


@upload_router.post(
    "/",
    summary="Загрузить файл в S3",
    description="""
    Загружает файл в хранилище S3 и создаёт запись в истории загрузок.

    Права:
    - Требуется авторизация (Bearer token)

    Параметры:
    - **file**: Файл для загрузки (multipart/form-data)
    - **folder**: Папка для файла (products, categories, manufacturers, etc.)
    - **original_filename**: Исходное имя файла (опционально)

    Возвращает:
    - **upload_id**: ID записи в истории загрузок
    - **file_path**: Путь к файлу в S3
    - **public_url**: Публичный URL для доступа к файлу
    """,
    response_description="Данные о загруженном файле",
    responses={
        200: {
            "description": "Файл успешно загружен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "upload_id": 1,
                            "file_path": "products/55f1d02c-image.jpg",
                            "public_url": "https://cdn.example.com/products/55f1d02c-image.jpg",
                            "original_filename": "product.jpg",
                            "content_type": "image/jpeg",
                            "file_size": 102400,
                        }
                    }
                }
            },
        }
    },
)
async def upload_file(
    file: UploadFile = File(..., description="Файл для загрузки"),
    folder: str = Form(..., description="Папка для файла (products, categories, etc.)"),
    original_filename: Optional[str] = Form(None, description="Исходное имя файла"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Читаем содержимое файла
    file_data = await file.read()

    # Определяем content_type
    content_type = file.content_type or "application/octet-stream"

    # Используем имя файла из запроса или из самого файла
    filename = original_filename or file.filename or "unnamed"

    # Создаём сервис через composition root
    composition = UploadsComposition(db)
    service = composition.build_upload_service()

    # Загружаем файл
    result = await service.upload_file(
        file_data=file_data,
        folder=folder,
        filename=filename,
        content_type=content_type,
        user_id=current_user.id,
    )

    # Коммитим транзакцию
    await db.commit()

    return api_response(
        UploadResponseSchema(
            upload_id=result.upload_id,
            file_path=result.file_path,
            public_url=result.public_url,
            original_filename=filename,
            content_type=content_type,
            file_size=len(file_data),
        )
    )


@upload_router.get(
    "/{upload_id}",
    summary="Получить информацию о загрузке",
    description="""
    Возвращает информацию о загруженном файле по его ID.

    Права:
    - Требуется авторизация (Bearer token)
    """,
    response_description="Информация о загрузке",
    responses={
        200: {
            "description": "Информация получена успешно",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "file_path": "products/55f1d02c-image.jpg",
                            "folder": "products",
                            "user_id": 123,
                            "content_type": "image/jpeg",
                            "original_filename": "product.jpg",
                            "file_size": 102400,
                            "created_at": "2025-01-01T12:00:00",
                        }
                    }
                }
            },
        },
        404: {"description": "Загрузка не найдена"},
    },
)
async def get_upload_info(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    composition = UploadsComposition(db)
    service = composition.build_upload_service()

    dto = await service.get_upload(upload_id)

    if not dto:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Upload not found")

    return api_response(
        UploadHistoryReadSchema(
            id=dto.id,
            file_path=dto.file_path,
            folder=dto.folder,
            user_id=dto.user_id,
            content_type=dto.content_type,
            original_filename=dto.original_filename,
            file_size=dto.file_size,
            created_at=dto.created_at,
        )
    )
