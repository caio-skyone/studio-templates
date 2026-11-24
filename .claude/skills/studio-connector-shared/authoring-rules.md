# IAC authoring rules (REST)

Apply on every edit to `iac/{slug}.json`, before `uv run studio-iac validate`.

## Parametrization and naming
- Parameterize every variable you can (path segments, query values, headers,
  body fields).
- Hardcode in path/body only when the user explicitly asks.
- Example values belong in parameter `sample`, not hardcoded in routes.
- Parameter `name`: snake_case only (`^[a-z][a-z0-9_]*$`, e.g. `user_id`,
  `order_code`.
- Descriptions: concise, max 25 words; match the user's language unless told otherwise.
- Each parameter needs: `name`, `type` (object|string|number|array), `required`,
  `sensitive`, `sample`.

## Parameter references
In `request.url.path`, `request.query`, `request.header`, and
`request.body.raw`, reference parameters as:
`<>parameter_name</>`

## Operation — required schema
Do NOT use OpenAPI field names (http_method, path, produces, consumes,
responses, parameters).
Correct shape:
```
{
  "id": "",
  "name": "List Repos",
  "description": "optional",
  "parameters": [ ... ],
  "request": {
    "method": "GET",
    "url": {"path": ["user", "repos"]},
    "query": [{"key": "per_page", "value": "<>per_page</>"}],
    "header": [{"key": "Authorization", "value": "Bearer <>pat</>"}]
  }
}
```
url.path is a segment array — NEVER a URL string.
Parameters live in the operation's `parameters` array. New entities get
`"id": ""`; `uv run studio-iac ids <file>` fills them.

## Request body (`body.mode` = `raw`)

Decide by **content type and method**, never by how the JSON looks:

| Situation | Modelling | `body.raw` |
|---|---|---|
| GET / DELETE, **or** no `requestBody` | no body | `""` |
| `application/x-www-form-urlencoded` | **one** parameter, type `string` | `"<>body</>"` |
| `application/json` | **one** parameter, type `object` | `"<>body</>"` |
| `multipart/form-data` | granular lines, **required fields only** | one `key:<>value</>` per line |
| binary body, **not** multipart (Content-Type *is* the file's mime type — e.g. `application/pdf`, `image/png`, `application/octet-stream`) | **one** parameter for the raw content, **plus** a header parameter for `Content-Type` | `"<>body</>"` |

Multipart lines may carry file metadata:
`key:<>value</>:mime:<>mime_param</>:filename:<>filename_param</>`
(the mime slot is required whenever the filename slot is set). Both slots are
**parameter references, never literal text** — never write
`file:<>file</>:mime:application/pdf:comprovante.pdf`. Create a `mime_type`
parameter (required, `sample: "application/pdf"`) and a `file_name` parameter
(required, `sample: "comprovante.pdf"`) and reference both. The literal value
belongs in the parameter's `sample`, exactly like any other body field —
never inline in `body.raw`. Never a single object parameter for a multipart
body, and **never set `Content-Type` by hand** for one — without the boundary
the request breaks.

### Binary body — the Content-Type header IS the file type

When the API takes the raw file bytes as the entire body (not wrapped in
multipart), the request needs a `Content-Type` header equal to the file's mime
type (`application/pdf`, `image/png`, …). That value varies with whatever file
the user sends, so it is a parameter like any other header — create one
(required, `sample` set to the expected mime type) and reference it in
`request.header`. Never hardcode the mime type as a literal header value.

This is also the one body shape where the Studio interface has a setting IAC
cannot express: **"Forçar bufferização da requisição"** ("force request
buffering"), an advanced option in the Studio operation editor with no
equivalent field in IAC — it cannot be set from here. If
documentation is requested for a connector with a binary-body operation, say
explicitly in `docs/connectors/{slug}.md` that the user must check that
option in the Studio UI (if not already checked) for the operation to work.

Three rules the table depends on:

- **A parameterized skeleton (`{"status": "<>new_status</>"}`) exists only when
  asked for** — declared under `overrides.body` in the generator config (see
  [`openapi-pipeline.md`](openapi-pipeline.md)), or requested by the user in
  the thread. Never inferred from the body "looking small and predictable".
  That inference cost three round trips and one discarded generation on a
  279-operation build.
- **Never drill into nested body properties.** The 50-character limit on
  parameter `name` is a wall, not a preference: at depth 3 of the reference
  spec, 106 names exceeded it (worst case
  `payment_method_options[us_bank_account][financial_connections][filters][account_subcategories]`).
  One `object` parameter carries the whole nested body.
- **A `requestBody` on a GET is a phantom.** Some specs attach one to every
  method with empty `properties`. Filter by method first.

## Headers and query params — opposite policies, one reason

The platform fact: a header with an empty value is sent **with the key present
and the value empty** (`X-Foo: `), exactly like a formdata line. A query param
with an empty value the Studio **discards**. That asymmetry is why the two have
opposite defaults.

An optional header the user leaves blank does not disappear — it reaches the API
as an empty header, and some APIs reject that.

| Header origin | Enters the connector? |
|---|---|
| `in: header` in the spec, `required: true` | **yes** |
| `in: header` in the spec, optional | **no** — recorded in `report.json` as available |
| auth header (name matches `authorization`, `token`, `api_key`, `apikey`, `access_token`, `bearer`, `x-api-key`) | **no** — the connected account controls it |
| declared under `headers` in the generator config | **yes, always** — declaring is the explicit instruction |
| asked for explicitly by the user | **yes** — the rule yields to their wish |

**Query params: emit all of them**, required and optional alike — the empty one
is discarded and costs nothing. `expand` becomes the key `expand[]`. Do not
expand `object`/`deepObject` query params: what varies in them is the query
**key** (`created[gte]`, `metadata[field]`, `recurring[interval]`), not the
value, so the description must tell the user to edit the key in the operation.

All of this is default, not law. If the user asks for a specific optional
header, or a body shaped a particular way, that is what you do.

### An API-optional header can be required in the connector

Depending on a provider's implicit default is a risk. `Stripe-Version` is the
canonical case: without it, the account's configured version decides the shape
of every response, and it can change under you.

Promoting one means three places, never one:

1. `required: true` on the header entry in the connector config.
2. The parameter description saying it is mandatory **in this connector**.
3. `docs/connectors/{slug}.md` explaining the divergence between API and
   connector.

### `key` is the wire, `name` is the parameter

`request.query[].key` and `request.header[].key` are the literal strings sent
on the wire. The parameter `name` they reference is snake_case, and the two do
**not** have to match. This is what lets you represent `CONFIG`, `url[]`,
`StartTime<`, `StartTime>` and `forward.url` without breaking the snake_case
rule: the parameters are `config`, `url`, `start_time_before`,
`start_time_after`, `forward_url`, and the keys stay as the API wrote them.

### Two query formats — use `request.query`

`request.query` is the sibling of `request.header` and is what you should
write. `request.url.query` is legacy: the server stringifies it into the
endpoint. `studio-iac validate` warns on `url.query`, and warns harder when an
operation fills both — the server sends both, so a shared key arrives twice.

## Paths and URLs
- `request.url.path` is a segment array joined with `/` and prefixed by the
  connected account host (outside IAC).
- Example: host `https://api.example.com`, endpoint
  `https://api.example.com/api/v1/users` → path `["api", "v1", "users"]`.
- All operations in one connector must share the same path prefix level.
- `urlType` (alias for url_type):
  - `base-url` (default): path[] is appended to the connected account host.
  - `full-url`: path[] contains the entire URL including host, for calling a
    different API.

## Module metadata
- Module `type` is `rest` (lowercase).
- Set `settings.authentication_type` directly in the file.
- Valid values: no-auth | basic | bearer-token | oauth-1 | oauth-2 | cookie |
  aws | oauth2-jwt | ca-certificate | google-oauth | header-auth |
  mtls-certificate
- Infer auth from docs when possible, then confirm with the user.

### Descriptions are plain text

`description` — of the module, of an operation, of a parameter — is rendered
**literally** by the Studio. Nothing is parsed. `**bold**` reaches the user with
the asterisks, `&quot;` as the entity, `<br>` as the tag.

So markdown and HTML in a description are forbidden, whoever is writing:
generator, translator or you, by hand. Convert the intent into prose instead of
deleting the markers — `<ul><li>A</li><li>B</li></ul>` becomes "A; B", a
`[texto](https://exemplo.dev)` link becomes just "texto".

`studio-iac validate` warns on what it finds (`description carries markdown or
HTML`). It is a warning, not an error, only because a connector published before
this rule can carry markup that predates it — not because it is optional in new
work. The one exception is an explicit, reasoned request from the user for
markup in that specific field.

The `<>parameter_name</>` reference is not markup and never gets stripped.

## CLI quick reference

All commands: `uv run studio-iac <command> --help`.

| Command | Does |
|---|---|
| `validate [files…]` | offline rule set; exits 1 on errors (default: every IAC in `iac/`) |
| `ids <files…>` | UUID for every module/operation/parameter with an empty `id` |
| `tidy [files…]` | removes the legacy `request.url.query: []` |
| `summary <file>` | name, auth, one line per operation (`--grep`, `--limit`) |
| `analyze <spec> [--config]` | measures an OpenAPI spec |
| `generate <spec> --config --out` | `iac.json` + `prose_worklist.json` + `report.json` |
| `apply-prose <iac> <prose> --out` | merges the translated prose |

Defaults the Studio injects: see
[`server-normalization.md`](server-normalization.md).

## Patching a published connector

Same rules, with two differences: existing ids are real Studio ids and must
never be regenerated, and errors the connector already had on operations you
do not touch are inherited, not yours. The full protocol is in
[studio-connector-patch](../studio-connector-patch/SKILL.md).
