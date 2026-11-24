from dataclasses import replace

from studio_iac.openapi.body import _skeleton_plan, plan_body
from studio_iac.openapi.config import BodyOverride
from studio_iac.openapi.shape import SpecOperation

_SPEC: dict = {"components": {"schemas": {}}}


def _operation(
    *,
    method: str = "POST",
    request_body: dict | None = None,
) -> SpecOperation:
    return SpecOperation(
        path="/v1/customers",
        method=method,
        summary="Create customer",
        description=None,
        parameters=(),
        request_body=request_body,
        servers=(),
        shape_key="customers",
        operation_key=f"customers.{method.lower()}",
    )


def _urlencoded(properties: dict, required: list[str] | None = None) -> dict:
    return {
        "content": {
            "application/x-www-form-urlencoded": {
                "schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required or [],
                }
            }
        }
    }


def test_get_with_a_request_body_produces_no_body():
    plan = plan_body(_SPEC, _operation(method="GET", request_body=_urlencoded({})))

    assert plan.raw == ""
    assert plan.parameters == ()
    assert plan.strategy == "none"


def test_delete_produces_no_body():
    plan = plan_body(
        _SPEC, _operation(method="DELETE", request_body=_urlencoded({"a": {}}))
    )

    assert plan.strategy == "none"


def test_missing_request_body_produces_no_body():
    plan = plan_body(_SPEC, _operation(request_body=None))

    assert plan.strategy == "none"


def test_urlencoded_becomes_one_string_parameter():
    plan = plan_body(
        _SPEC,
        _operation(request_body=_urlencoded({"name": {"type": "string"}})),
    )

    assert plan.raw == "<>body</>"
    assert len(plan.parameters) == 1
    assert plan.parameters[0].name == "body"
    assert plan.parameters[0].type == "string"
    assert plan.strategy == "single-string"


def test_json_becomes_one_object_parameter():
    request_body = {
        "content": {
            "application/json": {
                "schema": {"type": "object", "properties": {"a": {"type": "string"}}}
            }
        }
    }

    plan = plan_body(_SPEC, _operation(request_body=request_body))

    assert plan.raw == "<>body</>"
    assert plan.parameters[0].type == "object"
    assert plan.strategy == "single-object"


def test_multipart_emits_granular_lines_for_required_only():
    request_body = {
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string", "format": "binary"},
                        "purpose": {"type": "string"},
                        "optional_note": {"type": "string"},
                    },
                    "required": ["file", "purpose"],
                }
            }
        }
    }

    plan = plan_body(_SPEC, _operation(request_body=request_body))

    assert plan.strategy == "multipart-granular"
    assert plan.raw == "file:<>file</>\npurpose:<>purpose</>"
    assert [param.name for param in plan.parameters] == ["file", "purpose"]
    assert all(param.required for param in plan.parameters)


def test_multipart_never_declares_a_content_type_parameter():
    request_body = {
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {"file": {"type": "string"}},
                    "required": ["file"],
                }
            }
        }
    }

    plan = plan_body(_SPEC, _operation(request_body=request_body))

    assert all(param.name != "content_type" for param in plan.parameters), (
        "the boundary is set by the runtime; declaring Content-Type breaks it"
    )


def test_multipart_with_no_required_properties_keeps_multipart_strategy():
    """No required properties still means a real multipart requestBody exists.

    Collapsing this to strategy "none" would silently drop an operation that
    genuinely needs a multipart body — the report would then lie about what
    was decided. Zero granular lines is a legitimate outcome; losing the
    fact that the body was multipart is not.
    """
    request_body = {
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {"optional_note": {"type": "string"}},
                    "required": [],
                }
            }
        }
    }

    plan = plan_body(_SPEC, _operation(request_body=request_body))

    assert plan.strategy == "multipart-granular"
    assert plan.content_type == "multipart/form-data"
    assert plan.parameters == ()
    assert plan.raw == ""


