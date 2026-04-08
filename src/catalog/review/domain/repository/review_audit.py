"""Интерфейс репозитория для audit логов отзывов."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple

from src.catalog.review.application.dto.review import ReviewAuditDTO


class ReviewAuditRepository(ABC):
    """Абстрактный репозиторий для audit логов отзывов."""

    @abstractmethod
    async def log(self, dto: ReviewAuditDTO) -> None:
        """Записать запись в audit лог."""


class ReviewAuditQueryRepository(ABC):
    """Абстрактный репозиторий для чтения audit логов."""

    @abstractmethod
    async def filter_logs(
        self,
        review_id: Optional[int] = None,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Any], int]:
        """Фильтровать audit логи с пагинацией."""
