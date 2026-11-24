# Prose contract (translation subagents)

`studio-iac generate` writes `prose_worklist.json` with every
`description` empty and the English source filled in. Filling it is the only
step of the pipeline that needs a model.

The translator's contract lives in the agent definition —
[`../../agents/studio-connector-translator.md`](../../agents/studio-connector-translator.md).
Do not restate it in the dispatch prompt. This file is the **operator's** half:
how to slice, dispatch, check and merge.

## The worklist

```jsonc
{
  "parameters": [                     // keyed by NAME: 1,553 occurrences → 91 names
    { "name": "status", "kind": "query", "occurrences": 12,
      "domains": ["Meters", "Invoices", "Subscriptions"],
      "source_en": "The status of the meter.",
      "note": "shared by 3 domains — the description must serve all of them",
      "description": "" }
  ],
  "operations": [                     // keyed by unique op_key
    { "op_key": "customers.post", "name": "Customers - Create customer",
      "source_en": "Creates a new customer object.",
      "description": "", "body_sample": "{\"name\":\"Widget\"}" }
  ]
}
```

`body_sample` arrives **already derived from the schema** wherever the spec
described the body. It is data, not prose: nobody overwrites it.

## Dispatch

1. **Sweep `source_en` first.** Design notes, "Full API documentation: …", empty
   text, an abnormally long block — spec junk. A translator translates junk
   faithfully, so it is the operator who cuts it, before dispatching.
2. **Split into one FILE per slice** — `scratchpad/slices/slice1.json` …
   `sliceN.json`. Never give two subagents the same key.
3. **Dispatch one `studio-connector-translator` per slice, in parallel**, each
   prompt carrying the **absolute path** to its slice and nothing else of
   substance. The agent reads and overwrites the file itself: the payload never
   crosses the orchestrator's context, in either direction.
4. **Do not narrate the file handling** ("read it, then write it back"). The
   agent definition already specifies that flow, including the hard rule to call
   `Read` before translating anything. Rephrasing it only drifts from it.

## Check — against the disk, never against the summary

Reread each slice file. Confirm every `op_key`/`name` you sent comes back, and
spot-check a few `description` fields against `source_en`. A confident summary
is not proof of a correct write: a zero-tool dispatch of this same agent once
fabricated a full translated worklist in ~8s without ever opening the file
(Snowflake build, 2026-08-24).

Two more checks the operator owns, both before merging:

- **Broken slice.** When a slice comes back unparseable, rebuild it from the
  original file and take only the `description` field from what came back.
- **`body_sample` in both directions.** Operations carrying a `body` parameter
  in the IAC against operations carrying a `body_sample` in the worklist. An
  invented sample on a bodyless operation is as wrong as a missing one.

## Merge and apply

Merge the checked slices back into one worklist file, then run
`uv run studio-iac apply-prose <iac> <prose> --out iac/{slug}.json`. It validates the merged result,
including the shared-name warning — the same parameter name carrying divergent
descriptions across operations — and the markup warning, which is where any
markdown or HTML that survived the contract shows up. Fix both before importing.
