from fixtures.spec_stripe_like import CONFIG, SPEC

from studio_iac.openapi.analyze import analyze_spec
from studio_iac.openapi.config import load_config

_DEEP_SPEC = {
    "paths": {
        "/v1/intents": {
            "post": {
                "summary": "Create",
                "requestBody": {
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "payment_method_options": {
                                        "type": "object",
                                        "properties": {
                                            "us_bank_account": {
                                                "type": "object",
                                                "properties": {
                                                    "financial_connections_filters_"
                                                    "account_subcategories_long_name": {
                                                        "type": "string"
                                                    },
                                                    "routing_number": {
                                                        "type": "string"
                                                    },
                                                },
                                            }
                                        },
                                    },
                                    "amount": {"type": "integer"},
                                },
                            }
                        }
                    }
                },
            }
        }
    }
}


def test_analysis_without_config_is_a_raw_survey():
    report = analyze_spec(SPEC, None)

    assert report.total_paths == 9
    assert report.total_operations == 10
    assert report.selected_operations == report.total_operations


def test_analysis_with_config_reports_the_post_filter_count():
    report = analyze_spec(SPEC, load_config(CONFIG, "config.json"))

    assert report.selected_operations < report.total_operations


def test_domain_rows_carry_operation_and_param_counts():
    report = analyze_spec(SPEC, load_config(CONFIG, "config.json"))

    by_domain = {row.domain: row for row in report.domains}
    assert by_domain["Customers"].operations == 3
    assert by_domain["Customers"].query_params == 3


def test_content_types_are_counted():
    report = analyze_spec(SPEC, load_config(CONFIG, "config.json"))

    assert report.content_types["application/x-www-form-urlencoded"] == 1
    assert report.content_types["multipart/form-data"] == 1


def test_depth_table_has_one_row_per_level():
    report = analyze_spec(_DEEP_SPEC, None)

    levels = [row.level for row in report.depth]
    assert levels == ["1", "2", "3", "recursive"]


def test_depth_table_shows_params_growing_with_depth():
    report = analyze_spec(_DEEP_SPEC, None)

    by_level = {row.level: row for row in report.depth}
    assert by_level["1"].body_params == 2
    assert by_level["3"].body_params > by_level["1"].body_params


def test_depth_table_counts_names_over_the_fifty_char_limit():
    report = analyze_spec(_DEEP_SPEC, None)

    by_level = {row.level: row for row in report.depth}
    assert by_level["1"].names_over_limit == 0
    assert by_level["3"].names_over_limit >= 1
    assert by_level["3"].worst_name is not None
    assert len(by_level["3"].worst_name) > 50


def test_collisions_are_reported_without_raising():
    spec = {
        "paths": {
            "/v1/customers/cards": {"get": {"summary": "List sources"}},
            "/v1/customers/sources": {"get": {"summary": "List sources"}},
        }
    }
    config = load_config(
        {
            "module": {"name": "Stripe", "strip_path_prefix": ["v1"]},
            "include_roots": ["customers"],
        },
        "config.json",
    )

    report = analyze_spec(spec, config)

    assert len(report.collisions) == 1
    assert report.collisions[0]["name"] == "Customers - List sources"


def test_path_params_show_the_name_that_would_be_derived():
    report = analyze_spec(SPEC, load_config(CONFIG, "config.json"))

    derived = {
        (row.operation_key, row.placeholder): row.derived_name
        for row in report.path_params
    }
    assert derived[("payment_intents.item.get", "intent")] == "payment_intent_id"
    assert derived[("setup_intents.item.get", "intent")] == "setup_intent_id"


def test_analysis_reports_ref_cycles():
    spec = {
        "paths": {"/things": {"get": {"summary": "List"}}},
        "components": {
            "schemas": {
                "Filter": {
                    "type": "object",
                    "properties": {"child": {"$ref": "#/components/schemas/Filter"}},
                }
            }
        },
    }

    report = analyze_spec(spec, None)

    assert report.ref_cycles == ["#/components/schemas/Filter"]


def test_analysis_of_an_acyclic_spec_reports_no_cycles():
    report = analyze_spec({"paths": {"/a": {"get": {}}}}, None)

    assert report.ref_cycles == []
