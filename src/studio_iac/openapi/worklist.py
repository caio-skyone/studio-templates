"""The prose worklist: the one artifact an LLM is supposed to fill in.

Parameters are keyed by NAME, not by occurrence. On a real build that collapsed
1,553 parameter occurrences into 91 distinct names — the whole reason the prose
stage is affordable.

`domains` on each parameter entry is not decoration: a name that appears in 12
domains needs a description that serves all 12. Writing "filters meters by
status" for a `status` that also filters invoices is wrong in 11 of them.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from studio_iac.openapi.errors import ProseWorklistMismatch

ParameterKind = Literal["path", "query", "header", "body"]


class ProseParameterEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    kind: ParameterKind
    occurrences: int
    domains: list[str] = Field(default_factory=list)
    source_en: str | None = None
    note: str | None = None
    description: str = ""


class ProseOperationEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    op_key: str
    name: str
    source_en: str | None = None
    description: str = ""
    body_sample: str = ""


class ProseWorklist(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parameters: list[ProseParameterEntry] = Field(default_factory=list)
    operations: list[ProseOperationEntry] = Field(default_factory=list)

    def parameter_descriptions(self) -> dict[str, str]:
        return {
            entry.name: entry.description
            for entry in self.parameters
            if entry.description.strip()
        }

    def operation_prose(self) -> dict[str, ProseOperationEntry]:
        return {entry.op_key: entry for entry in self.operations}


def load_worklist(payload: object, source: object) -> ProseWorklist:
    if not isinstance(payload, dict):
        raise ProseWorklistMismatch(
            missing=[],
            unknown=[f"{source}: expected a JSON object, got {type(payload).__name__}"],
        )
    try:
        worklist = ProseWorklist.model_validate(payload)
    except ValidationError as error:
        details = [
            f"{'.'.join(str(part) for part in detail['loc'])}: {detail['msg']}"
            for detail in error.errors()[:10]
        ]
        raise ProseWorklistMismatch(missing=[], unknown=details) from error
    _reject_duplicates(worklist)
    return worklist


def _reject_duplicates(worklist: ProseWorklist) -> None:
    duplicates: list[str] = []
    seen: set[str] = set()
    for entry in worklist.parameters:
        if entry.name in seen:
            duplicates.append(entry.name)
        seen.add(entry.name)
    seen.clear()
    for operation in worklist.operations:
        if operation.op_key in seen:
            duplicates.append(operation.op_key)
        seen.add(operation.op_key)
    if duplicates:
        raise ProseWorklistMismatch(missing=[], unknown=duplicates)


def check_coverage(
    worklist: ProseWorklist,
    *,
    parameter_names: set[str],
    operation_keys: set[str],
) -> None:
    """Every IAC name must be in the worklist, and vice versa. No silent gaps."""
    listed_params = {entry.name for entry in worklist.parameters}
    listed_ops = {entry.op_key for entry in worklist.operations}
    missing = sorted((parameter_names - listed_params) | (operation_keys - listed_ops))
    unknown = sorted((listed_params - parameter_names) | (listed_ops - operation_keys))
    if missing or unknown:
        raise ProseWorklistMismatch(missing=missing, unknown=unknown)
