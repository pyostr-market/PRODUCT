"""Запросы для получения audit логов отзывов."""

from typing import Any, Dict, List, Optional, Tuple


class ReviewAdminQueries:

    def __init__(self, repository):
        self.repository = repository

    async def filter_logs(
        self,
        review_id: Optional[int] = None,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Any], int]:
        """Фильтровать audit логи."""
        return await self.repository.filter_logs(
            review_id=review_id,
            user_id=user_id,
            action=action,
            limit=limit,
            offset=offset,
        )
