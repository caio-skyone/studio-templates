# tests/unit/domain/openapi/test_openapi_naming.py
from studio_iac.openapi.config import NamingConfig
from studio_iac.openapi.naming import (
    humanize_operation_id,
    iac_path_segments,
    path_param_name,
    singularize,
    snake_case,
)
from studio_iac.openapi.shape import SpecOperation, placeholders_in


def _naming(**overrides) -> NamingConfig:
    return NamingConfig.model_validate(overrides or {})


def _name(path: str, placeholder_index: int, naming: NamingConfig | None = None) -> str:
    segments = [segment for segment in path.split("/") if segment]
    return path_param_name(
        segments,
        placeholder_index,
        placeholders_in(segments[placeholder_index])[0],
        naming=naming or _naming(),
        shape_key="irrelevant",
        overrides={},
    )


def test_generic_placeholder_derives_from_preceding_collection():
    assert _name("payment_intents/{intent}", 1) == "payment_intent_id"


def test_the_same_generic_placeholder_in_another_resource_gets_another_name():
    assert _name("setup_intents/{intent}", 1) == "setup_intent_id"


def test_bare_id_placeholder_derives_from_collection():
    assert _name("customers/{id}", 1) == "customer_id"


def test_specific_placeholder_keeps_the_spec_name():
    assert _name("customers/{customer}/tax_ids", 1) == "customer"


def test_irregular_plural_people_becomes_person():
    assert _name("accounts/{account}/people/{id}", 3) == "person_id"


def test_config_can_add_a_generic_placeholder():
    naming = _naming(generic_placeholders={"add": ["subscription_exposed_id"]})

    result = _name("subscriptions/{subscription_exposed_id}", 1, naming)

    assert result == "subscription_id"


def test_config_can_remove_a_default_generic_placeholder():
    naming = _naming(generic_placeholders={"remove": ["session"]})

    assert _name("checkout/sessions/{session}", 2, naming) == "session"


def test_config_singular_override_wins():
    naming = _naming(singular={"history": "balance_transaction"})

    assert _name("balance/history/{id}", 2, naming) == "balance_transaction_id"


def test_config_singular_override_beats_irregular_plural():
    naming = _naming(singular={"people": "human"})

    assert _name("accounts/{account}/people/{id}", 3, naming) == "human_id"


def test_explicit_override_beats_every_rule():
    segments = ["subscriptions", "{subscription_exposed_id}"]

    result = path_param_name(
        segments,
        1,
        "subscription_exposed_id",
        naming=_naming(),
        shape_key="subscriptions",
        overrides={"subscriptions:subscription_exposed_id": "sub_ref"},
    )

    assert result == "sub_ref"


def test_generic_placeholder_with_no_preceding_literal_falls_back_to_itself():
    assert _name("{id}", 0) == "id"


def test_singularize_rules():
    overrides: dict[str, str] = {}
    assert singularize("customers", overrides) == "customer"
    assert singularize("tax_ids", overrides) == "tax_id"
    assert singularize("addresses", overrides) == "address"
    assert singularize("categories", overrides) == "category"
    assert singularize("people", overrides) == "person"
    assert singularize("balance", overrides) == "balance"
    assert singularize("series", overrides) == "series"
    assert singularize("species", overrides) == "species"


def test_snake_case_normalizes_camel_and_dashes():
    assert snake_case("valueListItem") == "value_list_item"
    assert snake_case("value-list-item") == "value_list_item"
    assert snake_case("Value List Item") == "value_list_item"


def _operation(path: str) -> SpecOperation:
    shape = ".".join(
        segment
        for segment in path.split("/")
        if segment and not (segment.startswith("{") and segment.endswith("}"))
    )
    return SpecOperation(
        path=path,
        method="GET",
        summary=None,
        description=None,
        parameters=(),
        request_body=None,
        servers=(),
        shape_key=shape,
        operation_key=f"{shape}.get",
    )


