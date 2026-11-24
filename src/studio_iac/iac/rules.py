"""Offline validation of an IAC module against Studio schema rules.

Runs with no network. Everything here was learned by shipping a 279-operation
connector: the bidirectional reference check and the shared-name warning are
the two that caught real defects.
"""

import re
from collections import defaultdict

from studio_iac.iac.models import (
    PARAMETER_TYPES,
    IACModule,
    IACOperation,
    IACValidationError,
    IACValidationResult,
)
from studio_iac.iac.secrets import scan_secrets
from studio_iac.text import has_markup

MODULE_NAME_MAX = 30
OPERATION_NAME_MAX = 100
PARAMETER_NAME_MAX = 50
DESCRIPTION_MAX = 250

PARAM_REF_RE = re.compile(r"<>([^<>/]+)</>")
PARAMETER_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def request_parameter_refs(operation: IACOperation) -> set[str]:
    """Every `<>name</>` occurring anywhere in the serialized request."""
    payload = operation.request.model_dump_json(by_alias=True)
    return set(PARAM_REF_RE.findall(payload))


def _route(operation: IACOperation) -> str:
    return f"{operation.request.method} /{'/'.join(operation.request.url.path)}"


def _check_lengths(module: IACModule, errors: list[IACValidationError]) -> None:
    if len(module.name) > MODULE_NAME_MAX:
        errors.append(
            IACValidationError(
                path="name",
                message=(
                    f"module name is {len(module.name)} chars; max is {MODULE_NAME_MAX}"
                ),
            )
        )
    if module.description and len(module.description) > DESCRIPTION_MAX:
        errors.append(
            IACValidationError(
                path="description",
                message=(
                    f"module description is {len(module.description)} chars; "
                    f"max is {DESCRIPTION_MAX}"
                ),
            )
        )


def _check_operation(
    index: int,
    operation: IACOperation,
    errors: list[IACValidationError],
) -> None:
    where = f"operations[{index}]"
    if not operation.request.url.path:
        errors.append(
            IACValidationError(
                path=f"{where}.request.url.path",
                message=(
                    f"operation {operation.name!r} has an empty url.path — an "
                    "operation with no endpoint cannot be called"
                ),
            )
        )
    if len(operation.name) > OPERATION_NAME_MAX:
        errors.append(
            IACValidationError(
                path=f"{where}.name",
                message=(
                    f"operation name {operation.name!r} is {len(operation.name)} "
                    f"chars; max is {OPERATION_NAME_MAX}"
                ),
            )
        )
    if operation.description and len(operation.description) > DESCRIPTION_MAX:
        errors.append(
            IACValidationError(
                path=f"{where}.description",
                message=(
                    f"operation description is {len(operation.description)} "
                    f"chars; max is {DESCRIPTION_MAX}"
                ),
            )
        )
    for param_index, parameter in enumerate(operation.parameters):
        param_where = f"{where}.parameters[{param_index}]"
        if not PARAMETER_NAME_RE.fullmatch(parameter.name):
            errors.append(
                IACValidationError(
                    path=f"{param_where}.name",
                    message=(
                        f"parameter name {parameter.name!r} must be snake_case "
                        "(^[a-z][a-z0-9_]*$)"
                    ),
                )
            )
        if parameter.type not in PARAMETER_TYPES:
            errors.append(
                IACValidationError(
                    path=f"{param_where}.type",
                    message=(
                        f"parameter type {parameter.type!r} is not one of: "
                        + ", ".join(sorted(PARAMETER_TYPES))
                    ),
                )
            )
        if len(parameter.name) > PARAMETER_NAME_MAX:
            errors.append(
                IACValidationError(
                    path=f"{param_where}.name",
                    message=(
                        f"parameter name {parameter.name!r} is "
                        f"{len(parameter.name)} chars; max is {PARAMETER_NAME_MAX}"
                    ),
                )
            )
        if parameter.description and len(parameter.description) > DESCRIPTION_MAX:
            errors.append(
                IACValidationError(
                    path=f"{param_where}.description",
                    message=(
                        f"parameter description is {len(parameter.description)} "
                        f"chars; max is {DESCRIPTION_MAX}"
                    ),
                )
            )


