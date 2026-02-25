from dataclasses import fields

from src.catalog.category.application.dto.pricing_policy import (
    CategoryPricingPolicyReadDTO,
    CategoryPricingPolicyUpdateDTO,
)
from src.catalog.category.domain.exceptions import (
    CategoryPricingPolicyAlreadyExists,
    CategoryPricingPolicyInvalidRateValue,
    CategoryPricingPolicyNotFound,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class UpdateCategoryPricingPolicyCommand:

    def __init__(self, repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        pricing_policy_id: int,
        dto: CategoryPricingPolicyUpdateDTO,
        user: User,
        raw_data: dict | None = None,
    ) -> CategoryPricingPolicyReadDTO:
        """
        Обновляет политику ценообразования.
        
        Args:
            pricing_policy_id: ID политики
            dto: DTO с данными для обновления
            user: Текущий пользователь
            raw_data: Сырые данные из запроса (для определения явно установленных None)
        """

        async with self.uow:
            aggregate = await self.repository.get(pricing_policy_id)

            if not aggregate:
                raise CategoryPricingPolicyNotFound()

            old_data = {
                "markup_fixed": str(aggregate.markup_fixed) if aggregate.markup_fixed else None,
                "markup_percent": str(aggregate.markup_percent) if aggregate.markup_percent else None,
                "commission_percent": str(aggregate.commission_percent) if aggregate.commission_percent else None,
                "discount_percent": str(aggregate.discount_percent) if aggregate.discount_percent else None,
                "tax_rate": str(aggregate.tax_rate),
            }

            # Обновляем поля, которые были явно переданы (включая None)
            if raw_data:
                if "markup_fixed" in raw_data:
                    aggregate.update_markup_fixed(dto.markup_fixed)
                if "markup_percent" in raw_data:
                    aggregate.update_markup_percent(dto.markup_percent)
                if "commission_percent" in raw_data:
                    aggregate.update_commission_percent(dto.commission_percent)
                if "discount_percent" in raw_data:
                    aggregate.update_discount_percent(dto.discount_percent)
                if "tax_rate" in raw_data:
                    aggregate.update_tax_rate(dto.tax_rate)
            else:
                # Старая логика: обновляем только не-None значения
                if dto.markup_fixed is not None:
                    aggregate.update_markup_fixed(dto.markup_fixed)
                if dto.markup_percent is not None:
                    aggregate.update_markup_percent(dto.markup_percent)
                if dto.commission_percent is not None:
                    aggregate.update_commission_percent(dto.commission_percent)
                if dto.discount_percent is not None:
                    aggregate.update_discount_percent(dto.discount_percent)
                if dto.tax_rate is not None:
                    aggregate.update_tax_rate(dto.tax_rate)

            await self.repository.update(aggregate)

            new_data = {
                "markup_fixed": str(aggregate.markup_fixed) if aggregate.markup_fixed else None,
                "markup_percent": str(aggregate.markup_percent) if aggregate.markup_percent else None,
                "commission_percent": str(aggregate.commission_percent) if aggregate.commission_percent else None,
                "discount_percent": str(aggregate.discount_percent) if aggregate.discount_percent else None,
                "tax_rate": str(aggregate.tax_rate),
            }

            result = CategoryPricingPolicyReadDTO(
                id=aggregate.id,
                category_id=aggregate.category_id,
                markup_fixed=aggregate.markup_fixed,
                markup_percent=aggregate.markup_percent,
                commission_percent=aggregate.commission_percent,
                discount_percent=aggregate.discount_percent,
                tax_rate=aggregate.tax_rate,
            )

        changed_fields = {
            key: value
            for key, value in new_data.items()
            if old_data.get(key) != value
        }
        if changed_fields:
            self.event_bus.publish_nowait(
                build_event(
                    event_type="crud",
                    method="update",
                    app="categories",
                    entity="category_pricing_policy",
                    entity_id=result.id,
                    data={
                        "pricing_policy_id": result.id,
                        "fields": changed_fields,
                    },
                )
            )
        return result
