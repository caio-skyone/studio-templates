---
name: studio-connector-plan
description: First phase of building a Skyone Studio REST connector — detect intent, gather API references, scope the use case, and map domains/endpoints before any IAC file is written. Use when the user wants to create/build a new Studio connector or module and iac/{slug}.json does not exist yet.
---

# Studio connector — plan phase

This skill covers everything **before** `iac/{slug}.json` is written. When the plan is confirmed, hand off to [`studio-connector-build`](../studio-connector-build/SKILL.md).

Authoring conventions: [`../studio-connector-shared/authoring-rules.md`](../studio-connector-shared/authoring-rules.md).
Template pattern (naming and hygiene conventions): [`../studio-connector-shared/template-pattern.md`](../studio-connector-shared/template-pattern.md).

---

## 1. Trigger

Apply when the user wants a **new** REST connector or module and
`iac/{slug}.json` does not exist yet. If it exists and the connector is
published, use [`studio-connector-patch`](../studio-connector-patch/SKILL.md)
instead.

Everything deterministic runs through the repo CLI (`uv run studio-iac …`).
It needs only `uv` and works on Windows, Linux and macOS — no MCP server.

---

## 2. Collect references

Ask the user for official API documentation before doing anything else. Do **not** web-search first — ask first.

| Source type | Action |
|-------------|--------|
| OpenAPI / Swagger URL | Fetch and parse. |
| REST API docs URL | Fetch and review. |
| PDF / Postman collection | Ask the user to paste or upload the content. |
| None available | Warn; offer to proceed from baseline knowledge or define operations one-by-one with the user. |

---

## 3. Measure before asking (OpenAPI spec present)

**Trigger:** an OpenAPI/Swagger spec is available as a local file. If there is
no spec, skip to section 4 and ask as usual.

Do **not** ask about scope in the abstract first. Save the spec as
`scratchpad/{slug}/spec.json`, run `uv run studio-iac analyze scratchpad/{slug}/spec.json`
and let the numbers drive the conversation.

1. **Survey.** `studio-iac analyze <spec>` — no config. It writes
   nothing. It returns: raw path and operation counts, a per-domain table
   (operations, query params, body params), the body-depth measurement
   (levels 1/2/3/recursive × params × names over 50 chars), the content types
   present, operation-name collisions, and every path placeholder with the name
   it would derive.
2. **Ask over the numbers.** Show the domain table and ask concretely —
   "Balance is 4 operations and 12 query params; Connect is 61 — include it?"
   — instead of "which workflows do you need?". One question at a time.
3. **Write `iac/{slug}.openapi-config.json`.** Once the user has chosen: `include_roots`,
   `domains` (with `block`), and `exclude` with a **reason** per cut. Format and
   field meanings: [`../studio-connector-shared/openapi-pipeline.md`](../studio-connector-shared/openapi-pipeline.md).
4. **Re-run with the config.** `studio-iac analyze <spec> --config <config>`
   gives the post-filter view. Confirm it with the user before anything is
   generated.

If step 1 reports operation-name collisions, they are not a failure — the
colliding shape keys are your `exclude` candidates. Show them to the user with
the reason you propose for each.

**Second, independent trigger — which build path.** Count the operations in the
confirmed scope:

| Confirmed scope | Path |
|---|---|
| more than ~20 operations, spec available | the bulk pipeline — carry the **config path** into build |
| ~20 or fewer, or no spec | incremental |

The cut is about fixed cost, not about size for its own sake: the pipeline
charges for writing a config, reading a report and orchestrating prose
subagents, while a small scope is a few operations written straight into the
file.

---

## 4. Scope (one question at a time)

For broad requests (e.g. "build an iFood connector") with **no spec to measure**, **do not map the entire API**. Ask the concrete use case first:

> "Which specific workflows or entities does this connector need to support?"

Wait for the answer before asking the next clarifying question. Avoid multi-question blasts.

Narrow until you have a clear, bounded set of endpoints to cover.

---

## 5. Map before building

On the bulk pipeline the config **is** the map — the domain table and the
`exclude` list you confirmed in section 3 replace the hand-written operations
table below. Do not transcribe operations into the thread.

With scope confirmed, plan the module before writing the IAC.

**Produce a planning summary:**

- **Auth type** (inferred from docs — e.g. `bearer-token`, `oauth-2`; confirm with user).
- **Domains**: group endpoints into logical domains (`Users`, `Orders`, `Products`, …).
- **Operations list**: `{Domain} - {Action}` per planned endpoint (see naming conventions in [`../studio-connector-shared/authoring-rules.md`](../studio-connector-shared/authoring-rules.md)).
- **Exclusions**: note what is intentionally out of scope.

Rules for the map:

- Global query params (`limit`, `skip`, `select`) are **not** separate operations — note them once in planning notes.
- Skip placeholder paths with no real endpoints (e.g. paths containing `RESOURCE` literally).
- List the planned operations in a table and ask the user to confirm or adjust before proceeding.

Example table:

| Domain | Action | Method | Path |
|--------|--------|--------|------|
| Users | Get all users | GET | `/api/v1/users` |
| Users | Get user by id | GET | `/api/v1/users/{id}` |
| Orders | Create order | POST | `/api/v1/orders` |

---

## 6. Hand off to build

When the user confirms the plan:

1. State the inferred auth type and ask for a final confirmation if not already given.
2. Invoke the **`studio-connector-build`** skill to write `iac/{slug}.json` and add operations.

> **Publishing is manual:** the workflow ends with a validated
> `iac/{slug}.json` that the user imports in the Studio UI. Set this
> expectation with the user up front.

Carry forward into the build skill:
- Module name / slug
- Confirmed auth type
- Confirmed operations list (domain + action + method + path)
- Any special notes (full-url paths, body modes, known header requirements)
- Which build path was chosen (bulk pipeline or incremental), and why
- On the bulk path: the **absolute path of `iac/{slug}.openapi-config.json`** and of the spec file — never a transcribed operations list
