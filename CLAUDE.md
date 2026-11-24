# Instruções do projeto studio-templates

## Padrão de corpo multipart/form-data

Referência: operação `Issues - Add attachment` do conector Jira publicado no
Studio (`z8Zht5wExX`). Toda operação multipart deve ter:

1. Header `{"key": "Content-Type", "value": "multipart/form-data", "enabled": true}`
   explícito — sem ele o Studio não envia como multipart.
2. Linha de arquivo no corpo raw no formato
   `campo:<>param_arquivo</>:<>mime_type</>:<>file_name</>` — **sem** a palavra
   literal `mime:` e sem mime/nome fixos (`file:<>file</>:mime:application/octet-stream:anexo.pdf`
   está errado).
3. Parâmetros `mime_type` e `file_name` opcionais (`required: false`), com
   sample (ex.: `application/pdf`, `anexo.pdf`).

Campos de texto do multipart ficam como linhas `campo:<>param</>`, uma por linha.

## Sem MCP: os arquivos de `iac/` são o rascunho

Este repo não usa o `studio-connector-mcp` nem o `skytk`. As skills em
`.claude/skills/` editam `iac/{slug}.json` diretamente, e tudo que é
determinístico passa pela CLI `uv run studio-iac` (validate, ids, tidy,
summary, analyze, generate, apply-prose). Não sugira instalar o MCP nem chamar
a API do Studio: a importação e a exportação de conectores são feitas pelo
usuário na UI do Studio.

Artefatos intermediários (spec, `iac.json` gerado, worklists) vão em
`scratchpad/{slug}/`, que fica fora do git.

## `query` no IAC

Escreva sempre `request.query` — o array irmão de `request.header`, no formato
`{key, value, enabled}`.

**Nunca** use `request.url.query`. É o formato legado: o Studio o stringifica
dentro do endpoint e, nesse caminho, lê só `key` e `value` — `enabled` é
ignorado. O `studio-iac validate` avisa quando uma operação usa `url.query`, e
avisa mais forte quando preenche os dois, porque aí a mesma chave vai duas
vezes na requisição.

O export do Studio injeta um `request.url.query: []` legado em toda operação.
Antes de commitar um IAC exportado, rode:

```sh
uv run studio-iac tidy iac/{slug}.json
```

Isso deixa `request.url` apenas com `path`. É higiene de arquivo, não correção
de defeito: o `url.query` injetado é sempre `[]` e não duplica nada na
requisição real. A lista completa dos campos que o Studio preenche por conta
própria está em
`.claude/skills/studio-connector-shared/server-normalization.md`.
