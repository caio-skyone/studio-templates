import pytest
from fixtures.spec_stripe_like import CONFIG, SPEC

from studio_iac.iac.rules import PARAM_REF_RE, validate_module
from studio_iac.openapi.config import ConnectorConfig, load_config
from studio_iac.openapi.emit import build_module, root_server_segments
from studio_iac.openapi.errors import (
    OperationKeyCollision,
    OperationNameCollision,
)
from studio_iac.openapi.shape import operation_key


@pytest.fixture
def result():
    return build_module(SPEC, load_config(CONFIG, "config.json"), module_id="m-1")


def _operation(result, name: str):
    return next(op for op in result.module.operations if op.name == name)


def test_generated_module_passes_the_offline_validator(result):
    validation = validate_module(result.module)

    assert validation.ok, [error.message for error in validation.errors]


def test_operation_names_follow_domain_dash_summary(result):
    names = {op.name for op in result.module.operations}

    assert "Customers - List customers" in names
    assert "Payment Intents - Retrieve payment intent" in names


def test_same_generic_placeholder_yields_distinct_names(result):
    payment = _operation(result, "Payment Intents - Retrieve payment intent")
    setup = _operation(result, "Setup Intents - Retrieve setup intent")

    assert payment.request.url.path == [
        "v1",
        "payment_intents",
        "<>payment_intent_id</>",
    ]
    assert setup.request.url.path == ["v1", "setup_intents", "<>setup_intent_id</>"]


def test_specific_placeholder_keeps_the_spec_name(result):
    operation = _operation(result, "Customers - Retrieve customer")

    assert operation.request.url.path == ["v1", "customers", "<>customer</>"]


def test_irregular_plural_and_singular_override(result):
    person = _operation(result, "Accounts - Retrieve person")
    balance = _operation(result, "Balance - Retrieve balance transaction")

    assert person.request.url.path[-1] == "<>person_id</>"
    assert balance.request.url.path[-1] == "<>balance_transaction_id</>"


def test_excluded_alias_is_absent_and_recorded_with_its_reason(result):
    paths = [op.request.url.path for op in result.module.operations]

    assert not any("persons" in segment for path in paths for segment in path)
    reasons = {entry["key"]: entry["reason"] for entry in result.report.excluded}
    assert reasons["accounts.persons"] == "alias exato de accounts.people"


def test_expand_query_key_gets_bracket_suffix(result):
    operation = _operation(result, "Customers - List customers")
    keys = {param.key for param in operation.request.query}

    assert "expand[]" in keys
    assert "limit" in keys


def test_deep_object_query_param_is_flagged_in_the_worklist(result):
    entry = next(item for item in result.worklist.parameters if item.name == "created")

    assert entry.note is not None
    assert "key" in entry.note.lower()


def test_urlencoded_post_gets_one_string_body_param(result):
    operation = _operation(result, "Customers - Create customer")

    assert operation.request.body.raw == "<>body</>"
    body_param = next(p for p in operation.parameters if p.name == "body")
    assert body_param.type == "string"


def test_multipart_operation_becomes_full_url_with_host_first(result):
    operation = _operation(result, "Files - Create file")

    assert operation.request.url_type == "full-url"
    assert operation.request.url.path[0] == "https://files.stripe.com"
    assert operation.request.body.raw == "file:<>file</>\npurpose:<>purpose</>"
    assert not any(p.name == "note" for p in operation.parameters)


def test_get_operations_carry_no_body(result):
    operation = _operation(result, "Customers - List customers")

    assert operation.request.body.raw == ""


def test_cross_cutting_headers_respect_the_method_filter(result):
    listing = _operation(result, "Customers - List customers")
    creating = _operation(result, "Customers - Create customer")

    assert [header.key for header in listing.request.header] == ["Stripe-Version"]
    assert {header.key for header in creating.request.header} == {
        "Stripe-Version",
        "Idempotency-Key",
        # The body plan owns Content-Type and emits it for every non-multipart body.
        "Content-Type",
    }


def test_worklist_collapses_parameters_by_name(result):
    names = [entry.name for entry in result.worklist.parameters]

    assert len(names) == len(set(names))
    limit = next(entry for entry in result.worklist.parameters if entry.name == "limit")
    assert limit.source_en == "A limit on the number of objects."


def test_worklist_records_every_domain_a_shared_name_appears_in(result):
    entry = next(
        item for item in result.worklist.parameters if item.name == "stripe_version"
    )

    assert len(entry.domains) > 1
    assert entry.note is not None


