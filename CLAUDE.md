# Instruções do projeto studio-templates

## Normalização de `query` no IAC exportado (workaround de bug do MCP)

O `studio-connector-mcp` modela `request.query` dentro de `request.url.query`,
enquanto `request.header` fica um nível acima, como irmão de `url`. Isso é
inconsistente: `query` deveria ser um array irmão de `header`, no mesmo
formato (`{key, value, enabled}`).

Enquanto esse bug não for corrigido no servidor MCP, **depois** de exportar
um draft para este repositório (`export_draft`, já com `validate_draft`
aprovado), aplique esta transformação em cada operação do JSON antes de
commitar em `iac/`:

1. Pegue o array `request.url.query` (se existir e não for vazio).
2. Crie `request.query` como um novo array irmão de `request.header`, com os
   mesmos itens, no mesmo formato do header (`{"key": ..., "value": ...,
   "enabled": true}` — adicione `enabled: true` a cada item, já que o MCP não
   emite esse campo para query).
3. Remova a chave `query` de dentro de `request.url` (mantendo apenas
   `request.url.path`).

Exemplo — antes (como sai do `export_draft`):

```json
"request": {
  "method": "GET",
  "url": {
    "path": ["authorized_payments"],
    "query": [
      {"key": "status", "value": "<>status</>"}
    ]
  },
  "header": [],
  "body": {...}
}
```

Depois (formato final para este repo):

```json
"request": {
  "method": "GET",
  "url": {
    "path": ["authorized_payments"]
  },
  "header": [],
  "query": [
    {"key": "status", "value": "<>status</>", "enabled": true}
  ],
  "body": {...}
}
```

**Escopo do workaround:** isso se aplica só aos arquivos finais versionados
em `iac/` neste repo. Não tente enviar `request.query` (fora de `url`) para
as ferramentas do MCP (`add_draft_operation`, `update_draft_operation`,
etc.) — o servidor não lê esse campo daí; ele só reconhece
`request.url.query`. A transformação é estritamente pós-exportação/pós-validação.

Remova esta cláusula quando o bug for corrigido no `studio-connector-mcp`
(query passar a ser aceito nativamente como array irmão de `header`).
