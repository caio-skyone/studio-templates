---
name: studio-connector-publish
description: Publish phase of a Skyone Studio REST connector — validate iac/{slug}.json with the studio-iac CLI and guide the user through importing it in the Studio UI. Use when an IAC file is complete and the user wants to validate, publish or import it.
---

# Studio connector — publish phase

Validation and the final disposition of `iac/{slug}.json` produced by
[`studio-connector-build`](../studio-connector-build/SKILL.md). Afterwards,
offer a connected account
([`studio-connector-account`](../studio-connector-account/SKILL.md)) and
documentation ([`studio-connector-document`](../studio-connector-document/SKILL.md)).

There is no API client in this repo: **the import into Studio is done by the
user in the Studio UI.** Never claim the connector was published — only the
user can confirm that.

---

## 1. Validate (gate)

```sh
uv run studio-iac validate iac/{slug}.json
```

- Errors block. Fix them in the file and run again until it exits 0.
- Warnings: summarize them for the user; fix the ones that are real.
- Summarize what was built: number of operations, domains covered, auth type,
  and the path prefix shared by the operations, if any.

Checks only Studio can do (not covered locally): a module name already used in
the space, and server-side schema rules newer than this validator.

---

## 2. Import in the Studio UI (user)

Tell the user:

1. The file to import: the absolute path of `iac/{slug}.json`.
2. To import it as an IAC module in the Studio UI.
3. Studio may rename a module whose name already exists in the space to
   `Nome(01)`, `Nome(02)`, … — ask them to check the name after import.

Wait for the user to confirm the import before going on.

---

## 3. Sync back what Studio assigned

After the import, Studio issues its own module and operation ids. Ask the user
to export the connector from the Studio UI and save the export over
`iac/{slug}.json`, then:

```sh
uv run studio-iac tidy iac/{slug}.json
uv run studio-iac validate iac/{slug}.json
git diff --stat iac/{slug}.json
```

`tidy` removes the legacy `request.url.query: []` the export injects (see
[`../studio-connector-shared/server-normalization.md`](../studio-connector-shared/server-normalization.md)).
The committed file must carry the **real Studio ids** — the patch skill
depends on them.

---

## 4. Account and docs (optional)

- Connected account: [`studio-connector-account`](../studio-connector-account/SKILL.md).
- Documentation in `docs/connectors/{slug}.md`:
  [`studio-connector-document`](../studio-connector-document/SKILL.md).
