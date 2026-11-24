---
name: studio-connector-account
description: Prepare a Skyone Studio connected account for a REST connector — resolve the account fields and write the payload with template placeholders for credentials, for the user to create in the Studio UI. Use when the user asks to create or configure a connected account.
---

# Studio connector — connected account

Prepares a Studio connected account. There is no API client in this repo:
you resolve every field and hand the user a ready payload (and a field list for
the UI form); **the user creates the account in the Studio UI.** This flow is
independent of the IAC: it can run before, after, or without one.

---

## 1. Hard rules

1. **Never ask the user for credential values.** Secrets default to Studio
   template placeholders (see §4). Only include a real credential when the
   user **explicitly provided the value and asked** for it to be stored
   directly — and never write it to a file in the repo.
2. **Never invent field values** — resolve them from the sources in §2 or ask
   the user (except credential values, which stay as templates).
3. **Never claim the account exists** — only the user can confirm that.

---

## 2. Gather the account facts

Resolve, in this order (stop when resolved):

| Priority | Source | Use for |
|----------|--------|---------|
| 1 | Session context | Auth type, host, and API research already in the thread |
| 2 | `iac/{slug}.json` — if it exists (read slices, see [iac-extract.md](../studio-connector-shared/iac-extract.md)) | `settings.authentication_type`, host prefix from `base-url` operations |
| 3 | Connector doc `docs/connectors/{slug}.md` — if it exists | Auth type label and the account variable table (align field names with it) |
| 4 | Web (official API docs) | Auth flow details: token endpoint, scopes, host |
| 5 | User | Anything still unknown — **except credential values** |

Confirm `name`, `sub_type`, and host with the user before writing the payload.

---

## 3. Payload contract

The payload mirrors Studio's `POST /api/account`, which is strict: it
rejects unknown top-level fields and does **no type coercion** — numbers and
booleans must be real JSON numbers/booleans (they can never be templates).
`spaceId` comes from the session; do not send it.

- `type: "rest"` requires `sub_type`. The account vocabulary matches the IAC
  `authentication_type` one-to-one, `oauth2-jwt` included.
- Secrets always go in `protected_configuration`; `configuration` holds only
  non-secret connection settings.
- `configuration.host` may include the scheme (`https://api.example.com`) but
  must **not** end with `/`; `port` is a number (usually `443`). A templated
  host (`https://<>seu-subdominio</>.example.com`) is accepted by Studio.

Required fields per `sub_type`:

| sub_type | `configuration` requires | `protected_configuration` requires | Optional highlights |
|----------|--------------------------|------------------------------------|---------------------|
| `no-auth` | host, port | — | method |
| `basic` | host, port | username, password | |
| `bearer-token` | host, port | token | |
| `oauth-1` | host, port | consumerKey, consumerSecret, accessToken, tokenSecret | config: signatureMethod (`HMAC-SHA1`\|`HMAC-SHA256`) |
| `oauth-2` | host, port, contentType, headerParametersRequestAfterAuth, sendRefreshTokenParametersInQueryString, tokenExchangeEndpoint, tokenPayloadParameters, tokenResponseKey | clientId, clientSecret | config: expiration, refreshTokenResponseKey, tokenHeaderParameters, tokenPrefix, refreshStatusCode, refreshJsonata; protected: accessToken, refreshToken |
| `oauth2-jwt` | host, port, contentType, headerParametersRequestAfterAuth, jwtPayloadParameters, jwtTokenExpiration, tokenExchangeEndpoint, tokenPayloadParameters, tokenResponseKey | privateKey | config: tokenPayloadParametersPlacement (`queryParams`\|`body`), jwtAlgorithm (`HS256`\|`RS256`\|`PS256`\|`ES256`), includeJwtIdClaim; protected: accessToken, refreshToken, keyId |
| `google-oauth` | host, port, scope, tokenPrefix | — (send refreshToken, accessToken, token as templates) | |
| `header-auth` | host, port | headers | object map `{name: value}` or fromTo array |
| `cookie` | host, port | — | config: authenticationEndpoint; protected: body, cookie |
| `aws` | host, port, awsRegion | awsAccessKeyId, awsSecretAccessKey, awsService | |
| `ca-certificate` | host, port | certificate | |
| `mtls-certificate` | host, port | clientCertificate, clientPrivateKey, caCertificate | |

---

## 4. Credentials are templates

Every secret string defaults to a Studio placeholder in the form
`<>descricao_do_valor</>` — e.g. `<>seu_client_id</>`, `<>seu_client_secret</>`,
`<>seu_token</>`, `<>sua_senha</>`, `<>seu-subdominio</>` (host). If the
connector doc exists, name the placeholders after its account-table variables
so the doc and the account match.

Example — `oauth-2` account with templated credentials:

```json
{
  "name": "Example API",
  "type": "rest",
  "sub_type": "oauth-2",
  "configuration": {
    "host": "https://api.example.com",
    "port": 443,
    "contentType": "application/x-www-form-urlencoded",
    "tokenExchangeEndpoint": "https://auth.example.com/oauth/token",
    "tokenResponseKey": "access_token",
    "tokenPayloadParameters": { "grant_type": "client_credentials" },
    "headerParametersRequestAfterAuth": {},
    "sendRefreshTokenParametersInQueryString": false
  },
  "protected_configuration": {
    "clientId": "<>seu_client_id</>",
    "clientSecret": "<>seu_client_secret</>"
  }
}
```

Numbers and booleans (`port`, `expiration`, `sendRefreshTokenParametersInQueryString`,
`jwtTokenExpiration`, …) can **not** be templates — use real values (defaults:
`port` 443, booleans as documented by the API).

---

## 5. Hand over

Give the user:

- The payload as a JSON block in chat (not a file in the repo).
- The same fields as a list matching the Studio UI form: `configuration`
  fields first, then `protected_configuration`.
- Every field left as a `<>template</>` — they must replace them with real
  values in the Studio UI before using the account.
- Any field left unresolved (host unknown, token endpoint not found, …).

## Related skills

- Publishing the IAC: [studio-connector-publish](../studio-connector-publish/SKILL.md)
- Connector documentation: [studio-connector-document](../studio-connector-document/SKILL.md)
