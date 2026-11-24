"""Per-connector config: the decisions about a spec that the spec cannot hold."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from studio_iac.openapi.errors import ConnectorConfigInvalid


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ModuleConfig(_Strict):
    name: str = Field(min_length=1)
    description: str | None = None
    authentication_type: str = ""
    strip_path_prefix: list[str] = Field(
        default_factory=list,
        description="Leading path segments dropped before building the shape key.",
    )


class DomainConfig(_Strict):
    domain: str = Field(min_length=1)
    block: str = "default"


class ExcludeEntry(_Strict):
    key: str = Field(min_length=1, description="Shape key to drop.")
    reason: str = Field(min_length=1, description="Why — this is the audit trail.")


class HeaderConfig(_Strict):
    key: str = Field(min_length=1)
    param: str = Field(min_length=1)
    methods: list[str] | None = Field(
        default=None, description="None means every method."
    )
    required: bool = Field(
        default=False,
        description=(
            "Mark the parameter required in the connector. An API-optional "
            "header may still be required here — depending on a provider's "
            "implicit default is a risk (Stripe-Version is the canonical case)."
        ),
    )
    sample: str = Field(
        default="",
        description=(
            "Example value for the parameter. A config header is exactly what "
            "the spec does not describe, so nothing else can fill this in."
        ),
    )


class GenericPlaceholders(_Strict):
    add: list[str] = Field(default_factory=list)
    remove: list[str] = Field(default_factory=list)


class NamingConfig(_Strict):
    generic_placeholders: GenericPlaceholders = Field(
        default_factory=GenericPlaceholders
    )
    singular: dict[str, str] = Field(
        default_factory=dict,
        description="Plural segment -> singular, for words the rules get wrong.",
    )


class BodyOverride(_Strict):
    mode: Literal["skeleton", "none"]
    raw: str = ""
    # Um skeleton é sempre um corpo escrito à mão: sem Content-Type ele sai
    # como body cru e a API responde 415. JSON é a forma que o
    # authoring-rules descreve; urlencoded é o único outro caso real.
    content_type: str = "application/json"


class AuthHeaderOverrides(_Strict):
    """Ajustes à heurística de nome que identifica headers de autenticação.

    Mesma forma de GenericPlaceholders de propósito: é o mesmo padrão de
    "defaults no código, config acrescenta ou remove".
    """

    add: list[str] = Field(default_factory=list)
    remove: list[str] = Field(default_factory=list)


class OverridesConfig(_Strict):
    path_params: dict[str, str] = Field(
        default_factory=dict,
        description="'{shape_key}:{placeholder}' -> parameter name.",
    )
    body: dict[str, BodyOverride] = Field(
        default_factory=dict, description="Operation key -> body override."
    )
    auth_headers: AuthHeaderOverrides = Field(default_factory=AuthHeaderOverrides)


class ConnectorConfig(_Strict):
    module: ModuleConfig
    include_roots: list[str] = Field(min_length=1)
    domains: dict[str, DomainConfig] = Field(default_factory=dict)
    exclude: list[ExcludeEntry] = Field(default_factory=list)
    headers: list[HeaderConfig] = Field(default_factory=list)
    naming: NamingConfig = Field(default_factory=NamingConfig)
    overrides: OverridesConfig = Field(default_factory=OverridesConfig)

    def excluded_keys(self) -> dict[str, str]:
        return {entry.key: entry.reason for entry in self.exclude}


def load_config(payload: object, source: object) -> ConnectorConfig:
    if not isinstance(payload, dict):
        raise ConnectorConfigInvalid(
            source, f"expected a JSON object, got {type(payload).__name__}"
        )
    try:
        return ConnectorConfig.model_validate(payload)
    except ValidationError as error:
        details = "; ".join(
            f"{'.'.join(str(part) for part in detail['loc']) or '<root>'}: "
            f"{detail['msg']}"
            for detail in error.errors()[:10]
        )
        raise ConnectorConfigInvalid(source, details) from error
