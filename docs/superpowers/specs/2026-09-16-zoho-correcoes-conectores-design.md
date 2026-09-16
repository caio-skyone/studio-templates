# Correções nos conectores Zoho (Desk, CRM, Analytics, WorkDrive, Books)

**Data:** 2026-09-16
**Escopo:** corrigir três classes de defeito nos conectores Zoho já publicados e
propagar as correções para o Studio remoto, não só para o IAC local.

## Contexto

Os conectores Zoho foram gerados pelo pipeline `analyze → config → generate →
prose → import` a partir das specs oficiais em `github.com/zoho/*-oas`. Três
defeitos sobreviveram à geração:

1. **Bodies faltantes.** A spec `zohodesk-oas` tem 1846 `$ref` externos para
   `Common.json`; 51 das 326 operações `POST/PUT/PATCH` chegam sem
   `requestBody`. O gerador foi fiel à spec e emitiu `request.body.raw = ""`,
   deixando operações como `Contacts - Create Contact` e `Tickets - Create a
   ticket` sem como enviar corpo. O mesmo defeito, em menor escala, atingiu CRM,
   WorkDrive e Books.
2. **CONFIG no lugar errado (Analytics).** A API REST v2 do Zoho Analytics
   recebe a configuração da chamada no parâmetro de query `CONFIG`. O conector
   modelou isso como corpo da requisição em 78 operações, enquanto outras 22
   ficaram corretas — o conector está inconsistente consigo mesmo e as 78 não
   funcionam.
3. **Nomes de fallback no domínio Appointments (CRM).** A spec da Zoho traz
   `summary` cru (`"GET /Appointments__s"`) para esse módulo, e o domínio saiu
   como `Appointments  S` (dois espaços). Além disso o delete em massa perdeu o
   parâmetro `ids` e é inexecutável.

## Estado medido (2026-09-16)

| Conector | `module_id` | Ops no IAC | Publicado |
|---|---|---|---|
| Zoho Desk | `In23lcm6eQ` | 339 | sim |
| Zoho CRM | `PORy1eg57X` | 170 | sim |
| Zoho Analytics | `McnWvZq9EZ` | 176 | sim |
| Zoho WorkDrive | `ioneV7_cQY` | 163 | sim |
| Zoho Books (operação) | — | — | **não** |

## Decisões

- **Body genérico, sem pesquisa na doc HTML.** O parâmetro `body` segue o padrão
  já usado pelas operações corretas de cada conector. O Studio não valida o
  schema interno do corpo; descrever cada payload endpoint a endpoint não
  compensa o custo.
- **Converter todas as 78 ops do Analytics.** A API v2 é uniformemente
  CONFIG-como-query. Exceções encontradas durante a execução são sinalizadas ao
  usuário, não silenciadas.
- **Incluir Books e WorkDrive** na correção de bodies, por ser o mesmo defeito
  mecânico. Books recebe só correção de IAC local (não está publicado).
- **`sample: "{}"`** em todo parâmetro de corpo ou configuração criado, nunca
  string vazia.
- **Entrega via `pull_connector` + `patch_connector`**, um conector por vez, com
  `dry_run=True` e aprovação explícita antes de cada aplicação.

## Mudança 1 — Bodies faltantes

Para cada operação com método `POST`, `PUT` ou `PATCH` e
`request.body.raw == ""`:

- criar o parâmetro `body`, com `required: true`, `sensitive: false`,
  `sample: "{}"` e descrição em português no molde das operações já corretas do
  mesmo conector;
- definir `request.body.raw = "<>body</>"`, mantendo
  `options.raw.language = "json"`.

O `type` do parâmetro segue o que já predomina no conector, conforme
`.claude/skills/studio-connector-shared/authoring-rules.md` (`object` para JSON,
`string` para urlencoded):

| Conector | Ops afetadas | `type` do `body` |
|---|---|---|
| Zoho Desk | 39 | `object` |
| Zoho CRM | 3 | `object` |
| Zoho Books (operação) | 78 | `object` |
| Zoho WorkDrive | 4 | `string` |

As operações do Desk incluem `Contacts - Create Contact`, `Contacts - Update
Contact`, `Tickets - Create a ticket`, `Tickets - Update a ticket`, `Accounts -
Create Account`, `Tasks - Create task`, `Products - Create product` e `Events -
Create event`. As do CRM são `Settings - Add specific user`, `Actions - Share
Emails of a record` e `Actions - Unshare Emails of a record`.

Operações `GET` e `DELETE` sem corpo continuam sem corpo — a regra só se aplica
a métodos que carregam `requestBody` na prática da API.

## Mudança 2 — Zoho Analytics: CONFIG na query

Para cada uma das 78 operações que hoje têm o parâmetro `body`:

- remover o parâmetro `body` e definir `request.body.raw = ""`;
- criar o parâmetro `config` com `type: "string"`, `required: true`,
  `sensitive: false`, `sample: "{}"` e a descrição já usada pelas operações
  corretas;
- acrescentar `{"key": "CONFIG", "value": "<>config</>", "enabled": true}` a
  `request.query`.

