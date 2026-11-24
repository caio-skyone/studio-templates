---
name: studio-connector-document
description: Writes Portuguese connector documentation in docs/connectors/{slug}.md (published by the MkDocs/Zensical site) from iac/{slug}.json or session context. Use when the user asks to document a module or connector, or generate connector markdown docs.
---

# Connector documentation (PT)

## Trigger

User wants **module/connector documentation** for Studio REST IAC → `docs/connectors/{slug}.md`.

Language: **Portuguese** for all prose. Operation `name` stays as in IAC (often English `{Domain} - {Action}`).

## Output path

**The user's path wins.** If they named a file or directory — in this thread or
in an earlier instruction still in scope — write exactly there, and do not also
write a copy at the default. Only when no path was given does the default apply:

| Item | Rule (default) |
|------|------|
| Directory | `docs/connectors/` |
| Filename | `{slug}.md` — lowercase, hyphens, API id (`dummyjson`, `stripe`) |
| Title `#` | Module **display name** from IAC (`IACModule.name`), not necessarily slug |

Report the absolute path you wrote to, always.

**Add the page to the site nav** — a new file needs an entry under
`Conectores:` in `mkdocs.yml`, in alphabetical order, or it will not show in
the menu. Check with `uv run zensical build --strict`.

## Workflow

```
1. Resolve slug → iac/{slug}.json (user, `ls iac/`, or path)
2. Collect facts (sources below) — never load full huge IAC JSON into context
3. Draft doc from [doc-template.md](../studio-connector-shared/doc-template.md)
4. Fill gaps: web (official API docs) or ask user — never invent
5. Write docs/connectors/{slug}.md and add it to the mkdocs.yml nav
6. Tell user what is still missing (*não informado* / lacunas)
```

## Data sources (priority)

| Priority | Source | Use for |
|----------|--------|---------|
| 1 | **`iac/{slug}.json`** | Partial extract only (see [iac-extract.md](../studio-connector-shared/iac-extract.md)) |
| 2 | **Session** | API research already in thread |
| 3 | **Existing docs** | Other `docs/connectors/*.md` for tone and structure |
| 4 | **Web** | Contexto, auth account fields, official doc URL |
| 5 | **User** | Anything still unknown after above |

Never load a whole large IAC into context — extract only the fields you need.

## IAC fields (domain model)

What IAC actually carries (JSON shape reference: [iac-extract.md](../studio-connector-shared/iac-extract.md)):

| Model / field | Doc section |
|---------------|-------------|
| `IACModule.name` | Title `#` |
| `IACModule.description` | Seed for **Contexto** only — expand with API knowledge; do not copy blindly if thin |
| `IACModule.settings.authentication_type` | **Autenticação → Tipo** (map via [auth-config.md](../studio-connector-shared/auth-config.md)) |
| `IACOperation.name` | Operations table — **Nome da Operação** |
| `IACOperation.description` | Operations table — use PT text; if null → `*sem descrição*` |
| `IACRestRequest.method` | Operations table — **Método** |
| `IACOperation.parameters` | Not in user template — omit unless user asks for appendix |

**Not in IAC (usually):** API business context beyond `description`, connected-account variable values, official doc URL, OAuth token endpoint URL. Treat as **lacunas** until web search or user fills them.

## Section rules

### Contexto

- What the API does + common domains/concepts.
- Start from `description` + prior API research in session.
- If unknown: short bullet `*A preencher:* …` and ask user or search official docs.
- Do not fabricate endpoints or auth behavior.

### Autenticação

- **Tipo:** Portuguese label from `authentication_type` → [auth-config.md](../studio-connector-shared/auth-config.md).
- **Configuração da conta conectada:** pick **one** variable table for that auth type from [auth-config.md](../studio-connector-shared/auth-config.md).
- Placeholders `{{…}}` as in template (Studio account refs). Unknown cell → `*não informado*`.
- Extra keys only when docs/user supply them — add rows to the fallback table, do not guess secrets.

### Operações

Build table from every operation:

| Nome da Operação | Método | Descrição da Função |
| ---------------- | ------ | ------------------- |

- Sort: same order as IAC (or alphabetical by domain prefix if user asks).
- **Método:** uppercase `GET`, `POST`, … from `request.method`.
- Build the table with the extract in [iac-extract.md](../studio-connector-shared/iac-extract.md), not by reading the JSON.
- If an operation sends a raw binary body (Content-Type = the file's mime
  type, not multipart — see [authoring-rules.md](../studio-connector-shared/authoring-rules.md)),
  add a short note telling the user to check **"Forçar bufferização da
  requisição"** in that operation's advanced options in the Studio UI — IAC
  has no field for it, so it cannot be set from the IAC.

### Documentação oficial

- Single best URL (API root or docs home). From module research, session context, or web search.
- If only per-operation links exist, use API-wide docs link.
- Missing → `*Link não informado — forneça a documentação oficial.*`

## Lacunas (required honesty)

After writing the file, report to the user:

- Which sections used only IAC vs exported JSON vs web vs assumptions (none).
- List fields left `*não informado*` or `*A preencher*`.
- Offer to fill via user input or web search.

**Never** fill Contexto or auth tables with plausible fiction.

## Related skills

- Building/editing IAC: [studio-connector-build](../studio-connector-build/SKILL.md)
- Connected account creation: [studio-connector-account](../studio-connector-account/SKILL.md) — its `<>template</>` placeholders should align with the doc's account-table variables

## Reference files

- [doc-template.md](../studio-connector-shared/doc-template.md) — output skeleton (user format)
- [auth-config.md](../studio-connector-shared/auth-config.md) — auth type labels + account tables
- [iac-extract.md](../studio-connector-shared/iac-extract.md) — partial reads of large JSON
