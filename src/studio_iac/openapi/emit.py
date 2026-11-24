"""Assemble an IACModule (structure only) plus the prose worklist and a report.

Descriptions are left empty here on purpose: structure is deterministic and
belongs to code; prose is the one thing that needs a language model. The two
meet in `apply_worklist`.
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from studio_iac.iac.models import (
    IACModule,
    IACModuleSettings,
    IACOperation,
    IACParameter,
    IACQueryParam,
    IACRequestBody,
    IACRequestHeader,
    IACRequestUrl,
    IACRestRequest,
)
from studio_iac.iac.rules import (
    OPERATION_NAME_MAX,
    validate_module,
)
from studio_iac.iac.secrets import AUTH_HEADER_HINTS
from studio_iac.openapi.body import (
    BODY_PARAM_NAME,
    BodyParamSpec,
    plan_body,
)
from studio_iac.openapi.config import ConnectorConfig
from studio_iac.openapi.errors import (
    OperationKeyCollision,
    OperationNameCollision,
)
from studio_iac.openapi.naming import (
    iac_path_segments,
    operation_action,
    snake_case,
)
from studio_iac.openapi.refs import deref
from studio_iac.openapi.samples import parameter_sample
from studio_iac.openapi.shape import (
    SpecOperation,
    domain_for,
    select_operations,
)
from studio_iac.openapi.worklist import (
    ProseOperationEntry,
    ProseParameterEntry,
    ProseWorklist,
)
from studio_iac.text import plain_text

_DEEP_OBJECT_NOTE = (
    "object/deepObject query parameter — the description MUST tell the user to "
    "edit the query KEY in the operation (e.g. created[gte]), not just the value"
)
_EXPAND_SUFFIX = "[]"
_BODY_REF_RE = re.compile(r"<>([^<>/]+)</>")
_CONTENT_TYPE_HEADER = "content-type"
_EMITTED_CONTENT_TYPES = frozenset(
    {"application/x-www-form-urlencoded", "application/json"}
)


class GenerationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    included: int
    excluded: list[dict[str, str]] = Field(default_factory=list)
    path_params: list[dict[str, str]] = Field(default_factory=list)
    body_decisions: list[dict[str, str]] = Field(default_factory=list)
    truncated_names: list[dict[str, str]] = Field(default_factory=list)
    skipped_headers: list[dict[str, str]] = Field(default_factory=list)
    empty_samples: int = 0
    renamed_params: list[dict[str, str]] = Field(default_factory=list)
    name_fallbacks: list[dict[str, str]] = Field(default_factory=list)
    blocks: dict[str, int] = Field(default_factory=dict)
    server_prefix: list[str] = Field(default_factory=list)
    errors: list[dict[str, str]] = Field(default_factory=list)
    warnings: list[dict[str, str]] = Field(default_factory=list)


@dataclass(frozen=True, slots=True)
class GenerationResult:
    module: IACModule
    worklist: ProseWorklist
    report: GenerationReport
    operation_keys: dict[str, str]  # operation name -> operation_key


@dataclass(slots=True)
class _ParamAccumulator:
    """Collects distinct parameter names across every operation."""

    kinds: dict[str, str]
    occurrences: dict[str, int]
    domains: dict[str, list[str]]
    sources: dict[str, str | None]
    notes: dict[str, str | None]

    @classmethod
    def empty(cls) -> "_ParamAccumulator":
        return cls(kinds={}, occurrences={}, domains={}, sources={}, notes={})

    def record(
        self,
        name: str,
        *,
        kind: str,
        domain: str,
        source_en: str | None,
        note: str | None,
    ) -> None:
        self.kinds.setdefault(name, kind)
        self.occurrences[name] = self.occurrences.get(name, 0) + 1
        domains = self.domains.setdefault(name, [])
        if domain not in domains:
            domains.append(domain)
        if self.sources.get(name) is None:
            self.sources[name] = source_en
        if note is not None:
            self.notes[name] = note

    def to_entries(self) -> list[ProseParameterEntry]:
        entries: list[ProseParameterEntry] = []
        for name in sorted(self.occurrences):
            domains = self.domains[name]
            note = self.notes.get(name)
            if len(domains) > 1:
                shared = (
                    f"shared by {len(domains)} domains — the description must "
                    "serve all of them, never just one"
                )
                note = f"{note}; {shared}" if note else shared
            entries.append(
                ProseParameterEntry(
                    name=name,
                    kind=self.kinds[name],  # type: ignore[arg-type]
                    occurrences=self.occurrences[name],
                    domains=domains,
                    source_en=self.sources.get(name),
                    note=note,
                )
            )
        return entries


def _truncate(name: str) -> tuple[str, bool]:
    if len(name) <= OPERATION_NAME_MAX:
        return name, False
    return name[: OPERATION_NAME_MAX - 1].rstrip() + "…", True


def _query_key(spec_name: str, schema_type: str | None) -> str:
    if spec_name == "expand" or schema_type == "array":
        return f"{spec_name}{_EXPAND_SUFFIX}"
    return spec_name


def _param_type(schema: dict[str, Any]) -> str:
    mapping = {
        "integer": "number",
        "number": "number",
        "array": "array",
        "object": "object",
        "boolean": "string",
        "string": "string",
    }
    return mapping.get(str(schema.get("type", "string")), "string")


def _full_url_prefix(operation: SpecOperation) -> str | None:
    for server in operation.servers:
        url = server.get("url")
        if isinstance(url, str) and url:
            return url.rstrip("/")
    return None


@dataclass(slots=True)
class _NameAllocator:
    """Unique parameter names inside ONE operation.

    OpenAPI identifies a parameter by (name, in), so `ip` in the path and `ip`
    in the query is legal — and the IAC has only `name`. The later one takes a
    suffix from its own `in`; the wire `key` keeps the spec's name, which is
    exactly what `key` and `name` being separate fields is for.
    """

    operation_key: str
    renames: list[dict[str, str]]
    taken: set[str] = field(default_factory=set)

    def allocate(self, name: str, *, kind: str) -> str:
        if name not in self.taken:
            self.taken.add(name)
            return name
        candidate = f"{name}_{kind}"
        suffix = 2
        while candidate in self.taken:
            candidate = f"{name}_{kind}_{suffix}"
            suffix += 1
        self.taken.add(candidate)
        self.renames.append(
            {
                "operation_key": self.operation_key,
                "from": name,
                "to": candidate,
                "kind": kind,
            }
        )
        return candidate


def root_server_segments(spec: dict[str, Any]) -> list[str]:
    """Path segments of the document-level `servers` URL, if it carries a path.

    `https://www.zohoapis.com/workdrive` means every endpoint lives under
    `/workdrive`; emitting `["api","v1",…]` calls the wrong URL with the right
    Host, in silence. Only the PATH is taken — host and scheme stay with the
    connected account, which is where "Host is account configuration" lives.
    A templated path (`/{basePath}`) is a config decision, not ours.
    """
    servers = spec.get("servers")
    if not isinstance(servers, list):
        return []
    for server in servers:
        if not isinstance(server, dict):
            continue
        url = server.get("url")
        if not isinstance(url, str) or not url:
            continue
        path = url.split("://", 1)[-1]
        path = path.partition("/")[2]
        if "{" in path or "}" in path:
            return []
        return [segment for segment in path.split("/") if segment]
    return []


def _build_operation(
    spec: dict[str, Any],
    operation: SpecOperation,
    config: ConnectorConfig,
    root_segments: list[str],
    accumulator: _ParamAccumulator,
    report_paths: list[dict[str, str]],
    report_bodies: list[dict[str, str]],
    skipped_headers: list[dict[str, str]],
    renames: list[dict[str, str]],
    name_fallbacks: list[dict[str, str]],
) -> tuple[IACOperation, str]:
    domain = domain_for(operation, config)
    allocator = _NameAllocator(operation_key=operation.operation_key, renames=renames)
    segments, path_params = iac_path_segments(
        operation,
        naming=config.naming,
        path_param_overrides=config.overrides.path_params,
        strip_prefix=config.module.strip_path_prefix,
        allocate=lambda name: allocator.allocate(name, kind="path"),
    )
    url_type = "base-url"
    prefix = _full_url_prefix(operation)
    if prefix is not None:
        url_type = "full-url"
        segments = [prefix, *segments]
    elif root_segments:
        segments = [*root_segments, *segments]

    parameters: list[IACParameter] = []
    path_raw = {
        str(raw.get("name")): raw
        for raw in operation.parameters
        if raw.get("in") == "path" and isinstance(raw.get("name"), str)
    }

    # O nome já vem alocado de `iac_path_segments`: é o mesmo texto que está
    # no segmento renderizado.
    for placeholder, name in path_params:
        raw_path = path_raw.get(placeholder) or {}
        sample = parameter_sample(raw_path, deref(spec, raw_path.get("schema") or {}))
        report_paths.append(
            {
                "operation_key": operation.operation_key,
                "placeholder": placeholder,
                "parameter": name,
            }
        )
        accumulator.record(
            name, kind="path", domain=domain.domain, source_en=None, note=None
        )
        parameters.append(
            IACParameter(
                id=str(uuid4()),
                name=name,
                type="string",
                description=None,
                required=True,
                sensitive=False,
                sample=sample,
            )
        )

    query: list[IACQueryParam] = []
    for raw in operation.parameters:
        if raw.get("in") != "query":
            continue
        spec_name = str(raw.get("name", ""))
        if not spec_name:
            continue
        schema = raw.get("schema") if isinstance(raw.get("schema"), dict) else {}
        name = allocator.allocate(snake_case(spec_name), kind="query")
        note = (
            _DEEP_OBJECT_NOTE
            if raw.get("style") == "deepObject" or schema.get("type") == "object"
            else None
        )
        query.append(
            IACQueryParam(
                key=_query_key(spec_name, schema.get("type")), value=f"<>{name}</>"
            )
        )
        accumulator.record(
            name,
            kind="query",
            domain=domain.domain,
            source_en=plain_text(raw.get("description")) or None,
            note=note,
        )
        parameters.append(
            IACParameter(
                id=str(uuid4()),
                name=name,
                type=_param_type(schema),
                description=None,
                required=bool(raw.get("required")),
                sensitive=False,
                sample=parameter_sample(raw, deref(spec, schema)),
            )
        )

    headers: list[IACRequestHeader] = []

    # Headers do SPEC: só os obrigatórios, e nunca os de autenticação.
    # Um header de valor vazio é enviado com a chave presente e valor vazio
    # (ao contrário de query param, que o Studio descarta), então um opcional
    # não preenchido chega à API como "X-Foo: " e há APIs que rejeitam isso.
    auth_hints = (AUTH_HEADER_HINTS | set(config.overrides.auth_headers.add)) - set(
        config.overrides.auth_headers.remove
    )
    for raw in operation.parameters:
        if raw.get("in") != "header":
            continue
        spec_name = str(raw.get("name", ""))
        if not spec_name:
            continue
        if spec_name.lower() == _CONTENT_TYPE_HEADER:
            # The body plan owns the Content-Type. A hand-declared one is at
            # best redundant and at worst fatal: on a multipart body it
            # replaces the 'multipart/form-data; boundary=...' the platform
            # builds and the request breaks.
            skipped_headers.append(
                {
                    "operation_key": operation.operation_key,
                    "header": spec_name,
                    "reason": (
                        "Content-Type comes from the body plan, never from the spec"
                    ),
                }
            )
            continue
        if spec_name.lower() in auth_hints:
            skipped_headers.append(
                {
                    "operation_key": operation.operation_key,
                    "header": spec_name,
                    "reason": "auth header — controlled by the connected account",
                }
            )
            continue
        if not raw.get("required"):
            skipped_headers.append(
                {
                    "operation_key": operation.operation_key,
                    "header": spec_name,
                    "reason": "optional — add it explicitly if the API needs it",
                }
            )
            continue
        name = allocator.allocate(snake_case(spec_name), kind="header")
        schema = raw.get("schema") if isinstance(raw.get("schema"), dict) else {}
        headers.append(
            IACRequestHeader(key=spec_name, value=f"<>{name}</>", enabled=True)
        )
        accumulator.record(
            name,
            kind="header",
            domain=domain.domain,
            source_en=plain_text(raw.get("description")) or None,
            note=None,
        )
        parameters.append(
            IACParameter(
                id=str(uuid4()),
                name=name,
                type=_param_type(schema),
                description=None,
                required=True,
                sensitive=False,
                sample=parameter_sample(raw, deref(spec, schema)),
            )
        )

    # Headers do CONFIG: sempre entram — declarar no config É a instrução
    # explícita do usuário, então a regra de "só obrigatórios" não se aplica.
    for header in config.headers:
        if header.methods is not None and operation.method not in header.methods:
            continue
        name = allocator.allocate(header.param, kind="header")
        headers.append(
            IACRequestHeader(key=header.key, value=f"<>{name}</>", enabled=True)
        )
        accumulator.record(
            name,
            kind="header",
            domain=domain.domain,
            source_en=None,
            note=None,
        )
        parameters.append(
            IACParameter(
                id=str(uuid4()),
                name=name,
                type="string",
                description=None,
                required=header.required,
                sensitive=False,
                sample=header.sample,
            )
        )

    body_plan = plan_body(
        spec, operation, config.overrides.body.get(operation.operation_key)
    )
    report_bodies.append(
        {
            "operation_key": operation.operation_key,
            "content_type": body_plan.content_type or "none",
            "strategy": body_plan.strategy,
            "reason": body_plan.reason or "",
        }
    )
    if body_plan.content_type in _EMITTED_CONTENT_TYPES:
        headers.append(
            IACRequestHeader(
                key="Content-Type", value=body_plan.content_type, enabled=True
            )
        )

    body_raw = body_plan.raw
    allocated: list[tuple[str, BodyParamSpec]] = []
    renamed: dict[str, str] = {}
    for body_param in body_plan.parameters:
        name = allocator.allocate(body_param.name, kind="body")
        if name != body_param.name:
            renamed[body_param.name] = name
        allocated.append((name, body_param))
    if renamed:
        # Uma passada só: reescrever incrementalmente com str.replace faz o
        # segundo rename clobberar a referência que o primeiro acabou de
        # escrever, e o parâmetro anterior fica sem referência nenhuma.
        body_raw = _BODY_REF_RE.sub(
            lambda match: f"<>{renamed.get(match.group(1), match.group(1))}</>",
            body_raw,
        )
    for name, body_param in allocated:
        accumulator.record(
            name,
            kind="body",
            domain=domain.domain,
            source_en=body_param.source_en,
            note=None,
        )
        parameters.append(
            IACParameter(
                id=str(uuid4()),
                name=name,
                type=body_param.type,  # type: ignore[arg-type]
                description=None,
                required=body_param.required,
                sensitive=False,
                sample=body_param.sample,
            )
        )

    action, fallback_level = operation_action(operation)
    operation_name = f"{domain.domain} - {action}"
    if fallback_level is not None:
        name_fallbacks.append(
            {"operation_key": operation.operation_key, "level": fallback_level}
        )
    request = IACRestRequest(
        method=operation.method,  # type: ignore[arg-type]
        url_type=url_type,  # type: ignore[arg-type]
        url=IACRequestUrl(path=segments),
        query=query,
        header=headers,
        body=IACRequestBody(mode="raw", raw=body_raw),
    )
    return (
        IACOperation(
            id=str(uuid4()),
            name=operation_name,
            description=None,
            parameters=parameters,
            request=request,
        ),
        domain.block,
    )


def build_module(
    spec: dict[str, Any],
    config: ConnectorConfig,
    *,
    module_id: str,
) -> GenerationResult:
    selection = select_operations(spec, config)
    accumulator = _ParamAccumulator.empty()
    report_paths: list[dict[str, str]] = []
    report_bodies: list[dict[str, str]] = []
    truncated: list[dict[str, str]] = []
    skipped_headers: list[dict[str, str]] = []
    blocks: dict[str, int] = {}
    renames: list[dict[str, str]] = []
    name_fallbacks: list[dict[str, str]] = []
    build_errors: list[dict[str, str]] = []
    root_segments = root_server_segments(spec)

    operations: list[IACOperation] = []
    operation_keys: dict[str, str] = {}
    worklist_ops: list[ProseOperationEntry] = []
    collisions: list[tuple[str, str, str]] = []

    for spec_operation in selection.selected:
        try:
            built, block = _build_operation(
                spec,
                spec_operation,
                config,
                root_segments,
                accumulator,
                report_paths,
                report_bodies,
                skipped_headers,
                renames,
                name_fallbacks,
            )
        except Exception as error:  # noqa: BLE001 - the report is the point
            build_errors.append(
                {
                    "path": spec_operation.operation_key,
                    "message": f"{type(error).__name__}: {error}",
                }
            )
            continue
        name, was_truncated = _truncate(built.name)
        if was_truncated:
            truncated.append(
                {"operation_key": spec_operation.operation_key, "name": built.name}
            )
            built = built.model_copy(update={"name": name})
        if name in operation_keys:
            collisions.append(
                (name, operation_keys[name], spec_operation.operation_key)
            )
            continue
        operation_keys[name] = spec_operation.operation_key
        blocks[block] = blocks.get(block, 0) + 1
        operations.append(built)
        worklist_ops.append(
            ProseOperationEntry(
                op_key=spec_operation.operation_key,
                name=name,
                source_en=plain_text(
                    spec_operation.description or spec_operation.summary
                )
                or None,
                body_sample=next(
                    (
                        parameter.sample
                        for parameter in built.parameters
                        if parameter.name == BODY_PARAM_NAME
                    ),
                    "",
                ),
            )
        )

    module = IACModule(
        id=module_id,
        name=config.module.name,
        description=config.module.description,
        type="rest",
        settings=IACModuleSettings(
            authentication_type=config.module.authentication_type
        ),
        operations=operations,
    )
    validation = validate_module(module)
    empty_samples = sum(
        1
        for built_operation in operations
        for parameter in built_operation.parameters
        if parameter.sample == ""
    )
    report = GenerationReport(
        included=len(operations),
        excluded=[
            {
                "key": operation.shape_key,
                "operation_key": operation.operation_key,
                "reason": reason,
            }
            for operation, reason in selection.excluded
        ],
        path_params=report_paths,
        body_decisions=report_bodies,
        truncated_names=truncated,
        skipped_headers=skipped_headers,
        empty_samples=empty_samples,
        renamed_params=renames,
        name_fallbacks=name_fallbacks,
        blocks=blocks,
        server_prefix=root_segments,
        errors=build_errors
        + [
            {"path": error.path, "message": error.message}
            for error in validation.errors
        ],
        warnings=[
            {"path": warning.path, "message": warning.message}
            for warning in validation.warnings
        ],
    )
    if collisions:
        raise OperationNameCollision(collisions, report=report.model_dump())
    duplicates = [
        key for key, count in Counter(operation_keys.values()).items() if count > 1
    ]
    if duplicates:
        raise OperationKeyCollision(duplicates, report=report.model_dump())
    return GenerationResult(
        module=module,
        worklist=ProseWorklist(
            parameters=accumulator.to_entries(), operations=worklist_ops
        ),
        report=report,
        operation_keys=operation_keys,
    )


def apply_worklist(
    module: IACModule,
    worklist: ProseWorklist,
    *,
    operation_keys: dict[str, str],
) -> IACModule:
    """Merge prose into structure. Parameter prose is by NAME, operation by key."""
    by_name = worklist.parameter_descriptions()
    by_key = worklist.operation_prose()
    operations: list[IACOperation] = []
    for operation in module.operations:
        entry = by_key.get(operation_keys.get(operation.name, ""))
        parameters = [
            parameter.model_copy(
                update={
                    "description": by_name.get(parameter.name) or parameter.description,
                    "sample": (
                        entry.body_sample
                        if entry is not None
                        and entry.body_sample.strip()
                        and parameter.name == BODY_PARAM_NAME
                        else parameter.sample
                    ),
                }
            )
            for parameter in operation.parameters
        ]
        operations.append(
            operation.model_copy(
                update={
                    "description": (
                        entry.description
                        if entry is not None and entry.description.strip()
                        else operation.description
                    ),
                    "parameters": parameters,
                }
            )
        )
    return module.model_copy(update={"operations": operations})
