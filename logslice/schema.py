"""Validate log entries against a simple field schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator

_TYPE_MAP: dict[str, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


@dataclass
class FieldSpec:
    """Specification for a single log field."""

    name: str
    required: bool = False
    expected_type: str | None = None  # one of: str, int, float, bool

    def validate(self, entry: dict) -> list[str]:
        """Return a list of validation error messages for *entry*."""
        errors: list[str] = []
        if self.name not in entry:
            if self.required:
                errors.append(f"Missing required field: {self.name!r}")
            return errors

        if self.expected_type is not None:
            python_type = _TYPE_MAP.get(self.expected_type)
            if python_type is None:
                errors.append(
                    f"Unknown expected_type {self.expected_type!r} for field {self.name!r}"
                )
            elif not isinstance(entry[self.name], python_type):
                actual = type(entry[self.name]).__name__
                errors.append(
                    f"Field {self.name!r} expected {self.expected_type}, got {actual!r}"
                )
        return errors


@dataclass
class Schema:
    """Collection of :class:`FieldSpec` objects."""

    specs: list[FieldSpec] = field(default_factory=list)

    def validate_entry(self, entry: dict) -> list[str]:
        """Return all validation errors for *entry*."""
        errors: list[str] = []
        for spec in self.specs:
            errors.extend(spec.validate(entry))
        return errors

    def is_valid(self, entry: dict) -> bool:
        return len(self.validate_entry(entry)) == 0


def validate_entries(
    entries: Iterable[dict],
    schema: Schema,
    drop_invalid: bool = False,
) -> Iterator[tuple[dict, list[str]]]:
    """Yield *(entry, errors)* pairs.

    If *drop_invalid* is ``True``, entries with errors are silently skipped
    and only valid entries are yielded (with an empty error list).
    """
    for entry in entries:
        errors = schema.validate_entry(entry)
        if drop_invalid and errors:
            continue
        yield entry, errors
