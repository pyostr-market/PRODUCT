from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from src.catalog.manufacturer.domain.exceptions import ManufacturerNameTooShort


class ManufacturerImageReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    upload_id: int  # ID из UploadHistory
    image_url: str  # Публичный URL


class ManufacturerImageReferenceSchema(BaseModel):
    """Ссылка на загруженное изображение для создания производителя."""
    model_config = ConfigDict(from_attributes=True)

    upload_id: int  # ID из UploadHistory


class ManufacturerImageActionSchema(BaseModel):
    """Операция с изображением при обновлении производителя."""
    model_config = ConfigDict(from_attributes=True)

    action: Literal["create", "update", "pass", "delete"]
    upload_id: Optional[int] = None  # ID изображения из UploadHistory
    image_url: Optional[str] = None  # URL изображения (альтернатива upload_id)


class ManufacturerCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    image: Optional[ManufacturerImageReferenceSchema] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ManufacturerNameTooShort()
        return v.strip()

    @model_validator(mode="after")
    def check_name_length(self):
        if len(self.name) < 2:
            raise ManufacturerNameTooShort()
        return self


class ManufacturerUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[ManufacturerImageActionSchema] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ManufacturerNameTooShort()
            return v.strip()
        return v

    @model_validator(mode="after")
    def check_name_length(self):
        if self.name is not None and len(self.name) < 2:
            raise ManufacturerNameTooShort()
        return self


class ManufacturerReadSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )
    id: int
    name: str
    description: Optional[str]
    image: Optional[ManufacturerImageReadSchema] = None


class ManufacturerListResponse(BaseModel):
    total: int
    items: List[ManufacturerReadSchema]