def test_iac_path_segments_marks_placeholders_and_keeps_literals():
    operation = _operation("/v1/payment_intents/{intent}")

    segments, params = iac_path_segments(
        operation,
        naming=_naming(),
        path_param_overrides={},
        strip_prefix=[],
    )

    assert segments == ["v1", "payment_intents", "<>payment_intent_id</>"]
    assert params == [("intent", "payment_intent_id")]


def test_iac_path_segments_returns_pairs_in_path_order():
    operation = _operation("/v1/accounts/{account}/people/{id}")

    segments, params = iac_path_segments(
        operation,
        naming=_naming(),
        path_param_overrides={},
        strip_prefix=[],
    )

    assert segments == [
        "v1",
        "accounts",
        "<>account</>",
        "people",
        "<>person_id</>",
    ]
    assert params == [("account", "account"), ("id", "person_id")]


def test_iac_path_segments_with_no_placeholders_returns_segments_unchanged():
    operation = _operation("/v1/balance")

    segments, params = iac_path_segments(
        operation,
        naming=_naming(),
        path_param_overrides={},
        strip_prefix=[],
    )

    assert segments == ["v1", "balance"]
    assert params == []


def test_iac_path_segments_honours_explicit_override():
    operation = SpecOperation(
        path="/v1/subscriptions/{subscription_exposed_id}",
        method="GET",
        summary=None,
        description=None,
        parameters=(),
        request_body=None,
        servers=(),
        shape_key="subscriptions",
        operation_key="subscriptions.get",
    )

    segments, params = iac_path_segments(
        operation,
        naming=_naming(),
        path_param_overrides={"subscriptions:subscription_exposed_id": "sub_ref"},
        strip_prefix=[],
    )

    assert segments == ["v1", "subscriptions", "<>sub_ref</>"]
    assert params == [("subscription_exposed_id", "sub_ref")]


def _segments(path: str) -> tuple[list[str], list[tuple[str, str]]]:
    return iac_path_segments(
        _operation(path),
        naming=_naming(),
        path_param_overrides={},
        strip_prefix=[],
    )


def test_suffixed_placeholder_keeps_the_literal_suffix():
    segments, params = _segments("/Accounts/Messages/{Sid}.json")

    assert segments == ["Accounts", "Messages", "<>message_id</>.json"]
    assert params == [("Sid", "message_id")]


def test_action_suffix_keeps_the_action():
    segments, params = _segments("/databases/{name}:set-tags")

    assert segments == ["databases", "<>name</>:set-tags"]
    assert params == [("name", "name")]


def test_prefixed_placeholder_keeps_the_prefix():
    segments, params = _segments("/services/data/v{version}/sobjects")

    assert segments == ["services", "data", "v<>version</>", "sobjects"]
    assert params == [("version", "version")]


def test_two_placeholders_in_one_segment_yield_two_parameters():
    segments, params = _segments("/reports/{year}-{month}")

    assert segments == ["reports", "<>year</>-<>month</>"]
    assert params == [("year", "year"), ("month", "month")]


def test_no_brace_survives_in_the_generated_path():
    segments, _ = _segments("/Accounts/{AccountSid}/Calls/{Sid}.json")

    assert not any("{" in segment or "}" in segment for segment in segments)


def test_humanize_operation_id_splits_camel_case():
    assert humanize_operation_id("CreateAlphaSender") == "Create alpha sender"


def test_humanize_operation_id_keeps_only_the_last_underscore_chunk():
    assert humanize_operation_id("schemas_getAll") == "Get all"


def test_humanize_operation_id_handles_dashes_and_slashes():
    assert humanize_operation_id("get-/crm-object-schemas_getAll") == "Get all"


def test_short_acronym_ending_in_s_is_not_singularized():
    assert singularize("pos", {}) == "pos"
    assert singularize("ips", {}) == "ips"


def test_override_still_wins_over_the_short_word_guard():
    assert singularize("pos", {"pos": "point_of_sale"}) == "point_of_sale"


def test_normal_plurals_still_singularize():
    assert singularize("customers", {}) == "customer"
    assert singularize("cards", {}) == "card"
    assert singularize("policies", {}) == "policy"
