from abc import ABC


class PageSlugUniquenessService(ABC):
    """
    Domain Service для проверки уникальности slug страницы.
    
    Используется для проверки бизнес-инварианта:
    - slug страницы должен быть уникальным в пределах системы
    
    Почему Domain Service:
    - Логика не принадлежит конкретному агрегату
    - Требует доступа к репозиторию для проверки существования
    - Представляет доменную операцию проверки инварианта
    """

    async def is_slug_unique(self, slug: str, exclude_id: int | None = None) -> bool:
        """
        Проверить, является ли slug уникальным.
        
        Args:
            slug: Slug для проверки
            exclude_id: Исключить страницу с данным ID (для обновления)
            
        Returns:
            True если slug уникален, False если уже существует
        """
        ...

    async def ensure_slug_is_unique(self, slug: str, exclude_id: int | None = None):
        """
        Убедиться, что slug уникален, иначе выбросить исключение.
        
        Args:
            slug: Slug для проверки
            exclude_id: Исключить страницу с данным ID (для обновления)
            
        Raises:
            PageSlugAlreadyExists: Если slug уже существует
        """
        ...
