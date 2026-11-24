"""Measure a spec before deciding anything about it.

Two outputs earn their keep. The domain table lets a user pick scope from real
numbers instead of an abstract question — on a 416-path API, measuring first
changed the decision twice. The depth table turns "do not expand nested bodies"
from an opinion into a fact: at depth 3 the 50-char parameter name limit starts
producing violations by the hundred.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from studio_iac.iac.rules import PARAMETER_NAME_MAX
from studio_iac.openapi.config import ConnectorConfig, NamingConfig
from studio_iac.openapi.naming import (
    iac_path_segments,
    operation_action,
)
from studio_iac.openapi.refs import deref
from studio_iac.openapi.refs import ref_cycles as find_ref_cycles
from studio_iac.openapi.shape import (
    SpecOperation,
    domain_for,
    iter_spec_operations,
    select_operations,
)

_RECURSIVE_DEPTH = 8
_LEVELS: tuple[tuple[str, int], ...] = (
    ("1", 1),
    ("2", 2),
    ("3", 3),
    ("recursive", _RECURSIVE_DEPTH),
)


class DomainRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: str
    block: str
    operations: int
    query_params: int
    body_params: int


class DepthRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: str
    body_params: int
    names_over_limit: int
    worst_name: str | None = None


class PathParamRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation_key: str
    placeholder: str
    derived_name: str


class AnalysisReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_paths: int
    total_operations: int
    selected_operations: int
    content_types: dict[str, int] = Field(default_factory=dict)
    domains: list[DomainRow] = Field(default_factory=list)
    depth: list[DepthRow] = Field(default_factory=list)
    collisions: list[dict[str, str]] = Field(default_factory=list)
    path_params: list[PathParamRow] = Field(default_factory=list)
    ref_cycles: list[str] = Field(default_factory=list)


def _body_schema(spec: dict[str, Any], operation: SpecOperation) -> dict[str, Any]:
    if operation.request_body is None or operation.method in {"GET", "DELETE"}:
        return {}
    content = operation.request_body.get("content")
    if not isinstance(content, dict):
        return {}
    for entry in content.values():
        if isinstance(entry, dict) and entry.get("schema") is not None:
            resolved = deref(spec, entry["schema"], max_depth=_RECURSIVE_DEPTH + 2)
            return resolved if isinstance(resolved, dict) else {}
    return {}


def _content_type(operation: SpecOperation) -> str | None:
    if operation.request_body is None or operation.method in {"GET", "DELETE"}:
        return None
    content = operation.request_body.get("content")
    if not isinstance(content, dict) or not content:
        return None
    return next(iter(content))


def _leaf_names(schema: dict[str, Any], limit: int, prefix: str = "") -> list[str]:
    """Bracket-joined leaf names down to `limit` levels of nesting."""
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        return []
    names: list[str] = []
    for key, child in properties.items():
        name = key if not prefix else f"{prefix}[{key}]"
        child_props = child.get("properties") if isinstance(child, dict) else None
        if limit > 1 and isinstance(child_props, dict) and child_props:
            names.extend(_leaf_names(child, limit - 1, name))
        else:
            names.append(name)
    return names


def _depth_rows(
    spec: dict[str, Any], operations: list[SpecOperation]
) -> list[DepthRow]:
    schemas = [_body_schema(spec, operation) for operation in operations]
    rows: list[DepthRow] = []
    for label, limit in _LEVELS:
        names: list[str] = []
        for schema in schemas:
            names.extend(_leaf_names(schema, limit))
        over = [name for name in names if len(name) > PARAMETER_NAME_MAX]
        rows.append(
            DepthRow(
                level=label,
                body_params=len(names),
                names_over_limit=len(over),
                worst_name=max(over, key=len) if over else None,
            )
        )
    return rows


def _fallback_config(config: ConnectorConfig | None) -> NamingConfig:
    return config.naming if config is not None else NamingConfig()


def analyze_spec(
    spec: dict[str, Any], config: ConnectorConfig | None
) -> AnalysisReport:
    paths = spec.get("paths")
    total_paths = len(paths) if isinstance(paths, dict) else 0
    strip_prefix = config.module.strip_path_prefix if config is not None else []
    every = iter_spec_operations(spec, strip_prefix)

    if config is None:
        selected = list(every)
    else:
        selected = list(select_operations(spec, config).selected)

    content_types: dict[str, int] = {}
    for operation in selected:
        name = _content_type(operation)
        if name is not None:
            content_types[name] = content_types.get(name, 0) + 1

    domain_rows: dict[str, DomainRow] = {}
    collisions: list[dict[str, str]] = []
    seen_names: dict[str, str] = {}
    path_params: list[PathParamRow] = []
    naming = _fallback_config(config)
    overrides = config.overrides.path_params if config is not None else {}

    for operation in selected:
        label = domain_for(operation, config)
        row = domain_rows.get(label.domain)
        query_count = sum(1 for raw in operation.parameters if raw.get("in") == "query")
        body_count = len(_leaf_names(_body_schema(spec, operation), 1))
        if row is None:
            domain_rows[label.domain] = DomainRow(
                domain=label.domain,
                block=label.block,
                operations=1,
                query_params=query_count,
                body_params=body_count,
            )
        else:
            domain_rows[label.domain] = row.model_copy(
                update={
                    "operations": row.operations + 1,
                    "query_params": row.query_params + query_count,
                    "body_params": row.body_params + body_count,
                }
            )
        action, _ = operation_action(operation)
        name = f"{label.domain} - {action}"
        if name in seen_names:
            collisions.append(
                {
                    "name": name,
                    "first": seen_names[name],
                    "second": operation.operation_key,
                }
            )
        else:
            seen_names[name] = operation.operation_key
        _, derived = iac_path_segments(
            operation,
            naming=naming,
            path_param_overrides=overrides,
            strip_prefix=strip_prefix,
        )
        for placeholder, parameter in derived:
            path_params.append(
                PathParamRow(
                    operation_key=operation.operation_key,
                    placeholder=placeholder,
                    derived_name=parameter,
                )
            )

    return AnalysisReport(
        total_paths=total_paths,
        total_operations=len(every),
        selected_operations=len(selected),
        content_types=content_types,
        domains=sorted(domain_rows.values(), key=lambda row: row.domain),
        depth=_depth_rows(spec, selected),
        collisions=collisions,
        path_params=path_params,
        ref_cycles=find_ref_cycles(spec),
    )
