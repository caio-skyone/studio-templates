from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from studio_iac.iac.models import IACValidationResult


class IACDraftNotFound(Exception):
    def __init__(self, draft_id: str) -> None:
        self.draft_id = draft_id
        super().__init__(f"IAC draft {draft_id!r} not found")


class IACOperationNotFound(Exception):
    def __init__(self, operation_id: str) -> None:
        self.operation_id = operation_id
        super().__init__(f"operation {operation_id!r} not found in draft")


class IACParameterNotFound(Exception):
    def __init__(self, parameter_id: str) -> None:
        self.parameter_id = parameter_id
        super().__init__(f"parameter {parameter_id!r} not found in operation")


class IACDuplicateOperationName(Exception):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"operation name {name!r} already exists in this module")


class IACDuplicateParameterName(Exception):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"parameter name {name!r} already exists in this operation")


class IACFileInvalid(Exception):
    def __init__(self, path: object, detail: str) -> None:
        self.path = path
        self.detail = detail
        super().__init__(f"invalid IAC file {path}: {detail}")


class IACValidationFailed(Exception):
    def __init__(self, validation: "IACValidationResult") -> None:
        self.validation = validation
        super().__init__(_format_validation_failure(validation))


def _format_validation_failure(validation: "IACValidationResult") -> str:
    if not validation.errors:
        return "IAC validation failed before import"
    lines = ["IAC validation failed:"]
    for error in validation.errors:
        lines.append(f"  {error.path}: {error.message}")
    return "\n".join(lines)


class ConnectorNotPulled(Exception):
    def __init__(self, draft_id: str) -> None:
        self.draft_id = draft_id
        super().__init__(
            f"draft {draft_id!r} did not come from Studio — patch_connector only "
            "updates a connector pulled with pull_connector. To create a new "
            "connector from this draft, use push_connector."
        )


class RemoteDriftDetected(Exception):
    def __init__(self, module_id: str, operations: list[str]) -> None:
        self.module_id = module_id
        self.operations = operations
        listed = ", ".join(operations[:10])
        more = "" if len(operations) <= 10 else f" (+{len(operations) - 10} more)"
        super().__init__(
            f"connector {module_id!r} changed in Studio after the pull: "
            f"{listed}{more}. Run pull_connector again, or pass "
            "allow_remote_drift=True to overwrite those changes."
        )
