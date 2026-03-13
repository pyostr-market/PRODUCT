from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class ManufacturerImageReadDTO:
    upload_id: int
    image_url: Optional[str] = None


@dataclass
class ManufacturerImageInputDTO:
    upload_id: Optional[int] = None


@dataclass
class ManufacturerImageOperationDTO:
    """Операция с изображением при обновлении производителя."""
    action: Literal["create", "update", "delete", "pass"]
    upload_id: Optional[int] = None
    image_url: Optional[str] = None


@dataclass
class ManufacturerReadDTO:
    id: int
    name: str
    description: Optional[str]
    image: Optional[ManufacturerImageReadDTO] = None


@dataclass
class ManufacturerCreateDTO:
    name: str
    description: Optional[str]
    image: Optional[ManufacturerImageInputDTO] = None


@dataclass
class ManufacturerUpdateDTO:
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[ManufacturerImageOperationDTO] = None