from collections.abc import Sequence
from typing import Protocol

from studio_iac.iac.errors import (
    IACDuplicateOperationName,
    IACDuplicateParameterName,
)


class _Named(Protocol):
    name: str


class _IdentifiedNamed(Protocol):
    id: str
    name: str


def _duplicate_in_sequence(names: list[str]) -> str | None:
    seen: set[str] = set()
    for name in names:
        if name in seen:
            return name
        seen.add(name)
    return None


def ensure_unique_operation_names(operations: list[_Named]) -> None:
    duplicate = _duplicate_in_sequence([operation.name for operation in operations])
    if duplicate is not None:
        raise IACDuplicateOperationName(duplicate)


def ensure_operation_name_available(
    operations: list[_IdentifiedNamed],
    name: str,
    *,
    exclude_operation_id: str | None = None,
) -> None:
    for operation in operations:
        if operation.id == exclude_operation_id:
            continue
        if operation.name == name:
            raise IACDuplicateOperationName(name)


def ensure_operation_names_available_for_batch(
    operations: list[_Named],
    new_names: list[str],
) -> None:
    existing = {operation.name for operation in operations}
    pending: set[str] = set()
    for name in new_names:
        if name in existing or name in pending:
            raise IACDuplicateOperationName(name)
        pending.add(name)


def ensure_unique_parameter_names(parameters: Sequence[_Named]) -> None:
    duplicate = _duplicate_in_sequence([parameter.name for parameter in parameters])
    if duplicate is not None:
        raise IACDuplicateParameterName(duplicate)


def ensure_parameter_name_available(
    parameters: list[_IdentifiedNamed],
    name: str,
    *,
    exclude_parameter_id: str | None = None,
) -> None:
    for parameter in parameters:
        if parameter.id == exclude_parameter_id:
            continue
        if parameter.name == name:
            raise IACDuplicateParameterName(name)


def ensure_parameter_names_available_for_batch(
    parameters: list[_Named],
    new_names: list[str],
) -> None:
    existing = {parameter.name for parameter in parameters}
    pending: set[str] = set()
    for name in new_names:
        if name in existing or name in pending:
            raise IACDuplicateParameterName(name)
        pending.add(name)
