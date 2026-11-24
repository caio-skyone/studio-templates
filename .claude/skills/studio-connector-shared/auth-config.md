# Authentication mapping for connector docs

Use **one** account table per doc. Remove unused tables from the final file — only the block for the module's `authentication_type`.

## `authentication_type` → Portuguese **Tipo**

| IAC value | Label (Tipo) |
|-----------|----------------|
| `no-auth` | Sem autenticação |
| `basic` | Autenticação básica (HTTP Basic) |
| `bearer-token` | Bearer Token |
| `oauth-1` | OAuth 1.0 |
| `oauth-2` | OAuth 2.0 |
| `cookie` | Cookie |
| `aws` | AWS Signature Version 4 |
| `oauth2-jwt` | OAuth 2.0 com JWT |
| `ca-certificate` | Certificado CA |
| `google-oauth` | Google OAuth |
| `header-auth` | Autenticação por cabeçalho customizado |
| `mtls-certificate` | mTLS (certificado mútuo) |
| empty / unknown | `*não informado*` — ask user or infer from API docs then confirm |

## Host field (universal)

**Host is present in every REST connector account table**, regardless of `authentication_type`. It defines the API base URL used as a prefix for all operations whose `url_type` is `base-url`.

Infer the Host value from the API documentation and `iac/{slug}.json` (look at the `path` of any `base-url` operation to confirm the prefix matches).

- **Fixed host:** use the literal URL — e.g. `https://api.example.com`
- **User-dependent host** (subdomain, tenant ID, region, etc.): use a Studio parameter placeholder — e.g. `https://<>seu-subdominio</>.zendesk.com`, `https://<>sua-regiao</>.api.example.com`

If the host cannot be determined, use `*não informado*`.

**Porta** is also present in every REST connector account table. Default is `443` for HTTPS (the vast majority of cases). Only use a different value when the API documentation explicitly states a non-standard port.

## Account table by type

### `basic`

| Variável | Valor |
| -------- | ----- |
| Host | {{host}} |
| Porta | 443 |
| password | {{api_token}} |
| username | {{account_email}} |

### `oauth-2`, `oauth2-jwt`, `google-oauth`

| Variável | Valor |
| -------- | ----- |
| Host | {{host}} |
| Porta | 443 |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Access Token | {{access_token}} |
| Refresh Token | {{refresh_token}} |
| Endpoint de troca de token | {{token_endpoint}} |

`token_endpoint`: often **not** in IAC — use official OAuth doc URL or `*não informado*`.

### `bearer-token`, `header-auth`, `cookie` (token-style account)

| Variável | Valor |
| -------- | ----- |
| Host | {{host}} |
| Porta | 443 |
| token | {{token}} |

For `header-auth`, add rows only if user/docs name extra header keys (fallback table).

### `no-auth`

Include Host and Porta even for `no-auth` connectors — authentication is absent but the base URL is still required for `base-url` operations:

| Variável | Valor |
| -------- | ----- |
| Host | {{host}} |
| Porta | 443 |

If the connector truly has no account configuration at all (no `base-url` operations either), omit the **Configuração da conta conectada** subsection and state: *Nenhuma credencial na conta conectada — autenticação por operação, se houver, usa parâmetros da requisição.*

### `oauth-1`, `aws`, `ca-certificate`, `mtls-certificate`

No standard Studio table in template — use **fallback** table; always include Host and Porta as the first rows, then one row per known account field from official docs or user:

| Variável | Valor |
| -------- | ----- |
| Host | {{host}} |
| Porta | 443 |
| *detalhes da conta* | *não informado* |
