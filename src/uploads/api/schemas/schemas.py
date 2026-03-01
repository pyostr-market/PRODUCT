from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UploadResponseSchema(BaseModel):
    """Ответ API после загрузки файла."""
    model_config = ConfigDict(from_attributes=True)

    upload_id: int
    file_path: str
    public_url: str
    original_filename: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None


class UploadHistoryReadSchema(BaseModel):
    """Информация о загрузке из истории."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_path: str
    folder: str
    user_id: Optional[int] = None
    content_type: Optional[str] = None
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    created_at: str


class UploadImageReferenceSchema(BaseModel):
    """Ссылка на изображение для использования в товарах/категориях."""
    model_config = ConfigDict(from_attributes=True)

    image_id: int  # ID из upload_history
    image_url: str  # Публичный URL
    ordering: int = 0
    is_main: bool = False


class UploadImageActionSchema(BaseModel):
    """Операция с изображением при обновлении товара/категории."""
    model_config = ConfigDict(from_attributes=True)

    action: str  # "create", "update", "pass", "delete"
    image_id: Optional[int] = None  # ID существующего изображения
    image_url: Optional[str] = None  # URL изображения (альтернатива image_id)
    ordering: Optional[int] = None
    is_main: Optional[bool] = None