def test_worklist_operations_are_keyed_uniquely(result):
    keys = [entry.op_key for entry in result.worklist.operations]

    assert len(keys) == len(set(keys))
    assert "customers.post" in keys


def test_report_counts_operations_per_block(result):
    assert result.report.blocks["core"] == 3
    assert result.report.blocks["ops"] == 1


def test_colliding_operation_names_abort_before_anything_is_produced():
    spec = {
        "paths": {
            "/v1/customers/{customer}/cards": {"get": {"summary": "List sources"}},
            "/v1/customers/{customer}/sources": {"get": {"summary": "List sources"}},
        }
    }
    config = load_config(
        {
            "module": {"name": "Stripe", "strip_path_prefix": ["v1"]},
            "include_roots": ["customers"],
            "domains": {
                "customers.cards": {"domain": "Customers"},
                "customers.sources": {"domain": "Customers"},
            },
        },
        "config.json",
    )

    with pytest.raises(OperationNameCollision) as excinfo:
        build_module(spec, config, module_id="m-1")

    assert "Customers - List sources" in str(excinfo.value)
    assert "exclude" in str(excinfo.value)


def test_required_spec_header_becomes_a_parameter(result):
    charges = _operation(result, "Charges - List charges")

    header = next(h for h in charges.request.header if h.key == "X-Required-Header")
    assert header.value == "<>x_required_header</>"
    param = next(p for p in charges.parameters if p.name == "x_required_header")
    assert param.required is True


def test_optional_spec_header_is_skipped_and_recorded(result):
    charges = _operation(result, "Charges - List charges")

    assert not any(h.key == "X-Optional-Header" for h in charges.request.header)
    entries = [
        entry
        for entry in result.report.skipped_headers
        if entry["header"] == "X-Optional-Header"
    ]
    assert entries
    assert "optional" in entries[0]["reason"].lower()


def test_auth_header_is_skipped_by_name_heuristic(result):
    charges = _operation(result, "Charges - List charges")

    assert not any(h.key == "Authorization" for h in charges.request.header)
    entries = [
        entry
        for entry in result.report.skipped_headers
        if entry["header"] == "Authorization"
    ]
    assert entries
    assert "connected account" in entries[0]["reason"].lower()


def test_config_can_rescue_a_header_the_heuristic_would_skip(result):
    charges = _operation(result, "Charges - List charges")

    assert any(h.key == "token" for h in charges.request.header)
    assert not any(
        entry["header"] == "token" for entry in result.report.skipped_headers
    )


def test_config_headers_are_emitted_regardless_of_being_optional(result):
    listing = _operation(result, "Customers - List customers")
    creating = _operation(result, "Customers - Create customer")

    assert any(header.key == "Stripe-Version" for header in listing.request.header)
    assert any(header.key == "Idempotency-Key" for header in creating.request.header)


def test_query_parameters_land_in_request_query_not_url_query(result):
    with_query = [
        op
        for op in result.module.operations
        if op.request.query or op.request.url.query
    ]

    assert with_query, "fixture must contain at least one query parameter"
    for operation in with_query:
        assert operation.request.url.query == []
        assert all(item.enabled is True for item in operation.request.query)


def test_root_server_path_becomes_literal_leading_segments():
    spec = {
        "servers": [{"url": "https://www.zohoapis.com/workdrive"}],
        "paths": {"/api/v1/files": {"get": {"summary": "List files"}}},
    }
    config = load_config(
        {"module": {"name": "WorkDrive"}, "include_roots": ["api"]}, "config.json"
    )

    result = build_module(spec, config, module_id="m-1")
    operation = result.module.operations[0]

    assert operation.request.url.path == ["workdrive", "api", "v1", "files"]
    assert operation.request.url_type == "base-url"
    assert result.report.server_prefix == ["workdrive"]


def test_operation_level_server_still_wins_as_full_url():
    spec = {
        "servers": [{"url": "https://www.zohoapis.com/workdrive"}],
        "paths": {
            "/api/v1/files": {
                "get": {
                    "summary": "List files",
                    "servers": [{"url": "https://upload.zoho.com"}],
                }
            }
        },
    }
    config = load_config(
        {"module": {"name": "WorkDrive"}, "include_roots": ["api"]}, "config.json"
    )

    operation = build_module(spec, config, module_id="m-1").module.operations[0]

    assert operation.request.url_type == "full-url"
    assert operation.request.url.path[0] == "https://upload.zoho.com"


