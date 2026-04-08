from dataclasses import dataclass


@dataclass(frozen=True)
class RegionId:
    """Value Object для ID региона."""

    value: int
