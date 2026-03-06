"""
Тесты для ManufacturerAggregate.

Проверяют:
- Создание агрегата
- Инварианты (валидация имени)
- Поведение (rename, change_description)
- Генерацию доменных событий
"""
import pytest

from src.catalog.manufacturer.domain.aggregates.manufacturer import ManufacturerAggregate
from src.catalog.manufacturer.domain.events.manufacturer_events import (
    ManufacturerDescriptionChangedEvent,
    ManufacturerNameChangedEvent,
)
from src.catalog.manufacturer.domain.exceptions import ManufacturerNameTooShort


# =========================================================
# Создание агрегата
# =========================================================

class TestManufacturerAggregateCreation:

    def test_create_manufacturer_success(self):
        """Успешное создание производителя"""
        aggregate = ManufacturerAggregate(
            name="Test Manufacturer",
            description="Test description",
        )

        assert aggregate.id is None
        assert aggregate.name == "Test Manufacturer"
        assert aggregate.description == "Test description"

    def test_create_manufacturer_without_description(self):
        """Создание без описания"""
        aggregate = ManufacturerAggregate(
            name="Test Manufacturer",
        )

        assert aggregate.name == "Test Manufacturer"
        assert aggregate.description is None

    def test_create_manufacturer_name_trimmed(self):
        """Имя обрезается при создании"""
        aggregate = ManufacturerAggregate(
            name="  Test Manufacturer  ",
        )

        assert aggregate.name == "Test Manufacturer"

    def test_create_manufacturer_with_id(self):
        """Создание с указанным ID"""
        aggregate = ManufacturerAggregate(
            name="Test Manufacturer",
            manufacturer_id=42,
        )

        assert aggregate.id == 42


# =========================================================
# Валидация имени
# =========================================================

class TestManufacturerNameValidation:

    def test_create_manufacturer_name_too_short(self):
        """Имя слишком короткое (1 символ)"""
        with pytest.raises(ManufacturerNameTooShort):
            ManufacturerAggregate(name="A")

    def test_create_manufacturer_name_empty(self):
        """Пустое имя"""
        with pytest.raises(ManufacturerNameTooShort):
            ManufacturerAggregate(name="")

    def test_create_manufacturer_name_whitespace_only(self):
        """Имя только из пробелов"""
        with pytest.raises(ManufacturerNameTooShort):
            ManufacturerAggregate(name="   ")

    def test_create_manufacturer_name_two_chars_valid(self):
        """Имя из 2 символов валидно"""
        aggregate = ManufacturerAggregate(name="AB")
        assert aggregate.name == "AB"


# =========================================================
# Переименование
# =========================================================

class TestManufacturerRename:

    def test_rename_success(self):
        """Успешное переименование"""
        aggregate = ManufacturerAggregate(name="Old Name")
        aggregate.rename("New Name")

        assert aggregate.name == "New Name"

    def test_rename_generates_event(self):
        """Переименование генерирует событие"""
        aggregate = ManufacturerAggregate(
            name="Old Name",
            manufacturer_id=42,
        )
        aggregate.rename("New Name")

        events = aggregate.get_events()

        assert len(events) == 1
        assert isinstance(events[0], ManufacturerNameChangedEvent)
        assert events[0].manufacturer_id == 42
        assert events[0].old_name == "Old Name"
        assert events[0].new_name == "New Name"

    def test_rename_name_too_short(self):
        """Переименование в слишком короткое имя"""
        aggregate = ManufacturerAggregate(name="Valid Name")

        with pytest.raises(ManufacturerNameTooShort):
            aggregate.rename("A")

    def test_rename_name_empty(self):
        """Переименование в пустое имя"""
        aggregate = ManufacturerAggregate(name="Valid Name")

        with pytest.raises(ManufacturerNameTooShort):
            aggregate.rename("")

    def test_rename_name_trimmed(self):
        """Имя обрезается при переименовании"""
        aggregate = ManufacturerAggregate(name="Old Name")
        aggregate.rename("  New Name  ")

        assert aggregate.name == "New Name"

    def test_rename_multiple_times(self):
        """Многократное переименование"""
        aggregate = ManufacturerAggregate(name="Name 1")
        aggregate.rename("Name 2")
        aggregate.rename("Name 3")

        assert aggregate.name == "Name 3"

        events = aggregate.get_events()
        assert len(events) == 2  # Два события переименования


# =========================================================
# Изменение описания
# =========================================================

