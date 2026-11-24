import time

import pytest

from studio_iac.openapi.errors import OpenApiSpecInvalid
from studio_iac.openapi.refs import (
    deref,
    ref_cycles,
    resolve_node,
    resolve_ref,
    strip_responses,
)

_SPEC = {
    "components": {
        "schemas": {
            "Customer": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "address": {"$ref": "#/components/schemas/Address"},
                },
            },
            "Address": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
            },
            "Node": {
                "type": "object",
                "properties": {"child": {"$ref": "#/components/schemas/Node"}},
            },
        }
    }
}


def test_resolve_ref_returns_the_target_schema():
    result = resolve_ref(_SPEC, "#/components/schemas/Address")

    assert result["properties"]["city"] == {"type": "string"}


def test_resolve_ref_rejects_external_ref():
    with pytest.raises(OpenApiSpecInvalid) as excinfo:
        resolve_ref(_SPEC, "other.json#/components/schemas/Address")

    assert "external" in str(excinfo.value)


def test_resolve_ref_rejects_unknown_pointer():
    with pytest.raises(OpenApiSpecInvalid) as excinfo:
        resolve_ref(_SPEC, "#/components/schemas/Nope")

    assert "Nope" in str(excinfo.value)


def test_resolve_ref_rejects_non_object_target():
    with pytest.raises(OpenApiSpecInvalid) as excinfo:
        resolve_ref(_SPEC, "#/components/schemas/Address/properties/city/type")

    assert "is not an object" in str(excinfo.value)


def test_deref_inlines_nested_refs():
    result = deref(_SPEC, {"$ref": "#/components/schemas/Customer"})

    assert result["properties"]["address"]["properties"]["city"] == {"type": "string"}


def test_deref_breaks_recursive_refs_instead_of_hanging():
    """The cycle guard cuts at the first re-entry, before the depth cap is reached."""
    result = deref(_SPEC, {"$ref": "#/components/schemas/Node"}, max_depth=3)

    assert result["properties"]["child"] == {}


def test_deref_still_caps_depth_on_an_acyclic_ref_chain():
    spec = {
        "components": {
            "schemas": {
                f"Level{index}": {
                    "type": "object",
                    "properties": {
                        "next": {"$ref": f"#/components/schemas/Level{index + 1}"}
                    },
                }
                for index in range(5)
            }
            | {"Level5": {"type": "string"}}
        }
    }

    result = deref(spec, {"$ref": "#/components/schemas/Level0"}, max_depth=2)

    assert result["properties"]["next"]["properties"]["next"] == {}


def test_deref_walks_lists():
    result = deref(_SPEC, [{"$ref": "#/components/schemas/Address"}])

    assert result[0]["properties"]["city"] == {"type": "string"}


_CYCLE_SPEC = {
    "components": {
        "schemas": {
            "A": {
                "type": "object",
                "properties": {"b": {"$ref": "#/components/schemas/B"}},
            },
            "B": {
                "type": "object",
                "properties": {"c": {"$ref": "#/components/schemas/C"}},
            },
            "C": {
                "type": "object",
                "properties": {"a": {"$ref": "#/components/schemas/A"}},
            },
            "Leaf": {"type": "string"},
        },
        "parameters": {
            "PageSize": {
                "name": "page_size",
                "in": "query",
                "schema": {"type": "integer"},
            }
        },
    }
}


def test_deref_cuts_a_three_node_cycle_instead_of_recursing():
    result = deref(_CYCLE_SPEC, {"$ref": "#/components/schemas/A"})

    assert result["properties"]["b"]["properties"]["c"]["properties"]["a"] == {}


def test_deref_of_a_wide_recursive_schema_stays_fast():
    """The regression that took the host to 95% CPU must fail as a timeout here."""
    branch = {
        "type": "object",
        "properties": {
            f"child_{index}": {"$ref": "#/components/schemas/Branch"}
            for index in range(6)
        },
    }
    spec = {"components": {"schemas": {"Branch": branch}}}

    started = time.perf_counter()
    deref(spec, {"$ref": "#/components/schemas/Branch"})
    elapsed = time.perf_counter() - started

    assert elapsed < 1.0


def test_deref_memoizes_a_repeated_ref_into_the_same_object():
    node = {
        "one": {"$ref": "#/components/schemas/Address"},
        "two": {"$ref": "#/components/schemas/Address"},
    }

    result = deref(_SPEC, node)

    assert result["one"] is result["two"]


def test_resolve_node_follows_only_the_top_level_ref():
    resolved = resolve_node(_CYCLE_SPEC, {"$ref": "#/components/parameters/PageSize"})

    assert resolved["name"] == "page_size"
    assert resolved["in"] == "query"


def test_resolve_node_lets_siblings_override_the_target():
    resolved = resolve_node(
        _CYCLE_SPEC, {"$ref": "#/components/parameters/PageSize", "required": True}
    )

    assert resolved["required"] is True
    assert resolved["name"] == "page_size"


def test_resolve_node_returns_a_plain_node_untouched():
    node = {"name": "limit", "in": "query"}

    assert resolve_node(_CYCLE_SPEC, node) is node


def test_strip_responses_drops_every_response_block_and_keeps_the_rest():
    spec = {
        "paths": {
            "/things": {
                "get": {"summary": "List", "responses": {"200": {"description": "ok"}}},
                "post": {"requestBody": {"content": {}}, "responses": {}},
            }
        }
    }

    pruned = strip_responses(spec)

    assert "responses" not in pruned["paths"]["/things"]["get"]
    assert pruned["paths"]["/things"]["get"]["summary"] == "List"
    assert pruned["paths"]["/things"]["post"]["requestBody"] == {"content": {}}


def test_ref_cycles_names_every_schema_in_a_cycle_and_ignores_the_acyclic_ones():
    cycles = ref_cycles(_CYCLE_SPEC)

    assert cycles == ["#/components/schemas/A"]


def test_ref_cycles_is_empty_on_an_acyclic_spec():
    assert ref_cycles({"components": {"schemas": {"Leaf": {"type": "string"}}}}) == []
