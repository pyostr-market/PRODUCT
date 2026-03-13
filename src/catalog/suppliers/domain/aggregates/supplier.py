from typing import Optional

from src.catalog.suppliers.domain.events.base import DomainEvent
from src.catalog.suppliers.domain.events.supplier_events import (
    SupplierContactEmailChangedEvent,
    SupplierNameChangedEvent,
    SupplierPhoneChangedEvent,
)
from src.catalog.suppliers.domain.exceptions import SupplierNameTooShort
from src.catalog.suppliers.domain.value_objects import (
    ContactEmail,
    PhoneNumber,
    SupplierName,
)


class SupplierAggregate:
    """
    Aggregate Root для Supplier.

    Отвечает за:
    - Согласованность данных поставщика
    - Публикацию доменных событий при изменениях
    """

    def __init__(
        self,
        name: str | SupplierName,
        contact_email: str | ContactEmail | None = None,
        phone: str | PhoneNumber | None = None,
        supplier_id: Optional[int] = None,
    ):
        # Используем Value Objects
        self._name_obj = name if isinstance(name, SupplierName) else SupplierName(name)
        self._contact_email_obj = ContactEmail.create_optional(
            contact_email.value if isinstance(contact_email, ContactEmail) else contact_email
        )
        self._phone_obj = PhoneNumber.create_optional(
            phone.value if isinstance(phone, PhoneNumber) else phone
        )

        self._id = supplier_id
        self._events: list[DomainEvent] = []

    # -----------------------------
    # Identity
    # -----------------------------

    @property
    def id(self) -> Optional[int]:
        return self._id

    # -----------------------------
    # State
    # -----------------------------

    @property
    def name(self) -> str:
        return str(self._name_obj)

    @property
    def name_obj(self) -> SupplierName:
        """Вернуть Value Object имени поставщика."""
        return self._name_obj

    @property
    def contact_email(self) -> Optional[str]:
        return self._contact_email_obj.value if self._contact_email_obj else None

    @property
    def contact_email_obj(self) -> Optional[ContactEmail]:
        """Вернуть Value Object email."""
        return self._contact_email_obj

    @property
    def phone(self) -> Optional[str]:
        return self._phone_obj.value if self._phone_obj else None

    @property
    def phone_obj(self) -> Optional[PhoneNumber]:
        """Вернуть Value Object телефона."""
        return self._phone_obj

    # -----------------------------
    # Events
    # -----------------------------

    def get_events(self) -> list[DomainEvent]:
        """Вернуть все накопленные события и очистить очередь."""
        events = self._events.copy()
        self._events.clear()
        return events

    def clear_events(self):
        """Очистить очередь событий."""
        self._events.clear()

    def _record_event(self, event: DomainEvent):
        """Записать доменное событие."""
        self._events.append(event)

    # -----------------------------
    # Behavior
    # -----------------------------

    def rename(self, new_name: str | SupplierName):
        """Изменить имя поставщика."""
        old_name = self._name_obj
        new_name_obj = new_name if isinstance(new_name, SupplierName) else SupplierName(new_name)
        self._name_obj = new_name_obj
        self._record_event(SupplierNameChangedEvent(
            supplier_id=self._id,
            old_name=str(old_name),
            new_name=str(new_name_obj),
        ))

    def change_contact_email(self, contact_email: str | ContactEmail | None):
        """Изменить контактный email."""
        old_email = self._contact_email_obj
        new_email_obj = ContactEmail.create_optional(
            contact_email.value if isinstance(contact_email, ContactEmail) else contact_email
        )
        self._contact_email_obj = new_email_obj
        self._record_event(SupplierContactEmailChangedEvent(
            supplier_id=self._id,
            old_email=old_email.value if old_email else None,
            new_email=new_email_obj.value if new_email_obj else None,
        ))

    def change_phone(self, phone: str | PhoneNumber | None):
        """Изменить телефон."""
        old_phone = self._phone_obj
        new_phone_obj = PhoneNumber.create_optional(
            phone.value if isinstance(phone, PhoneNumber) else phone
        )
        self._phone_obj = new_phone_obj
        self._record_event(SupplierPhoneChangedEvent(
            supplier_id=self._id,
            old_phone=old_phone.value if old_phone else None,
            new_phone=new_phone_obj.value if new_phone_obj else None,
        ))

    # -----------------------------
    # Internal
    # -----------------------------

    def _set_id(self, supplier_id: int):
        self._id = supplier_id

    def update(
        self,
        name: Optional[str],
        contact_email: Optional[str],
        phone: Optional[str],
    ):
        """Обновить данные поставщика."""
        if name is not None:
            self.rename(name)

        if contact_email is not None:
            self.change_contact_email(contact_email)

        if phone is not None:
            self.change_phone(phone)