def test_urlencoded_required_body_is_required_even_without_required_properties():
    """`required` on the body param must read `requestBody.required`.

    A body can be mandatory even when its schema marks none of its
    properties as required — that's a fact about the request, not about
    the schema's own `required` list.
    """
    request_body = _urlencoded({"name": {"type": "string"}}, required=[])
    request_body["required"] = True

    plan = plan_body(_SPEC, _operation(request_body=request_body))

    assert plan.parameters[0].required is True


def test_urlencoded_body_without_required_flag_is_optional_even_if_property_is():
    """Regression guard: a required *property* must not make the body itself
    required. `requestBody.required` defaults to False when omitted.
    """
    request_body = _urlencoded({"name": {"type": "string"}}, required=["name"])

    plan = plan_body(_SPEC, _operation(request_body=request_body))

    assert plan.parameters[0].required is False


def test_unrecognized_content_type_falls_back_to_a_single_string_parameter():
    request_body = {
        "content": {
            "text/plain": {
                "schema": {
                    "type": "object",
                    "properties": {"note": {"type": "string"}},
                }
            }
        }
    }

    plan = plan_body(_SPEC, _operation(request_body=request_body))

    assert len(plan.parameters) == 1
    assert plan.parameters[0].type == "string"
    assert plan.content_type == "text/plain"


def test_nested_properties_are_never_expanded():
    request_body = _urlencoded(
        {
            "payment_method_options": {
                "type": "object",
                "properties": {"us_bank_account": {"type": "object"}},
            }
        }
    )

    plan = plan_body(_SPEC, _operation(request_body=request_body))

    assert [param.name for param in plan.parameters] == ["body"]


def test_skeleton_override_replaces_the_generated_body():
    plan = plan_body(
        _SPEC,
        _operation(request_body=_urlencoded({"status": {"type": "string"}})),
        BodyOverride(mode="skeleton", raw='{"status": "<>new_status</>"}'),
    )

    assert plan.raw == '{"status": "<>new_status</>"}'
    assert [param.name for param in plan.parameters] == ["new_status"]
    assert plan.strategy == "skeleton"


def test_none_override_forces_no_body():
    plan = plan_body(
        _SPEC,
        _operation(request_body=_urlencoded({"a": {"type": "string"}})),
        BodyOverride(mode="none"),
    )

    assert plan.raw == ""
    assert plan.parameters == ()


def _operation_with_body(schema: dict, content_type: str = "application/json"):
    return SpecOperation(
        path="/things",
        method="POST",
        summary=None,
        description=None,
        parameters=(),
        request_body={"required": True, "content": {content_type: {"schema": schema}}},
        servers=(),
        shape_key="things",
        operation_key="things.post",
    )


def test_array_body_becomes_a_single_string_parameter():
    plan = plan_body(
        {}, _operation_with_body({"type": "array", "items": {"example": "tag"}})
    )

    assert plan.strategy == "single-string"
    assert plan.raw == "<>body</>"
    assert [p.name for p in plan.parameters] == ["body"]
    assert plan.parameters[0].type == "string"
    assert plan.parameters[0].sample == "tag"


def test_one_of_body_becomes_a_single_string_parameter_with_a_variant_sample():
    schema = {
        "oneOf": [
            {"type": "object", "example": {"action": "rename"}},
            {"type": "object", "example": {"action": "move"}},
        ]
    }

    plan = plan_body({}, _operation_with_body(schema))

    assert plan.strategy == "single-string"
    assert plan.parameters[0].sample == '{"action":"rename"}'


def test_object_with_only_an_example_becomes_a_single_object_parameter():
    schema = {"type": "object", "example": {"Name": "ACME", "Phone": "555"}}

    plan = plan_body({}, _operation_with_body(schema))

    assert plan.strategy == "single-object"
    assert plan.parameters[0].type == "object"
    assert plan.parameters[0].sample == '{"Name":"ACME","Phone":"555"}'