def _check_references(
    index: int,
    operation: IACOperation,
    errors: list[IACValidationError],
) -> None:
    """Bidirectional: no dangling refs, and no orphan declarations."""
    where = f"operations[{index}]"
    declared = {parameter.name for parameter in operation.parameters}
    referenced = request_parameter_refs(operation)
    for name in sorted(referenced - declared):
        errors.append(
            IACValidationError(
                path=f"{where}.request",
                message=(
                    f"request references <>{name}</> but {name!r} is not declared "
                    f"as a parameter of {operation.name!r}"
                ),
            )
        )
    for name in sorted(declared - referenced):
        errors.append(
            IACValidationError(
                path=f"{where}.parameters",
                message=(
                    f"parameter {name!r} is declared but never referenced in the "
                    f"request of {operation.name!r}"
                ),
            )
        )


def _check_duplicates(module: IACModule, errors: list[IACValidationError]) -> None:
    names: dict[str, int] = {}
    routes: dict[str, str] = {}
    for index, operation in enumerate(module.operations):
        if operation.name in names:
            errors.append(
                IACValidationError(
                    path=f"operations[{index}].name",
                    message=(
                        f"duplicate operation name {operation.name!r} "
                        f"(first seen at operations[{names[operation.name]}]) — "
                        "two paths producing the same name are almost always aliases"
                    ),
                )
            )
        else:
            names[operation.name] = index
        route = _route(operation)
        if route in routes:
            errors.append(
                IACValidationError(
                    path=f"operations[{index}].request",
                    message=(
                        f"duplicate route {route} already used by {routes[route]!r}"
                    ),
                )
            )
        else:
            routes[route] = operation.name
        seen: set[str] = set()
        for parameter in operation.parameters:
            if parameter.name in seen:
                errors.append(
                    IACValidationError(
                        path=f"operations[{index}].parameters",
                        message=(
                            f"duplicate parameter name {parameter.name!r} in "
                            f"{operation.name!r}"
                        ),
                    )
                )
            seen.add(parameter.name)


def _shared_name_warnings(module: IACModule) -> list[IACValidationError]:
    """Same parameter name, different descriptions across operations.

    A shared name needs a description that serves every resource it appears in.
    """
    by_name: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for operation in module.operations:
        for parameter in operation.parameters:
            description = (parameter.description or "").strip()
            by_name[parameter.name][description].append(operation.name)
    warnings: list[IACValidationError] = []
    for name in sorted(by_name):
        variants = by_name[name]
        if len(variants) < 2:
            continue
        rendered = "; ".join(
            f"{description!r} in {', '.join(sorted(operations))}"
            for description, operations in sorted(variants.items())
        )
        warnings.append(
            IACValidationError(
                path="operations.parameters",
                message=(
                    f"parameter {name!r} has {len(variants)} divergent descriptions "
                    f"across operations — use one description that serves all: "
                    f"{rendered}"
                ),
            )
        )
    return warnings


def _check_query_format(
    index: int,
    operation: IACOperation,
    warnings: list[IACValidationError],
) -> None:
    """`url.query` still works, but it is not the format the server prefers."""
    where = f"operations[{index}]"
    if not operation.request.url.query:
        return
    if operation.request.query:
        warnings.append(
            IACValidationError(
                path=f"{where}.request",
                message=(
                    "operation fills both url.query and request.query — the "
                    "server sends both, so every shared key reaches the API "
                    "twice; keep request.query and empty url.query"
                ),
            )
        )
        return
    warnings.append(
        IACValidationError(
            path=f"{where}.request.url.query",
            message=(
                "url.query is the legacy format: it is stringified into the "
                "endpoint. Prefer request.query, sibling of request.header, "
                "which becomes the record {key: {value, enabled}}"
            ),
        )
    )


_WRITE_METHODS = frozenset({"POST", "PUT", "PATCH"})
# Uma linha multipart é `chave_de_wire:<>parametro</>`. A chave é o nome do
# campo no spec, então não há prefixo fixo para procurar — o que identifica o
# formato é a forma da linha. Um corpo JSON não casa: depois dos dois pontos
# vem aspas, nunca `<`.
_MULTIPART_LINE_RE = re.compile(r"(?m)^[^:\n]+:<>[^<>/]+</>")


