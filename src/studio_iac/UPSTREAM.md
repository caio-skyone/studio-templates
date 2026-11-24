# Origem do código

`studio_iac` é uma cópia do domínio do servidor MCP de
`toolkit-studio-connectors` (Bitbucket `skyoneteam`), sem o MCP, sem a camada
HTTP e sem o draft store.

| | |
|---|---|
| Versão de origem | `v0.6.0` |
| Commit | `14e692870ee8ea84c66a5b8c342a5702384c6800` |
| Copiado em | 2026-11-24 |

## Mapa de arquivos

| Aqui | No toolkit (`server/src/studio_connector_mcp/`) |
|---|---|
| `errors.py`, `text.py` | `domain/errors.py`, `domain/text.py` |
| `fs.py` | `infrastructure/fs.py` |
| `iac/{models,rules,naming,errors,secrets,validation}.py` | `domain/iac/` |
| `openapi/*.py` | `domain/openapi/` |
| `pipeline.py` | `application/openapi/use_cases.py` (síncrono, sem DTOs) |
| `cli.py` | novo — substitui as tools MCP |
| `tests/` | `server/tests/unit/domain/{iac,openapi}` + `test_openapi_use_cases.py` |

Fora da cópia: `domain/iac/{baseline,diff,plan,ports}.py`, `domain/auth`,
`domain/modules`, toda a camada `application/iac`, `infrastructure/http` e
`presentation` — dependem do draft store ou da API do Studio.

## Para trazer uma versão nova

1. Copie os arquivos da tabela acima por cima destes.
2. Troque os imports: `studio_connector_mcp.domain.` → `studio_iac.`,
   `studio_connector_mcp.infrastructure.fs` → `studio_iac.fs`.
3. Reaplique em `pipeline.py` o que mudou em `application/openapi/use_cases.py`.
4. `uv run pytest` e `uv run studio-iac validate`.
5. Atualize a tabela de versão deste arquivo.