O alvo é o formato que 22 operações já usam hoje — por exemplo `Bulk Data -
Create Export Job using SQL Query (Asynchronous)`. Onde a operação tiver um
sample específico em `scratchpad/iacs/zoho-analytics/query-config-samples.json`,
esse sample prevalece sobre `{}`.

As 13 operações sem `body` e sem `CONFIG` (`AutoML - Run AutoML Analysis`,
`Data Sources - Sync Data`, `Workspaces - Add Default Workspace`, `Workspaces -
Add Favorite Workspace`, `Folders - Make Default Folder`, `Columns - Auto
Analyse Column`, `Email Schedules - Create Email Schedule`, `Email Schedules -
Update Email Schedule`, `Email Schedules - Change Email Schedule Status`, `Email
Schedules - Trigger Email Schedule`, `Views - Add Favorite View`, `Views -
Refetch Data`, `Sharing - Enable Domain Workspace`) são revisadas uma a uma
contra a spec em `scratchpad/iacs/zoho-analytics/spec.json`: recebem o mesmo
tratamento quando a operação exigir configuração, e ficam como estão quando não
exigir.

## Mudança 3 — Zoho CRM: domínio Appointments

Renomear o domínio de `Appointments  S` para `Appointments` e substituir os
nomes de fallback, mantendo o inglês dos demais nomes de operação do conector:

| Nome atual | Nome novo |
|---|---|
| `Appointments  S - GET /Appointments__s` | `Appointments - List appointments` |
| `Appointments  S - POST /Appointments__s` | `Appointments - Create appointments` |
| `Appointments  S - PUT /Appointments__s` | `Appointments - Update appointments` |
| `Appointments  S - DELETE /Appointments__s/{ids}` | `Appointments - Delete appointments` |
| `Appointments  S - GET /Appointments__s/{appointmentId}` | `Appointments - Get appointment` |
| `Appointments  S - PUT /Appointments__s/{id}` | `Appointments - Update appointment` |
| `Appointments  S - DELETE /Appointments__s/id` | `Appointments - Delete appointment` |

As descrições em português dessas operações já estão corretas e não mudam. O
caminho (`request.url.path`) de cada operação também não muda — o segmento
literal `Appointments__s` é o nome real do módulo na API e está certo.

Em `Appointments - Delete appointments` (o delete em massa), acrescentar o
parâmetro `ids` (`type: "string"`, `required: true`, `sensitive: false`,
`sample: "1234567890,1234567891"`) e a entrada
`{"key": "ids", "value": "<>ids</>", "enabled": true}` em `request.query`.

As operações `Settings - Retrieve Appointment Preferences` e `Settings - Update
Appointment Preferences` estão corretas e ficam fora desta mudança.

## Entrega

Por conector publicado, nesta ordem — **Analytics, Desk, CRM, WorkDrive**:

1. `pull_connector(module_id)` — o draft preserva os ids reais do Studio, o que
   torna o patch uma atualização e não uma duplicação.
2. Aplicar as edições com as ferramentas de draft.
3. `validate_draft`.
4. `patch_connector(draft_id, dry_run=True)` e mostrar o plano ao usuário.
5. Aplicar apenas com um "sim" explícito. **Nunca** com
   `delete_missing_operations=True`. Se aparecer `drifted`, mostrar ao usuário
   antes de decidir sobre `allow_remote_drift`.
6. `export_draft` e regravar `iac/zoho-<produto>.json`, aplicando a normalização
   de `request.query` descrita no `CLAUDE.md` deste repositório.
7. Commitar.

O Zoho Books pula os passos 1, 4 e 5: a correção é feita direto no IAC local
`iac/zoho-books-operacao.json`, já que o conector não está publicado.

**Analytics vem primeiro por dois motivos:** é o defeito que impede o uso hoje, e
serve de teste do `patch_connector`. Existe um bug conhecido no
`push_connector` do `studio-connector-mcp`, que falha com `Invalid request
parameters` em qualquer draft com texto acentuado. Não se sabe se o
`patch_connector` compartilha o defeito. Se o dry-run ou a aplicação do
Analytics falhar com esse erro genérico, **parar e replanejar** antes de gastar
trabalho nos outros três — insistir não adianta e `skip_validation` não
contorna.

## Verificação

Para cada conector, depois do patch:

- `jq` sobre o IAC exportado: nenhuma operação `POST/PUT/PATCH` com
  `request.body.raw == ""`;
- Analytics: nenhuma operação com o parâmetro `body`; contagem de operações com
  `CONFIG` em `request.query` igual a 100 (22 atuais + 78 convertidas), ajustada
  pelo que for decidido nas 13 operações em revisão;
- CRM: nenhuma operação com `Appointments  S` no nome; `Appointments - Delete
  appointments` com `ids` na query;
- `get_connector_summary` de cada módulo com a contagem de operações inalterada
  (nenhuma criação ou remoção acidental).

## Fora de escopo

- Traduzir os nomes de operação para português — os conectores Zoho usam nomes
  em inglês e essa convenção fica como está.
- Rever descrições de parâmetros que já existem e estão corretas.
- Publicar o conector Zoho Books.
- O conector Zoho Projects, que não tem IAC neste repositório.
