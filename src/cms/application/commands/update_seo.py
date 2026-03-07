from src.cms.application.dto.cms_dto import SeoReadDTO, SeoUpdateDTO
from src.cms.domain.repository.seo import SeoRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class UpdateSeoCommand:
    """Command для обновления SEO данных."""

    def __init__(
        self,
        repository: SeoRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, seo_id: int, dto: SeoUpdateDTO) -> SeoReadDTO:
        aggregate = await self.repository.get_by_id(seo_id)
        if not aggregate:
            from src.cms.domain.exceptions import SeoNotFound
            raise SeoNotFound()

        try:
            async with self.uow:
                aggregate.update(
                    title=dto.title,
                    description=dto.description,
                    keywords=dto.keywords,
                    og_image_id=dto.og_image_id,
                )

                await self.repository.update(aggregate)

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
