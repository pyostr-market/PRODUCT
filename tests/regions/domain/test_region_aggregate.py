"""
Тесты для RegionAggregate.

Проверяют:
- Создание агрегата
- Инварианты (валидация имени)
- Поведение (rename, change_parent)
- Генерацию доменных событий
"""
import pytest

from src.regions.domain.aggregates.region import RegionAggregate
from src.regions.domain.events.region_events import (
    RegionNameChangedEvent,
    RegionParentChangedEvent,
)
from src.regions.domain.exceptions import RegionNameTooShort

# =========================================================
# Создание агрегата
# =========================================================

class TestRegionAggregateCreation:

    def test_create_region_success(self):
        """Успешное создание региона"""
        aggregate = RegionAggregate(
            name="Северо-Западный",
        )

        assert aggregate.id is None
        assert aggregate.name == "Северо-Западный"
        assert aggregate.parent_id is None

    def test_create_region_with_parent(self):
        """Создание с родительским регионом"""
        aggregate = RegionAggregate(
            name="Санкт-Петербург",
            parent_id=1,
        )

        assert aggregate.name == "Санкт-Петербург"
        assert aggregate.parent_id == 1

    def test_create_region_name_trimmed(self):
        """Имя обрезается при создании"""
        aggregate = RegionAggregate(
            name="  Северо-Западный  ",
        )

        assert aggregate.name == "Северо-Западный"

    def test_create_region_with_id(self):
        """Создание с указанным ID"""
        aggregate = RegionAggregate(
            name="Северо-Западный",
            region_id=42,
        )

        assert aggregate.id == 42


# =========================================================
# Валидация имени
# =========================================================

class TestRegionNameValidation:

    def test_create_region_name_too_short(self):
        """Имя слишком короткое (1 символ)"""
        with pytest.raises(RegionNameTooShort):
            RegionAggregate(name="А")

    def test_create_region_name_empty(self):
        """Пустое имя"""
        with pytest.raises(RegionNameTooShort):
            RegionAggregate(name="")

    def test_create_region_name_whitespace_only(self):
        """Имя только из пробелов"""
        with pytest.raises(RegionNameTooShort):
            RegionAggregate(name="   ")

    def test_create_region_name_two_chars_valid(self):
        """Имя из 2 символов валидно"""
        aggregate = RegionAggregate(name="СП")
        assert aggregate.name == "СП"


# =========================================================
# Переименование
# =========================================================

class TestRegionRename:

    def test_rename_success(self):
        """Успешное переименование"""
        aggregate = RegionAggregate(name="Северо-Западный")
        aggregate.rename("Северо-Западный федеральный округ")

        assert aggregate.name == "Северо-Западный федеральный округ"

    def test_rename_generates_event(self):
        """Переименование генерирует событие"""
        aggregate = RegionAggregate(
            name="Северо-Западный",
            region_id=42,
        )
        aggregate.rename("Северо-Западный ФО")

        events = aggregate.get_events()

        assert len(events) == 1
        assert isinstance(events[0], RegionNameChangedEvent)
        assert events[0].region_id == 42
        assert events[0].old_name == "Северо-Западный"
        assert events[0].new_name == "Северо-Западный ФО"

    def test_rename_name_too_short(self):
        """Переименование в слишком короткое имя"""
        aggregate = RegionAggregate(name="Северо-Западный")

        with pytest.raises(RegionNameTooShort):
            aggregate.rename("А")

    def test_rename_name_empty(self):
        """Переименование в пустое имя"""
        aggregate = RegionAggregate(name="Северо-Западный")

        with pytest.raises(RegionNameTooShort):
            aggregate.rename("")

    def test_rename_name_trimmed(self):
        """Имя обрезается при переименовании"""
        aggregate = RegionAggregate(name="Северо-Западный")
        aggregate.rename("  Санкт-Петербург  ")

        assert aggregate.name == "Санкт-Петербург"

    def test_rename_multiple_times(self):
        """Многократное переименование"""
        aggregate = RegionAggregate(name="Регион 1")
        aggregate.rename("Регион 2")
        aggregate.rename("Регион 3")

        assert aggregate.name == "Регион 3"

        events = aggregate.get_events()
        assert len(events) == 2  # Два события переименования


# =========================================================
# Изменение родителя
# =========================================================

