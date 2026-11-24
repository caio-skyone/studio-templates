"""Path parameter naming.

The single most valuable rule in this module: a GENERIC placeholder takes its
name from the literal collection segment immediately before it, singularized,
with `_id`. `{intent}` appears in both /payment_intents/ and /setup_intents/ —
trusting the placeholder produces two parameters called `intent_id` that mean
different things. The preceding segment never lies.

Specific placeholders (`customer`, `charge`, `invoice`, `account`) keep the
spec's name: they already say what they are.
"""

import re
from collections.abc import Callable

from studio_iac.openapi.config import NamingConfig
from studio_iac.openapi.shape import (
    SpecOperation,
    has_placeholder,
    placeholders_in,
)

GENERIC_PLACEHOLDERS = frozenset(
    {
        "id",
        "sid",
        "item",
        "intent",
        "fee",
        "schedule",
        "code",
        "session",
        "link",
        "transaction",
        "capability",
        "person",
        "feature",
        "configuration",
        "reversal",
        "value_list",
    }
)

IRREGULAR_SINGULAR = {
    "people": "person",
    "children": "child",
    "men": "man",
    "women": "woman",
    "teeth": "tooth",
    "feet": "foot",
    "indices": "index",
    "matrices": "matrix",
    "data": "datum",
    "criteria": "criterion",
}

_UNCOUNTABLE = frozenset(
    {"balance", "status", "metadata", "usage", "history", "series", "species"}
)

_CAMEL_BOUNDARY_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")

_NON_WORD_RE = re.compile(r"[^a-z0-9]+")

_ID_SEPARATOR_RE = re.compile(r"[^A-Za-z0-9]+")


def humanize_operation_id(operation_id: str) -> str:
    """`CreateAlphaSender` -> "Create alpha sender".

    Only the chunk after the last `_` is used: several APIs derive the id from
    the path (`get-/crm-object-schemas/2026-09/schemas_getAll`) and everything
    before it is the route again, not a name. A better fallback, not a
    universal one — the report says who landed on it.
    """
    tail = operation_id.rsplit("_", 1)[-1]
    spaced = _ID_SEPARATOR_RE.sub(" ", _CAMEL_BOUNDARY_RE.sub(" ", tail)).strip()
    if not spaced:
        return ""
    return spaced[0].upper() + spaced[1:].lower()


def operation_action(operation: SpecOperation) -> tuple[str, str | None]:
    """The action half of the name, plus which fallback level produced it.

    Level is None when the spec had a summary — the normal case, and the only
    one the report stays quiet about.
    """
    summary = (operation.summary or "").strip()
    if summary:
        return summary, None
    if operation.operation_id:
        humanized = humanize_operation_id(operation.operation_id)
        if humanized:
            return humanized, "operation_id"
    return operation.operation_key, "operation_key"


def snake_case(value: str) -> str:
    spaced = _CAMEL_BOUNDARY_RE.sub("_", value)
    return _NON_WORD_RE.sub("_", spaced.lower()).strip("_")


def singularize(word: str, overrides: dict[str, str]) -> str:
    if word in overrides:
        return overrides[word]
    if word in IRREGULAR_SINGULAR:
        return IRREGULAR_SINGULAR[word]
    if word in _UNCOUNTABLE:
        return word
    if len(word) <= 3:
        # `pos`, `ips`, `abs`: an acronym that happens to end in `s`. Chopping
        # it produced `po_id` on a real build. Overrides and irregulars are
        # checked first, so a genuine three-letter plural is still reachable.
        return word
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith(("shes", "ches", "xes", "ses", "zes")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _preceding_literal(segments: list[str], index: int) -> str | None:
    """The nearest earlier segment with no placeholder in it at all.

    A composite segment (`{Sid}.json`) is not a collection name: its literal
    part is a file extension or an action, never the resource.
    """
    for position in range(index - 1, -1, -1):
        segment = segments[position]
        if not has_placeholder(segment):
            return segment
    return None


def path_param_name(
    segments: list[str],
    index: int,
    placeholder: str,
    *,
    naming: NamingConfig,
    shape_key: str,
    overrides: dict[str, str],
) -> str:
    explicit = overrides.get(f"{shape_key}:{placeholder}")
    if explicit is not None:
        return explicit

    generic = (GENERIC_PLACEHOLDERS | set(naming.generic_placeholders.add)) - set(
        naming.generic_placeholders.remove
    )
    normalized = snake_case(placeholder)
    if normalized not in generic:
        return normalized

    collection = _preceding_literal(segments, index)
    if collection is None:
        return normalized
    return f"{singularize(snake_case(collection), naming.singular)}_id"


def iac_path_segments(
    operation: SpecOperation,
    *,
    naming: NamingConfig,
    path_param_overrides: dict[str, str],
    strip_prefix: list[str],
    allocate: Callable[[str], str] | None = None,
) -> tuple[list[str], list[tuple[str, str]]]:
    """Return (IAC path segments, [(placeholder, param_name), ...]).

    Substitution is PER OCCURRENCE, never per segment: `{Sid}.json` must come
    out as `<>message_id</>.json`, not as a bare parameter — the suffix is part
    of the real endpoint.

    `allocate` disambiguates the name against the rest of the operation and
    MUST run here, before substitution: two placeholders can normalize to the
    same name, and renaming afterwards could not tell the two `<>name</>`
    occurrences apart.

    strip_prefix is NOT applied: the IAC path must reach the real endpoint. It
    is only used to build the shape key, which is done elsewhere.
    """
    del strip_prefix
    raw = [segment for segment in operation.path.split("/") if segment]
    segments: list[str] = []
    params: list[tuple[str, str]] = []
    assigned: dict[str, str] = {}
    for index, segment in enumerate(raw):
        if not has_placeholder(segment):
            segments.append(segment)
            continue
        rendered = segment
        for placeholder in placeholders_in(segment):
            name = assigned.get(placeholder)
            if name is None:
                # O mesmo placeholder repetido na path é o MESMO valor: aloca
                # uma vez só, senão `/{id}/x/{id}` viraria `id` e `id_path`.
                name = path_param_name(
                    raw,
                    index,
                    placeholder,
                    naming=naming,
                    shape_key=operation.shape_key,
                    overrides=path_param_overrides,
                )
                if allocate is not None:
                    name = allocate(name)
                assigned[placeholder] = name
            rendered = rendered.replace(f"{{{placeholder}}}", f"<>{name}</>", 1)
            if (placeholder, name) not in params:
                params.append((placeholder, name))
        segments.append(rendered)
    return segments, params