def test_root_server_without_a_path_adds_nothing():
    assert root_server_segments({"servers": [{"url": "https://api.stripe.com"}]}) == []
    assert root_server_segments({"servers": [{"url": "https://api.stripe.com/"}]}) == []


def test_templated_root_server_path_is_ignored():
    assert (
        root_server_segments({"servers": [{"url": "https://{host}/{basePath}"}]}) == []
    )


_MAILGUN_SPEC = {
    "paths": {
        "/v3/domains/{name}/ips/{ip}": {
            "get": {
                "summary": "Get domain ip",
                "parameters": [
                    {"name": "ip", "in": "query", "schema": {"type": "string"}}
                ],
            }
        }
    }
}


def _mailgun_config():
    return load_config(
        {"module": {"name": "Mailgun"}, "include_roots": ["v3"]}, "config.json"
    )


def test_query_param_colliding_with_a_path_param_is_renamed_keeping_the_wire_key():
    result = build_module(_MAILGUN_SPEC, _mailgun_config(), module_id="m-1")
    operation = result.module.operations[0]

    names = [parameter.name for parameter in operation.parameters]
    assert names == ["name", "ip", "ip_query"]
    assert [(q.key, q.value) for q in operation.request.query] == [
        ("ip", "<>ip_query</>")
    ]
    assert result.report.renamed_params == [
        {
            "operation_key": operation_key("/v3/domains/{name}/ips/{ip}", "GET", []),
            "from": "ip",
            "to": "ip_query",
            "kind": "query",
        }
    ]


def test_generated_module_with_a_renamed_parameter_still_validates():
    validation = validate_module(
        build_module(_MAILGUN_SPEC, _mailgun_config(), module_id="m-1").module
    )

    assert validation.ok, [error.message for error in validation.errors]


def test_operation_key_duplicate_aborts_with_the_report_attached(monkeypatch):
    """Belt and braces: if the key scheme ever collides again, it must not pass."""
    from studio_iac.openapi import shape

    monkeypatch.setattr(shape, "operation_key", lambda path, method, prefix: "same.get")
    spec = {
        "paths": {
            "/v1/a": {"get": {"summary": "A"}},
            "/v1/b": {"get": {"summary": "B"}},
        }
    }
    config = load_config(
        {"module": {"name": "X"}, "include_roots": ["v1"]}, "config.json"
    )

    with pytest.raises(OperationKeyCollision) as excinfo:
        build_module(spec, config, module_id="m-1")

    assert excinfo.value.report is not None
    assert excinfo.value.report["included"] == 2


def test_operation_name_collision_carries_the_report():
    spec = {
        "paths": {
            "/v1/accounts/persons": {"get": {"summary": "List people"}},
            "/v1/accounts/people": {"get": {"summary": "List people"}},
        }
    }
    config = load_config(
        {
            "module": {"name": "X", "strip_path_prefix": ["v1"]},
            "include_roots": ["accounts"],
        },
        "config.json",
    )

    with pytest.raises(OperationNameCollision) as excinfo:
        build_module(spec, config, module_id="m-1")

    assert excinfo.value.report is not None
    assert "excluded" in excinfo.value.report


def _content_type_headers(operation):
    return [
        header.value
        for header in operation.request.header
        if header.key.lower() == "content-type"
    ]


def _built(spec, roots=("v1",)):
    config = load_config(
        {"module": {"name": "X"}, "include_roots": list(roots)}, "config.json"
    )
    return build_module(spec, config, module_id="m-1").module.operations[0]


def test_urlencoded_body_emits_the_content_type_header():
    spec = {
        "paths": {
            "/v1/charges": {
                "post": {
                    "summary": "Create charge",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"amount": {"type": "integer"}},
                                }
                            }
                        },
                    },
                }
            }
        }
    }

    assert _content_type_headers(_built(spec)) == ["application/x-www-form-urlencoded"]


def test_json_body_emits_the_content_type_header():
    spec = {
        "paths": {
            "/v1/things": {
                "post": {
                    "summary": "Create thing",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"a": {"type": "string"}},
                                }
                            }
                        }
                    },
                }
            }
        }
    }

    assert _content_type_headers(_built(spec)) == ["application/json"]


