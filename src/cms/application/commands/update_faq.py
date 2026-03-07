from src.cms.application.dto.cms_dto import FaqReadDTO, FaqUpdateDTO
from src.cms.domain.aggregates.faq import FaqAggregate
from src.cms.domain.repository.faq import FaqRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class UpdateFaqCommand:
    """Command для обновления FAQ."""

    def __init__(
        self,
        repository: FaqRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, faq_id: int, dto: FaqUpdateDTO) -> FaqReadDTO:
        aggregate = await self.repository.get_by_id(faq_id)
        if not aggregate:
            from src.cms.domain.exceptions import FaqNotFound
            raise FaqNotFound(faq_id)

        try:
            async with self.uow:
                aggregate.update(
                    question=dto.question,
                    answer=dto.answer,
                    category=dto.category,
                    order=dto.order,
                )

                if dto.is_active is not None:
                    if dto.is_active:
                        aggregate.activate()
                    else:
                        aggregate.deactivate()

                await self.repository.update(aggregate)
                domain_events = aggregate.get_events()

            # Публикуем события
            if domain_events:
                self.event_bus.publish_many_nowait([build_event(
                    event_type="crud",
                    method="update",
                    app="cms",
                    entity="faq",
                    entity_id=aggregate.id,
                    data={
                        "faq_id": aggregate.id,
                        "question": aggregate.question,
                    },
                )])

            return self._to_read_dto(aggregate)

        except Exception:
            raise

    def _to_read_dto(self, aggregate: FaqAggregate) -> FaqReadDTO:
        return FaqReadDTO(
            id=aggregate.id,
            question=aggregate.question,
            answer=aggregate.answer,
            category=aggregate.category,
            order=aggregate.order,
            is_active=aggregate.is_active,
        )