class TestManufacturerChangeDescription:

    def test_change_description_success(self):
        """Успешное изменение описания"""
        aggregate = ManufacturerAggregate(
            name="Test",
            description="Old description",
        )
        aggregate.change_description("New description")

        assert aggregate.description == "New description"

    def test_change_description_to_none(self):
        """Изменение описания на None"""
        aggregate = ManufacturerAggregate(
            name="Test",
            description="Old description",
        )
        aggregate.change_description(None)

        assert aggregate.description is None

    def test_change_description_generates_event(self):
        """Изменение описания генерирует событие"""
        aggregate = ManufacturerAggregate(
            name="Test",
            description="Old description",
            manufacturer_id=42,
        )
        aggregate.change_description("New description")

        events = aggregate.get_events()

        assert len(events) == 1
        assert isinstance(events[0], ManufacturerDescriptionChangedEvent)
        assert events[0].manufacturer_id == 42
        assert events[0].old_description == "Old description"
        assert events[0].new_description == "New description"

    def test_change_description_from_none(self):
        """Изменение описания с None на значение"""
        aggregate = ManufacturerAggregate(
            name="Test",
            description=None,
        )
        aggregate.change_description("New description")

        assert aggregate.description == "New description"


# =========================================================
# Метод update
# =========================================================

class TestManufacturerUpdate:

    def test_update_both_fields(self):
        """Обновление обоих полей"""
        aggregate = ManufacturerAggregate(
            name="Old Name",
            description="Old description",
        )
        aggregate.update(name="New Name", description="New description")

        assert aggregate.name == "New Name"
        assert aggregate.description == "New description"

    def test_update_only_name(self):
        """Обновление только имени"""
        aggregate = ManufacturerAggregate(
            name="Old Name",
            description="Description",
        )
        aggregate.update(name="New Name", description=None)

        assert aggregate.name == "New Name"
        assert aggregate.description == "Description"

    def test_update_only_description(self):
        """Обновление только описания"""
        aggregate = ManufacturerAggregate(
            name="Name",
            description="Old description",
        )
        aggregate.update(name=None, description="New description")

        assert aggregate.name == "Name"
        assert aggregate.description == "New description"

    def test_update_no_fields(self):
        """Обновление без полей (ничего не меняется)"""
        aggregate = ManufacturerAggregate(
            name="Name",
            description="Description",
        )
        aggregate.update(name=None, description=None)

        assert aggregate.name == "Name"
        assert aggregate.description == "Description"

    def test_update_generates_events(self):
        """Обновление генерирует события"""
        aggregate = ManufacturerAggregate(
            name="Old Name",
            description="Old description",
            manufacturer_id=42,
        )
        aggregate.update(name="New Name", description="New description")

        events = aggregate.get_events()

        assert len(events) == 2
        event_types = [type(e).__name__ for e in events]
        assert "ManufacturerNameChangedEvent" in event_types
        assert "ManufacturerDescriptionChangedEvent" in event_types


# =========================================================
# Domain Events
# =========================================================

class TestManufacturerEvents:

    def test_get_events_clears_queue(self):
        """get_events() очищает очередь событий"""
        aggregate = ManufacturerAggregate(name="Test", manufacturer_id=42)
        aggregate.rename("New Name")

        events1 = aggregate.get_events()
        events2 = aggregate.get_events()

        assert len(events1) == 1
        assert len(events2) == 0

    def test_clear_events(self):
        """clear_events() очищает очередь"""
        aggregate = ManufacturerAggregate(name="Test", manufacturer_id=42)
        aggregate.rename("New Name")

        aggregate.clear_events()
        events = aggregate.get_events()

        assert len(events) == 0

    def test_multiple_events_accumulated(self):
        """Несколько событий накапливаются"""
        aggregate = ManufacturerAggregate(name="Test", manufacturer_id=42)
        aggregate.rename("Name 2")
        aggregate.change_description("Description")
        aggregate.rename("Name 3")

        events = aggregate.get_events()

        assert len(events) == 3


# =========================================================
# Identity
# =========================================================

class TestManufacturerIdentity:

    def test_set_id(self):
        """Установка ID"""
        aggregate = ManufacturerAggregate(name="Test")
        aggregate._set_id(42)

        assert aggregate.id == 42

    def test_id_immutable_via_property(self):
        """ID нельзя изменить через property"""
        aggregate = ManufacturerAggregate(name="Test", manufacturer_id=42)

        # id - это property без setter, поэтому присваивание не сработает
        # или вызовет ошибку
        with pytest.raises(AttributeError):
            aggregate.id = 99
