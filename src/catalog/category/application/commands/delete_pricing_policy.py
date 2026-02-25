from src.catalog.category.application.dto.pricing_policy_audit import (
    CategoryPricingPolicyAuditDTO,
)
from src.catalog.category.domain.exceptions import CategoryPricingPolicyNotFound
from src.catalog.category.domain.repository.pricing_policy_audit import (
    CategoryPricingPolicyAuditRepository,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class DeleteCategoryPricingPolicyCommand:

    def __init__(
        self,
        repository,
        uow,
        event_bus: AsyncEventBus,
        audit_repository: CategoryPricingPolicyAuditRepository,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus
        self.audit_repository = audit_repository

    async def execute(
        self,
        pricing_policy_id: int,
        user: User,
    ) -> bool:

        async with self.uow:
            aggregate = await self.repository.get(pricing_policy_id)

            if not aggregate:
                raise CategoryPricingPolicyNotFound()

            # Логируем аудит перед удалением
            await self.audit_repository.log(
                CategoryPricingPolicyAuditDTO(
                    pricing_policy_id=pricing_policy_id,
                    action="delete",
                    old_data={
                        "category_id": aggregate.category_id,
                        "markup_fixed": str(aggregate.markup_fixed) if aggregate.markup_fixed else None,
                        "markup_percent": str(aggregate.markup_percent) if aggregate.markup_percent else None,
                        "commission_percent": str(aggregate.commission_percent) if aggregate.commission_percent else None,
                        "discount_percent": str(aggregate.discount_percent) if aggregate.discount_percent else None,
                        "tax_rate": str(aggregate.tax_rate),
                    },
                    new_data=None,
                    user_id=user.id,
                    fio=user.fio,
                )
            )

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
