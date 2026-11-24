"""Request body modeling, decided by content type. Never by inference.

The decision table is closed on purpose:

  GET/DELETE or no requestBody  -> no body
  x-www-form-urlencoded         -> ONE `string` parameter for the whole body
  application/json              -> ONE `object` parameter for the whole body
  multipart/form-data           -> granular lines, REQUIRED properties only

Expanding nested body properties is forbidden. Measured on a real spec: depth 2
yields 2,734 body parameters and 3 names over 50 chars; recursive yields 435
violations. The 50-char parameter name limit is a wall, not a preference.

A parameterized skeleton exists only via an explicit `overrides.body` entry.
"""

import re
from dataclasses import dataclass
from typing import Any

from studio_iac.openapi.config import BodyOverride
from studio_iac.openapi.naming import snake_case
from studio_iac.openapi.refs import deref
from studio_iac.openapi.samples import body_sample_for, sample_for
from studio_iac.openapi.shape import SpecOperation
from studio_iac.text import plain_text

BODY_PARAM_NAME = "body"
_METHODS_WITHOUT_BODY = frozenset({"GET", "DELETE"})
_REF_RE = re.compile(r"<>([a-z][a-z0-9_]*)</>")

_URLENCODED = "application/x-www-form-urlencoded"
_JSON = "application/json"
_MULTIPART = "multipart/form-data"


@dataclass(frozen=True, slots=True)
class BodyParamSpec:
    name: str
    type: str
    required: bool
    sample: str
    source_en: str | None = None


@dataclass(frozen=True, slots=True)
class BodyPlan:
    raw: str
    parameters: tuple[BodyParamSpec, ...]
    content_type: str | None
    strategy: str
    reason: str | None = None


_EMPTY = BodyPlan(raw="", parameters=(), content_type=None, strategy="none")


def _none_plan(reason: str) -> BodyPlan:
    """`none` WITH a requestBody present — the report must say why.

    Plain `strategy: none` cannot tell "this endpoint has no body" apart from
    "the generator could not read the body", and the second one silently ships
    a write operation that sends nothing.
    """
    return BodyPlan(
        raw="", parameters=(), content_type=None, strategy="none", reason=reason
    )


def _normalize_media_type(name: str) -> str:
    """`application/json; charset=utf-8` -> `application/json`."""
    return name.split(";", 1)[0].strip().lower()