def test_all_of_parts_are_merged_before_deciding():
    schema = {
        "allOf": [
            {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
            {"type": "object", "properties": {"email": {"type": "string"}}},
        ]
    }

    plan = plan_body({}, _operation_with_body(schema, "multipart/form-data"))

    assert plan.strategy == "multipart-granular"
    assert [p.name for p in plan.parameters] == ["name"]


def test_absent_request_body_stays_none_with_no_reason():
    operation = _operation_with_body({"type": "object", "properties": {}})
    operation = replace(operation, request_body=None)

    plan = plan_body({}, operation)

    assert plan.strategy == "none"
    assert plan.reason is None


def test_unreadable_body_is_none_but_records_why():
    plan = plan_body({}, _operation_with_body({}))

    assert plan.strategy == "none"
    assert plan.reason is not None
    assert "schema" in plan.reason


def test_multipart_without_properties_is_none_with_a_reason():
    plan = plan_body(
        {}, _operation_with_body({"type": "array", "items": {}}, "multipart/form-data")
    )

    assert plan.strategy == "none"
    assert "multipart" in (plan.reason or "")


def _json_body(properties: dict, required: list[str] | None = None) -> dict:
    return {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required or [],
                }
            }
        },
    }


def test_json_body_with_properties_carries_a_derived_sample():
    operation = _operation(
        request_body=_json_body(
            {"name": {"type": "string", "example": "Widget"}}, ["name"]
        )
    )

    plan = plan_body(_SPEC, operation)

    assert plan.parameters[0].name == "body"
    assert plan.parameters[0].sample == '{"name":"Widget"}'


def test_urlencoded_body_gets_no_json_skeleton():
    operation = _operation(request_body=_urlencoded({"name": {"type": "string"}}))

    plan = plan_body(_SPEC, operation)

    assert plan.parameters[0].sample == ""


def test_allof_json_body_carries_a_derived_sample():
    operation = _operation(
        request_body={
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "allOf": [
                            {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string", "example": "Widget"}
                                },
                            },
                            {
                                "type": "object",
                                "properties": {"qty": {"type": "integer"}},
                            },
                        ]
                    }
                }
            },
        }
    )

    plan = plan_body(_SPEC, operation)

    assert plan.parameters[0].sample == '{"name":"Widget","qty":1}'


def _multipart_op(properties: dict, required: list[str]) -> SpecOperation:
    return _operation(
        request_body={
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": required,
                        "properties": properties,
                    }
                }
            },
        }
    )


def test_multipart_parameter_name_is_snake_case_and_the_key_stays_raw():
    plan = plan_body({}, _multipart_op({"fileName": {"type": "string"}}, ["fileName"]))

    assert [param.name for param in plan.parameters] == ["file_name"]
    assert plan.raw == "fileName:<>file_name</>"


def test_multipart_source_en_is_sanitized():
    plan = plan_body(
        {},
        _multipart_op(
            {"file": {"type": "string", "description": "The <b>file</b> &amp; more"}},
            ["file"],
        ),
    )

    assert plan.parameters[0].source_en == "The file & more"


def test_multipart_names_that_collide_after_snake_case_are_disambiguated():
    plan = plan_body(
        {},
        _multipart_op(
            {"fileName": {"type": "string"}, "file_name": {"type": "string"}},
            ["fileName", "file_name"],
        ),
    )

    assert [param.name for param in plan.parameters] == ["file_name", "file_name_2"]
    assert plan.raw == "fileName:<>file_name</>\nfile_name:<>file_name_2</>"


def test_json_with_a_charset_parameter_is_still_json():
    op = _operation(
        request_body={
            "required": True,
            "content": {
                "application/json; charset=utf-8": {
                    "schema": {
                        "type": "object",
                        "properties": {"a": {"type": "string"}},
                    }
                }
            },
        }
    )

    plan = plan_body({}, op)

    assert plan.content_type == "application/json"
    assert plan.parameters[0].type == "object"


def test_a_skeleton_override_declares_json_by_default():
    plan = _skeleton_plan(BodyOverride(mode="skeleton", raw='{"a":"<>a</>"}'))

    assert plan.content_type == "application/json"


def test_a_skeleton_override_can_declare_another_content_type():
    override = BodyOverride(
        mode="skeleton",
        raw="a=<>a</>",
        content_type="application/x-www-form-urlencoded",
    )

    assert _skeleton_plan(override).content_type == "application/x-www-form-urlencoded"
