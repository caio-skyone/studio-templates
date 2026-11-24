"""Expõe iac/*.json como assets estáticos do site.

Copia cada arquivo de iac/ (raiz do repo) para docs/iac-data/ e gera
docs/iac-data/index.json com a lista de slugs, que a página
docs/iac-viewer.md consome via fetch. docs/iac-data/ é gerado e fica fora do
git. Rode antes de `zensical build` ou `zensical serve`:

    uv run python scripts/sync_iac_assets.py

JSONs inválidos são pulados com aviso (o visualizador não conseguiria
abri-los); passe --strict para sair com erro nesse caso.
"""

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IAC_DIR = REPO_ROOT / "iac"
OUT_DIR = REPO_ROOT / "docs" / "iac-data"


def main() -> int:
    # Console do Windows pode não ser UTF-8 quando a saída é redirecionada.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    slugs: list[str] = []
    invalid: list[str] = []
    for json_path in sorted(IAC_DIR.glob("*.json")):
        if json_path.name.endswith(".openapi-config.json"):
            continue  # config do gerador OpenAPI, não é IAC
        try:
            json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            invalid.append(f"{json_path.relative_to(REPO_ROOT).as_posix()}: {exc}")
            continue
        shutil.copy2(json_path, OUT_DIR / json_path.name)
        slugs.append(json_path.stem)

    (OUT_DIR / "index.json").write_text(
        json.dumps(slugs, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if invalid:
        print("JSON inválido em iac/ (pulado):", *invalid, sep="\n  ", file=sys.stderr)
    print(f"{len(slugs)} arquivos de iac/ copiados para docs/iac-data/")
    return 1 if invalid and "--strict" in sys.argv[1:] else 0


if __name__ == "__main__":
    sys.exit(main())
