"""Caminho entra, artefato sai. Nenhum modelo no caminho dos dados.

Versão síncrona e sem MCP dos casos de uso `analyze_openapi_spec`,
`generate_iac_from_openapi` e `apply_prose` do toolkit-studio-connectors.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from studio_iac.fs import read_json, resolve_path, write_text_atomic
from studio_iac.iac.models import IACModule
from studio_iac.openapi.analyze import AnalysisReport, analyze_spec
from studio_iac.openapi.config import load_config
from studio_iac.openapi.emit import GenerationReport, apply_worklist, build_module
from studio_iac.openapi.errors import (
    GenerationAborted,
    OpenApiSpecInvalid,
    OperationKeyCollision,
    OperationNameCollision,
)
from studio_iac.openapi.refs import strip_responses
from studio_iac.openapi.worklist import check_coverage, load_worklist

IAC_FILENAME = "iac.json"
WORKLIST_FILENAME = "prose_worklist.json"
REPORT_FILENAME = "report.json"
SIDECAR_FILENAME = "sidecar.json"


def _load_spec(raw_path: str) -> dict[str, Any]:
    path = resolve_path(raw_path)
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise OpenApiSpecInvalid(path, "expected a JSON object at the top level")
    # O IAC nunca modela resposta, e é nos schemas de resposta que vivem as
    # famílias de $ref recursivas. Podar aqui mantém análise e geração longe
    # do caminho patológico.
    return strip_responses(payload)


def _write_report(out_dir: Path, payload: dict[str, object] | None) -> None:
    """Uma geração que falha ainda deve um diagnóstico ao usuário."""
    if payload is None:
        return
    write_text_atomic(out_dir / REPORT_FILENAME, json.dumps(payload, indent=2))


@dataclass(frozen=True, slots=True)
class GenerateOutput:
    iac_path: str
    worklist_path: str
    report_path: str
    sidecar_path: str
    report: GenerationReport


@dataclass(frozen=True, slots=True)
class ApplyProseOutput:
    out_path: str
    operations: int
    parameters_filled: int


def analyze(spec_path: str, config_path: str | None = None) -> AnalysisReport:
    spec = _load_spec(spec_path)
    config = None
    if config_path is not None:
        resolved = resolve_path(config_path)
        config = load_config(read_json(resolved), resolved)
    return analyze_spec(spec, config)


def generate(spec_path: str, config_path: str, out_dir: str) -> GenerateOutput:
    spec = _load_spec(spec_path)
    resolved_config = resolve_path(config_path)
    config = load_config(read_json(resolved_config), resolved_config)

    out = resolve_path(out_dir)
    try:
        result = build_module(spec, config, module_id=str(uuid4()))
    except (OperationNameCollision, OperationKeyCollision) as error:
        _write_report(out, error.report)
        raise
    if result.report.errors:
        payload = result.report.model_dump()
        _write_report(out, payload)
        raise GenerationAborted(payload)

    return GenerateOutput(
        iac_path=str(
            write_text_atomic(
                out / IAC_FILENAME,
                result.module.model_dump_json(by_alias=True, indent=2),
            )
        ),
        worklist_path=str(
            write_text_atomic(
                out / WORKLIST_FILENAME, result.worklist.model_dump_json(indent=2)
            )
        ),
        report_path=str(
            write_text_atomic(
                out / REPORT_FILENAME, result.report.model_dump_json(indent=2)
            )
        ),
        sidecar_path=str(
            write_text_atomic(
                out / SIDECAR_FILENAME,
                json.dumps({"operation_keys": result.operation_keys}, indent=2),
            )
        ),
        report=result.report,
    )


def apply_prose(iac_path: str, prose_path: str, out_path: str) -> ApplyProseOutput:
    resolved_iac = resolve_path(iac_path)
    try:
        module = IACModule.model_validate(read_json(resolved_iac))
    except ValidationError as error:
        raise OpenApiSpecInvalid(resolved_iac, str(error)) from error

    resolved_prose = resolve_path(prose_path)
    worklist = load_worklist(read_json(resolved_prose), resolved_prose)

    sidecar_path = resolved_iac.with_name(SIDECAR_FILENAME)
    operation_keys: dict[str, str] = {}
    if sidecar_path.exists():
        payload = read_json(sidecar_path)
        if isinstance(payload, dict):
            keys = payload.get("operation_keys")
            if isinstance(keys, dict):
                operation_keys = {str(k): str(v) for k, v in keys.items()}

    check_coverage(
        worklist,
        parameter_names={
            parameter.name
            for operation in module.operations
            for parameter in operation.parameters
        },
        operation_keys=set(operation_keys.values()),
    )

    merged = apply_worklist(module, worklist, operation_keys=operation_keys)
    written = write_text_atomic(
        resolve_path(out_path), merged.model_dump_json(by_alias=True, indent=2)
    )
    return ApplyProseOutput(
        out_path=str(written),
        operations=len(merged.operations),
        parameters_filled=len(worklist.parameter_descriptions()),
    )
