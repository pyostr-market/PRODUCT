from src.cms.domain.repository.email_template import EmailTemplateRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class DeleteEmailTemplateCommand:
    """Command для удаления email шаблона."""

    def __init__(
        self,
        repository: EmailTemplateRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, template_id: int) -> bool:
        aggregate = await self.repository.get_by_id(template_id)
        if not aggregate:
            from src.cms.domain.exceptions import EmailTemplateNotFound
            raise EmailTemplateNotFound()

        try:
            async with self.uow:
                result = await self.repository.delete(template_id)

            if result:
                self.event_bus.publish_many_nowait([build_event(
                    event_type="crud",
                    method="delete",
                    app="cms",
                    entity="email_template",
                    entity_id=template_id,
                    data={"template_id": template_id},
                )])

            return result

        except Exception:
            raise
