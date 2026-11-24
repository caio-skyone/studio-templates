"""Deterministic parameter samples.

A sample is derived from the schema of THAT occurrence, never from a table
keyed by parameter name: `name` serves 29 domains on a real spec, and
`TABELA_EXEMPLO` reads wrong in a warehouse. Occurrence-local means
domain-local, for free.

A bare `{"type": "string"}` is left empty on purpose. There is no honest
fictitious value for it, and the report counts what was left empty so the loop
still closes.
"""

import json
from typing import Any

_FORMAT_SAMPLES = {
    "date": "2026-01-31",
    "date-time": "2026-01-31T12:00:00Z",
    "time": "12:00:00",
    "duration": "P1D",
    "email": "user@example.com",
    "hostname": "example.com",
    "ipv4": "192.0.2.1",
    "ipv6": "2001:db8::1",
    "uri": "https://example.com",
    "url": "https://example.com",
    "uuid": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
    "byte": "ZXhhbXBsZQ==",
    "binary": "file.bin",
    "password": "s3cr3t",
}

_TYPE_SAMPLES = {
    "boolean": "true",
    "integer": "10",
    "number": "10",
    "array": "[]",
    "object": "{}",
}


def _scalar(value: object) -> str | None:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str | int | float):
        return str(value)
    if isinstance(value, list | dict) and value:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return None


def sample_for(schema: object) -> str:
    """enum -> example -> default -> format -> type. Empty when nothing says."""
    if not isinstance(schema, dict):
        return ""
    enum = schema.get("enum")
    if isinstance(enum, list) and enum:
        rendered = _scalar(enum[0])
        if rendered is not None:
            return rendered
    for key in ("example", "default"):
        rendered = _scalar(schema.get(key))
        if rendered is not None:
            return rendered
    items: Any = schema.get("items")
    if isinstance(items, dict):
        nested = sample_for(items)
        if nested:
            return nested
    fmt = schema.get("format")
    if isinstance(fmt, str) and fmt in _FORMAT_SAMPLES:
        return _FORMAT_SAMPLES[fmt]
    return _TYPE_SAMPLES.get(str(schema.get("type")), "")


def parameter_sample(parameter: object, schema: object) -> str:
    """A parameter's own `example` outranks its schema — some specs use only it.

    `examples` is a map; the first entry wins, in spec order, because there is
    no other deterministic way to choose one.
    """
    if isinstance(parameter, dict):
        rendered = _scalar(parameter.get("example"))
        if rendered is not None:
            return rendered
        examples = parameter.get("examples")
        if isinstance(examples, dict):
            for entry in examples.values():
                if not isinstance(entry, dict):
                    continue
                rendered = _scalar(entry.get("value"))
                if rendered is not None:
                    return rendered
    return sample_for(schema)


_MAX_BODY_DEPTH = 3
_MAX_BODY_KEYS = 12


def _merged_properties(schema: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """`allOf` parts merged in first, outer wins — the body planner's own rule.

    A body composed only of `allOf` is ordinary in real specs. Reading just
    `properties` would hand back an empty skeleton for exactly the bodies
    `plan_body` already decided were modelable.
    """
    properties: dict[str, Any] = {}
    required: dict[str, None] = {}
    parts = schema.get("allOf")
    if isinstance(parts, list):
        for part in parts:
            if not isinstance(part, dict):
                continue
            part_properties, part_required = _merged_properties(part)
            properties.update(part_properties)
            required.update(dict.fromkeys(part_required))
    own = schema.get("properties")
    if isinstance(own, dict):
        properties.update(own)
    own_required = schema.get("required")
    if isinstance(own_required, list):
        required.update(
            dict.fromkeys(name for name in own_required if isinstance(name, str))
        )
    return properties, list(required)


def _ordered_properties(schema: dict[str, Any]) -> list[tuple[str, Any]]:
    """Required first, then spec order, capped. A truncated skeleton is useful."""
    properties, declared = _merged_properties(schema)
    if not properties:
        return []
    required = [name for name in declared if name in properties]
    ordered = required + [name for name in properties if name not in required]
    return [(name, properties[name]) for name in ordered[:_MAX_BODY_KEYS]]


def _json_value(schema: object, depth: int) -> Any:
    if not isinstance(schema, dict):
        return ""
    for key in ("example", "default"):
        if schema.get(key) is not None:
            return schema[key]
    enum = schema.get("enum")
    if isinstance(enum, list) and enum:
        return enum[0]
    declared = schema.get("type")
    if declared == "array" or "items" in schema:
        if depth >= _MAX_BODY_DEPTH:
            return []
        return [_json_value(schema.get("items"), depth + 1)]
    if declared == "object" or "properties" in schema or "allOf" in schema:
        if depth >= _MAX_BODY_DEPTH:
            return {}
        return {
            name: _json_value(sub, depth + 1)
            for name, sub in _ordered_properties(schema)
        }
    if declared == "boolean":
        return True
    if declared == "integer":
        return 1
    if declared == "number":
        return 1.5
    fmt = schema.get("format")
    if isinstance(fmt, str) and fmt in _FORMAT_SAMPLES:
        return _FORMAT_SAMPLES[fmt]
    return ""


def body_sample_for(schema: object) -> str:
    """A JSON body skeleton derived from the schema — never asked of a model.

    The schema carries the shape of the body; a translator does not. Asking for
    it is asking for invention, and an invented body sample reaches the user as
    if it were documentation.
    """
    if not isinstance(schema, dict) or not _ordered_properties(schema):
        return ""
    value = _json_value(schema, 0)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
