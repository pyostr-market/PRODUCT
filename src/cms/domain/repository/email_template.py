from abc import ABC
from typing import Optional

from src.cms.domain.aggregates.email_template import EmailTemplateAggregate


class EmailTemplateRepository(ABC):
    """Интерфейс репозитория для email шаблонов."""

    async def get_by_id(self, template_id: int) -> Optional[EmailTemplateAggregate]:
        """Получить шаблон по ID."""
        ...

    async def get_by_key(self, key: str) -> Optional[EmailTemplateAggregate]:
        """Получить шаблон по ключу."""
        ...

    async def get_all(self, is_active: Optional[bool] = True) -> list[EmailTemplateAggregate]:
        """Получить все шаблоны."""
        ...

    async def create(self, aggregate: EmailTemplateAggregate) -> EmailTemplateAggregate:
        """Создать шаблон."""
        ...

    async def delete(self, template_id: int) -> bool:
        """Удалить шаблон."""
        ...

    async def update(self, aggregate: EmailTemplateAggregate) -> EmailTemplateAggregate:
        """Обновить шаблон."""
        ...
