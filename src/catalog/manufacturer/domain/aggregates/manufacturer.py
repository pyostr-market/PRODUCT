from typing import Optional

from src.catalog.manufacturer.domain.exceptions import ManufacturerNameTooShort


class ManufacturerAggregate:

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        manufacturer_id: Optional[int] = None,
    ):
        if not name or len(name.strip()) < 2:
            raise ManufacturerNameTooShort()

        self._id = manufacturer_id
        self._name = name.strip()
        self._description = description

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
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    # -----------------------------
    # Behavior
    # -----------------------------

    def rename(self, new_name: str):
        if not new_name or len(new_name.strip()) < 2:
            raise ManufacturerNameTooShort()

        self._name = new_name.strip()

    def change_description(self, description: Optional[str]):
        self._description = description

    # -----------------------------
    # Internal
    # -----------------------------

    def _set_id(self, manufacturer_id: int):
        self._id = manufacturer_id

    def update(self, name: Optional[str], description: Optional[str]):
        if name is not None:
            self.rename(name)

        if description is not None:
            self.change_description(description)