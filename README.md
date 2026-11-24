# studio-templates

Repositório de documentação e fluxo de desenvolvimento dos templates do
Skyone Studio — conectores REST e, futuramente, outros tipos de template.

## Estrutura

- `docs/connectors/` — documentação de cada conector publicado
- `docs/dev-flow/` — guias de apoio ao desenvolvimento de templates (ex: OAuth2/callback)
- `docs/iac-viewer.md` — visualizador dos JSONs de IAC exportados (`iac/`)
- `iac/` — JSONs de IAC por conector (source of truth) e configs do gerador OpenAPI (`*.openapi-config.json`)
- `src/studio_iac/` — CLI `studio-iac`: validação, geração a partir de OpenAPI, ids e limpeza dos IACs
- `.claude/skills/` — skills do Claude Code que guiam plan → build → publish → patch → account → document
- `scratchpad/` — área de trabalho local das skills (specs, artefatos intermediários), fora do git

## Desenvolvendo conectores

As skills trabalham direto nos arquivos de `iac/` — não há servidor MCP. Tudo
que é determinístico passa pela CLI, que roda igual no Windows, Linux e macOS:

```sh
uv sync
uv run studio-iac validate                 # valida todos os IACs de iac/
uv run studio-iac validate iac/stripe.json # valida um
uv run studio-iac --help                   # analyze, generate, apply-prose, ids, tidy, summary
uv run pytest                              # testes da CLI
```

A importação no Studio é manual, pela UI. Depois de importar, exporte o
conector de volta por cima de `iac/{slug}.json` (para guardar os ids reais) e
rode `uv run studio-iac tidy iac/{slug}.json`.

O código de `src/studio_iac/` veio do `toolkit-studio-connectors` — veja
[`src/studio_iac/UPSTREAM.md`](src/studio_iac/UPSTREAM.md) para saber a versão
e como trazer atualizações.

## Fluxo de incremento das documentações

Crie a sua branch com o nome da plataforma alvo -> Adicione o arquivo markdown em `docs/connectors/` -> merge na main quando a documentação estiver pronta -> github actions inicia o novo deploy da documentação

## Rodando o site localmente

O site é gerado com [Zensical](https://zensical.org) a partir do `mkdocs.yml`.
Funciona igual no Windows, Linux e macOS; só precisa do [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run python scripts/sync_iac_assets.py   # copia iac/*.json para docs/iac-data/
uv run zensical serve                      # http://localhost:8000
```

Use links e imagens em Markdown padrão (`![alt](../img/<conector>/arquivo.png)`),
não `[[wikilinks]]` — o Zensical não tem plugin para eles.

Acesse em [Studio Templates](https://caio-skyone.github.io/studio-templates/)
