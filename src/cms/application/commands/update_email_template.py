from src.cms.application.dto.cms_dto import EmailTemplateReadDTO, EmailTemplateUpdateDTO
from src.cms.domain.repository.email_template import EmailTemplateRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class UpdateEmailTemplateCommand:
    """Command для обновления email шаблона."""

    def __init__(
        self,
        repository: EmailTemplateRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        template_id: int,
        dto: EmailTemplateUpdateDTO,
    ) -> EmailTemplateReadDTO:
        aggregate = await self.repository.get_by_id(template_id)
        if not aggregate:
            from src.cms.domain.exceptions import EmailTemplateNotFound
            raise EmailTemplateNotFound()

        try:
            async with self.uow:
                aggregate.update(
                    subject=dto.subject,
                    body_html=dto.body_html,
                    body_text=dto.body_text,
                    variables=dto.variables,
                )

                if dto.is_active is not None:
                    if dto.is_active:
                        aggregate.activate()
                    else:
                        aggregate.deactivate()

                await self.repository.update(aggregate)

            return self._to_read_dto(aggregate)

        except Exception:
            raise

    def _to_read_dto(self, aggregate) -> EmailTemplateReadDTO:
        return EmailTemplateReadDTO(
            id=aggregate.id,
            key=aggregate.key,
            subject=aggregate.subject,
            body_html=aggregate.body_html,
            body_text=aggregate.body_text,
            variables=aggregate.variables or [],
            is_active=aggregate.is_active,
        )
