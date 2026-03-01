from dataclasses import dataclass
from typing import Optional


@dataclass
class UploadHistoryAggregate:
    """Агрегат истории загрузок файлов."""
    file_path: str
    folder: str
    upload_id: Optional[int] = None
    user_id: Optional[int] = None
    content_type: Optional[str] = None
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
