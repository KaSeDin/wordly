from pathlib import Path


def validate_positive_int(field_name: str, value: int) -> int:
    """Validate that value is a positive int (excluding bool) and return it."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer, got {value!r}")
    return value


def validate_non_empty_path(field_name: str, value: Path) -> Path:
    """Validate that value is a Path with a non-empty string representation."""
    if not isinstance(value, Path) or not str(value).strip():
        raise ValueError(f"{field_name} must be a valid non-empty Path, got {value!r}")
    return value