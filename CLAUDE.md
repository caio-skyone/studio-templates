# Instruções do projeto studio-templates

## `query` no IAC exportado

Ao criar ou editar operações pelas ferramentas do MCP (`add_draft_operation`,
`add_draft_operations_batch`, `update_draft_operation`), escreva sempre
`request.query` — o array irmão de `request.header`, no formato
`{key, value, enabled}`. É o formato que o servidor prefere.

**Nunca** use `request.url.query`. É o formato legado: o servidor o stringifica
dentro do endpoint e, nesse caminho, lê só `key` e `value` — `enabled` é
ignorado. O `validate_draft` avisa quando uma operação usa `url.query`, e avisa
mais forte quando preenche os dois, porque aí a mesma chave vai duas vezes na
requisição.

O servidor normaliza o resto sozinho. Depois do `export_draft`, `request.query`
já vem como irmão de `header`, com `enabled: true` em cada item e `[]` nas
operações sem parâmetros de query — não há nada a transformar aí.

Resta **uma** limpeza manual antes de commitar em `iac/`: o servidor também
injeta um `request.url.query: []` legado em toda operação. Remova essa chave,
deixando `request.url` apenas com `path`.

Antes (como sai do `export_draft`):

```json
"url": {
  "path": ["authorized_payments"],
  "query": []
},
"query": [
  {"key": "status", "value": "<>status</>", "enabled": true}
]
```

Depois (formato final para este repo):

```json
"url": {
  "path": ["authorized_payments"]
},
"query": [
  {"key": "status", "value": "<>status</>", "enabled": true}
]
```

Isso é higiene de arquivo, não correção de defeito: o `url.query` injetado é
sempre `[]` e não duplica nada na requisição real. A lista completa dos campos
que o servidor preenche por conta própria está em
`.claude/skills/studio-connector-shared/server-normalization.md`.
