from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class ExportAttributeSchema(BaseModel):
    id: int
    name: str
    value: str
    is_filterable: bool
    is_groupable: bool = False


class ExportCategorySchema(BaseModel):
    id: int
    name: str


class ExportSupplierSchema(BaseModel):
    id: int
    name: str


class ExportProductSchema(BaseModel):
    id: int
    name: str
    price: Decimal
    description: Optional[str] = None
    category: Optional[ExportCategorySchema]
    supplier: Optional[ExportSupplierSchema]
    attributes: List[ExportAttributeSchema]


class ExportCatalogResponse(BaseModel):
    total: int
    items: List[ExportProductSchema]