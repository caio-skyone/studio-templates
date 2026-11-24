# OpenAPI → IAC pipeline (bulk path)

Use this path when an OpenAPI spec exists **and** the confirmed scope is above
~20 operations. Below that, or with no spec, use the incremental path in
[`../studio-connector-build/SKILL.md`](../studio-connector-build/SKILL.md).

The principle: **script the structure, LLM the language.** Deriving IAC from a
spec is deterministic. The only step that genuinely needs a model is the
Portuguese prose. Never transcribe operations or parameters through the context
window — the tools read and write files.

## The flow

```
spec.json ──► studio-iac analyze ──────────► domain table + body-depth measurement
                                             (user picks scope → you write the config)
config ──► studio-iac generate ────────────► iac.json + prose_worklist.json + report.json
                                                          │
                                        translation subagents (the only LLM step)
                                                          ▼
                                                 filled prose_worklist.json
                                                          │
                     studio-iac apply-prose ──────────────► iac/{slug}.json
                                                          │
                     studio-iac ids + validate ───────────► ready to import (Studio UI)
```

| Step | Command (`uv run studio-iac …`) | Writes |
|---|---|---|
| 1 | `analyze scratchpad/{slug}/spec.json` | nothing |
| 2 | you write `iac/{slug}.openapi-config.json` | the config |
| 3 | `analyze <spec> --config <config>` | nothing — post-filter view, confirm before generating |
| 4 | `generate <spec> --config <config> --out scratchpad/{slug}` | `iac.json`, `prose_worklist.json`, `report.json`, `sidecar.json` |
| 5 | translation subagents | the filled worklist |
| 6 | `apply-prose <iac.json> <prose_worklist.json> --out iac/{slug}.json` | the final IAC |
| 7 | `validate iac/{slug}.json` | nothing — gate before the user imports |

`generate` prints the **absolute paths** it wrote. Use them; do not guess.
The spec and generated artifacts stay in `scratchpad/{slug}/` (git-ignored);
the config and the final IAC are committed under `iac/`.

## The config

```jsonc
{
  "module": { "name": "Stripe", "description": "…",
              "authentication_type": "bearer-token",
              "strip_path_prefix": ["v1"] },

  "include_roots": ["customers", "invoices", "subscriptions", "balance"],

  "domains": { "customers.tax_ids": { "domain": "Customer Tax IDs", "block": "core" } },

  "exclude": [ { "key": "accounts.persons", "reason": "exact alias of accounts.people" } ],

  "headers": [ { "key": "Idempotency-Key", "param": "idempotency_key",
                 "methods": ["POST", "DELETE"] } ],

  "naming": {
    "generic_placeholders": { "add": ["subscription_exposed_id"], "remove": [] },
    "singular": { "history": "balance_transaction" }
  },

  "overrides": {
    "path_params": { "subscriptions:subscription_exposed_id": "subscription_id" },
    "body": { "subscriptions.post": { "mode": "skeleton",
                                      "raw": "{\"status\": \"<>new_status</>\"}" } },
    "auth_headers": { "add": ["x-tenant-signature"], "remove": ["token"] }
  }
}
```

`exclude[].reason` is **required** — it turns "N operations vanished" into an
auditable record.

## Shape key — the index for everything

The path, minus the prefix declared in `strip_path_prefix`, minus every
`{placeholder}`, joined by dots:

| Path | Shape key |
|---|---|
| `/v1/customers` | `customers` |
| `/v1/customers/{customer}/tax_ids` | `customers.tax_ids` |
| `/v1/customers/{customer}/tax_ids/{id}` | `customers.tax_ids` |

`domains` and `exclude` are keyed by shape key. When the target is one
**operation** rather than the resource, append the lowercase method:
`customers.tax_ids.post` — that is how `overrides.body` is keyed.

`overrides.path_params` is the single exception: its key is
`{shape_key}:{placeholder}`, because the target is one placeholder inside a
resource, not the resource.

**Blocks** (`core`, `billing`, `connect`, …) do two things: they group the
domain table the user reads when choosing scope, and they let you take
per-block checkpoints with the user.

## What the code already knows — do not put it in the config

- **Generic placeholders**, replaced by `{singular_previous_segment}_id`: `id`,
  `item`, `intent`, `fee`, `schedule`, `code`, `session`, `link`,
  `transaction`, `capability`, `person`, `feature`, `configuration`,
  `reversal`. So `/v1/payment_intents/{intent}` → `payment_intent_id` and
  `/v1/setup_intents/{intent}` → `setup_intent_id`. A **specific** placeholder
  (`customer`, `charge`, `invoice`, `account`) keeps the spec's own name.
- **English singularization**, including irregulars (`people` → `person`).

Config territory starts where the API gets idiosyncratic:
`subscription_exposed_id` is an internal Stripe name, and
`history` → `balance_transaction` is not a plural at all — it is a resource
alias. Both go under `naming`.

## Reading `report.json`

