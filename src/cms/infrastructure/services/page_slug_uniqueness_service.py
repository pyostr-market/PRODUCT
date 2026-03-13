from src.cms.domain.exceptions import PageSlugAlreadyExists
from src.cms.domain.repository.page import PageRepository
from src.cms.domain.services.page_slug_uniqueness_service import (
    PageSlugUniquenessService,
)


class PageSlugUniquenessServiceImpl(PageSlugUniquenessService):
    """
    Реализация Domain Service для проверки уникальности slug.
    
    Использует репозиторий для проверки существования slug в БД.
    """

    def __init__(self, page_repository: PageRepository):
        self._page_repository = page_repository

    async def is_slug_unique(self, slug: str, exclude_id: int | None = None) -> bool:
        """Проверить, является ли slug уникальным."""
        exists = await self._page_repository.exists_by_slug(slug, exclude_id=exclude_id)
        return not exists

    async def ensure_slug_is_unique(self, slug: str, exclude_id: int | None = None):
        """Убедиться, что slug уникален, иначе выбросить исключение."""
        if not await self.is_slug_unique(slug, exclude_id):
            raise PageSlugAlreadyExists(slug)
