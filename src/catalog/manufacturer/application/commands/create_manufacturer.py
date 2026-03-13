from typing import Any

from src.catalog.manufacturer.application.dto.audit import ManufacturerAuditDTO
from src.catalog.manufacturer.application.dto.manufacturer import (
    ManufacturerCreateDTO,
    ManufacturerImageReadDTO,
    ManufacturerReadDTO,
)
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
    ManufacturerImageAggregate,
)
from src.catalog.manufacturer.domain.events.manufacturer_events import (
    ManufacturerCreatedEvent,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.uploads.domain.repository.upload_history import UploadHistoryRepository
from src.core.db.unit_of_work import UnitOfWork


class CreateManufacturerCommand:

    def __init__(
        self,
        repository,
        audit_repository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
        upload_history_repository: UploadHistoryRepository,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus
        self.upload_history_repository = upload_history_repository
        self._image_storage = None

    @property
    def image_storage(self):
        if self._image_storage is None:
            from src.core.services.images.storage import S3ImageStorageService
            self._image_storage = S3ImageStorageService.from_settings()
        return self._image_storage

    def _build_image_url(self, file_path: str) -> str:
        """Построить публичный URL для изображения."""
        try:
            return self.image_storage.build_public_url(file_path)
        except Exception:
            return ""

    async def execute(
        self,
        dto: ManufacturerCreateDTO,
        user: User,
    ) -> ManufacturerReadDTO:

        image_dto = None
        if dto.image and dto.image.upload_id:
            upload_record = await self.upload_history_repository.get(dto.image.upload_id)
            if upload_record:
                image_dto = ManufacturerImageAggregate(
                    upload_id=upload_record.upload_id,
                    object_key=upload_record.file_path,
                )

        async with self.uow:
            aggregate = ManufacturerAggregate(
                name=dto.name,
                description=dto.description,
                image=image_dto,
            )

            await self.repository.create(aggregate)

            image_data = None
            if aggregate.image:
                image_data = {
                    "upload_id": aggregate.image.upload_id,
                }

            await self.audit_repository.log(
                ManufacturerAuditDTO(
                    manufacturer_id=aggregate.id,
                    action="create",
                    old_data=None,
                    new_data={
                        "name": aggregate.name,
                        "description": aggregate.description,
                        "image": image_data,
                    },
                    user_id=user.id,
                    fio=user.fio,
                )
            )

            result_image = None
            if aggregate.image:
                result_image = ManufacturerImageReadDTO(
                    upload_id=aggregate.image.upload_id,
                    image_url=self._build_image_url(aggregate.image.object_key),
                )

            result = ManufacturerReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                description=aggregate.description,
                image=result_image,
            )

            # Получаем доменные события из агрегата
            domain_events = aggregate.get_events()

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _build_domain_events(
        self,
        aggregate: ManufacturerAggregate,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, ManufacturerCreatedEvent):
                events.extend(self._build_manufacturer_created_events(aggregate))

        return events

    def _build_manufacturer_created_events(
        self,
        aggregate: ManufacturerAggregate,
    ) -> list[dict[str, Any]]:
        """Построить события для созданного производителя."""
        return [
            build_event(
                event_type="crud",
                method="create",
                app="manufacturers",
                entity="manufacturer",
                entity_id=aggregate.id,
                data={
                    "manufacturer_id": aggregate.id,
                    "fields": {
                        "name": aggregate.name,
                        "description": aggregate.description,
                    },
                },
            ),
        ]
