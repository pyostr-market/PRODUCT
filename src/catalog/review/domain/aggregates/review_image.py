"""Агрегат изображения отзыва."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ReviewImageAggregate:
    """Агрегат изображения отзыва."""

    upload_id: int  # ID из UploadHistory
    ordering: int = 0
    object_key: Optional[str] = None  # Ключ объекта в хранилище
