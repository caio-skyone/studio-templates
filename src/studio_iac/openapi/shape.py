"""Shape key: the index every config map is keyed by.

The shape key is the path with the configured prefix dropped and every
{placeholder} removed, joined by dots — `/v1/customers/{customer}/tax_ids`
becomes `customers.tax_ids`. It identifies a RESOURCE. When an individual
operation must be identified, the method is appended: `customers.tax_ids.post`.
"""

import re
from dataclasses import dataclass
from typing import Any

from studio_iac.openapi.config import ConnectorConfig, DomainConfig
from studio_iac.openapi.refs import resolve_node

PLACEHOLDER_RE = re.compile(r"^\{(.+)\}$")
PLACEHOLDER_IN_SEGMENT_RE = re.compile(r"\{([^{}]+)\}")
_FRAGMENT_UNSAFE_RE = re.compile(r"[^A-Za-z0-9_-]+")
_ITEM_MARKER = "item"

_METHODS = ("get", "post", "put", "patch", "delete")


def path_segments(path: str) -> list[str]:
    return [segment for segment in path.split("/") if segment]


def has_placeholder(segment: str) -> bool:
    """True for `{id}` AND for `{Sid}.json`, `{name}:set-tags`, `v{version}`.

    `PLACEHOLDER_RE` only matches a segment that is ONLY a placeholder. Three
    composite forms are common enough in production to have broken hundreds of
    operations each, and every one of them must be parameterized.
    """
    return PLACEHOLDER_IN_SEGMENT_RE.search(segment) is not None


def placeholders_in(segment: str) -> list[str]:
    return PLACEHOLDER_IN_SEGMENT_RE.findall(segment)


def _key_tokens(segment: str) -> list[str]:
    """Segment -> key tokens, in order: `{Sid}.json` -> ['item', 'json'].

    The key joins on '.', so a literal fragment carrying one would leak into
    the key structure: everything outside [A-Za-z0-9_-] becomes '_'.
    """
    tokens: list[str] = []
    for index, part in enumerate(PLACEHOLDER_IN_SEGMENT_RE.split(segment)):
        if index % 2:
            tokens.append(_ITEM_MARKER)
            continue
        cleaned = _FRAGMENT_UNSAFE_RE.sub("_", part).strip("_")
        if cleaned:
            tokens.append(cleaned)
    return tokens


def _stripped(segments: list[str], strip_prefix: list[str]) -> list[str]:
    index = 0
    while index < len(strip_prefix) and index < len(segments):
        if segments[index] != strip_prefix[index]:
            break
        index += 1
    return segments[index:]


def shape_key(path: str, strip_prefix: list[str]) -> str:
    """The RESOURCE index: prefix dropped, every segment with a placeholder gone.

    A composite segment goes whole, marker and literal alike — that is what
    keeps `/Messages` and `/Messages/{Sid}.json` on the same key, which is
    exactly what `domains` and `exclude` want.
    """
    segments = _stripped(path_segments(path), strip_prefix)
    literal = [segment for segment in segments if not has_placeholder(segment)]
    return ".".join(literal)


def operation_key(path: str, method: str, strip_prefix: list[str]) -> str:
    """Unique per operation — unlike `shape_key`, which collapses on purpose.

    Positional: every placeholder emits an `item` marker WHERE IT APPEARS, and
    the literal fragments of a composite segment stay around it. A trailing
    `.item` marker alone only separated collection from item, so `/a/{x}`,
    `/a/{x}/{y}` and `/a/{x}/{y}/{z}` all produced `a.item.get` — 7 keys for 18
    operations on a real spec, with prose merged into the wrong operation and
    `overrides.body` hitting two operations at once.
    """
    segments = _stripped(path_segments(path), strip_prefix)
    parts: list[str] = []
    for segment in segments:
        if has_placeholder(segment):
            parts.extend(_key_tokens(segment))
        else:
            parts.append(segment)
    parts.append(method.lower())
    return ".".join(parts)


