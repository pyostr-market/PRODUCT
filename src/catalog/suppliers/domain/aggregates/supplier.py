from typing import Optional

from src.catalog.suppliers.domain.exceptions import SupplierNameTooShort


class SupplierAggregate:

    def __init__(
        self,
        name: str,
        contact_email: Optional[str] = None,
        phone: Optional[str] = None,
        supplier_id: Optional[int] = None,
    ):
        if not name or len(name.strip()) < 2:
            raise SupplierNameTooShort()

        self._id = supplier_id
        self._name = name.strip()
        self._contact_email = contact_email
        self._phone = phone

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def contact_email(self) -> Optional[str]:
        return self._contact_email

    @property
    def phone(self) -> Optional[str]:
        return self._phone

    def rename(self, new_name: str):
        if not new_name or len(new_name.strip()) < 2:
            raise SupplierNameTooShort()

        self._name = new_name.strip()

    def change_contact_email(self, contact_email: Optional[str]):
        self._contact_email = contact_email

    def change_phone(self, phone: Optional[str]):
        self._phone = phone

    def _set_id(self, supplier_id: int):
        self._id = supplier_id

    def update(
        self,
        name: Optional[str],
        contact_email: Optional[str],
        phone: Optional[str],
    ):
        if name is not None:
            self.rename(name)

        if contact_email is not None:
            self.change_contact_email(contact_email)

        if phone is not None:
            self.change_phone(phone)
