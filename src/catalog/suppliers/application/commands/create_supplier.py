from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO
from src.catalog.suppliers.application.dto.supplier import (
    SupplierCreateDTO,
    SupplierReadDTO,
)
from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.core.auth.schemas.user import User


class CreateSupplierCommand:

    def __init__(self, repository, audit_repository, uow):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow

    async def execute(
        self,
        dto: SupplierCreateDTO,
        user: User,
    ) -> SupplierReadDTO:

        async with self.uow:
            aggregate = SupplierAggregate(
                name=dto.name,
                contact_email=dto.contact_email,
                phone=dto.phone,
            )

            await self.repository.create(aggregate)

            await self.audit_repository.log(
                SupplierAuditDTO(
                    supplier_id=aggregate.id,
                    action="create",
                    old_data=None,
                    new_data={
                        "name": aggregate.name,
                        "contact_email": aggregate.contact_email,
                        "phone": aggregate.phone,
                    },
                    user_id=user.id,
                )
            )

            return SupplierReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                contact_email=aggregate.contact_email,
                phone=aggregate.phone,
            )
