import pytest

from studio_iac.openapi.config import ConnectorConfig, load_config
from studio_iac.openapi.errors import ConnectorConfigInvalid

_MINIMAL = {
    "module": {"name": "Stripe", "authentication_type": "bearer-token"},
    "include_roots": ["customers"],
}


def test_minimal_config_fills_defaults():
    config = load_config(_MINIMAL, "config.json")

    assert isinstance(config, ConnectorConfig)
    assert config.module.strip_path_prefix == []
    assert config.domains == {}
    assert config.exclude == []
    assert config.headers == []
    assert config.naming.generic_placeholders.add == []
    assert config.naming.singular == {}
    assert config.overrides.path_params == {}
    assert config.overrides.body == {}


def test_full_config_round_trips():
    payload = {
        "module": {
            "name": "Stripe",
            "description": "Payments",
            "authentication_type": "bearer-token",
            "strip_path_prefix": ["v1"],
        },
        "include_roots": ["customers", "balance"],
        "domains": {
            "customers.tax_ids": {"domain": "Customer Tax IDs", "block": "core"}
        },
        "exclude": [{"key": "accounts.persons", "reason": "alias de people"}],
        "headers": [
            {
                "key": "Idempotency-Key",
                "param": "idempotency_key",
                "methods": ["POST", "DELETE"],
            }
        ],
        "naming": {
            "generic_placeholders": {"add": ["subscription_exposed_id"], "remove": []},
            "singular": {"history": "balance_transaction"},
        },
        "overrides": {
            "path_params": {"subscriptions:subscription_exposed_id": "subscription_id"},
            "body": {"customers.post": {"mode": "skeleton", "raw": '{"a": 1}'}},
        },
    }

    config = load_config(payload, "config.json")

    assert config.module.strip_path_prefix == ["v1"]
    assert config.domains["customers.tax_ids"].block == "core"
    assert config.exclude[0].reason == "alias de people"
    assert config.headers[0].methods == ["POST", "DELETE"]
    assert config.naming.singular["history"] == "balance_transaction"
    assert config.overrides.body["customers.post"].mode == "skeleton"


def test_header_without_methods_means_every_method():
    config = load_config(
        {**_MINIMAL, "headers": [{"key": "Stripe-Version", "param": "stripe_version"}]},
        "config.json",
    )

    assert config.headers[0].methods is None


def test_unknown_top_level_key_is_rejected_with_the_key_name():
    with pytest.raises(ConnectorConfigInvalid) as excinfo:
        load_config({**_MINIMAL, "includeRoots": ["x"]}, "config.json")

    assert "includeRoots" in str(excinfo.value)


def test_missing_include_roots_is_rejected():
    with pytest.raises(ConnectorConfigInvalid) as excinfo:
        load_config({"module": {"name": "Stripe"}}, "config.json")

    assert "include_roots" in str(excinfo.value)


def test_non_object_payload_is_rejected():
    with pytest.raises(ConnectorConfigInvalid):
        load_config(["not", "an", "object"], "config.json")


def test_header_config_required_defaults_to_false_and_is_settable():
    config = load_config(
        {
            "module": {"name": "Zoho Desk"},
            "include_roots": ["api"],
            "headers": [
                {"key": "orgId", "param": "org_id", "required": True},
                {"key": "X-Trace", "param": "trace"},
            ],
        },
        "config.json",
    )

    assert [header.required for header in config.headers] == [True, False]


def test_header_entry_accepts_a_sample():
    config = load_config(
        {
            "module": {"name": "Widgets"},
            "include_roots": ["widgets"],
            "headers": [
                {
                    "key": "orgId",
                    "param": "org_id",
                    "required": True,
                    "sample": "123456789",
                }
            ],
        },
        "config.json",
    )

    assert config.headers[0].sample == "123456789"


def test_header_sample_defaults_to_empty():
    config = load_config(
        {
            "module": {"name": "Widgets"},
            "include_roots": ["widgets"],
            "headers": [{"key": "orgId", "param": "org_id"}],
        },
        "config.json",
    )

    assert config.headers[0].sample == ""


def test_body_override_content_type_defaults_to_json():
    config = ConnectorConfig.model_validate(
        {
            "module": {
                "name": "T",
                "description": "d",
                "authentication_type": "bearer-token",
            },
            "include_roots": ["things"],
            "overrides": {
                "body": {"things.post": {"mode": "skeleton", "raw": '{"a":"<>a</>"}'}}
            },
        }
    )

    assert config.overrides.body["things.post"].content_type == "application/json"
