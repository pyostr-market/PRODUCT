from src.cms.application.dto.cms_dto import EmailTemplateCreateDTO, EmailTemplateReadDTO
from src.cms.domain.aggregates.email_template import EmailTemplateAggregate
from src.cms.domain.repository.email_template import EmailTemplateRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class CreateEmailTemplateCommand:
    """Command для создания email шаблона."""

    def __init__(
        self,
        repository: EmailTemplateRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, dto: EmailTemplateCreateDTO) -> EmailTemplateReadDTO:
        # Проверяем уникальность ключа
        existing = await self.repository.get_by_key(dto.key)
        if existing:
            from src.cms.domain.exceptions import EmailTemplateKeyAlreadyExists
            raise EmailTemplateKeyAlreadyExists(dto.key)

        aggregate = EmailTemplateAggregate(
            template_id=None,
            key=dto.key,
            subject=dto.subject,
            body_html=dto.body_html,
            body_text=dto.body_text,
            variables=dto.variables,
            is_active=dto.is_active,
        )

        try:
            async with self.uow:
                await self.repository.create(aggregate)

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
