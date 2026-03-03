from typing import Optional

from src.catalog.product.domain.aggregates.product import ProductAggregate
from src.catalog.product.domain.repository.product import ProductRepository
from src.core.cache.base import Cache


class CachedProductRepository(ProductRepository):

    def __init__(
        self,
        db_repository: ProductRepository,
        cache: Cache,
        ttl: int = 300,
    ):
        self._repo = db_repository
        self._cache = cache
        self._ttl = ttl

    def _key(self, product_id: int) -> str:
        return f"product:{product_id}"

    async def get(self, product_id: int) -> Optional[ProductAggregate]:
        key = self._key(product_id)

        cached = await self._cache.get(key)
        if cached:
            return cached

        product = await self._repo.get(product_id)
        if product:
            await self._cache.set(key, product, ttl=self._ttl)

        return product

    async def get_by_name(self, name: str) -> Optional[ProductAggregate]:
        # можно кэшировать тоже
        return await self._repo.get_by_name(name)

    async def create(self, aggregate: ProductAggregate) -> ProductAggregate:
        product = await self._repo.create(aggregate)
        await self._cache.set(self._key(product.id), product, ttl=self._ttl)
        return product

    async def update(self, aggregate: ProductAggregate) -> ProductAggregate:
        product = await self._repo.update(aggregate)
        await self._cache.delete(self._key(product.id))
        return product

    async def delete(self, product_id: int) -> bool:
        result = await self._repo.delete(product_id)
        await self._cache.delete(self._key(product_id))
        return result

    async def get_related_by_filterable_attributes(self, product_id: int, category_id: Optional[int]):
        return await self._repo.get_related_by_filterable_attributes(product_id, category_id)
