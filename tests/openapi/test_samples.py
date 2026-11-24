import json

from studio_iac.openapi.samples import (
    body_sample_for,
    parameter_sample,
    sample_for,
)


def test_enum_wins_over_everything():
    assert (
        sample_for({"type": "string", "enum": ["asc", "desc"], "example": "x"}) == "asc"
    )


def test_example_then_default():
    assert sample_for({"example": "cus_123"}) == "cus_123"
    assert sample_for({"default": 25}) == "25"


def test_structured_example_is_compact_json():
    assert sample_for({"example": {"a": 1}}) == '{"a":1}'
    assert sample_for({"example": ["a", "b"]}) == '["a","b"]'


def test_format_fills_in_when_the_schema_says_nothing_else():
    assert sample_for({"type": "string", "format": "date"}) == "2026-01-31"
    assert (
        sample_for({"type": "string", "format": "date-time"}) == "2026-01-31T12:00:00Z"
    )
    assert sample_for({"type": "string", "format": "email"}) == "user@example.com"


def test_type_fills_in_last():
    assert sample_for({"type": "boolean"}) == "true"
    assert sample_for({"type": "integer"}) == "10"


def test_a_bare_string_has_no_honest_sample():
    assert sample_for({"type": "string"}) == ""
    assert sample_for(None) == ""


def test_parameter_example_outranks_the_schema():
    parameter = {"name": "status", "example": "active", "schema": {"enum": ["a", "b"]}}

    assert parameter_sample(parameter, parameter["schema"]) == "active"


def test_parameter_examples_map_uses_the_first_entry_value():
    parameter = {
        "name": "cursor",
        "examples": {"first": {"value": "cur_1"}, "second": {"value": "cur_2"}},
    }

    assert parameter_sample(parameter, {}) == "cur_1"


def test_parameter_without_example_falls_back_to_the_schema():
    assert parameter_sample({"name": "limit"}, {"type": "integer"}) == "10"
    assert parameter_sample("not a dict", {"type": "boolean"}) == "true"


def test_body_sample_is_a_compact_json_skeleton_required_first():
    schema = {
        "type": "object",
        "required": ["name"],
        "properties": {
            "qty": {"type": "integer"},
            "name": {"type": "string", "example": "Widget"},
            "active": {"type": "boolean"},
        },
    }

    assert body_sample_for(schema) == '{"name":"Widget","qty":1,"active":true}'


def test_body_sample_stops_at_the_depth_cap():
    schema = {
        "type": "object",
        "properties": {
            "a": {
                "type": "object",
                "properties": {
                    "b": {
                        "type": "object",
                        "properties": {
                            "c": {"type": "object", "properties": {"d": {}}}
                        },
                    }
                },
            }
        },
    }

    assert body_sample_for(schema) == '{"a":{"b":{"c":{}}}}'


def test_body_sample_caps_the_number_of_keys():
    schema = {
        "type": "object",
        "properties": {f"f{index}": {"type": "integer"} for index in range(20)},
    }

    assert len(json.loads(body_sample_for(schema))) == 12


def test_body_sample_is_empty_without_properties():
    assert body_sample_for({"type": "string"}) == ""
    assert body_sample_for("not a dict") == ""


def test_body_sample_merges_allof_parts_like_the_body_planner_does():
    schema = {
        "allOf": [
            {
                "type": "object",
                "required": ["name"],
                "properties": {"name": {"type": "string", "example": "Widget"}},
            },
            {"type": "object", "properties": {"qty": {"type": "integer"}}},
        ]
    }

    assert body_sample_for(schema) == '{"name":"Widget","qty":1}'


def test_body_sample_lets_the_outer_schema_override_an_allof_part():
    schema = {
        "allOf": [{"type": "object", "properties": {"name": {"type": "integer"}}}],
        "properties": {"name": {"type": "string", "example": "Widget"}},
    }

    assert body_sample_for(schema) == '{"name":"Widget"}'


def test_body_sample_descends_into_a_nested_allof_object():
    schema = {
        "type": "object",
        "properties": {
            "owner": {
                "allOf": [{"type": "object", "properties": {"id": {"type": "integer"}}}]
            }
        },
    }

    assert body_sample_for(schema) == '{"owner":{"id":1}}'
