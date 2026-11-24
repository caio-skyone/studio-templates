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
from studio_iac.iac.rules import validate_module


def _param(name: str, description: str | None = "desc") -> IACParameter:
    return IACParameter(
        id=f"p-{name}",
        name=name,
        type="string",
        description=description,
        required=True,
        sensitive=False,
        sample="x",
    )


def _operation(
    op_id: str,
    name: str,
    *,
    path: list[str],
    parameters: list[IACParameter] | None = None,
    method: str = "GET",
) -> IACOperation:
    return IACOperation(
        id=op_id,
        name=name,
        description="desc",
        parameters=parameters or [],
        request=IACRestRequest(method=method, url=IACRequestUrl(path=path)),
    )


def _module(operations: list[IACOperation], *, name: str = "Stripe") -> IACModule:
    return IACModule(
        id="m-1",
        name=name,
        description="desc",
        type="rest",
        settings=IACModuleSettings(),
        operations=operations,
    )


def _messages(result) -> list[str]:
    return [error.message for error in result.errors]


def test_clean_module_is_ok():
    module = _module(
        [
            _operation(
                "op-1",
                "Customers - Get customer",
                path=["customers", "<>customer_id</>"],
                parameters=[_param("customer_id")],
            )
        ]
    )

    result = validate_module(module)

    assert result.ok
    assert result.errors == []
    assert result.warnings == []


def test_reference_without_declared_parameter_is_error():
    module = _module(
        [_operation("op-1", "Customers - Get", path=["customers", "<>customer_id</>"])]
    )

    result = validate_module(module)

    assert not result.ok
    assert any(
        "customer_id" in message and "not declared" in message
        for message in _messages(result)
    )


def test_declared_parameter_never_referenced_is_error():
    module = _module(
        [
            _operation(
                "op-1",
                "Customers - List",
                path=["customers"],
                parameters=[_param("orphan_param")],
            )
        ]
    )

    result = validate_module(module)

    assert not result.ok
    assert any(
        "orphan_param" in message and "never referenced" in message
        for message in _messages(result)
    )


def test_module_name_over_limit_is_error():
    module = _module([], name="A" * 31)

    result = validate_module(module)

    assert not result.ok
    assert any("module name" in message for message in _messages(result))


def test_duplicate_method_and_path_is_error():
    module = _module(
        [
            _operation("op-1", "Customers - List", path=["customers"]),
            _operation("op-2", "Customers - Index", path=["customers"]),
        ]
    )

    result = validate_module(module)

    assert not result.ok
    assert any("GET /customers" in message for message in _messages(result))


def test_description_over_limit_is_error():
    module = _module(
        [
            _operation(
                "op-1",
                "Customers - Get",
                path=["customers", "<>customer_id</>"],
                parameters=[_param("customer_id", description="d" * 251)],
            )
        ]
    )

    result = validate_module(module)

    assert not result.ok
    assert any("description" in message for message in _messages(result))


def test_operation_name_over_limit_is_error():
    module = _module(
        [
            _operation(
                "op-1",
                "C" * 101,
                path=["customers"],
            )
        ]
    )

    result = validate_module(module)

    assert not result.ok
    assert any("operation name" in message for message in _messages(result))


def test_parameter_name_over_limit_is_error():
    long_name = "a" * 51
    module = _module(
        [
            _operation(
                "op-1",
                "Customers - Get",
                path=["customers"],
                parameters=[_param(long_name)],
            )
        ]
    )
    module = module.model_copy(
        update={
            "operations": [
                operation.model_copy(
                    update={
                        "request": operation.request.model_copy(
                            update={
                                "url": IACRequestUrl(
                                    path=list(operation.request.url.path),
                                    query=[
                                        {
                                            "key": long_name,
                                            "value": f"<>{long_name}</>",
                                        }
                                    ],
                                )
                            }
                        )
                    }
                )
                for operation in module.operations
            ]
        }
    )

    result = validate_module(module)

    assert not result.ok
    assert any("parameter name" in message for message in _messages(result))


