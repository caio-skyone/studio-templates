# Defaults que o Studio injeta

O Studio preenche alguns campos que você pode não ter escrito, e eles aparecem
quando o conector é exportado pela UI de volta para `iac/{slug}.json`. Nenhum é
um bug — o payload do Studio os exige. Mas fazem qualquer `git diff` entre "o
que eu escrevi" e "o que o Studio exportou" acusar diferenças que não existem.

| Campo | Valor injetado | Quando |
|---|---|---|
| `request.query` | `[]` | nenhuma query escrita |
| `request.query[].enabled` | `true` | campo omitido na query |
| `request.url.query` | `[]` | formato legado, injetado em toda operação |
| `request.urlType` | `"base-url"` | campo omitido |
| `request.body` | `{"mode":"raw","raw":"","options":{"raw":{"language":"json"}}}` | campo omitido |
| `request.header[].enabled` | `true` | campo omitido no header |
| parâmetro `description` | `" "` (um espaço) | descrição omitida |

> `request.query` e `request.url.query` são duas representações distintas e o
> Studio envia **as duas**. `request.query` vira o record
> `volatile.query` `{key: {value, enabled}}`; `request.url.query` é
> stringificada no endpoint e, nesse caminho, só `key` e `value` são lidos —
> `enabled` é ignorado. Escreva sempre `request.query`.

## Limpeza antes de commitar

`uv run studio-iac tidy iac/{slug}.json` remove o `request.url.query: []`
injetado, deixando `request.url` só com `path`. É higiene de arquivo: o valor é
sempre `[]` e não duplica nada na requisição real.

## Se você está comparando à mão

Escreva os defaults acima explicitamente no IAC que você gera (o gerador
OpenAPI já faz isso) — assim o export do Studio volta igual e o `git diff` fica
limpo. Ao comparar, trate `null`, `""` e `" "` como o mesmo valor em qualquer
`description`.

## Header vazio é enviado; query param vazio não

Um header cujo valor resolve para string vazia é enviado **com a chave presente
e o valor vazio** (`X-Foo: `), exatamente como uma linha de `multipart`. Um
query param de valor vazio, ao contrário, o Studio **descarta**.

Por isso as duas políticas são opostas:

| | Default |
|---|---|
| Query params | emitir **todos**, obrigatórios e opcionais — o vazio some sozinho |
| Headers | emitir **só os obrigatórios** — um opcional vazio vira `X-Foo: ` na requisição real |
| Headers de autenticação | **não emitir** — a conta conectada os controla |

Isto é default, não lei. Se você precisa de um header opcional específico,
inclua-o: peça explicitamente, ou declare-o em `headers` no config do conector.
O `report.json` do gerador lista, em `skipped_headers`, todo header que ele
deixou de fora e por quê — é de lá que sai a lista do que está disponível para
acrescentar.
