from dataclasses import dataclass
from typing import Optional


@dataclass
class UploadHistoryReadDTO:
    id: int
    file_path: str
    folder: str
    user_id: Optional[int]
    content_type: Optional[str]
    original_filename: Optional[str]
    file_size: Optional[int]
    created_at: str


@dataclass
class UploadCreateDTO:
    file_path: str
    folder: str
    user_id: Optional[int] = None
    content_type: Optional[str] = None
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
