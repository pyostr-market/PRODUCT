from typing import Optional


class ProductTypeImageAggregate:
    """Агрегат изображения типа продукта."""

    def __init__(
        self,
        upload_id: int,
        object_key: Optional[str] = None,
    ):
        self.upload_id = upload_id
        self.object_key = object_key
