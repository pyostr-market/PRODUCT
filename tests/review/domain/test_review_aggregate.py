"""
Тесты для ReviewAggregate.

Проверяют:
- Создание агрегата
- Валидацию рейтинга (1-5)
- Валидацию текста
- Поведение (update_rating, update_text, update)
- Проверку владельца
- Генерацию доменных событий
"""
from decimal import Decimal

import pytest

from src.catalog.review.domain.aggregates.review import ReviewAggregate
from src.catalog.review.domain.aggregates.review_image import ReviewImageAggregate
from src.catalog.review.domain.events.review_events import (
    ReviewCreatedEvent,
    ReviewDeletedEvent,
    ReviewUpdatedEvent,
)
from src.catalog.review.domain.exceptions import (
    InvalidRatingError,
    ReviewNotOwnedError,
)


# =========================================================
# Создание агрегата
# =========================================================

class TestReviewAggregateCreation:

    def test_create_review_success(self):
        """Успешное создание отзыва с рейтингом"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Иван Петров",
            rating=4,
            text="Хороший товар",
        )

        assert aggregate.id is None
        assert aggregate.product_id == 1
        assert aggregate.user_id == 10
        assert aggregate.username == "Иван Петров"
        assert aggregate.rating == Decimal("4.0")
        assert aggregate.text == "Хороший товар"
        assert aggregate.images == []

    def test_create_review_without_text(self):
        """Создание отзыва только с рейтингом (без текста)"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Иван Петров",
            rating=5,
        )

        assert aggregate.text is None

    def test_create_review_with_images(self):
        """Создание отзыва с изображениями"""
        images = [
            ReviewImageAggregate(upload_id=1, ordering=0),
            ReviewImageAggregate(upload_id=2, ordering=1),
        ]
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test User",
            rating=5,
            text="С фото",
            images=images,
        )

        assert len(aggregate.images) == 2
        assert aggregate.images[0].upload_id == 1

    def test_create_review_username_trimmed(self):
        """Имя пользователя обрезается"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="  Иван Петров  ",
            rating=3,
        )

        assert aggregate.username == "Иван Петров"

    def test_create_review_with_id(self):
        """Создание с указанным ID"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=5,
            review_id=42,
        )

        assert aggregate.id == 42


# =========================================================
# Валидация рейтинга
# =========================================================

class TestReviewRatingValidation:

    def test_rating_minimum_valid(self):
        """Рейтинг 1 — валиден"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=1,
        )

        assert aggregate.rating == Decimal("1.0")

    def test_rating_maximum_valid(self):
        """Рейтинг 5 — валиден"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=5,
        )

        assert aggregate.rating == Decimal("5.0")

    def test_rating_decimal_valid(self):
        """Рейтинг 4.5 — валиден"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=Decimal("4.5"),
        )

        assert aggregate.rating == Decimal("4.5")

    def test_rating_below_minimum(self):
        """Рейтинг 0 — ниже минимума"""
        with pytest.raises(InvalidRatingError):
            ReviewAggregate(
                product_id=1,
                user_id=10,
                username="Test",
                rating=0,
            )

    def test_rating_above_maximum(self):
        """Рейтинг 6 — выше максимума"""
        with pytest.raises(InvalidRatingError):
            ReviewAggregate(
                product_id=1,
                user_id=10,
                username="Test",
                rating=6,
            )

    def test_rating_negative(self):
        """Рейтинг -1 — отрицательный"""
        with pytest.raises(InvalidRatingError):
            ReviewAggregate(
                product_id=1,
                user_id=10,
                username="Test",
                rating=-1,
            )

    def test_rating_float_valid(self):
        """Рейтинг 3.5 как float — валиден"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3.5,
        )

        assert aggregate.rating == Decimal("3.5")


# =========================================================
# Валидация текста
# =========================================================

class TestReviewTextValidation:

    def test_text_max_length_valid(self):
        """Текст максимальной длины (5000) — валиден"""
        text = "a" * 5000
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=4,
            text=text,
        )

        assert aggregate.text == text

    def test_text_too_long(self):
        """Текст длиннее 5000 символов"""
        with pytest.raises(ValueError):
            ReviewAggregate(
                product_id=1,
                user_id=10,
                username="Test",
                rating=4,
                text="a" * 5001,
            )

    def test_text_empty_string(self):
        """Пустая строка остаётся пустой строкой"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=4,
            text="",
        )

        assert aggregate.text == ""

    def test_text_whitespace_only(self):
        """Текст только из пробелов становится пустой строкой"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=4,
            text="   ",
        )

        assert aggregate.text == ""


# =========================================================
# Обновление рейтинга
# =========================================================