def test_shared_parameter_name_with_divergent_descriptions_is_warning():
    module = _module(
        [
            _operation(
                "op-1",
                "Meters - List",
                path=["meters"],
                parameters=[
                    IACParameter(
                        id="p-1",
                        name="status",
                        type="string",
                        description="Filtra medidores pelo status",
                        required=False,
                        sensitive=False,
                        sample="active",
                    )
                ],
            ),
            _operation(
                "op-2",
                "Invoices - List",
                path=["invoices"],
                parameters=[
                    IACParameter(
                        id="p-2",
                        name="status",
                        type="string",
                        description="Filtra faturas pelo status",
                        required=False,
                        sensitive=False,
                        sample="paid",
                    )
                ],
            ),
        ]
    )
    # Both operations must reference the param so the bidirectional check passes.
    module = module.model_copy(
        update={
            "operations": [
                operation.model_copy(
                    update={
                        "request": operation.request.model_copy(
                            update={
                                "url": IACRequestUrl(
                                    path=list(operation.request.url.path),
                                    query=[{"key": "status", "value": "<>status</>"}],
                                )
                            }
                        )
                    }
                )
                for operation in module.operations
            ]
        }
    )

    result = validate_module(module)

    assert result.ok, _messages(result)
    shared = [w for w in result.warnings if "query" not in w.path]
    assert len(shared) == 1
    warning = shared[0]
    assert "status" in warning.message
    assert "Meters - List" in warning.message
    assert "Invoices - List" in warning.message


def test_secret_warnings_reach_validate_module_without_failing_it():
    leaky = IACParameter(
        id="p-api_key",
        name="api_key",
        type="string",
        description="desc",
        required=True,
        sensitive=True,
        sample="sk_live_51H8xQz9abcdEFGH",
    )
    module = _module(
        [
            _operation(
                "op-1",
                "Customers - Get customer",
                path=["customers", "<>api_key</>"],
                parameters=[leaky],
            )
        ]
    )

    result = validate_module(module)

    assert result.ok
    assert any(
        warning.path == "operations[0].parameters[0].sample"
        for warning in result.warnings
    )


def _op_with_query(*, url_query=(), request_query=()):
    return IACOperation(
        id="op-1",
        name="Charges - List",
        parameters=[
            IACParameter(
                id="p-1",
                name="limit",
                type="string",
                description="Page size",
                required=False,
                sensitive=False,
                sample="10",
            )
        ],
        request=IACRestRequest(
            method="GET",
            url=IACRequestUrl(
                path=["v1", "charges"],
                query=[IACQueryParam(key=k, value=v) for k, v in url_query],
            ),
            query=[IACQueryParam(key=k, value=v) for k, v in request_query],
        ),
    )


def _module_with(operation):
    return IACModule(
        id="m-1",
        name="Payments",
        type="rest",
        settings=IACModuleSettings(),
        operations=[operation],
    )


def test_legacy_url_query_warns_and_points_at_request_query():
    result = validate_module(
        _module_with(_op_with_query(url_query=[("limit", "<>limit</>")]))
    )

    assert result.ok is True
    messages = [w.message for w in result.warnings]
    assert any("request.query" in message for message in messages)
    paths = [w.path for w in result.warnings]
    assert "operations[0].request.url.query" in paths


def test_both_query_formats_on_one_operation_warn_about_duplication():
    result = validate_module(
        _module_with(
            _op_with_query(
                url_query=[("limit", "<>limit</>")],
                request_query=[("limit", "<>limit</>")],
            )
        )
    )

    assert result.ok is True
    assert any("twice" in w.message for w in result.warnings)


def test_request_query_alone_produces_no_query_warning():
    result = validate_module(
        _module_with(_op_with_query(request_query=[("limit", "<>limit</>")]))
    )

    assert [w for w in result.warnings if "query" in w.path] == []


