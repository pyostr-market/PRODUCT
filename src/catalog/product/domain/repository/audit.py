from abc import ABC
from dataclasses import dataclass
from typing import Any


@dataclass
class ProductAuditDTO:
    product_id: int
    action: str
    old_data: dict | None
    new_data: dict | None
    user_id: int
    fio: str | None


@dataclass
class ProductTypeAuditDTO:
    product_type_id: int
    action: str
    old_data: dict | None
    new_data: dict | None
    user_id: int
    fio: str | None


@dataclass
class ProductAttributeAuditDTO:
    attribute_id: int
    action: str
    old_data: dict | None
    new_data: dict | None
    user_id: int
    fio: str | None


@dataclass
class ProductRelationAuditDTO:
    relation_id: int
    action: str
    old_data: dict | None
    new_data: dict | None
    user_id: int
    fio: str | None


class ProductAuditRepository(ABC):

    async def log(self, dto: ProductAuditDTO):
        ...

    async def log_product_type(self, dto: ProductTypeAuditDTO):
        ...

    async def log_product_attribute(self, dto: ProductAttributeAuditDTO):
        ...

    async def log_product_relation(self, dto: ProductRelationAuditDTO):
        ...