def _check_literal_placeholders(
    index: int,
    operation: IACOperation,
    errors: list[IACValidationError],
) -> None:
    """A `{...}` still in a path segment is a placeholder that never became one.

    The generator only parameterizes a segment that is ONLY a placeholder, so
    `{Sid}.json`, `{name}:set-tags` and `v{version}` come out literal — and the
    URL is called with the braces in it. The bidirectional reference check
    cannot see this: where there is no <>ref</> there is nothing to match.
    """
    where = f"operations[{index}].request.url.path"
    for segment_index, segment in enumerate(operation.request.url.path):
        if "{" not in segment and "}" not in segment:
            continue
        errors.append(
            IACValidationError(
                path=f"{where}[{segment_index}]",
                message=(
                    f"path segment {segment!r} still carries a literal "
                    "placeholder — the URL would be called with the braces in "
                    "it. Rewrite the variable part as <>parameter_name</> and "
                    "declare the parameter"
                ),
            )
        )


def _check_write_without_body(
    index: int,
    operation: IACOperation,
    warnings: list[IACValidationError],
) -> None:
    """A write verb whose body references nothing usually lost its payload."""
    if operation.request.method not in _WRITE_METHODS:
        return
    if PARAM_REF_RE.search(operation.request.body.raw):
        return
    warnings.append(
        IACValidationError(
            path=f"operations[{index}].request.body",
            message=(
                f"{operation.request.method} operation {operation.name!r} has no "
                "parameter reference in request.body — legitimate for endpoints "
                "like .../cancel, but usually means the request body was "
                "silently dropped when the operation was generated"
            ),
        )
    )


def _check_multipart_content_type(
    index: int,
    operation: IACOperation,
    warnings: list[IACValidationError],
) -> None:
    """A hand-declared Content-Type overwrites the multipart boundary."""
    if not _MULTIPART_LINE_RE.search(operation.request.body.raw):
        return
    # Só HEADER: uma chave de query chamada `content-type` é um parâmetro de
    # verdade da API e não substitui boundary nenhum.
    if not any(
        header.key.strip().lower() == "content-type"
        for header in operation.request.header
    ):
        return
    warnings.append(
        IACValidationError(
            path=f"operations[{index}].request",
            message=(
                f"operation {operation.name!r} declares a Content-Type header on "
                "a multipart body — it replaces the "
                "'multipart/form-data; boundary=...' the platform builds, and "
                "the request breaks. The real mime goes in the multipart line "
                "metadata (file:<>file</>:mime:text/csv:name.csv), never in a "
                "separate header"
            ),
        )
    )


_MARKUP_MESSAGE = (
    "description carries markdown or HTML — the Studio renders this field "
    "literally, so the markup reaches the user as characters. Write plain "
    "prose"
)


def _check_markup_in_prose(
    index: int,
    operation: IACOperation,
    warnings: list[IACValidationError],
) -> None:
    """Nothing parses `description`: markup in it is shown, never rendered."""
    where = f"operations[{index}]"
    if has_markup(operation.description):
        warnings.append(
            IACValidationError(path=f"{where}.description", message=_MARKUP_MESSAGE)
        )
    for param_index, parameter in enumerate(operation.parameters):
        if has_markup(parameter.description):
            warnings.append(
                IACValidationError(
                    path=f"{where}.parameters[{param_index}].description",
                    message=_MARKUP_MESSAGE,
                )
            )


def validate_module(module: IACModule) -> IACValidationResult:
    errors: list[IACValidationError] = []
    warnings: list[IACValidationError] = []
    _check_lengths(module, errors)
    for index, operation in enumerate(module.operations):
        _check_operation(index, operation, errors)
        _check_references(index, operation, errors)
        _check_literal_placeholders(index, operation, errors)
        _check_query_format(index, operation, warnings)
        _check_write_without_body(index, operation, warnings)
        _check_multipart_content_type(index, operation, warnings)
        _check_markup_in_prose(index, operation, warnings)
    _check_duplicates(module, errors)
    if has_markup(module.description):
        warnings.append(IACValidationError(path="description", message=_MARKUP_MESSAGE))
    return IACValidationResult(
        ok=not errors,
        errors=errors,
        warnings=warnings + _shared_name_warnings(module) + scan_secrets(module),
    )
