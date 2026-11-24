from studio_iac.openapi.config import load_config
from studio_iac.openapi.shape import (
    domain_for,
    has_placeholder,
    iter_spec_operations,
    operation_key,
    placeholders_in,
    select_operations,
    shape_key,
)

_SPEC = {
    "paths": {
        "/v1/customers": {
            "get": {"summary": "List customers"},
            "post": {"summary": "Create customer"},
        },
        "/v1/customers/{customer}/tax_ids": {"get": {"summary": "List tax ids"}},
        "/v1/accounts/{account}/persons": {"get": {"summary": "List persons"}},
        "/v1/files": {"post": {"summary": "Create file"}},
        "/v1/RESOURCE": {"get": {"summary": "Placeholder"}},
    }
}


def _config(**overrides) -> object:
    payload = {
        "module": {"name": "Stripe", "strip_path_prefix": ["v1"]},
        "include_roots": ["customers", "accounts"],
        **overrides,
    }
    return load_config(payload, "config.json")


def test_shape_key_strips_prefix_and_placeholders():
    assert shape_key("/v1/customers/{customer}/tax_ids", ["v1"]) == "customers.tax_ids"


def test_shape_key_without_prefix_config_keeps_every_segment():
    assert shape_key("/v1/customers", []) == "v1.customers"


def test_operation_key_appends_lowercase_method():
    assert operation_key("/v1/customers", "POST", ["v1"]) == "customers.post"


def test_operation_key_marks_item_routes_to_avoid_colliding_with_the_collection():
    collection = operation_key("/v1/customers", "GET", ["v1"])
    item = operation_key("/v1/customers/{customer}", "GET", ["v1"])

    assert collection == "customers.get"
    assert item == "customers.item.get"
    assert collection != item


def test_operation_key_marks_deeper_item_routes_too():
    key = operation_key("/v1/accounts/{account}/people/{person}", "GET", ["v1"])

    assert key == "accounts.item.people.item.get"


def test_iter_spec_operations_yields_one_per_method():
    operations = iter_spec_operations(_SPEC, ["v1"])

    keys = {operation.operation_key for operation in operations}
    assert "customers.get" in keys
    assert "customers.post" in keys
    assert len(operations) == 6


def test_select_operations_filters_by_include_roots():
    selection = select_operations(_SPEC, _config())

    selected_keys = {operation.operation_key for operation in selection.selected}
    assert selected_keys == {
        "customers.get",
        "customers.post",
        "customers.item.tax_ids.get",
        "accounts.item.persons.get",
    }


def test_select_operations_records_exclusions_with_reason():
    config = _config(
        exclude=[{"key": "accounts.persons", "reason": "alias de accounts.people"}]
    )

    selection = select_operations(_SPEC, config)

    assert all(
        operation.shape_key != "accounts.persons" for operation in selection.selected
    )
    excluded = {operation.shape_key: reason for operation, reason in selection.excluded}
    assert excluded["accounts.persons"] == "alias de accounts.people"


def test_select_operations_reports_roots_outside_scope_as_excluded():
    selection = select_operations(_SPEC, _config())

    excluded_keys = {operation.shape_key for operation, _ in selection.excluded}
    assert "files" in excluded_keys
    assert "RESOURCE" in excluded_keys


def test_domain_for_uses_config_mapping_when_present():
    config = _config(
        domains={"customers.tax_ids": {"domain": "Customer Tax IDs", "block": "core"}}
    )
    operation = next(
        op
        for op in select_operations(_SPEC, config).selected
        if op.shape_key == "customers.tax_ids"
    )

    result = domain_for(operation, config)

    assert result.domain == "Customer Tax IDs"
    assert result.block == "core"


def test_domain_for_falls_back_to_titlecased_root():
    config = _config()
    operation = next(
        op
        for op in select_operations(_SPEC, config).selected
        if op.shape_key == "customers"
    )

    result = domain_for(operation, config)

    assert result.domain == "Customers"
    assert result.block == "default"


def test_domain_for_all_placeholder_path_falls_back_to_default():
    spec = {"paths": {"/v1/{id}": {"get": {"summary": "Placeholder-only path"}}}}
    [operation] = iter_spec_operations(spec, ["v1"])

    assert operation.shape_key == ""
    assert operation.root == ""

    result = domain_for(operation, None)

    assert result.domain == "Default"
    assert result.block == "default"


def test_iter_spec_operations_operation_inherits_shared_path_parameter():
    spec = {
        "paths": {
            "/v1/customers/{customer}": {
                "parameters": [{"name": "customer", "in": "path"}],
                "get": {"summary": "Get customer"},
            }
        }
    }

    [operation] = iter_spec_operations(spec, ["v1"])

    assert operation.parameters == ({"name": "customer", "in": "path"},)


def test_iter_spec_operations_merges_differently_named_parameters():
    spec = {
        "paths": {
            "/v1/customers/{customer}": {
                "parameters": [{"name": "customer", "in": "path"}],
                "get": {
                    "summary": "Get customer",
                    "parameters": [{"name": "expand", "in": "query"}],
                },
            }
        }
    }

    [operation] = iter_spec_operations(spec, ["v1"])

    assert set(
        (parameter["name"], parameter["in"]) for parameter in operation.parameters
    ) == {("customer", "path"), ("expand", "query")}
    assert len(operation.parameters) == 2


