from typing import List, Tuple

from src.catalog.product.application.dto.product import ProductTagReadDTO, TagReadDTO
from src.catalog.product.domain.repository.product_tag_read import ProductTagReadRepositoryInterface
from src.catalog.product.domain.repository.tag import TagRepositoryInterface


class TagQueries:
    """Queries для получения тегов."""

    def __init__(
        self,
        tag_repository: TagRepositoryInterface,
        product_tag_read_repository: ProductTagReadRepositoryInterface,
    ):
        self.tag_repository = tag_repository
        self.product_tag_read_repository = product_tag_read_repository

    async def get_tag_by_id(self, tag_id: int) -> TagReadDTO | None:
        """Получить тег по ID."""
        tag = await self.tag_repository.get(tag_id)
        if not tag:
            return None
        return TagReadDTO(
            tag_id=tag.tag_id,
            name=tag.name,
            description=tag.description,
            color=tag.color,
        )

    async def get_all_tags(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[TagReadDTO], int]:
        """Получить все теги с пагинацией."""
        total = await self.tag_repository.count()
        tags = await self.tag_repository.get_all(limit=limit, offset=offset)

        return [
            TagReadDTO(
                tag_id=tag.tag_id,
                name=tag.name,
                description=tag.description,
                color=tag.color,
            )
            for tag in tags
        ], total

    async def get_product_tags(
        self,
        product_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[ProductTagReadDTO], int]:
        """Получить все теги товара."""
        product_tag_dtos, total = await self.product_tag_read_repository.get_by_product(
            product_id=product_id,
            limit=limit,
            offset=offset,
        )

        return product_tag_dtos, total
