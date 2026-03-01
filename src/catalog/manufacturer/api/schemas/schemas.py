from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ManufacturerCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None


class ManufacturerUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ManufacturerReadSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )
    id: int
    name: str
    description: Optional[str]


class ManufacturerListResponse(BaseModel):
    total: int
    items: List[ManufacturerReadSchema]