| Section | What to do with it |
|---|---|
| included operations | cross-check against the scope the user confirmed |
| excluded, with reason | paste into the scope summary you show the user |
| derived path param names | scan for a name that reads wrong; fix via `overrides.path_params` |
| body decisions per operation | confirm no operation you expected to carry a body came out empty |
| skipped headers | optional and auth headers that did not enter — if the user needs one, declare it under `headers` or `overrides.auth_headers.remove` |

## What to check after generating

Seven checks, in this order. Each one catches a defect class that validates
clean and imports clean.

1. **Operation count.** Compare `report.included` against the scope the user
   confirmed. A path that is 100% placeholder (`/{module}`) reduces to an
   EMPTY shape key: it has no root segment, no `include_roots` entry selects
   it, and it disappears **without appearing in `report.excluded`** — 13
   operations on a real Zoho CRM build, exactly the generic CRUD.
2. **Writes without a body.** Cross-check every POST/PUT/PATCH in the IAC
   against the ones carrying `requestBody` in the spec. `report.body_decisions`
   now carries a `reason` whenever the strategy is `none` with a requestBody
   present — an empty reason there means the endpoint genuinely has no body.
3. **Braces in the path.** Search `request.url.path` for `{`. There should be
   none: composite segments are parameterized. A survivor is a generator bug,
   and `studio-iac validate` fails on it.
4. **Empty samples.** `report.empty_samples` counts the parameters left with
   no sample. A number in the hundreds means the spec had no `enum`, `example`,
   `default` or `format` to work from — decide whether that scope is worth
   shipping as is.
5. **Renames and fallbacks.** `report.renamed_params` lists every query/header
   parameter that took a suffix because its name collided with a path
   parameter. `report.name_fallbacks` lists the operations named from an
   `operationId` or, worse, from the operation key — those are the ones to read
   before publishing.
6. **Body samples.** `report.body_decisions` names the strategy per operation.
   Every `single-object` on `application/json` should carry a derived
   `body_sample` in the worklist — the generator fills it from the schema, and
   the translator is told not to touch what is already there. An empty one means
   the spec described the body with nothing more than a `$ref` to an empty
   schema; that is where a hand-written sample is legitimate.
7. **Markup in descriptions.** `studio-iac validate` warns with `description carries
   markdown or HTML`. `source_en` reaches the worklist already flattened, so a
   warning here means the translator introduced it — fix the description, not
   the spec.

## Seven things the config does NOT let you do

- **`strip_path_prefix` is an ORDERED prefix, not a list of alternatives.**
  `["v1","v2"]` means `/v1/v2`. On a real build that made the 6 operations of
  `/v2/wallet_connect` disappear. Declare the dominant prefix and treat the
  others as literal roots.
- **`include_roots` is required** (`min_length=1`). There is no "include
  everything".
- **`domains` and `overrides.path_params` are keyed by the shape key WITHOUT
  any `item` marker**, even when the operation key in the report carries one.
- **`overrides.body.mode` accepts only `skeleton` or `none`.** `raw` is
  invalid — despite `raw` being the field where the `<>body</>` goes.
- **`overrides.body.content_type` is optional and defaults to
  `application/json`.** Declare another value only for a urlencoded skeleton
  (`application/x-www-form-urlencoded`) — a skeleton with no Content-Type ships
  as a raw body and the API answers 415.
- **`kind` in the worklist accepts only `path`, `query`, `header` or `body`.**
  A multipart field added by hand uses `kind: "body"`.
- **The operation key is positional.** Every placeholder emits an `item` marker
  where it appears: `/a/{x}/b` is `a.item.b.get`, not `a.b.get`. That is what
  keeps `/v3/stats/total` and `/v3/{domain}/stats/total` apart.
- **A fragmented spec is merged BEFORE anything else.** Snowflake ships 51
  files with cross-`$ref`; Zoho publishes an official OAS only for CRM, Desk,
  Analytics and WorkDrive; HubSpot runs concurrent rollouts, where 11 api+version
  pairs have more than one rollout and 7 of those have different paths — pick
  deterministically: most operations, ties broken by the larger id. Merge
  before measuring, always.

## When generation aborts

`studio-iac generate` refuses to write anything if two paths produce the
same `{Domain} - {Summary}`. `OperationNameCollision` carries the colliding
pairs **with their shape keys** — that list is your `exclude` candidate list,
not a failure. The three usual categories:

- exact aliases (`accounts/persons` ≡ `accounts/people`)
- legacy routes (`customers/{c}/cards`)
- nested collections that duplicate a filterable top-level one
  (`customers/{c}/subscriptions` ≡ `/v1/subscriptions?customer=`)

Add each one to `exclude` with a reason and regenerate.

`GenerationAborted` carries the whole report with offline-validation violations
grouped by operation. Fix the config, do not hand-edit `iac.json`.

## Closing the loop

After the user imports in the Studio UI and exports back over
`iac/{slug}.json`, run `studio-iac tidy` and `git diff`. The only expected
differences are the real ids Studio assigned and the defaults listed in
[`server-normalization.md`](server-normalization.md). Anything else is a real
defect, not noise.
