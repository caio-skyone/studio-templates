import re
from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from studio_iac.iac.errors import (
    IACDuplicateOperationName,
    IACDuplicateParameterName,
)
from studio_iac.iac.naming import (
    ensure_unique_operation_names,
    ensure_unique_parameter_names,
)

PARAMETER_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

IACModuleType = Literal["rest"]
IACParameterType = Literal["object", "string", "number", "array"]
PARAMETER_TYPES: frozenset[str] = frozenset({"object", "string", "number", "array"})
IACHttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
IACUrlType = Literal["base-url", "full-url"]
IACBodyMode = Literal["raw"]
IACBodyLanguage = Literal["json"]
IACAuthenticationType = Literal[
    "no-auth",
    "basic",
    "bearer-token",
    "oauth-1",
    "oauth-2",
    "cookie",
    "aws",
    "oauth2-jwt",
    "ca-certificate",
    "google-oauth",
    "header-auth",
    "mtls-certificate",
]

_SUPPORTED_MODULE_TYPES: frozenset[str] = frozenset({"rest"})


def _require_entity_id(value: str) -> str:
    if not value.strip():
        raise ValueError("id must be non-empty")
    return value


class IACQueryParam(BaseModel):
    model_config = ConfigDict(extra="ignore")

    key: str = Field(
        description=(
            "Query string key — the literal wire key, which need NOT match the "
            "parameter name (e.g. key 'StartTime<' for parameter "
            "'start_time_before')."
        )
    )
    value: str = Field(
        description=("Value or Studio parameter reference, e.g. '<>param_name</>'.")
    )
    enabled: bool = Field(
        default=True, description="Whether the query param is enabled."
    )


class IACRequestHeader(BaseModel):
    model_config = ConfigDict(extra="ignore")

    key: str = Field(description="Request header name.")
    value: str = Field(
        description=("Value or Studio parameter reference, e.g. '<>param_name</>'.")
    )
    enabled: bool = Field(default=True, description="Whether the header is enabled.")


class IACRequestUrl(BaseModel):
    model_config = ConfigDict(extra="ignore")

    path: list[str] = Field(
        default_factory=list,
        description=(
            "URL path as an array of segments joined by '/'. "
            "Do NOT put a full URL here — split it into segments. "
            "Example: endpoint /api/v1/users/{id} → "
            '["api", "v1", "users", "<>user_id</>"].'
        ),
    )
    query: list[IACQueryParam] = Field(
        default_factory=list,
        description="Query string key/value pairs.",
    )


class IACBodyRawOptions(BaseModel):
    model_config = ConfigDict(extra="ignore")

    language: IACBodyLanguage = Field(description="Body language, always 'json'.")


class IACBodyOptions(BaseModel):
    model_config = ConfigDict(extra="ignore")

    raw: IACBodyRawOptions


class IACRequestBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    mode: IACBodyMode = Field(description="Body mode, always 'raw'.")
    raw: str = Field(
        default="",
        description=(
            "Raw body string. Use a Studio parameter ref for dynamic bodies, "
            "e.g. '<>body_param</>' for object params or a JSON skeleton with "
            'embedded refs like \'{"status": "<>new_status</>"}\'.'
            "Empty string means no body."
        ),
    )
    options: IACBodyOptions = Field(
        default=IACBodyOptions(raw=IACBodyRawOptions(language="json")),
        description="Body options. Always json, even if body is empty.",
    )


class IACRestRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    method: IACHttpMethod = Field(
        description="HTTP method: GET, POST, PUT, PATCH, or DELETE."
    )
    url_type: IACUrlType = Field(
        default="base-url",
        serialization_alias="urlType",
        validation_alias=AliasChoices("urlType", "url_type"),
        description=(
            "'base-url' (default): path[] is appended to the connected account host. "
            "'full-url': path[] contains the entire URL including host, used when "
            "calling a different API from inside the same connector."
        ),
    )
    url: IACRequestUrl
    query: list[IACQueryParam] = Field(
        default_factory=list,
        description=(
            "PREFERRED query string format: [{key, value, enabled?}], sibling of "
            "header. Becomes the server-side record {key: {value, enabled}}. "
            "Use this instead of url.query."
        ),
    )
    header: list[IACRequestHeader] = Field(
        default_factory=list,
        description="Request headers as [{key, value, enabled?}] pairs.",
    )
    body: IACRequestBody = Field(
        default=IACRequestBody(mode="raw", raw=""),
        description="Request body. Omit for GET/DELETE with no body.",
    )


class IACParameter(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str = Field(min_length=1)
    # Legacy connectors carry types the current schema does not know. Parsing
    # must be lossless so a pulled module can be patched back; rules.py is
    # what rejects the unknown value.
    type: IACParameterType | str
    description: str | None = None
    required: bool
    sensitive: bool
    sample: str = ""

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        return _require_entity_id(value)

    @field_validator("sample", mode="before")
    @classmethod
    def coerce_null_sample(cls, value: object) -> object:
        return "" if value is None else value


class IACOperation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str = Field(min_length=1)
    description: str | None = None
    parameters: list[IACParameter] = Field(default_factory=list)
    request: IACRestRequest

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        return _require_entity_id(value)


class IACValidationError(BaseModel):
    model_config = ConfigDict(extra="ignore")

    path: str
    message: str


class IACValidationResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ok: bool
    errors: list[IACValidationError] = Field(default_factory=list)
    warnings: list[IACValidationError] = Field(default_factory=list)


class DraftProvenance(BaseModel):
    """Where a draft came from, and what it looked like when it arrived.

    Lives in the draft's `.meta.json`, never inside IACModule: `baseline` is
    what tells an inherited defect apart from one the agent introduced, and
    `remote_authorization` must not be reachable by any edit tool.
    """

    model_config = ConfigDict(extra="ignore")

    origin: str = ""
    baseline: dict[str, object] = Field(default_factory=dict)
    remote_authorization: dict[str, object] = Field(default_factory=dict)


class DraftIndexEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    type: str
    op_count: int
    updated_at: datetime
    provenance: DraftProvenance | None = None


class IACModuleSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    authentication_type: IACAuthenticationType | str = ""


class IACModule(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str
    name: str = Field(default="New Module")
    description: str | None = None
    type: Annotated[IACModuleType, Field()]
    settings: IACModuleSettings
    operations: list[IACOperation] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def validate_module_id(cls, value: str) -> str:
        return _require_entity_id(value)

    @field_validator("type", mode="before")
    @classmethod
    def normalize_module_type(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("type must be a string")
        normalized = value.lower()
        if normalized not in _SUPPORTED_MODULE_TYPES:
            supported = ", ".join(sorted(_SUPPORTED_MODULE_TYPES))
            raise ValueError(f"type must be one of: {supported}")
        return normalized

    @model_validator(mode="after")
    def validate_operations_for_module_type(self) -> Self:
        if self.type == "rest":
            for operation in self.operations:
                if operation.request is None:
                    raise ValueError(
                        f"operation {operation.id!r} requires request for REST modules"
                    )
        return self

    @model_validator(mode="after")
    def validate_unique_operation_and_parameter_names(self) -> Self:
        try:
            ensure_unique_operation_names(self.operations)
            for operation in self.operations:
                ensure_unique_parameter_names(operation.parameters)
        except IACDuplicateOperationName as error:
            raise ValueError(str(error)) from error
        except IACDuplicateParameterName as error:
            raise ValueError(str(error)) from error
        return self


class ExportedModule(BaseModel):
    """A module as it came off /api/iac/export, with its authorization intact.

    `authorization` lives here and not on IACModule on purpose: the agent must
    not be able to edit it. Patching sends back exactly what came out.
    """

    model_config = ConfigDict(extra="ignore")

    module: IACModule
    authorization: dict[str, object] = Field(default_factory=dict)
