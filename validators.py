from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")

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

def validate_not_none(field_name: str, value: T | None) -> T:
    """Validate that value is not None and return it."""
    if value is None:
        raise ValueError(f"{field_name} must not be None")
    return value

def validate_has_attr(
    field_name: str,
    value: Any,
    attr_name: str,
    *,
    callable_required: bool = False,
) -> Any:
    """Validate that value defines attr_name (and optionally is callable)."""
    if not hasattr(value, attr_name):
        raise AttributeError(f"{field_name} must have attribute '{attr_name}'")
    attr = getattr(value, attr_name)
    if callable_required and not callable(attr):
        raise TypeError(f"{field_name}.'{attr_name}' must be callable")
    return value