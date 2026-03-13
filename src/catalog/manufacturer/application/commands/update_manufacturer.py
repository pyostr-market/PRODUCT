from typing import Any

from src.catalog.manufacturer.application.dto.audit import ManufacturerAuditDTO
from src.catalog.manufacturer.application.dto.manufacturer import (
    ManufacturerImageReadDTO,
    ManufacturerReadDTO,
    ManufacturerUpdateDTO,
)
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
    ManufacturerImageAggregate,
)
from src.catalog.manufacturer.domain.events.manufacturer_events import (
    ManufacturerUpdatedEvent,
)
from src.catalog.manufacturer.domain.exceptions import ManufacturerNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.uploads.domain.repository.upload_history import UploadHistoryRepository
from src.core.db.unit_of_work import UnitOfWork


class UpdateManufacturerCommand:

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
        manufacturer_id: int,
        dto: ManufacturerUpdateDTO,
        user: User,
    ) -> ManufacturerReadDTO:

        async with self.uow:
            aggregate = await self.repository.get(manufacturer_id)

            if not aggregate:
                raise ManufacturerNotFound()

            old_image_data = None
            if aggregate.image:
                old_image_data = {"upload_id": aggregate.image.upload_id}

            old_data = {
                "name": aggregate.name,
                "description": aggregate.description,
                "image": old_image_data,
            }

            # Применяем операцию с изображением, если передана
            if dto.image:
                await self._process_image_operation(dto.image, aggregate)

            aggregate.update(dto.name, dto.description)

            await self.repository.update(aggregate)

            new_image_data = None
            if aggregate.image:
                new_image_data = {"upload_id": aggregate.image.upload_id}

            new_data = {
                "name": aggregate.name,
                "description": aggregate.description,
                "image": new_image_data,
            }

            if old_data != new_data:
                await self.audit_repository.log(
                    ManufacturerAuditDTO(
                        manufacturer_id=aggregate.id,
                        action="update",
                        old_data=old_data,
                        new_data=new_data,
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

        changed_fields = {
            key: value
            for key, value in new_data.items()
            if old_data.get(key) != value
        }

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events, changed_fields)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    async def _process_image_operation(
        self,
        op,
        aggregate: ManufacturerAggregate,
    ):
        """Обработать операцию с изображением."""
        if op.action == "delete":
            aggregate.remove_image()
        elif op.action in ("create", "update"):
            if op.upload_id:
                upload_record = await self.upload_history_repository.get(op.upload_id)
                if upload_record:
                    aggregate.set_image(ManufacturerImageAggregate(
                        upload_id=upload_record.upload_id,
                        object_key=upload_record.file_path,
                    ))
        # action "pass" — оставляем существующее изображение без изменений

    def _build_domain_events(
        self,
        aggregate: ManufacturerAggregate,
        domain_events: list,
        changed_fields: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, ManufacturerUpdatedEvent):
                events.append(self._build_manufacturer_updated_event(aggregate, changed_fields))

        if not events and changed_fields:
            events.append(self._build_manufacturer_updated_event(aggregate, changed_fields))

        return events

    def _build_manufacturer_updated_event(
        self,
        aggregate: ManufacturerAggregate,
        changed_fields: dict[str, Any],
    ) -> dict[str, Any]:
        """Построить событие для обновленного производителя."""
        return build_event(
            event_type="crud",
            method="update",
            app="manufacturers",
            entity="manufacturer",
            entity_id=aggregate.id,
            data={
                "manufacturer_id": aggregate.id,
                "fields": changed_fields,
            },
        )
