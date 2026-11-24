import pytest

from studio_iac.openapi.errors import ProseWorklistMismatch
from studio_iac.openapi.worklist import (
    ProseOperationEntry,
    ProseParameterEntry,
    ProseWorklist,
    check_coverage,
    load_worklist,
)


def _worklist() -> ProseWorklist:
    return ProseWorklist(
        parameters=[
            ProseParameterEntry(
                name="status",
                kind="query",
                occurrences=12,
                domains=["Meters", "Invoices"],
                source_en="The status of the meter.",
                note="shared across 2 domains",
            )
        ],
        operations=[
            ProseOperationEntry(
                op_key="customers.post",
                name="Customers - Create customer",
                source_en="Creates a new customer.",
            )
        ],
    )


def test_entries_default_to_empty_prose():
    worklist = _worklist()

    assert worklist.parameters[0].description == ""
    assert worklist.operations[0].description == ""
    assert worklist.operations[0].body_sample == ""


def test_load_worklist_round_trips_json():
    payload = _worklist().model_dump()

    loaded = load_worklist(payload, "prose.json")

    assert loaded.parameters[0].domains == ["Meters", "Invoices"]
    assert loaded.operations[0].op_key == "customers.post"


def test_load_worklist_rejects_a_non_object():
    with pytest.raises(ProseWorklistMismatch):
        load_worklist(["nope"], "prose.json")


def test_check_coverage_passes_when_names_match_exactly():
    check_coverage(
        _worklist(),
        parameter_names={"status"},
        operation_keys={"customers.post"},
    )


def test_check_coverage_reports_a_parameter_absent_from_the_worklist():
    with pytest.raises(ProseWorklistMismatch) as excinfo:
        check_coverage(
            _worklist(),
            parameter_names={"status", "customer_id"},
            operation_keys={"customers.post"},
        )

    assert "customer_id" in str(excinfo.value)
    assert excinfo.value.missing == ["customer_id"]


def test_check_coverage_reports_an_invented_parameter():
    with pytest.raises(ProseWorklistMismatch) as excinfo:
        check_coverage(
            _worklist(),
            parameter_names=set(),
            operation_keys={"customers.post"},
        )

    assert "status" in str(excinfo.value)
    assert excinfo.value.unknown == ["status"]


def test_check_coverage_reports_a_missing_operation_key():
    with pytest.raises(ProseWorklistMismatch) as excinfo:
        check_coverage(
            _worklist(),
            parameter_names={"status"},
            operation_keys={"customers.post", "customers.get"},
        )

    assert "customers.get" in str(excinfo.value)


def test_duplicate_parameter_name_in_the_worklist_is_rejected():
    payload = _worklist().model_dump()
    payload["parameters"].append(dict(payload["parameters"][0]))

    with pytest.raises(ProseWorklistMismatch) as excinfo:
        load_worklist(payload, "prose.json")

    assert "status" in str(excinfo.value)
