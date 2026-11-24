# Partial IAC JSON reads

Large IAC files (`iac/{slug}.json`, hundreds of operations) must **not** be
read entirely into context.

## `studio-iac summary` (preferred)

```sh
uv run studio-iac summary iac/{slug}.json                 # metadata + every operation
uv run studio-iac summary iac/{slug}.json --grep Users    # only operations whose name matches
uv run studio-iac summary iac/{slug}.json --limit 20      # first 20 operations
```

Prints module name, auth type and operation count, then one line per
operation: index, method, name, path. The index is the `operations[N]` used in
`studio-iac validate` messages.

## Python slices (anything else)

Works the same on Windows, Linux and macOS — no `jq` needed:

```sh
uv run python -c "import json; m=json.load(open('iac/{slug}.json', encoding='utf-8')); print(json.dumps(m['operations'][12], ensure_ascii=False, indent=2))"
```

Read **line ranges** with the Read tool (`offset` + `limit`) when you already
know where to look, not the whole JSON.

## `IACModule` JSON shape

| Key | Path |
|-----|------|
| Name | `.name` |
| Description | `.description` |
| Auth | `.settings.authentication_type` |
| Operations | `.operations[]` |
| Op name / description | `.operations[].name`, `.operations[].description` |
| HTTP method | `.operations[].request.method` |
| Path segments | `.operations[].request.url.path` |
| Parameters | `.operations[].parameters[]` |
