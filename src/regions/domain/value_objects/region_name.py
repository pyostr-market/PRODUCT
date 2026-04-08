from dataclasses import dataclass

from src.regions.domain.exceptions import RegionNameTooShort


@dataclass(frozen=True)
class RegionName:
    """Value Object для имени региона."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 2:
            raise RegionNameTooShort()
        object.__setattr__(self, 'value', self.value.strip())

    def __str__(self) -> str:
        return self.value
