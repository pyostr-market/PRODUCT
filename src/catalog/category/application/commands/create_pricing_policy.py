from src.catalog.category.application.dto.pricing_policy import (
    CategoryPricingPolicyCreateDTO,
    CategoryPricingPolicyReadDTO,
)
from src.catalog.category.domain.aggregates.pricing_policy import (
    CategoryPricingPolicyAggregate,
)
from src.catalog.category.domain.exceptions import (
    CategoryPricingPolicyAlreadyExists,
    CategoryPricingPolicyCategoryNotFound,
    CategoryPricingPolicyInvalidRateValue,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class CreateCategoryPricingPolicyCommand:

    def __init__(self, repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        dto: CategoryPricingPolicyCreateDTO,
        user: User,
    ) -> CategoryPricingPolicyReadDTO:

        async with self.uow:
            try:
                aggregate = CategoryPricingPolicyAggregate(
                    category_id=dto.category_id,
                    markup_fixed=dto.markup_fixed,
                    markup_percent=dto.markup_percent,
                    commission_percent=dto.commission_percent,
                    discount_percent=dto.discount_percent,
                    tax_rate=dto.tax_rate,
                )
            except CategoryPricingPolicyInvalidRateValue:
                raise

            await self.repository.create(aggregate)

            result = CategoryPricingPolicyReadDTO(
                id=aggregate.id,
                category_id=aggregate.category_id,
                markup_fixed=aggregate.markup_fixed,
                markup_percent=aggregate.markup_percent,
                commission_percent=aggregate.commission_percent,
                discount_percent=aggregate.discount_percent,
                tax_rate=aggregate.tax_rate,
            )

        self.event_bus.publish_nowait(
            build_event(
                event_type="crud",
                method="create",
                app="categories",
                entity="category_pricing_policy",
                entity_id=result.id,
                data={
                    "pricing_policy_id": result.id,
                    "category_id": result.category_id,
                    "fields": {
                        "markup_fixed": str(result.markup_fixed) if result.markup_fixed else None,
                        "markup_percent": str(result.markup_percent) if result.markup_percent else None,
                        "commission_percent": str(result.commission_percent) if result.commission_percent else None,
                        "discount_percent": str(result.discount_percent) if result.discount_percent else None,
                        "tax_rate": str(result.tax_rate),
                    },
                },
            )
        )
        return result