def _pick_content(request_body: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    content = request_body.get("content")
    if not isinstance(content, dict):
        return None
    normalized: dict[str, dict[str, Any]] = {}
    for name, entry in content.items():
        if isinstance(entry, dict):
            normalized.setdefault(_normalize_media_type(name), entry)
    for candidate in (_MULTIPART, _URLENCODED, _JSON):
        entry = normalized.get(candidate)
        if entry is not None:
            return candidate, entry
    for name, entry in normalized.items():
        return name, entry
    return None


def _properties_of(schema: dict[str, Any]) -> tuple[dict[str, Any], set[str]]:
    """Properties and required names, with `allOf` parts merged in first.

    Outer wins: a part is a base, the schema's own properties are the override.
    """
    properties: dict[str, Any] = {}
    required: set[str] = set()
    parts = schema.get("allOf")
    if isinstance(parts, list):
        for part in parts:
            if isinstance(part, dict):
                part_properties, part_required = _properties_of(part)
                properties.update(part_properties)
                required.update(part_required)
    own = schema.get("properties")
    if isinstance(own, dict):
        properties.update(own)
    own_required = schema.get("required")
    if isinstance(own_required, list):
        required.update(str(name) for name in own_required)
    return properties, required


def _variant_sample(variants: list[Any]) -> str:
    for variant in variants:
        sample = sample_for(variant)
        if sample:
            return sample
    return ""


def _single_plan(
    *,
    content_type: str,
    param_type: str,
    required: bool,
    sample: str,
) -> BodyPlan:
    return BodyPlan(
        raw=f"<>{BODY_PARAM_NAME}</>",
        parameters=(
            BodyParamSpec(
                name=BODY_PARAM_NAME,
                type=param_type,
                required=required,
                sample=sample,
            ),
        ),
        content_type=content_type,
        strategy="single-object" if param_type == "object" else "single-string",
    )


def _skeleton_plan(override: BodyOverride) -> BodyPlan:
    names = dict.fromkeys(_REF_RE.findall(override.raw))
    return BodyPlan(
        raw=override.raw,
        parameters=tuple(
            BodyParamSpec(name=name, type="string", required=True, sample="")
            for name in names
        ),
        content_type=override.content_type,
        strategy="skeleton",
    )


def _multipart_plan(properties: dict[str, Any], required: set[str]) -> BodyPlan:
    """Uma linha por campo obrigatório: `chave_de_wire:<>parametro</>`.

    A chave continua sendo o nome do spec — é o que vai no envelope multipart.
    O nome do parâmetro é snake_case porque `rules.py` só aceita essa forma, e
    dois campos do spec podem colapsar no mesmo snake_case.
    """
    lines: list[str] = []
    parameters: list[BodyParamSpec] = []
    taken: set[str] = set()
    for key in (name for name in properties if name in required):
        base = snake_case(key) or "field"
        name, suffix = base, 2
        while name in taken:
            name = f"{base}_{suffix}"
            suffix += 1
        taken.add(name)
        schema = properties[key] if isinstance(properties[key], dict) else {}
        lines.append(f"{key}:<>{name}</>")
        parameters.append(
            BodyParamSpec(
                name=name,
                type="string",
                required=True,
                sample=sample_for(schema),
                source_en=plain_text(schema.get("description")) or None,
            )
        )
    return BodyPlan(
        raw="\n".join(lines),
        parameters=tuple(parameters),
        content_type=_MULTIPART,
        strategy="multipart-granular",
    )


def plan_body(
    spec: dict[str, Any],
    operation: SpecOperation,
    override: BodyOverride | None = None,
) -> BodyPlan:
    if override is not None:
        return _EMPTY if override.mode == "none" else _skeleton_plan(override)
    if operation.method in _METHODS_WITHOUT_BODY or operation.request_body is None:
        return _EMPTY
    picked = _pick_content(operation.request_body)
    if picked is None:
        return _none_plan("requestBody has no readable `content` entry")
    content_type, entry = picked

    resolved = deref(spec, entry.get("schema") or {})
    schema = resolved if isinstance(resolved, dict) else {}
    properties, required = _properties_of(schema)
    required_body = bool(operation.request_body.get("required", False))

    if properties:
        if content_type == _MULTIPART:
            return _multipart_plan(properties, required)
        return _single_plan(
            content_type=content_type,
            param_type="object" if content_type == _JSON else "string",
            required=required_body,
            # urlencoded is a single string on the wire — a JSON object there
            # would be a lie.
            sample=body_sample_for(schema) if content_type == _JSON else "",
        )

    if content_type == _MULTIPART:
        return _none_plan(
            "multipart body with no properties — there are no form fields to "
            "model as granular lines"
        )

    # No `properties` does NOT mean no body. An array of tags, a oneOf of
    # actions and a Postman-converted `object` carrying only an `example` are
    # all real payloads; they all fit the single `<>body</>` parameter.
    if schema.get("type") == "array":
        return _single_plan(
            content_type=content_type,
            param_type="string",
            required=required_body,
            sample=sample_for(schema.get("items")),
        )
    variants = schema.get("oneOf") or schema.get("anyOf")
    if isinstance(variants, list) and variants:
        return _single_plan(
            content_type=content_type,
            param_type="string",
            required=required_body,
            sample=_variant_sample(variants),
        )
    if schema.get("example") is not None or schema.get("default") is not None:
        return _single_plan(
            content_type=content_type,
            param_type="object" if content_type == _JSON else "string",
            required=required_body,
            sample=sample_for(schema),
        )
    return _none_plan(
        "requestBody present but its schema carries no properties, no items, "
        "no variants and no example — nothing to model"
    )
