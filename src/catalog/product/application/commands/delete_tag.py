from src.catalog.product.domain.repository.tag import TagRepositoryInterface
from src.core.db.unit_of_work import UnitOfWork


class DeleteTagCommand:
    """Команда для удаления тега."""

    def __init__(
        self,
        tag_repository: TagRepositoryInterface,
        uow: UnitOfWork,
    ):
        self.tag_repository = tag_repository
        self.uow = uow

    async def execute(self, tag_id: int) -> None:
        """Выполнить команду."""
        tag = await self.tag_repository.get_by_id(tag_id)
        if not tag:
            raise ValueError(f"Тег с ID {tag_id} не найден")

        async with self.uow:
            await self.tag_repository.delete(tag_id)
