---
name: studio-connector-build
description: Build phase of a Skyone Studio REST connector — write the IAC file iac/{slug}.json directly (from an OpenAPI spec via the studio-iac CLI, or by hand) and map operations and parameters. Use when a connector plan exists and you need to create the IAC and map operations/parameters.
---

# Studio connector — build phase

This skill covers everything from creating `iac/{slug}.json` through mapping
all operations and parameters. It assumes a confirmed plan from
[`studio-connector-plan`](../studio-connector-plan/SKILL.md). When operations
and parameters are fully mapped, hand off to
[`studio-connector-publish`](../studio-connector-publish/SKILL.md).

Authoring conventions (request schema, `<>param</>` references, body modes,
snake_case names): [`../studio-connector-shared/authoring-rules.md`](../studio-connector-shared/authoring-rules.md).

> Editing a connector that is **already published**? Do not rebuild it — a
> rebuild loses the real operation ids and breaks the flows wired to them. Use
> [studio-connector-patch](../studio-connector-patch/SKILL.md).

---

## 1. Hard rules

1. **The file is the draft.** The connector lives in `iac/{slug}.json`
   (an `IACModule` JSON). There is no MCP server and no draft store: create,
   read and edit that file directly. Git is the history.
2. **Deterministic steps go through the CLI** — `uv run studio-iac <command>`.
   Never hand-roll what it already does (generation from OpenAPI, prose merge,
   id generation, validation). It runs the same on Windows, Linux and macOS.
3. **Research only the target REST API** — use the official docs of the API
   being connected, not Studio internals.
4. **Checkpoint at every macro block** — on a build of hundreds of operations,
   stop at the end of each block (Core, Billing, Connect) and ask before going
   on. Short report: what finished, and the request to continue.
5. **Announce before the translation batches** — stop at the translation step,
   report the slices, and wait for the go-ahead before dispatching subagents.

Working files (spec, `iac.json`, `prose_worklist.json`, `report.json`, slices)
go in `scratchpad/{slug}/` — it is git-ignored. Only the final IAC
(`iac/{slug}.json`) and the generator config (`iac/{slug}.openapi-config.json`)
are committed.

---

## 2. Choose the path

| Path | When | Section |
|---|---|---|
| **Bulk pipeline** | an OpenAPI spec exists **and** the confirmed scope is above ~20 operations | 3 |
| **Incremental** | no spec, or ~20 or fewer operations | 4–5 |
| **Import a finished IAC** | the user handed you a complete `IACModule` JSON | save it as `iac/{slug}.json`, then section 6 |

The plan skill normally hands you this decision along with the config path. If
it did not, decide here and say which path you took and why.

---

## 3. Bulk pipeline (spec-driven)

The full manual — config format, shape keys, `report.json`, collision
recovery — is
[`../studio-connector-shared/openapi-pipeline.md`](../studio-connector-shared/openapi-pipeline.md).
Read it before starting. The steps here are the orchestration.

1. **Generate.**
   `uv run studio-iac generate scratchpad/{slug}/spec.json --config iac/{slug}.openapi-config.json --out scratchpad/{slug}`
   writes `iac.json`, `prose_worklist.json`, `report.json` and `sidecar.json`.
   If it aborts with `OperationNameCollision` or `GenerationAborted`, fix the
   **config** and regenerate — never hand-edit `iac.json`.
2. **Review the report** with the user: what was included, what was cut and
   why, the derived path param names, the body decisions, the skipped headers.
3. **Translate.** Split `prose_worklist.json` into one file per slice and
   dispatch one
   [`studio-connector-translator`](../../agents/studio-connector-translator.md)
   per slice file, in parallel, each prompted with the absolute path to its
   slice. Protocol — slicing, checking the slices on disk, merging —
   [`../studio-connector-shared/prose-contract.md`](../studio-connector-shared/prose-contract.md).
   Never give two subagents the same key. This is the only step that uses a
   model.
4. **Merge and apply.** Reassemble one worklist file, then
   `uv run studio-iac apply-prose scratchpad/{slug}/iac.json scratchpad/{slug}/prose_worklist.json --out iac/{slug}.json`.
   It refuses a worklist with an invented or missing key
   (`ProseWorklistMismatch`).
5. Go to section 6.

---

## 4. Incremental: create the file

Start from this skeleton, saved as `iac/{slug}.json`:

```json
{
  "id": "",
  "name": "Example API",
  "description": "Conector REST para ...",
  "type": "rest",
  "settings": { "authentication_type": "bearer-token" },
  "operations": []
}
```

Valid `authentication_type` values:

```
no-auth | basic | bearer-token | oauth-1 | oauth-2 | cookie |
aws | oauth2-jwt | ca-certificate | google-oauth | header-auth | mtls-certificate
```

Infer the auth type from API docs when possible, then confirm with the user.

---

## 5. Add operations and parameters

Append to `operations`. Full schema in
[`../studio-connector-shared/authoring-rules.md`](../studio-connector-shared/authoring-rules.md).
Leave every `id` as `""` — section 6 fills them.

```json
{
  "id": "",
  "name": "Users - Get user by id",
  "description": "Retorna um usuário pelo id.",
  "parameters": [
    { "id": "", "name": "user_id", "type": "string", "description": "ID do usuário.",
      "required": true, "sensitive": false, "sample": "123" }
  ],
  "request": {
    "method": "GET",
    "urlType": "base-url",
    "url": { "path": ["api", "v1", "users", "<>user_id</>"] },
    "query": [],
    "header": [],
    "body": { "mode": "raw", "raw": "", "options": { "raw": { "language": "json" } } }
  }
}
```

Key rules:

- `request.url.path` is a **segment array** — never a URL string.
- Query string goes in `request.query` (sibling of `header`), never `url.query`.
- Do **not** use OpenAPI field names (`http_method`, `path`, `produces`, …).
- Do **not** add auth parameters (tokens, API keys) unless the user explicitly
  asks — auth is handled by the connected account.
- Each parameter needs `name` (snake_case), `type`
  (`object | string | number | array`), `required`, `sensitive`, `sample`.

Editing technique: for a handful of operations, edit the file with the Edit
tool. For many, write a short Python script (`uv run python script.py`) that
loads the JSON, appends, and dumps with `ensure_ascii=False, indent=2` —
never paste a large module through the context window.

---

## 6. Fill ids and validate

```sh
uv run studio-iac ids iac/{slug}.json
uv run studio-iac validate iac/{slug}.json
```

`ids` generates a UUID for every module, operation and parameter whose `id` is
empty; existing ids are never touched. `validate` runs the full offline rule
set (lengths, snake_case, references, duplicates, multipart, secrets, markup)
and exits non-zero on errors. Fix every error; review warnings with the user.

For large files, read slices instead of the whole JSON —
[`../studio-connector-shared/iac-extract.md`](../studio-connector-shared/iac-extract.md).

---

## 7. Naming convention

**Default (Template Pattern):** operation `name` follows `{Domain} - {Action}`
in English (e.g. `Users - Get all users`) — see
[`../studio-connector-shared/template-pattern.md`](../studio-connector-shared/template-pattern.md).
The user may specify a different convention in the same thread.

Operation `description`: concise, in Portuguese, plain — what the call does.

---

## 8. Hand off to publish

When `validate` is clean, go to
[`studio-connector-publish`](../studio-connector-publish/SKILL.md).