@dataclass(frozen=True, slots=True)
class SpecOperation:
    path: str
    method: str
    summary: str | None
    description: str | None
    parameters: tuple[dict[str, Any], ...]
    request_body: dict[str, Any] | None
    servers: tuple[dict[str, Any], ...]
    shape_key: str
    operation_key: str
    operation_id: str | None = None

    @property
    def root(self) -> str:
        return self.shape_key.split(".", 1)[0]


def _merge_parameters(
    shared: list[dict[str, Any]], own: list[dict[str, Any]]
) -> tuple[dict[str, Any], ...]:
    """Merge path-item and operation-level parameters.

    OpenAPI identifies a parameter by (name, in); an operation-level
    parameter overrides a path-item one sharing that identity rather than
    duplicating it. Parameters missing name/in are malformed and passed
    through untouched — they must not collapse together under a shared
    (None, None) key.
    """
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    extras: list[Any] = []
    for parameter in (*shared, *own):
        if not isinstance(parameter, dict):
            extras.append(parameter)
            continue
        name = parameter.get("name")
        location = parameter.get("in")
        if isinstance(name, str) and isinstance(location, str):
            merged[(name, location)] = parameter
        else:
            extras.append(parameter)
    return (*merged.values(), *extras)


def _resolved_parameters(spec: dict[str, Any], raw: object) -> list[dict[str, Any]]:
    """One `$ref` hop per entry — enough to see `name` and `in`.

    A `{"$ref": "#/components/parameters/X"}` has neither, so the emitter skips
    it in silence: 1692 parameters vanished this way on a real spec.
    """
    if not isinstance(raw, list):
        return []
    resolved: list[dict[str, Any]] = []
    for entry in raw:
        node = resolve_node(spec, entry)
        if isinstance(node, dict):
            resolved.append(node)
    return resolved


def iter_spec_operations(
    spec: dict[str, Any], strip_prefix: list[str]
) -> list[SpecOperation]:
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        return []
    operations: list[SpecOperation] = []
    for path, path_item in sorted(paths.items()):
        if not isinstance(path_item, dict):
            continue
        shared_params = _resolved_parameters(spec, path_item.get("parameters"))
        for method in _METHODS:
            entry = path_item.get(method)
            if not isinstance(entry, dict):
                continue
            own_params = _resolved_parameters(spec, entry.get("parameters"))
            servers = entry.get("servers")
            request_body = resolve_node(spec, entry.get("requestBody"))
            operations.append(
                SpecOperation(
                    path=path,
                    method=method.upper(),
                    summary=entry.get("summary"),
                    description=entry.get("description"),
                    parameters=_merge_parameters(shared_params, own_params),
                    request_body=request_body
                    if isinstance(request_body, dict)
                    else None,
                    servers=tuple(servers) if isinstance(servers, list) else (),
                    shape_key=shape_key(path, strip_prefix),
                    operation_key=operation_key(path, method, strip_prefix),
                    operation_id=entry.get("operationId"),
                )
            )
    return operations


@dataclass(frozen=True, slots=True)
class Selection:
    selected: tuple[SpecOperation, ...]
    excluded: tuple[tuple[SpecOperation, str], ...]


def select_operations(spec: dict[str, Any], config: ConnectorConfig) -> Selection:
    excluded_keys = config.excluded_keys()
    roots = set(config.include_roots)
    selected: list[SpecOperation] = []
    excluded: list[tuple[SpecOperation, str]] = []
    for operation in iter_spec_operations(spec, config.module.strip_path_prefix):
        if operation.root not in roots:
            excluded.append((operation, "root not in include_roots"))
            continue
        reason = excluded_keys.get(operation.shape_key) or excluded_keys.get(
            operation.operation_key
        )
        if reason is not None:
            excluded.append((operation, reason))
            continue
        selected.append(operation)
    return Selection(selected=tuple(selected), excluded=tuple(excluded))


def domain_for(
    operation: SpecOperation, config: ConnectorConfig | None
) -> DomainConfig:
    """Config mapping when present, else the title-cased root segment.

    Accepts None so `analyze_spec` can survey a spec before a config exists.
    """
    if config is not None:
        mapped = config.domains.get(operation.shape_key)
        if mapped is not None:
            return mapped
    label = operation.root.replace("_", " ").title() or "Default"
    return DomainConfig(domain=label, block="default")
