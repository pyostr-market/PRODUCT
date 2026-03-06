from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.catalog.suppliers.domain.events import (
    SupplierContactEmailChangedEvent,
    SupplierCreatedEvent,
    SupplierDeletedEvent,
    SupplierNameChangedEvent,
    SupplierPhoneChangedEvent,
    SupplierUpdatedEvent,
)
from src.catalog.suppliers.domain.exceptions import (
    InvalidContactEmail,
    InvalidPhoneNumber,
    InvalidSupplierName,
    SupplierAlreadyExists,
    SupplierNameTooLong,
    SupplierNameTooShort,
    SupplierNotFound,
)
from src.catalog.suppliers.domain.repository import (
    SupplierAuditRepository,
    SupplierReadRepositoryInterface,
    SupplierRepository,
)
from src.catalog.suppliers.domain.value_objects import (
    ContactEmail,
    PhoneNumber,
    SupplierId,
    SupplierName,
)

__all__ = [
    # Aggregates
    'SupplierAggregate',
    # Events
    'SupplierCreatedEvent',
    'SupplierUpdatedEvent',
    'SupplierDeletedEvent',
    'SupplierNameChangedEvent',
    'SupplierContactEmailChangedEvent',
    'SupplierPhoneChangedEvent',
    # Exceptions
    'SupplierAlreadyExists',
    'SupplierNotFound',
    'SupplierNameTooShort',
    'SupplierNameTooLong',
    'InvalidSupplierName',
    'InvalidContactEmail',
    'InvalidPhoneNumber',
    # Repository Interfaces
    'SupplierRepository',
    'SupplierAuditRepository',
    'SupplierReadRepositoryInterface',
    # Value Objects
    'SupplierId',
    'SupplierName',
    'ContactEmail',
    'PhoneNumber',
]
