from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RegionCreateSchema(BaseModel):
    name: str
    parent_id: Optional[int] = None


class RegionUpdateSchema(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class RegionReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: Optional[int]


class RegionListResponse(BaseModel):
    total: int
    items: List[RegionReadSchema]
