from src.catalog.product.application.dto.product import TagUpdateDTO, TagReadDTO
from src.catalog.product.domain.repository.tag import TagRepositoryInterface
from src.core.db.unit_of_work import UnitOfWork


class UpdateTagCommand:
    """Команда для обновления тега."""

    def __init__(
        self,
        tag_repository: TagRepositoryInterface,
        uow: UnitOfWork,
    ):
        self.tag_repository = tag_repository
        self.uow = uow

    async def execute(self, tag_id: int, dto: TagUpdateDTO) -> TagReadDTO:
        """Выполнить команду."""
        tag = await self.tag_repository.get_by_id(tag_id)
        if not tag:
            raise ValueError(f"Тег с ID {tag_id} не найден")

        # Проверяем уникальность имени, если оно меняется
        if dto.name and dto.name != tag.name:
            existing = await self.tag_repository.get_by_name(dto.name)
            if existing:
                raise ValueError(f"Тег с именем '{dto.name}' уже существует")

        tag.update(name=dto.name, description=dto.description)

        async with self.uow:
            updated = await self.tag_repository.update(tag)

        return TagReadDTO(
            tag_id=updated.tag_id,
            name=updated.name,
            description=updated.description,
        )
