def normalize_optional_fk(value: int | None) -> int | None:
    if value is None or value <= 0:
        return None
    return value