def test_multipart_body_never_emits_a_content_type_header():
    spec = {
        "paths": {
            "/v1/files": {
                "post": {
                    "summary": "Upload file",
                    "parameters": [
                        {
                            "name": "Content-Type",
                            "in": "header",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"file": {"type": "string"}},
                                    "required": ["file"],
                                }
                            }
                        }
                    },
                }
            }
        }
    }
    operation = _built(spec)

    assert _content_type_headers(operation) == []
    assert "content_type" not in [p.name for p in operation.parameters]


def test_get_operation_emits_no_content_type_header():
    spec = {"paths": {"/v1/things": {"get": {"summary": "List things"}}}}

    assert _content_type_headers(_built(spec)) == []


def test_required_config_header_produces_a_required_parameter():
    spec = {"paths": {"/api/tickets": {"get": {"summary": "List tickets"}}}}
    config = load_config(
        {
            "module": {"name": "Zoho Desk"},
            "include_roots": ["api"],
            "headers": [{"key": "orgId", "param": "org_id", "required": True}],
        },
        "config.json",
    )

    operation = build_module(spec, config, module_id="m-1").module.operations[0]
    parameter = next(p for p in operation.parameters if p.name == "org_id")

    assert parameter.required is True


def test_query_param_sample_comes_from_the_enum():
    spec = {
        "paths": {
            "/v1/things": {
                "get": {
                    "summary": "List things",
                    "parameters": [
                        {
                            "name": "order",
                            "in": "query",
                            "schema": {"type": "string", "enum": ["asc", "desc"]},
                        }
                    ],
                }
            }
        }
    }
    operation = _built(spec)
    parameter = next(p for p in operation.parameters if p.name == "order")

    assert parameter.sample == "asc"


def test_path_param_sample_comes_from_its_spec_schema():
    spec = {
        "paths": {
            "/v1/things/{thing}": {
                "get": {
                    "summary": "Get thing",
                    "parameters": [
                        {
                            "name": "thing",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string", "example": "thg_42"},
                        }
                    ],
                }
            }
        }
    }
    operation = _built(spec)
    parameter = next(p for p in operation.parameters if p.name == "thing")

    assert parameter.sample == "thg_42"


def test_report_counts_parameters_left_without_a_sample():
    spec = {
        "paths": {
            "/v1/things": {
                "get": {
                    "summary": "List things",
                    "parameters": [
                        {"name": "q", "in": "query", "schema": {"type": "string"}},
                        {
                            "name": "order",
                            "in": "query",
                            "schema": {"type": "string", "enum": ["asc"]},
                        },
                    ],
                }
            }
        }
    }
    config = load_config(
        {"module": {"name": "X"}, "include_roots": ["v1"]}, "config.json"
    )

    report = build_module(spec, config, module_id="m-1").report

    assert report.empty_samples == 1


def test_operation_without_summary_falls_back_to_the_operation_id():
    spec = {"paths": {"/v1/senders": {"post": {"operationId": "CreateAlphaSender"}}}}
    config = load_config(
        {"module": {"name": "T"}, "include_roots": ["v1"]}, "config.json"
    )

    result = build_module(spec, config, module_id="m-1")

    assert result.module.operations[0].name == "V1 - Create alpha sender"
    assert result.report.name_fallbacks == [
        {"operation_key": "v1.senders.post", "level": "operation_id"}
    ]


def test_operation_without_summary_or_operation_id_falls_back_to_the_key():
    spec = {"paths": {"/v1/senders": {"post": {}}}}
    config = load_config(
        {"module": {"name": "T"}, "include_roots": ["v1"]}, "config.json"
    )

    result = build_module(spec, config, module_id="m-1")

    assert result.report.name_fallbacks == [
        {"operation_key": "v1.senders.post", "level": "operation_key"}
    ]


_MARKUP_SPEC = {
    "openapi": "3.0.0",
    "paths": {
        "/widgets": {
            "get": {
                "summary": "List widgets",
                "description": "<p>Lists the <b>&quot;active&quot;</b> widgets.</p>",
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "description": "See [the docs](https://x.dev/s).",
                        "schema": {"type": "string"},
                    }
                ],
            }
        }
    },
}
_MARKUP_CONFIG = {"module": {"name": "Widgets"}, "include_roots": ["widgets"]}


def test_worklist_source_en_is_plain_text():
    result = build_module(
        _MARKUP_SPEC, load_config(_MARKUP_CONFIG, "config.json"), module_id="m-1"
    )

    operation_entry = result.worklist.operations[0]
    parameter_entry = next(
        entry for entry in result.worklist.parameters if entry.name == "status"
    )

    assert operation_entry.source_en == 'Lists the "active" widgets.'
    assert parameter_entry.source_en == "See the docs."