def test_iter_spec_operations_operation_parameter_overrides_shared_one():
    spec = {
        "paths": {
            "/v1/customers/{customer}": {
                "parameters": [
                    {"name": "customer", "in": "path", "description": "shared"}
                ],
                "get": {
                    "summary": "Get customer",
                    "parameters": [
                        {"name": "customer", "in": "path", "description": "own"}
                    ],
                },
            }
        }
    }

    [operation] = iter_spec_operations(spec, ["v1"])

    assert len(operation.parameters) == 1
    assert operation.parameters[0]["description"] == "own"


def test_iter_spec_operations_keeps_malformed_parameters_without_collapsing():
    spec = {
        "paths": {
            "/v1/customers": {
                "parameters": [{"description": "missing name and in, #1"}],
                "get": {
                    "summary": "List customers",
                    "parameters": [{"description": "missing name and in, #2"}],
                },
            }
        }
    }

    [operation] = iter_spec_operations(spec, ["v1"])

    assert len(operation.parameters) == 2
    descriptions = {parameter["description"] for parameter in operation.parameters}
    assert descriptions == {
        "missing name and in, #1",
        "missing name and in, #2",
    }


def test_has_placeholder_sees_composite_segments():
    assert has_placeholder("{Sid}.json")
    assert has_placeholder("{name}:set-tags")
    assert has_placeholder("v{version}")
    assert has_placeholder("{id}")
    assert not has_placeholder("Messages.json")


def test_placeholders_in_returns_every_name_in_order():
    assert placeholders_in("{a}-{b}") == ["a", "b"]
    assert placeholders_in("Messages.json") == []


def test_shape_key_drops_a_composite_segment_whole():
    collection = shape_key("/2010/Accounts/Messages", [])
    item = shape_key("/2010/Accounts/Messages/{Sid}.json", [])

    assert collection == item == "2010.Accounts.Messages"


def test_shape_key_drops_an_action_suffix_segment_too():
    assert shape_key("/api/v2/databases/{name}:set-tags", []) == "api.v2.databases"


def test_shape_key_drops_a_prefixed_placeholder_segment():
    assert (
        shape_key("/services/data/v{version}/sobjects", []) == "services.data.sobjects"
    )


def test_operation_key_keeps_the_literal_part_of_a_composite_segment():
    assert (
        operation_key("/Accounts/Messages/{Sid}.json", "GET", [])
        == "Accounts.Messages.item.json.get"
    )
    assert (
        operation_key("/databases/{name}:set-tags", "POST", [])
        == "databases.item.set-tags.post"
    )
    assert (
        operation_key("/data/v{version}/sobjects", "GET", [])
        == "data.v.item.sobjects.get"
    )


def test_operation_key_is_positional_so_placeholder_arity_never_collides():
    keys = {
        operation_key("/a/{x}", "GET", []),
        operation_key("/a/{x}/{y}", "GET", []),
        operation_key("/a/{x}/{y}/{z}", "GET", []),
    }

    assert keys == {"a.item.get", "a.item.item.get", "a.item.item.item.get"}


def test_operation_key_distinguishes_a_leading_placeholder_from_its_absence():
    assert operation_key("/v3/stats/total", "GET", []) != operation_key(
        "/v3/{domain}/stats/total", "GET", []
    )


def test_operation_key_of_a_plain_collection_is_unchanged():
    assert operation_key("/v1/customers", "POST", ["v1"]) == "customers.post"


def test_composite_fragment_never_leaks_the_join_separator():
    assert operation_key("/files/{id}.tar.gz", "GET", []) == "files.item.tar_gz.get"


_REF_SPEC = {
    "paths": {
        "/tickets": {
            "parameters": [{"$ref": "#/components/parameters/OrgId"}],
            "get": {
                "summary": "List tickets",
                "parameters": [{"$ref": "#/components/parameters/Limit"}],
            },
            "post": {
                "summary": "Create ticket",
                "requestBody": {"$ref": "#/components/requestBodies/Ticket"},
            },
        }
    },
    "components": {
        "parameters": {
            "OrgId": {
                "name": "orgId",
                "in": "header",
                "required": True,
                "schema": {"type": "string"},
            },
            "Limit": {"name": "limit", "in": "query", "schema": {"type": "integer"}},
        },
        "requestBodies": {
            "Ticket": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"subject": {"type": "string"}},
                        }
                    }
                },
            }
        },
    },
}


def test_referenced_parameters_are_resolved_into_the_operation():
    operations = {op.method: op for op in iter_spec_operations(_REF_SPEC, [])}

    listed = {(p.get("name"), p.get("in")) for p in operations["GET"].parameters}
    assert listed == {("orgId", "header"), ("limit", "query")}


def test_referenced_request_body_is_resolved_into_the_operation():
    operations = {op.method: op for op in iter_spec_operations(_REF_SPEC, [])}
    body = operations["POST"].request_body

    assert body is not None
    assert "application/json" in body["content"]
    assert body["required"] is True


def test_referenced_and_inline_parameters_merge_by_name_and_location():
    spec = {
        "paths": {
            "/t": {
                "parameters": [{"$ref": "#/components/parameters/Limit"}],
                "get": {
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ]
                },
            }
        },
        "components": _REF_SPEC["components"],
    }

    operation = iter_spec_operations(spec, [])[0]

    assert len(operation.parameters) == 1
    assert operation.parameters[0]["required"] is True
