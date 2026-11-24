import uuid
from typing import get_args

import pytest
from pydantic import ValidationError

from studio_iac.iac.models import (
    IACAuthenticationType,
    IACModule,
    IACModuleSettings,
    IACOperation,
    IACParameter,
    IACQueryParam,
    IACRequestHeader,
    IACRequestUrl,
    IACRestRequest,
)


def _uuid4() -> str:
    return str(uuid.uuid4())


def _rest_request() -> IACRestRequest:
    return IACRestRequest(method="GET", url=IACRequestUrl(path=["api", "v1"]))


def _parameter(name: str = "user_id") -> IACParameter:
    return IACParameter(
        id=_uuid4(),
        name=name,
        type="string",
        required=True,
        sensitive=False,
        sample="123",
    )


def _operation() -> IACOperation:
    return IACOperation(
        id=_uuid4(),
        name="Get user",
        request=_rest_request(),
    )


def test_module_type_normalizes_case_insensitive_rest():
    module = IACModule(
        id=_uuid4(),
        type="REST",
        settings=IACModuleSettings(authentication_type="Basic"),
    )
    assert module.type == "rest"


def test_module_type_rejects_unsupported_values():
    with pytest.raises(ValidationError, match="type must be one of"):
        IACModule(
            id=_uuid4(),
            type="database",
            settings=IACModuleSettings(),
        )


def test_parameter_name_is_not_rejected_at_parse_time():
    # Legacy connectors carry camelCase names; validate_module reports them.
    assert _parameter(name="UserId").name == "UserId"


def test_parameter_name_accepts_valid_snake_case():
    parameter = _parameter(name="user_id")
    assert parameter.name == "user_id"


def test_query_param_has_key_value_and_enabled():
    query_param = IACQueryParam(key="page", value="<>page</>")
    dumped = query_param.model_dump()
    assert dumped == {"key": "page", "value": "<>page</>", "enabled": True}


def test_request_accepts_first_class_query_sibling_of_header():
    request = IACRestRequest.model_validate(
        {
            "method": "GET",
            "url": {"path": ["v1", "charges"]},
            "query": [{"key": "limit", "value": "<>limit</>"}],
        }
    )

    assert [(q.key, q.value, q.enabled) for q in request.query] == [
        ("limit", "<>limit</>", True)
    ]
    assert request.url.query == []


def test_query_param_enabled_is_explicitly_settable():
    param = IACQueryParam(key="expand[]", value="<>expand</>", enabled=False)

    assert param.enabled is False


def test_url_query_still_parses_and_gains_enabled_default():
    request = IACRestRequest.model_validate(
        {
            "method": "GET",
            "url": {
                "path": ["v1", "charges"],
                "query": [{"key": "limit", "value": "10"}],
            },
        }
    )

    assert request.url.query[0].enabled is True
    assert request.query == []


def test_oauth2_jwt_is_the_studio_spelling():
    settings = IACModuleSettings(authentication_type="oauth2-jwt")

    assert settings.authentication_type == "oauth2-jwt"
    assert "oauth2-jwt" in get_args(IACAuthenticationType)
    assert "oauth-2-jwt" not in get_args(IACAuthenticationType)


def test_request_header_includes_enabled():
    header = IACRequestHeader(
        key="Authorization",
        value="Bearer <>pat</>",
        enabled=False,
    )
    dumped = header.model_dump()
    assert dumped == {
        "key": "Authorization",
        "value": "Bearer <>pat</>",
        "enabled": False,
    }


def test_rest_request_url_type_defaults_to_base_url():
    request = _rest_request()
    assert request.url_type == "base-url"


def test_rest_request_serializes_url_type_as_camel_case():
    request = IACRestRequest(
        method="POST",
        urlType="full-url",
        url=IACRequestUrl(path=["https://other.api.example/v1"]),
    )
    dumped = request.model_dump(by_alias=True)
    assert dumped["urlType"] == "full-url"
    assert "url_type" not in dumped


def test_module_serializes_lowercase_type():
    module = IACModule(
        id=_uuid4(),
        type="rest",
        settings=IACModuleSettings(authentication_type="bearer-token"),
        operations=[_operation()],
    )
    dumped = module.model_dump()
    assert dumped["type"] == "rest"


def test_module_id_rejects_empty():
    with pytest.raises(ValidationError, match="non-empty"):
        IACModule(
            id="   ",
            type="rest",
            settings=IACModuleSettings(),
        )


def test_operation_id_accepts_studio_opaque_ids():
    operation = IACOperation(
        id="Mmkv7z-4dU",
        name="Get user",
        request=_rest_request(),
    )
    assert operation.id == "Mmkv7z-4dU"


def test_operation_id_rejects_empty():
    with pytest.raises(ValidationError, match="non-empty"):
        IACOperation(
            id="   ",
            name="Get user",
            request=_rest_request(),
        )


def test_module_rejects_rest_operation_without_request():
    with pytest.raises(ValidationError, match="requires request"):
        IACModule(
            id=_uuid4(),
            type="rest",
            settings=IACModuleSettings(),
            operations=[
                IACOperation.model_construct(
                    id=_uuid4(),
                    name="Broken",
                    request=None,
                )
            ],
        )


LEGACY_MODULE = {
    "id": "m1",
    "name": "Legacy",
    "type": "rest",
    "settings": {"authentication_type": "bearer-token"},
    "operations": [
        {
            "id": "op-1",
            "name": "Legacy op",
            "request": {"method": "GET", "url": {"path": []}},
            "parameters": [
                {
                    "id": "p-1",
                    "name": "accountId",
                    "type": "boolean",
                    "required": True,
                    "sensitive": False,
                    "sample": None,
                }
            ],
        }
    ],
}


def test_legacy_module_parses_without_raising():
    module = IACModule.model_validate(LEGACY_MODULE)

    parameter = module.operations[0].parameters[0]
    assert parameter.name == "accountId"
    assert parameter.type == "boolean"
    assert parameter.sample == ""
    assert module.operations[0].request.url.path == []


def test_missing_sample_defaults_to_empty_string():
    module = IACModule.model_validate(
        {
            **LEGACY_MODULE,
            "operations": [
                {
                    **LEGACY_MODULE["operations"][0],
                    "parameters": [
                        {
                            "id": "p-1",
                            "name": "ok_name",
                            "type": "string",
                            "required": True,
                            "sensitive": False,
                        }
                    ],
                }
            ],
        }
    )

    assert module.operations[0].parameters[0].sample == ""
