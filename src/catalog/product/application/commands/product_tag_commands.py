from typing import Any

from src.catalog.product.application.dto.product import ProductTagReadDTO, TagReadDTO
from src.catalog.product.domain.aggregates.product_tag import ProductTagAggregate, ProductTagLinkedEvent
from src.catalog.product.domain.exceptions import (
    ProductTagAlreadyExists,
    ProductTagInvalidProduct,
    ProductTagNotFound,
    TagNotFound,
)
from src.catalog.product.domain.repository.product import ProductRepository
from src.catalog.product.domain.repository.product_tag import ProductTagRepositoryInterface
from src.catalog.product.domain.repository.tag import TagRepositoryInterface
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class AddProductTagCommand:
    """Команда для добавления тега к товару."""

    def __init__(
        self,
        product_tag_repository: ProductTagRepositoryInterface,
        product_repository: ProductRepository,
        tag_repository: TagRepositoryInterface,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.product_tag_repository = product_tag_repository
        self.product_repository = product_repository
        self.tag_repository = tag_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        product_id: int,
        tag_id: int,
        user: User,
    ) -> ProductTagReadDTO:
        """Выполнить команду."""
        # Проверяем существование товара
        product = await self.product_repository.get(product_id)
        if not product:
            raise ProductTagInvalidProduct(
                details={"invalid_product_id": product_id}
            )

        # Проверяем существование тега
        tag = await self.tag_repository.get(tag_id)
        if not tag:
            raise TagNotFound(details={"invalid_tag_id": tag_id})

        # Проверяем, что связь не существует
        already_exists = await self.product_tag_repository.exists(product_id, tag_id)
        ProductTagAggregate.validate_not_exists(product_id, tag_id, already_exists)

        async with self.uow:
            aggregate = ProductTagAggregate(
                _product_id=product_id,
                _tag_id=tag_id,
            )

            await self.product_tag_repository.create(aggregate)

            # Получаем доменные события
            domain_events = aggregate.get_events()

            result = self._to_read_dto(aggregate, tag)

        # Публикуем события
        events = self._build_domain_events(aggregate, domain_events)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _build_domain_events(
        self,
        aggregate: ProductTagAggregate,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, ProductTagLinkedEvent):
                events.append(
                    build_event(
                        event_type="crud",
                        method="create",
                        app="products",
                        entity="product_tag",
                        entity_id=aggregate.id,
                        data={
                            "product_id": aggregate.product_id,
                            "tag_id": aggregate.tag_id,
                        },
                    )
                )

        return events

    def _to_read_dto(
        self,
        aggregate: ProductTagAggregate,
        tag,
    ) -> ProductTagReadDTO:
        """Преобразовать агрегат в DTO для чтения."""
        return ProductTagReadDTO(
            id=aggregate.id,
            product_id=aggregate.product_id,
            tag_id=aggregate.tag_id,
            tag=TagReadDTO(
                tag_id=tag.tag_id,
                name=tag.name,
                description=tag.description,
            ),
        )


class RemoveProductTagCommand:
    """Команда для удаления тега у товара."""

    def __init__(
        self,
        product_tag_repository: ProductTagRepositoryInterface,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.product_tag_repository = product_tag_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        product_id: int,
        tag_id: int,
        user: User,
    ) -> None:
        """Выполнить команду."""
        # Проверяем, что связь существует
        exists = await self.product_tag_repository.exists(product_id, tag_id)
        if not exists:
            raise ProductTagNotFound(
                details={"product_id": product_id, "tag_id": tag_id}
            )

        async with self.uow:
            await self.product_tag_repository.delete(product_id, tag_id)

        # Публикуем событие
        self.event_bus.publish_many_nowait([
            build_event(
                event_type="crud",
                method="delete",
                app="products",
                entity="product_tag",
                entity_id=0,
                data={
                    "product_id": product_id,
                    "tag_id": tag_id,
                },
            )
        ])
