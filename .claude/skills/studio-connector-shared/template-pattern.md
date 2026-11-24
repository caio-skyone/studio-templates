# Template Pattern (default convention)

This is the default Skyone connector convention. The phase skills link here as
the active convention; if the user states a different one in the thread, follow
theirs instead — an explicit instruction always wins over this file.

## Operation naming
- Operation `name`: `{Domain} - {Action}` in English, aligned with the API's doc
  titles. Examples: `Users - Get all users`, `Orders - Create order`.
- Domains group related endpoints: `Users`, `Orders`, `Products`, `Auth`, …
- Operation `description`: concise, in the user's language, plain — what the call does.

## Parameter naming
- Parameter `name`: `snake_case` (`^[a-z][a-z0-9_]*$`), e.g. `user_id`, `order_code`.
- Parameter `description`: clearer than the name — what the value means for whoever
  configures the flow.

## Schema hygiene
- Use IAC request fields only (`method`, `url`, `header`, `body`). Do **not** use
  OpenAPI field names (`http_method`, `produces`, `consumes`, `responses`).
- `request.url.path` is a segment array, never a URL string.

## Auth parameters
- Do **not** add auth parameters (tokens, API keys, credentials) unless the user
  explicitly asks — auth is handled by the connected account.

## Path consistency
- All operations in one connector share the same path-prefix level.

## How much of this is checked automatically

| Rule | Checked by |
|---|---|
| `snake_case` parameter name | `studio-iac validate` — blocks |
| name/description length limits (30/100/50/250) | `studio-iac validate` — blocks |
| duplicate operation name, duplicate `(method, path)` | `studio-iac validate` — blocks |
| `<>param</>` with no declared parameter, and declared-but-never-referenced | `studio-iac validate` — blocks |
| credential-looking sample, hardcoded auth header, `sensitive: false` on a credential name | `studio-iac validate` — warns |
| same parameter name with divergent descriptions | `studio-iac validate` — warns |
| `{Domain} - {Action}` operation naming | nothing — the generator produces it, this file states it, no check enforces it |
| "no auth parameters unless asked" | nothing — judgement |

There is **no** hook enforcing this. Run `uv run studio-iac validate` before
handing a file to the user for import, always. Server-side rules newer than
this validator only surface on import in the Studio UI.
