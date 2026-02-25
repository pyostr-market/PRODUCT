from src.catalog.category.domain.exceptions import CategoryPricingPolicyNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class DeleteCategoryPricingPolicyCommand:

    def __init__(self, repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        pricing_policy_id: int,
        user: User,
    ) -> bool:

        async with self.uow:
            aggregate = await self.repository.get(pricing_policy_id)

            if not aggregate:
                raise CategoryPricingPolicyNotFound()

            await self.repository.delete(pricing_policy_id)

        self.event_bus.publish_nowait(
            build_event(
                event_type="crud",
                method="delete",
                app="categories",
                entity="category_pricing_policy",
                entity_id=pricing_policy_id,
                data={"pricing_policy_id": pricing_policy_id},
            )
        )
        return True
