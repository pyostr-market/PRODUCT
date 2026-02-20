from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO
from src.catalog.suppliers.domain.exceptions import SupplierNotFound
from src.core.auth.schemas.user import User


class DeleteSupplierCommand:

    def __init__(self, repository, audit_repository, uow):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow

    async def execute(
        self,
        supplier_id: int,
        user: User,
    ) -> bool:

        async with self.uow:
            aggregate = await self.repository.get(supplier_id)

            if not aggregate:
                raise SupplierNotFound()

            old_data = {
                "name": aggregate.name,
                "contact_email": aggregate.contact_email,
                "phone": aggregate.phone,
            }

            await self.repository.delete(supplier_id)

            await self.audit_repository.log(
                SupplierAuditDTO(
                    supplier_id=supplier_id,
                    action="delete",
                    old_data=old_data,
                    new_data=None,
                    user_id=user.id,
                )
            )

            return True
