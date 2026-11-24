"""CLI `studio-iac`: ferramentas determinísticas para os IACs de iac/.

Substitui as tools do studio-connector-mcp por comandos que leem e escrevem
arquivos. Rode com `uv run studio-iac <comando> --help`.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from studio_iac import pipeline
from studio_iac.fs import FileReadError, write_text_atomic
from studio_iac.iac.models import IACModule
from studio_iac.iac.validation import local_validation

REPO_ROOT = Path(__file__).resolve().parents[2]
IAC_DIR = REPO_ROOT / "iac"
# Configs do gerador OpenAPI moram ao lado dos IACs, mas não são IAC.
CONFIG_SUFFIX = ".openapi-config.json"


def _dump(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _targets(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(p) for p in paths]
    return sorted(
        p for p in IAC_DIR.glob("*.json") if not p.name.endswith(CONFIG_SUFFIX)
    )


# --- validate ---------------------------------------------------------------


def _validate_one(path: Path, *, show_warnings: bool) -> bool:
    try:
        raw = _read(path)
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERRO {path}: JSON ilegível: {error}")
        return False
    try:
        module = IACModule.model_validate(raw)
    except ValidationError as error:
        print(f"ERRO {path}: fora do schema IAC")
        for item in error.errors():
            where = ".".join(str(part) for part in item["loc"])
            print(f"  - {where}: {item['msg']}")
        return False

    result = local_validation(module)
    status = "ok" if result.ok else "ERRO"
    print(
        f"{status} {path}: {len(module.operations)} operações, "
        f"{len(result.errors)} erros, {len(result.warnings)} avisos"
    )
    for error in result.errors:
        print(f"  ✗ {error.path}: {error.message}")
    if show_warnings:
        for warning in result.warnings:
            print(f"  ! {warning.path}: {warning.message}")
    return result.ok


def cmd_validate(args: argparse.Namespace) -> int:
    paths = _targets(args.files)
    ok = [_validate_one(p, show_warnings=not args.quiet) for p in paths]
    return 0 if all(ok) else 1


# --- ids --------------------------------------------------------------------


def _fill(entity: dict[str, Any]) -> int:
    if isinstance(entity.get("id"), str) and entity["id"].strip():
        return 0
    entity["id"] = str(uuid4())
    return 1


def cmd_ids(args: argparse.Namespace) -> int:
    """Gera id para módulo, operações e parâmetros sem id (ou com id vazio)."""
    for path in _targets(args.files):
        module = _read(path)
        filled = _fill(module)
        for operation in module.get("operations", []):
            filled += _fill(operation)
            for parameter in operation.get("parameters", []):
                filled += _fill(parameter)
        if filled:
            write_text_atomic(path, _dump(module))
        print(f"{path}: {filled} ids gerados")
    return 0


# --- tidy -------------------------------------------------------------------


def cmd_tidy(args: argparse.Namespace) -> int:
    """Remove o `request.url.query: []` legado que o export do Studio injeta."""
    for path in _targets(args.files):
        module = _read(path)
        removed = 0
        for operation in module.get("operations", []):
            url = operation.get("request", {}).get("url", {})
            if "query" in url and url["query"] == []:
                del url["query"]
                removed += 1
        if removed:
            write_text_atomic(path, _dump(module))
        print(f"{path}: {removed} url.query vazios removidos")
    return 0


# --- summary ----------------------------------------------------------------


def cmd_summary(args: argparse.Namespace) -> int:
    """Resumo compacto de um IAC, para não carregar o JSON inteiro no contexto."""
    module = _read(Path(args.file))
    operations = module.get("operations", [])
    auth = module.get("settings", {}).get("authentication_type", "")
    print(f"{module.get('name')} | auth: {auth} | {len(operations)} operações")
    needle = args.grep.lower() if args.grep else None
    shown = 0
    for index, operation in enumerate(operations):
        name = operation.get("name", "")
        if needle and needle not in name.lower():
            continue
        if args.limit is not None and shown >= args.limit:
            break
        request = operation.get("request", {})
        path = "/".join(request.get("url", {}).get("path", []))
        print(f"[{index}] {request.get('method', '?'):6} {name} | /{path}")
        shown += 1
    return 0


# --- openapi ----------------------------------------------------------------


def cmd_analyze(args: argparse.Namespace) -> int:
    report = pipeline.analyze(args.spec, args.config)
    print(report.model_dump_json(indent=2))
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    out = pipeline.generate(args.spec, args.config, args.out)
    print(
        _dump(
            {
                "iac": out.iac_path,
                "prose_worklist": out.worklist_path,
                "report": out.report_path,
                "sidecar": out.sidecar_path,
                "warnings": len(out.report.warnings),
            }
        ),
        end="",
    )
    return 0


def cmd_apply_prose(args: argparse.Namespace) -> int:
    out = pipeline.apply_prose(args.iac, args.prose, args.out)
    print(
        f"{out.out_path}: {out.operations} operações, "
        f"{out.parameters_filled} descrições de parâmetro aplicadas"
    )
    return 0


# --- entry point ------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="studio-iac", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="valida IACs (padrão: todos de iac/)")
    p.add_argument("files", nargs="*")
    p.add_argument("-q", "--quiet", action="store_true", help="esconde avisos")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("ids", help="gera ids faltantes (módulo/operação/parâmetro)")
    p.add_argument("files", nargs="+")
    p.set_defaults(func=cmd_ids)

    p = sub.add_parser("tidy", help="remove request.url.query: [] legado")
    p.add_argument("files", nargs="*")
    p.set_defaults(func=cmd_tidy)

    p = sub.add_parser("summary", help="resumo: metadados + uma linha por operação")
    p.add_argument("file")
    p.add_argument("--grep", help="filtra operações pelo nome")
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("analyze", help="mede um spec OpenAPI antes de gerar")
    p.add_argument("spec")
    p.add_argument("--config")
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("generate", help="gera iac.json + prose_worklist.json")
    p.add_argument("spec")
    p.add_argument("--config", required=True)
    p.add_argument("--out", required=True, help="pasta de saída")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("apply-prose", help="aplica a prosa traduzida ao IAC")
    p.add_argument("iac")
    p.add_argument("prose")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_apply_prose)

    return parser


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except FileReadError as error:
        print(f"erro: {error}", file=sys.stderr)
        return 2
    except Exception as error:  # erros de domínio já trazem mensagem útil
        name = type(error).__name__
        if name.endswith(("Invalid", "Collision", "Aborted", "Mismatch")):
            print(f"erro ({name}): {error}", file=sys.stderr)
            return 1
        raise


if __name__ == "__main__":
    sys.exit(main())