_EXAMPLE_SPEC = {
    "openapi": "3.0.0",
    "paths": {
        "/widgets/{widget_id}": {
            "get": {
                "summary": "Retrieve widget",
                "parameters": [
                    {
                        "name": "widget_id",
                        "in": "path",
                        "required": True,
                        "example": "wid_42",
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "status",
                        "in": "query",
                        "example": "active",
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "x-tenant",
                        "in": "header",
                        "required": True,
                        "examples": {"one": {"value": "tenant_7"}},
                        "schema": {"type": "string"},
                    },
                ],
            }
        }
    },
}
_EXAMPLE_CONFIG = {"module": {"name": "Widgets"}, "include_roots": ["widgets"]}


def test_parameter_level_example_becomes_the_sample():
    result = build_module(
        _EXAMPLE_SPEC, load_config(_EXAMPLE_CONFIG, "config.json"), module_id="m-1"
    )

    operation = result.module.operations[0]
    samples = {parameter.name: parameter.sample for parameter in operation.parameters}

    assert samples["widget_id"] == "wid_42"
    assert samples["status"] == "active"
    assert samples["x_tenant"] == "tenant_7"


_HEADER_CONFIG = {
    "module": {"name": "Widgets"},
    "include_roots": ["widgets"],
    "headers": [
        {"key": "orgId", "param": "org_id", "required": True, "sample": "123456789"}
    ],
}


def test_config_header_sample_reaches_the_parameter():
    result = build_module(
        _EXAMPLE_SPEC, load_config(_HEADER_CONFIG, "config.json"), module_id="m-1"
    )

    parameter = next(
        item for item in result.module.operations[0].parameters if item.name == "org_id"
    )

    assert parameter.sample == "123456789"
    assert parameter.required


_BODY_SPEC = {
    "openapi": "3.0.0",
    "paths": {
        "/widgets": {
            "post": {
                "summary": "Create widget",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string", "example": "Widget"}
                                },
                            }
                        }
                    },
                },
            }
        }
    },
}


def test_worklist_ships_the_derived_body_sample():
    result = build_module(
        _BODY_SPEC, load_config(_EXAMPLE_CONFIG, "config.json"), module_id="m-1"
    )

    entry = result.worklist.operations[0]
    body = next(
        parameter
        for parameter in result.module.operations[0].parameters
        if parameter.name == "body"
    )

    assert entry.body_sample == '{"name":"Widget"}'
    assert body.sample == '{"name":"Widget"}'


def test_two_path_placeholders_colliding_on_one_name_stay_referenced():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "servers": [{"url": "https://api.example.com"}],
        "paths": {
            "/items/{id}/items/{itemId}": {
                "get": {
                    "operationId": "getSub",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "itemId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {},
                }
            }
        },
    }
    config = ConnectorConfig.model_validate(
        {
            "module": {
                "name": "T",
                "description": "d",
                "authentication_type": "bearer-token",
            },
            "include_roots": ["items"],
        }
    )

    operation = build_module(spec, config, module_id="m1").module.operations[0]

    declared = {parameter.name for parameter in operation.parameters}
    referenced = set(PARAM_REF_RE.findall("/".join(operation.request.url.path)))
    assert referenced == declared
    assert len(operation.request.url.path) == len(set(operation.request.url.path)) or (
        operation.request.url.path.count("<>item_id</>") == 1
    )


def test_cascading_body_renames_do_not_clobber_each_other():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "T", "version": "1"},
        "servers": [{"url": "https://api.example.com"}],
        "paths": {
            "/things": {
                "post": {
                    "operationId": "createThing",
                    "parameters": [
                        {"name": "a", "in": "query", "schema": {"type": "string"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["a", "a_body"],
                                    "properties": {
                                        "a": {"type": "string"},
                                        "a_body": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {},
                }
            }
        },
    }
    config = ConnectorConfig.model_validate(
        {
            "module": {
                "name": "T",
                "description": "d",
                "authentication_type": "bearer-token",
            },
            "include_roots": ["things"],
        }
    )

    operation = build_module(spec, config, module_id="m1").module.operations[0]

    declared = {parameter.name for parameter in operation.parameters}
    referenced = set(PARAM_REF_RE.findall(operation.request.body.raw))
    referenced |= {
        ref
        for item in operation.request.query
        for ref in PARAM_REF_RE.findall(item.value)
    }
    assert declared == referenced
