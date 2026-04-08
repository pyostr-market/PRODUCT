from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class ExportAttributeSchema(BaseModel):
    id: int
    name: str
    value: str
    is_filterable: bool
    is_groupable: bool = False


class ExportParentCategorySchema(BaseModel):
    id: int
    name: str


class ExportCategorySchema(BaseModel):
    id: int
    name: str
    parent_categories: List[ExportParentCategorySchema] = []


class ExportSupplierSchema(BaseModel):
    id: int
    name: str


class ExportRegionSchema(BaseModel):
    id: int
    name: str


class ExportProductSchema(BaseModel):
    id: int
    name: str
    price: Decimal
    description: Optional[str] = None
    category: Optional[ExportCategorySchema]
    supplier: Optional[ExportSupplierSchema]
    region: Optional[ExportRegionSchema] = None
    attributes: List[ExportAttributeSchema]


class ExportCatalogResponse(BaseModel):
    total: int
    items: List[ExportProductSchema]