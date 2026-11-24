from studio_iac.iac.models import (
    IACModule,
    IACModuleSettings,
    IACOperation,
    IACParameter,
    IACRequestBody,
    IACRequestHeader,
    IACRequestUrl,
    IACRestRequest,
)
from studio_iac.iac.secrets import AUTH_HEADER_HINTS, scan_secrets


def _param(
    name: str,
    *,
    sample: str = "x",
    sensitive: bool = False,
    description: str | None = "desc",
) -> IACParameter:
    return IACParameter(
        id=f"p-{name}",
        name=name,
        type="string",
        description=description,
        required=True,
        sensitive=sensitive,
        sample=sample,
    )


def _module(
    *,
    parameters: list[IACParameter] | None = None,
    header: list[IACRequestHeader] | None = None,
    body_raw: str = "",
    path: list[str] | None = None,
) -> IACModule:
    return IACModule(
        id="m-1",
        name="Stripe",
        description="desc",
        type="rest",
        settings=IACModuleSettings(),
        operations=[
            IACOperation(
                id="op-1",
                name="Customers - Create customer",
                description="desc",
                parameters=parameters or [],
                request=IACRestRequest(
                    method="POST",
                    url=IACRequestUrl(path=path or ["customers"]),
                    header=header or [],
                    body=IACRequestBody(mode="raw", raw=body_raw),
                ),
            )
        ],
    )


def _paths(warnings) -> list[str]:
    return [warning.path for warning in warnings]


def _messages(warnings) -> list[str]:
    return [warning.message for warning in warnings]


def test_clean_module_has_no_secret_warnings():
    module = _module(
        parameters=[_param("customer_id")],
        path=["customers", "<>customer_id</>"],
    )

    assert scan_secrets(module) == []


def test_live_secret_prefix_in_sample_warns():
    module = _module(
        parameters=[
            _param("api_key", sample="sk_live_51H8xQz9abcdEFGH", sensitive=True)
        ],
        header=[IACRequestHeader(key="X-Key", value="<>api_key</>")],
    )

    warnings = scan_secrets(module)

    assert _paths(warnings) == ["operations[0].parameters[0].sample"]
    assert "sk_live_51H8xQz9abcdEFGH" in _messages(warnings)[0]


def test_every_credential_prefix_is_covered():
    for prefix in ("sk", "rk", "pk", "whsec"):
        module = _module(
            parameters=[_param("secret_value", sample=f"{prefix}_test_abcdefgh12345")],
        )

        assert len(scan_secrets(module)) == 1, prefix


def test_secret_in_body_raw_warns():
    module = _module(body_raw='{"key": "whsec_abcdefgh12345678"}')

    warnings = scan_secrets(module)

    assert _paths(warnings) == ["operations[0].request.body.raw"]


def test_secret_in_header_value_warns():
    module = _module(
        header=[IACRequestHeader(key="X-Signature", value="rk_test_abcdefgh12345")]
    )

    warnings = scan_secrets(module)

    assert _paths(warnings) == ["operations[0].request.header[0].value"]


def test_hardcoded_bearer_literal_in_auth_header_warns():
    module = _module(
        header=[IACRequestHeader(key="Authorization", value="Bearer abcdef1234567890")]
    )

    warnings = scan_secrets(module)

    assert _paths(warnings) == ["operations[0].request.header[0].value"]


def test_auth_header_with_parameter_reference_is_fine():
    module = _module(
        parameters=[_param("pat", sensitive=True)],
        header=[IACRequestHeader(key="Authorization", value="Bearer <>pat</>")],
    )

    assert scan_secrets(module) == []


def test_auth_header_with_literal_value_warns_even_without_prefix():
    module = _module(header=[IACRequestHeader(key="X-Api-Key", value="my-team-key")])

    warnings = scan_secrets(module)

    assert _paths(warnings) == ["operations[0].request.header[0]"]
    assert "<>param</>" in _messages(warnings)[0]


def test_empty_auth_header_value_is_not_flagged():
    module = _module(header=[IACRequestHeader(key="Authorization", value="")])

    assert scan_secrets(module) == []


def test_credential_named_parameter_must_be_sensitive():
    module = _module(
        parameters=[_param("access_token", sensitive=False)],
        header=[IACRequestHeader(key="X-Token", value="<>access_token</>")],
    )

    warnings = scan_secrets(module)

    assert _paths(warnings) == ["operations[0].parameters[0].sensitive"]


def test_credential_named_parameter_with_sensitive_true_is_fine():
    module = _module(
        parameters=[_param("access_token", sensitive=True)],
        header=[IACRequestHeader(key="X-Token", value="<>access_token</>")],
    )

    assert scan_secrets(module) == []


def test_hyphenated_hint_matches_snake_case_parameter_name():
    module = _module(parameters=[_param("x_api_key", sensitive=False)])

    warnings = scan_secrets(module)

    assert _paths(warnings) == ["operations[0].parameters[0].sensitive"]


def test_prefix_inside_prose_description_is_not_flagged():
    module = _module(
        parameters=[
            _param(
                "customer_id",
                description="O token da conta começa com sk_live_ e nunca vai no IAC.",
            )
        ]
    )

    assert scan_secrets(module) == []


def test_auth_header_hints_keep_their_hyphenated_form():
    # emit.py compara nome de header do spec (com hífen) contra este conjunto.
    assert "x-api-key" in AUTH_HEADER_HINTS