LEGACY_MODULE_FOR_RULES = {
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


def test_unknown_parameter_type_is_an_error():
    result = validate_module(IACModule.model_validate(LEGACY_MODULE_FOR_RULES))

    assert result.ok is False
    assert any(
        "boolean" in error.message and error.path.endswith(".type")
        for error in result.errors
    )


def test_empty_url_path_is_an_error():
    result = validate_module(IACModule.model_validate(LEGACY_MODULE_FOR_RULES))

    assert any(
        error.path == "operations[0].request.url.path" for error in result.errors
    )


def test_camel_case_parameter_name_still_errors_from_the_validator():
    result = validate_module(IACModule.model_validate(LEGACY_MODULE_FOR_RULES))

    assert any("snake_case" in error.message for error in result.errors)


def test_known_type_and_non_empty_path_produce_no_such_errors():
    module = IACModule.model_validate(
        {
            "id": "m1",
            "name": "Clean",
            "type": "rest",
            "settings": {"authentication_type": "bearer-token"},
            "operations": [
                {
                    "id": "op-1",
                    "name": "Clean op",
                    "request": {"method": "GET", "url": {"path": ["v1", "things"]}},
                    "parameters": [],
                }
            ],
        }
    )

    paths = [error.path for error in validate_module(module).errors]

    assert "operations[0].request.url.path" not in paths


def _op_with(request: IACRestRequest, *, name="Op", parameters=()) -> IACOperation:
    return IACOperation(
        id="op-1", name=name, parameters=list(parameters), request=request
    )


def test_literal_placeholder_left_in_a_path_segment_is_an_error():
    module = _module_with(
        _op_with(
            IACRestRequest(
                method="GET",
                url=IACRequestUrl(path=["2010-04-01", "Calls", "{Sid}.json"]),
            )
        )
    )

    result = validate_module(module)

    assert result.ok is False
    assert any(
        error.path == "operations[0].request.url.path[2]"
        and "{Sid}.json" in error.message
        for error in result.errors
    )


def test_a_composite_placeholder_with_a_suffix_is_caught_too():
    module = _module_with(
        _op_with(
            IACRestRequest(
                method="POST",
                url=IACRequestUrl(path=["api", "v2", "{name}:set-tags"]),
            )
        )
    )

    assert validate_module(module).ok is False


def test_a_properly_parameterized_path_is_clean():
    module = _module_with(
        _op_with(
            IACRestRequest(
                method="GET",
                url=IACRequestUrl(path=["v1", "things", "<>thing_id</>"]),
            ),
            parameters=[
                IACParameter(
                    id="p1",
                    name="thing_id",
                    type="string",
                    description="Id",
                    required=True,
                    sensitive=False,
                    sample="1",
                )
            ],
        )
    )

    paths = [error.path for error in validate_module(module).errors]

    assert not any(path.startswith("operations[0].request.url.path[") for path in paths)


def test_a_write_verb_with_no_body_reference_warns_but_does_not_block():
    module = _module_with(
        _op_with(
            IACRestRequest(method="POST", url=IACRequestUrl(path=["v1", "things"]))
        )
    )

    result = validate_module(module)

    assert result.ok is True
    assert any("body" in warning.message for warning in result.warnings)


def test_a_write_verb_with_a_body_reference_is_clean():
    module = _module_with(
        _op_with(
            IACRestRequest(
                method="POST",
                url=IACRequestUrl(path=["v1", "things"]),
                body=IACRequestBody(mode="raw", raw="<>payload</>"),
            ),
            parameters=[
                IACParameter(
                    id="p1",
                    name="payload",
                    type="object",
                    description="Body",
                    required=True,
                    sensitive=False,
                    sample="{}",
                )
            ],
        )
    )

    assert [w for w in validate_module(module).warnings if "body" in w.message] == []


def test_a_get_with_no_body_is_never_warned_about():
    module = _module_with(
        _op_with(IACRestRequest(method="GET", url=IACRequestUrl(path=["v1", "things"])))
    )

    assert [w for w in validate_module(module).warnings if "body" in w.message] == []


def test_content_type_declared_by_hand_on_a_multipart_operation_warns():
    module = _module_with(
        _op_with(
            IACRestRequest(
                method="POST",
                url=IACRequestUrl(path=["v3", "lists", "import"]),
                header=[
                    IACRequestHeader(key="content-type", value="<>content_type</>")
                ],
                body=IACRequestBody(
                    mode="raw", raw="file:<>file</>:mime:text/csv:list.csv"
                ),
            ),
            parameters=[
                IACParameter(
                    id="p1",
                    name="content_type",
                    type="string",
                    description="CT",
                    required=True,
                    sensitive=False,
                    sample="text/csv",
                ),
                IACParameter(
                    id="p2",
                    name="file",
                    type="string",
                    description="File",
                    required=True,
                    sensitive=False,
                    sample="list.csv",
                ),
            ],
        )
    )

    result = validate_module(module)

    assert any("Content-Type" in warning.message for warning in result.warnings)


def test_content_type_on_a_json_operation_is_not_warned_about():
    module = _module_with(
        _op_with(
            IACRestRequest(
                method="POST",
                url=IACRequestUrl(path=["v1", "things"]),
                header=[IACRequestHeader(key="Content-Type", value="application/json")],
                body=IACRequestBody(mode="raw", raw="<>payload</>"),
            ),
            parameters=[
                IACParameter(
                    id="p1",
                    name="payload",
                    type="object",
                    description="Body",
                    required=True,
                    sensitive=False,
                    sample="{}",
                )
            ],
        )
    )

    assert [
        w for w in validate_module(module).warnings if "Content-Type" in w.message
    ] == []


def _markup_module(description: str, parameter_description: str) -> IACModule:
    operation = _operation(
        "op-1",
        "Customers - Get customer",
        path=["customers", "<>customer_id</>"],
        parameters=[_param("customer_id", parameter_description)],
    ).model_copy(update={"description": description})
    return _module([operation])


def test_markup_in_a_description_is_a_warning_not_an_error():
    result = validate_module(
        _markup_module("Lista os widgets <b>ativos</b>.", "Filtra por **status**.")
    )

    paths = [warning.path for warning in result.warnings]
    assert result.ok
    assert "operations[0].description" in paths
    assert "operations[0].parameters[0].description" in paths


def test_plain_prose_raises_no_markup_warning():
    result = validate_module(
        _markup_module("Lista os widgets ativos.", "Filtra faturas pelo status.")
    )

    assert [warning.path for warning in result.warnings] == []


def _module_with_operation(*, body_raw: str, headers=(), query=()) -> IACModule:
    """POST operation whose body, headers and query come from the arguments."""
    return _module_with(
        _op_with(
            IACRestRequest(
                method="POST",
                url=IACRequestUrl(path=["v1", "things"]),
                header=[IACRequestHeader(**header) for header in headers],
                query=[IACQueryParam(**item) for item in query],
                body=IACRequestBody(mode="raw", raw=body_raw),
            )
        )
    )


def test_content_type_on_a_multipart_body_warns_whatever_the_field_is_called():
    module = _module_with_operation(
        body_raw="document:<>document</>\nnote:<>note</>",
        headers=[{"key": "Content-Type", "value": "multipart/form-data"}],
    )

    result = validate_module(module)

    assert any("multipart" in warning.message for warning in result.warnings)


def test_a_query_key_named_content_type_is_not_a_multipart_warning():
    module = _module_with_operation(
        body_raw="document:<>document</>",
        query=[{"key": "content-type", "value": "json"}],
    )

    result = validate_module(module)

    assert not any("multipart" in warning.message for warning in result.warnings)


def test_a_json_body_is_not_read_as_multipart():
    module = _module_with_operation(
        body_raw='{"status":"<>new_status</>"}',
        headers=[{"key": "Content-Type", "value": "application/json"}],
    )

    result = validate_module(module)

    assert not any("multipart" in warning.message for warning in result.warnings)
