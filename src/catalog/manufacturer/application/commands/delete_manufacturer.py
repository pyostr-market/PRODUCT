from src.catalog.manufacturer.application.dto.audit import ManufacturerAuditDTO
from src.catalog.manufacturer.domain.exceptions import ManufacturerNotFound
from src.core.auth.schemas.user import User


class DeleteManufacturerCommand:

    def __init__(self, repository, audit_repository, uow):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow

    async def execute(
        self,
        manufacturer_id: int,
        user: User,
    ) -> bool:

        async with self.uow:
            aggregate = await self.repository.get(manufacturer_id)

            if not aggregate:
                raise ManufacturerNotFound()

            old_data = {
                "name": aggregate.name,
                "description": aggregate.description,
            }

            await self.repository.delete(manufacturer_id)

            await self.audit_repository.log(
                ManufacturerAuditDTO(
                    manufacturer_id=manufacturer_id,
                    action="delete",
                    old_data=old_data,
                    new_data=None,
                    user_id=user.id,
                )
            )

            return True