class TestReviewUpdateRating:

    def test_update_rating_success(self):
        """Успешное обновление рейтинга"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3,
        )
        aggregate.update_rating(5)

        assert aggregate.rating == Decimal("5.0")

    def test_update_rating_generates_event(self):
        """Обновление рейтинга генерирует событие"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3,
            review_id=42,
        )
        aggregate.update_rating(4)

        events = aggregate.get_events()

        assert len(events) == 1
        assert isinstance(events[0], ReviewUpdatedEvent)
        assert events[0].old_rating == Decimal("3.0")
        assert events[0].new_rating == Decimal("4.0")

    def test_update_rating_invalid(self):
        """Обновление на невалидный рейтинг"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3,
        )

        with pytest.raises(InvalidRatingError):
            aggregate.update_rating(6)


# =========================================================
# Обновление текста
# =========================================================

class TestReviewUpdateText:

    def test_update_text_success(self):
        """Успешное обновление текста"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=4,
            text="Old text",
        )
        aggregate.update_text("New text")

        assert aggregate.text == "New text"

    def test_update_text_generates_event(self):
        """Обновление текста генерирует событие"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=4,
            text="Old text",
            review_id=42,
        )
        aggregate.update_text("New text")

        events = aggregate.get_events()

        assert len(events) == 1
        assert isinstance(events[0], ReviewUpdatedEvent)
        assert events[0].old_text == "Old text"
        assert events[0].new_text == "New text"

    def test_update_text_to_none(self):
        """Обновление текста на None"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=4,
            text="Old text",
        )
        aggregate.update_text(None)

        assert aggregate.text is None

    def test_update_text_too_long(self):
        """Обновление на слишком длинный текст"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=4,
            text="Old",
        )

        with pytest.raises(ValueError):
            aggregate.update_text("a" * 5001)


# =========================================================
# Метод update
# =========================================================

class TestReviewUpdate:

    def test_update_both_fields(self):
        """Обновление и рейтинга и текста"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3,
            text="Old",
        )
        aggregate.update(rating=5, text="New")

        assert aggregate.rating == Decimal("5.0")
        assert aggregate.text == "New"

    def test_update_only_rating(self):
        """Обновление только рейтинга"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3,
            text="Text",
        )
        aggregate.update(rating=4)

        assert aggregate.rating == Decimal("4.0")
        assert aggregate.text == "Text"

    def test_update_only_text(self):
        """Обновление только текста"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3,
            text="Old",
        )
        aggregate.update(text="New")

        assert aggregate.text == "New"
        assert aggregate.rating == Decimal("3.0")

    def test_update_no_fields(self):
        """Обновление без полей"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3,
            text="Text",
        )
        aggregate.update()

        assert aggregate.rating == Decimal("3.0")
        assert aggregate.text == "Text"

    def test_update_generates_two_events(self):
        """Обновление обоих полей генерирует два события"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3,
            text="Old",
            review_id=42,
        )
        aggregate.update(rating=4, text="New")

        events = aggregate.get_events()

        assert len(events) == 2


# =========================================================
# Работа с изображениями
# =========================================================

class TestReviewImages:

    def test_add_image(self):
        """Добавление изображения"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=5,
        )
        aggregate.add_image(ReviewImageAggregate(upload_id=1, ordering=0))

        assert len(aggregate.images) == 1
        assert aggregate.images[0].upload_id == 1

    def test_remove_image_by_upload_id(self):
        """Удаление изображения по upload_id"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=5,
            images=[
                ReviewImageAggregate(upload_id=1, ordering=0),
                ReviewImageAggregate(upload_id=2, ordering=1),
            ],
        )
        aggregate.remove_image_by_upload_id(1)

        assert len(aggregate.images) == 1
        assert aggregate.images[0].upload_id == 2

    def test_set_images(self):
        """Замена всех изображений"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=5,
        )
        aggregate.set_images([
            ReviewImageAggregate(upload_id=10, ordering=0),
            ReviewImageAggregate(upload_id=20, ordering=1),
        ])

        assert len(aggregate.images) == 2
        assert aggregate.images[0].upload_id == 10


# =========================================================
# Проверка владельца
# =========================================================

class TestReviewOwnership:

    def test_check_ownership_success(self):
        """Пользователь владеет отзывом"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=5,
        )

        # Не должно вызывать исключение
        aggregate.check_ownership(10)

    def test_check_ownership_fail(self):
        """Пользователь не владеет отзывом"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=5,
            review_id=42,
        )

        with pytest.raises(ReviewNotOwnedError) as exc_info:
            aggregate.check_ownership(99)

        assert exc_info.value.user_id == 99
        assert exc_info.value.review_id == 42


# =========================================================
# Domain Events
# =========================================================

class TestReviewEvents:

    def test_get_events_clears_queue(self):
        """get_events() очищает очередь событий"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3,
            review_id=42,
        )
        aggregate.update_rating(4)

        events1 = aggregate.get_events()
        events2 = aggregate.get_events()

        assert len(events1) == 1
        assert len(events2) == 0

    def test_clear_events(self):
        """clear_events() очищает очередь"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3,
            review_id=42,
        )
        aggregate.update_rating(4)
        aggregate.clear_events()

        events = aggregate.get_events()
        assert len(events) == 0

    def test_multiple_events_accumulated(self):
        """Несколько событий накапливаются"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=3,
            review_id=42,
        )
        aggregate.update_rating(4)
        aggregate.update_text("Text")
        aggregate.update_rating(5)

        events = aggregate.get_events()
        assert len(events) == 3

    def test_capture_state(self):
        """_capture_state возвращает dict с текущим состоянием"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test User",
            rating=4,
            text="Good",
        )

        state = aggregate._capture_state()

        assert state["product_id"] == 1
        assert state["user_id"] == 10
        assert state["username"] == "Test User"
        assert state["rating"] == "4"
        assert state["text"] == "Good"
        assert state["image_upload_ids"] == []

    def test_capture_state_with_images(self):
        """_capture_state с изображениями"""
        aggregate = ReviewAggregate(
            product_id=1,
            user_id=10,
            username="Test",
            rating=5,
            images=[
                ReviewImageAggregate(upload_id=10),
                ReviewImageAggregate(upload_id=20),
            ],
        )

        state = aggregate._capture_state()

        assert state["image_upload_ids"] == [10, 20]
