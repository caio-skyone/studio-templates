import json

import pytest

from studio_iac import pipeline
from studio_iac.openapi.errors import OperationNameCollision


def _write(path, payload) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_report_is_written_even_when_generation_aborts(tmp_path):
    spec = {
        "paths": {
            "/v1/accounts/persons": {"get": {"summary": "List people"}},
            "/v1/accounts/people": {"get": {"summary": "List people"}},
        }
    }
    config = {
        "module": {"name": "X", "strip_path_prefix": ["v1"]},
        "include_roots": ["accounts"],
    }
    spec_path = tmp_path / "spec.json"
    config_path = tmp_path / "config.json"
    _write(spec_path, spec)
    _write(config_path, config)
    out_dir = tmp_path / "out"

    with pytest.raises(OperationNameCollision):
        pipeline.generate(str(spec_path), str(config_path), str(out_dir))

    written = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
    assert "excluded" in written


def test_prose_round_trips_across_three_placeholder_arities(tmp_path):
    """The end-to-end proof that `operation_key` is now unique.

    With the old trailing `.item` marker these three paths shared one key:
    `check_coverage` accepted exactly one worklist entry and its description
    went to all three operations.
    """
    spec = {
        "paths": {
            "/v1/a/{x}": {"get": {"summary": "One"}},
            "/v1/a/{x}/{y}": {"get": {"summary": "Two"}},
            "/v1/a/{x}/{y}/{z}": {"get": {"summary": "Three"}},
        }
    }
    config = {
        "module": {"name": "X", "strip_path_prefix": ["v1"]},
        "include_roots": ["a"],
    }
    spec_path = tmp_path / "spec.json"
    config_path = tmp_path / "config.json"
    _write(spec_path, spec)
    _write(config_path, config)
    out_dir = tmp_path / "out"

    pipeline.generate(str(spec_path), str(config_path), str(out_dir))

    worklist = json.loads((out_dir / "prose_worklist.json").read_text(encoding="utf-8"))
    assert len({entry["op_key"] for entry in worklist["operations"]}) == 3
    for entry in worklist["operations"]:
        entry["description"] = f"desc for {entry['op_key']}"
    for entry in worklist["parameters"]:
        entry["description"] = f"param {entry['name']}"
    _write(out_dir / "prose_worklist.json", worklist)

    pipeline.apply_prose(
        str(out_dir / "iac.json"),
        str(out_dir / "prose_worklist.json"),
        str(out_dir / "iac_final.json"),
    )

    final = json.loads((out_dir / "iac_final.json").read_text(encoding="utf-8"))
    descriptions = {operation["description"] for operation in final["operations"]}
    assert len(descriptions) == 3
