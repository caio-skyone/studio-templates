"""Errors raised while turning an OpenAPI spec into an IAC module.

Every one carries structured detail, never just a message: the agent has to be
able to act on it without guessing which config key to touch.
"""


class OpenApiSpecInvalid(Exception):
    def __init__(self, path: object, detail: str) -> None:
        self.path = path
        self.detail = detail
        super().__init__(f"invalid OpenAPI spec {path}: {detail}")


class ConnectorConfigInvalid(Exception):
    def __init__(self, path: object, detail: str) -> None:
        self.path = path
        self.detail = detail
        super().__init__(f"invalid connector config {path}: {detail}")


class OperationNameCollision(Exception):
    """Two paths producing the same '{Domain} - {Summary}'.

    Almost always aliases of the same resource. The fix is an `exclude` entry.
    """

    def __init__(
        self,
        collisions: list[tuple[str, str, str]],
        report: dict[str, object] | None = None,
    ) -> None:
        self.collisions = collisions
        self.report = report
        rendered = "; ".join(
            f"{name!r} produced by both {first!r} and {second!r}"
            for name, first, second in collisions
        )
        super().__init__(
            f"{len(collisions)} operation name collision(s) — these are almost "
            f"always resource aliases; add the redundant shape key to `exclude`: "
            f"{rendered}"
        )


class OperationKeyCollision(Exception):
    """Two operations sharing one `operation_key`.

    The key is the address of an operation in `overrides.body` and in the prose
    worklist. A duplicate means prose merged into the wrong operation and an
    override hitting two — silently. This is a generator bug, not a config
    mistake: report it.
    """

    def __init__(
        self,
        duplicates: list[str],
        report: dict[str, object] | None = None,
    ) -> None:
        self.duplicates = duplicates
        self.report = report
        super().__init__(
            f"{len(duplicates)} operation key(s) are not unique: "
            + ", ".join(sorted(duplicates)[:20])
        )


class GenerationAborted(Exception):
    def __init__(self, report: dict[str, object]) -> None:
        self.report = report
        errors = report.get("errors", [])
        count = len(errors) if isinstance(errors, list) else 0
        super().__init__(
            f"generation aborted: {count} validation error(s); see the report"
        )


class ProseWorklistMismatch(Exception):
    def __init__(self, missing: list[str], unknown: list[str]) -> None:
        self.missing = missing
        self.unknown = unknown
        parts = []
        if missing:
            parts.append(f"absent from the worklist: {', '.join(sorted(missing)[:20])}")
        if unknown:
            parts.append(f"not present in the IAC: {', '.join(sorted(unknown)[:20])}")
        super().__init__("prose worklist does not match the IAC — " + "; ".join(parts))
