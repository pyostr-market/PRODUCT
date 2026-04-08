"""DTO для модуля отзывов."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


# ==================== Image DTOs ====================

@dataclass
class ReviewImageInputDTO:
    """DTO для входного изображения отзыва."""
    upload_id: int
    ordering: int = 0


@dataclass
class ReviewImageOperationDTO:
    """Операция с изображением при обновлении отзыва."""
    action: str  # "create", "delete", "pass"
    upload_id: Optional[int] = None
    ordering: Optional[int] = None


@dataclass
class ReviewImageReadDTO:
    """DTO для чтения изображения отзыва."""
    upload_id: int
    image_key: str
    image_url: Optional[str] = None
    ordering: int = 0


# ==================== Review DTOs ====================

@dataclass
class ReviewCreateDTO:
    """DTO для создания отзыва."""
    product_id: int
    rating: Decimal | float | int
    text: Optional[str] = None
    images: list[ReviewImageInputDTO] = field(default_factory=list)


@dataclass
class ReviewUpdateDTO:
    """DTO для обновления отзыва."""
    rating: Optional[Decimal | float | int] = None
    text: Optional[str] = None
    images: Optional[list[ReviewImageOperationDTO]] = None


@dataclass
class ReviewReadDTO:
    """DTO для чтения отзыва."""
    id: int
    product_id: int
    user_id: int
    username: str
    rating: Decimal
    text: Optional[str] = None
    images: list[ReviewImageReadDTO] = field(default_factory=list)


@dataclass
class ReviewListDTO:
    """DTO для списка отзывов с пагинацией."""
    items: list[ReviewReadDTO]
    total: int
    average_rating: Optional[float] = None


# ==================== Audit DTOs ====================

@dataclass
class ReviewAuditDTO:
    """DTO для audit лога отзыва."""
    review_id: int
    action: str
    old_data: Optional[dict] = None
    new_data: Optional[dict] = None
    user_id: Optional[int] = None
    fio: Optional[str] = None
