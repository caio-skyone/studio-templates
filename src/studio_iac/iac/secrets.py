"""Secret-shaped values in an IAC module.

Always warnings, never errors: a live-looking key in a `sample` is a suspicion,
not a certainty, and a `sk_` that blocks the generation of 279 operations costs
more than a warning somebody ignores.

Only VALUES are scanned — never prose. "O token começa com sk_live_" is
legitimate documentation.
"""

import re

from studio_iac.iac.models import IACModule, IACValidationError

# Lowercase, hyphenated form — `domain/openapi/emit.py` compares OpenAPI header
# names against this set verbatim. Keep it here (and not in `openapi/`) because
# `iac/` must not import from `openapi/`.
AUTH_HEADER_HINTS = frozenset(
    {
        "authorization",
        "token",
        "api_key",
        "apikey",
        "access_token",
        "bearer",
        "x-api-key",
    }
)

SECRET_PREFIX_RE = re.compile(r"(?:sk|rk|pk|whsec)_[A-Za-z0-9_\-]{8,}")
BEARER_LITERAL_RE = re.compile(r"Bearer\s+(?!<>)[A-Za-z0-9._\-]{8,}")


def _normalize(name: str) -> str:
    """Hyphen and case folded, so `X-Api-Key` matches the param name `x_api_key`."""
    return name.strip().lower().replace("-", "_")


AUTH_NAME_HINTS = frozenset(_normalize(hint) for hint in AUTH_HEADER_HINTS)


def _secret_match(value: str) -> str | None:
    for pattern in (SECRET_PREFIX_RE, BEARER_LITERAL_RE):
        found = pattern.search(value)
        if found:
            return found.group(0)
    return None


def scan_secrets(module: IACModule) -> list[IACValidationError]:
    warnings: list[IACValidationError] = []
    for index, operation in enumerate(module.operations):
        where = f"operations[{index}]"
        for param_index, parameter in enumerate(operation.parameters):
            param_where = f"{where}.parameters[{param_index}]"
            found = _secret_match(getattr(parameter, "sample", ""))
            if found:
                warnings.append(
                    IACValidationError(
                        path=f"{param_where}.sample",
                        message=(
                            f"sample of {parameter.name!r} looks like a real "
                            f"credential ({found!r}) — replace it with a fake value; "
                            "samples travel to Studio and into documentation"
                        ),
                    )
                )
            if _normalize(parameter.name) in AUTH_NAME_HINTS and not getattr(
                parameter, "sensitive", False
            ):
                warnings.append(
                    IACValidationError(
                        path=f"{param_where}.sensitive",
                        message=(
                            f"parameter {parameter.name!r} looks like a credential "
                            "but sensitive is false"
                        ),
                    )
                )
        found = _secret_match(operation.request.body.raw)
        if found:
            warnings.append(
                IACValidationError(
                    path=f"{where}.request.body.raw",
                    message=(
                        f"request body of {operation.name!r} carries what looks like "
                        f"a real credential ({found!r}) — parameterize it"
                    ),
                )
            )
        for header_index, header in enumerate(operation.request.header):
            header_where = f"{where}.request.header[{header_index}]"
            found = _secret_match(header.value)
            if found:
                warnings.append(
                    IACValidationError(
                        path=f"{header_where}.value",
                        message=(
                            f"header {header.key!r} carries what looks like a real "
                            f"credential ({found!r}) — use <>param</> instead"
                        ),
                    )
                )
                continue
            if (
                _normalize(header.key) in AUTH_NAME_HINTS
                and header.value.strip()
                and "<>" not in header.value
            ):
                warnings.append(
                    IACValidationError(
                        path=header_where,
                        message=(
                            f"auth header {header.key!r} has a literal value; use "
                            "<>param</> or let the connected account supply it"
                        ),
                    )
                )
    return warnings
