from src.cms.application.dto.cms_dto import FaqCreateDTO, FaqReadDTO
from src.cms.domain.aggregates.faq import FaqAggregate
from src.cms.domain.repository.faq import FaqRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class CreateFaqCommand:
    """Command для создания FAQ."""

    def __init__(
        self,
        repository: FaqRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, dto: FaqCreateDTO) -> FaqReadDTO:
        aggregate = FaqAggregate(
            faq_id=None,
            question=dto.question,
            answer=dto.answer,
            category=dto.category,
            order=dto.order,
            is_active=dto.is_active,
        )

        try:
            async with self.uow:
                await self.repository.create(aggregate)
                domain_events = aggregate.get_events()

            # Публикуем события
            if domain_events:
                self.event_bus.publish_many_nowait([build_event(
                    event_type="crud",
                    method="create",
                    app="cms",
                    entity="faq",
                    entity_id=aggregate.id,
                    data={
                        "faq_id": aggregate.id,
                        "question": aggregate.question,
                        "category": aggregate.category,
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