class TestRegionChangeParent:

    def test_change_parent_success(self):
        """Успешное изменение родителя"""
        aggregate = RegionAggregate(
            name="Санкт-Петербург",
            parent_id=1,
        )
        aggregate.change_parent(2)

        assert aggregate.parent_id == 2

    def test_change_parent_to_none(self):
        """Изменение родителя на None"""
        aggregate = RegionAggregate(
            name="Санкт-Петербург",
            parent_id=1,
        )
        aggregate.change_parent(None)

        assert aggregate.parent_id is None

    def test_change_parent_from_none(self):
        """Изменение родителя с None на значение"""
        aggregate = RegionAggregate(
            name="Санкт-Петербург",
        )
        aggregate.change_parent(1)

        assert aggregate.parent_id == 1

    def test_change_parent_generates_event(self):
        """Изменение родителя генерирует событие"""
        aggregate = RegionAggregate(
            name="Санкт-Петербург",
            parent_id=1,
            region_id=42,
        )
        aggregate.change_parent(2)

        events = aggregate.get_events()

        assert len(events) == 1
        assert isinstance(events[0], RegionParentChangedEvent)
        assert events[0].region_id == 42
        assert events[0].old_parent_id == 1
        assert events[0].new_parent_id == 2


# =========================================================
# Метод update
# =========================================================

class TestRegionUpdate:

    def test_update_both_fields(self):
        """Обновление обоих полей"""
        aggregate = RegionAggregate(
            name="Северо-Западный",
            parent_id=None,
        )
        aggregate.update(name="Северо-Западный ФО", parent_id=1)

        assert aggregate.name == "Северо-Западный ФО"
        assert aggregate.parent_id == 1

    def test_update_only_name(self):
        """Обновление только имени"""
        aggregate = RegionAggregate(
            name="Северо-Западный",
            parent_id=1,
        )
        aggregate.update(name="Северо-Западный ФО", parent_id=None)

        assert aggregate.name == "Северо-Западный ФО"
        assert aggregate.parent_id == 1

    def test_update_only_parent(self):
        """Обновление только родителя"""
        aggregate = RegionAggregate(
            name="Северо-Западный",
            parent_id=None,
        )
        aggregate.update(name=None, parent_id=2)

        assert aggregate.name == "Северо-Западный"
        assert aggregate.parent_id == 2

    def test_update_no_fields(self):
        """Обновление без полей (ничего не меняется)"""
        aggregate = RegionAggregate(
            name="Северо-Западный",
            parent_id=1,
        )
        aggregate.update(name=None, parent_id=None)

        assert aggregate.name == "Северо-Западный"
        assert aggregate.parent_id == 1

    def test_update_generates_events(self):
        """Обновление генерирует события"""
        aggregate = RegionAggregate(
            name="Северо-Западный",
            parent_id=None,
            region_id=42,
        )
        aggregate.update(name="Северо-Западный ФО", parent_id=1)

        events = aggregate.get_events()

        assert len(events) == 2
        event_types = [type(e).__name__ for e in events]
        assert "RegionNameChangedEvent" in event_types
        assert "RegionParentChangedEvent" in event_types


# =========================================================
# Domain Events
# =========================================================

class TestRegionEvents:

    def test_get_events_clears_queue(self):
        """get_events() очищает очередь событий"""
        aggregate = RegionAggregate(name="Северо-Западный", region_id=42)
        aggregate.rename("Новое имя")

        events1 = aggregate.get_events()
        events2 = aggregate.get_events()

        assert len(events1) == 1
        assert len(events2) == 0

    def test_clear_events(self):
        """clear_events() очищает очередь"""
        aggregate = RegionAggregate(name="Северо-Западный", region_id=42)
        aggregate.rename("Новое имя")

        aggregate.clear_events()
        events = aggregate.get_events()

        assert len(events) == 0

    def test_multiple_events_accumulated(self):
        """Несколько событий накапливаются"""
        aggregate = RegionAggregate(name="Северо-Западный", region_id=42)
        aggregate.rename("Новое имя")
        aggregate.change_parent(1)
        aggregate.rename("Еще имя")

        events = aggregate.get_events()

        assert len(events) == 3


# =========================================================
# Identity
# =========================================================

class TestRegionIdentity:

    def test_set_id(self):
        """Установка ID"""
        aggregate = RegionAggregate(name="Северо-Западный")
        aggregate._set_id(42)

        assert aggregate.id == 42

    def test_id_immutable_via_property(self):
        """ID нельзя изменить через property"""
        aggregate = RegionAggregate(name="Северо-Западный", region_id=42)

        # id - это property без setter, поэтому присваивание не сработает
        with pytest.raises(AttributeError):
            aggregate.id = 99
