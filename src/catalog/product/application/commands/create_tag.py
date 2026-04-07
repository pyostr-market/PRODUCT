from src.catalog.product.application.dto.product import TagCreateDTO, TagReadDTO
from src.catalog.product.domain.aggregates.tag import TagAggregate
from src.catalog.product.domain.repository.tag import TagRepositoryInterface
from src.core.db.unit_of_work import UnitOfWork


class CreateTagCommand:
    """Команда для создания тега."""

    def __init__(
        self,
        tag_repository: TagRepositoryInterface,
        uow: UnitOfWork,
    ):
        self.tag_repository = tag_repository
        self.uow = uow

    async def execute(self, dto: TagCreateDTO) -> TagReadDTO:
        """Выполнить команду."""
        # Проверяем, что тег с таким именем не существует
        existing = await self.tag_repository.get_by_name(dto.name)
        if existing:
            raise ValueError(f"Тег с именем '{dto.name}' уже существует")

        aggregate = TagAggregate(
            tag_id=0,  # Будет установлен после создания
            name=dto.name,
            description=dto.description,
        )

        async with self.uow:
            created = await self.tag_repository.create(aggregate)

        return TagReadDTO(
            tag_id=created.tag_id,
            name=created.name,
            description=created.description,
        )
