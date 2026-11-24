---
name: studio-connector-patch
description: Use when the user asks to edit, fix, rename or extend a connector that is ALREADY published in Studio — not when building a new one. Triggers on "fix the connector", "add an operation to X", "rename", "corrigir o conector", "editar conector publicado".
---

# Patching a published connector

Never rebuild a published connector from scratch to change it: a rebuild loses
every real operation id, which means flows already wired to those operations
break. Edit the existing IAC, keeping every id.

There is no API client in this repo — reading from and writing to Studio is
done by the user in the Studio UI.

## The protocol — every step, every time

1. **Get the current version.** Ask the user to export the connector from the
   Studio UI and save it over `iac/{slug}.json` (or confirm the committed file
   is current). Then `uv run studio-iac tidy iac/{slug}.json`.
   `git diff iac/{slug}.json` shows whether Studio drifted from the repo —
   report any drift before editing.
2. **Record the baseline.** `uv run studio-iac validate iac/{slug}.json` and
   note the error and warning counts: those are **inherited** defects.
3. **Edit** the file. Follow
   [authoring-rules.md](../studio-connector-shared/authoring-rules.md).
   - Never change an existing `id`.
   - New operations/parameters get `"id": ""`, then
     `uv run studio-iac ids iac/{slug}.json`.
4. **Validate again.** No new errors may appear beyond the baseline. Errors in
   operations you edited must be fixed.
5. **Show the change and get an explicit yes.** Summarize `git diff` by
   operation name: created, updated, removed. The diff is what the user
   approves.
6. **Apply in Studio (user).** The user applies the change in the Studio UI —
   either editing the connector there or re-importing the file. Before they
   re-import, make sure they know whether their Studio import **updates the
   existing module in place** or **creates a new one**; a new module means new
   ids and flows must be rewired. Do not assume either behavior.
7. **Sync back.** After applying, export again from Studio over
   `iac/{slug}.json`, `tidy`, and check `git diff` contains only the intended
   change.

## Removing operations needs its own yes

Deleting an operation that a flow uses breaks that flow. Name each operation
to be removed and ask separately — approving the edit does not approve the
deletion.

## Inherited issues

A connector published before the current validation rules can carry many
errors. Fixing one description on a 300-operation legacy connector does not
oblige you to fix all 300. If the user wants the inherited defects fixed, that
is a separate, explicit piece of work — surface the count, do not silently
start fixing.

## Out of scope

Authorization groups, non-REST modules (soap, database, file, rfc, email,
as2), flows, and module duplication/publication/deletion. Those stay manual in
the Studio UI.
