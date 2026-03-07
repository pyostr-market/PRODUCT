from src.cms.application.dto.cms_dto import SeoCreateDTO, SeoReadDTO
from src.cms.domain.aggregates.seo import SeoAggregate
from src.cms.domain.repository.seo import SeoRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class CreateSeoCommand:
    """Command для создания SEO данных."""

    def __init__(
        self,
        repository: SeoRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, dto: SeoCreateDTO) -> SeoReadDTO:
        aggregate = SeoAggregate(
            seo_id=None,
            page_slug=dto.page_slug,
            title=dto.title,
            description=dto.description,
            keywords=dto.keywords,
            og_image_id=dto.og_image_id,
        )

        try:
            async with self.uow:
                await self.repository.create(aggregate)

            return self._to_read_dto(aggregate)

        except Exception:
            raise

    def _to_read_dto(self, aggregate) -> SeoReadDTO:
        return SeoReadDTO(
            id=aggregate.id,
            page_slug=aggregate.page_slug,
            title=aggregate.title,
            description=aggregate.description,
            keywords=aggregate.keywords or [],
            og_image_id=aggregate.og_image_id,
        )
