# Airtable

## Contexto

A **Web API do Airtable** é REST sobre HTTPS, com troca de dados em JSON, e expõe as bases do Airtable: os registros das tabelas, o schema que os descreve (tabelas, campos e views), os comentários, os webhooks de alteração e, nos planos Enterprise, a administração da organização.

**Conceitos fundamentais**

- **Base (`app…`)** é o equivalente a um banco de dados. Toda operação de dados recebe o `base_id`.
- **Tabela (`tbl…`)** fica dentro de uma base. Nos caminhos, o Airtable aceita tanto o ID quanto o nome da tabela; prefira o ID, que não muda quando a tabela é renomeada.
- **Registro (`rec…`)** é uma linha da tabela. Campos vazios **não aparecem** na resposta, em vez de virem como `null`.
- **Campo (`fld…`)** é uma coluna, com tipo e opções próprios (texto, número, seleção, anexo, link para outro registro etc.).
- **View (`viw…`)** é um recorte salvo de uma tabela, com filtro, ordenação e campos visíveis. Informar a view numa listagem aplica esse recorte.
- **Workspace (`wsp…`)** agrupa bases e define quem colabora nelas.
- **Interface (`pbd…`)** é uma aplicação montada sobre a base. Pode ter colaboradores próprios e um portal para usuários externos.
- **Conta Enterprise (`ent…`)** é a organização nos planos Enterprise. É a raiz das operações de usuários, grupos, auditoria e eDiscovery.
- **HyperDB** é o armazenamento de grandes volumes do Enterprise Scale, endereçado por chave primária em vez de ID de registro.

**Escopo deste conector**

O módulo cobre **todos** os endpoints REST documentados pelo Airtable: registros, comentários, schema, views, webhooks, workspaces, compartilhamentos, colaboradores, interfaces, extensões, administração Enterprise, auditoria, eDiscovery, SCIM e HyperDB, num total de 103 operações.

Não existem operações para **excluir tabela** ou **excluir campo**, porque a API não oferece esses endpoints. O escopo `block:manage` também fica de fora: ele serve apenas ao Blocks CLI e não tem endpoint REST.

---

## Autenticação

**Tipo:** Bearer Token

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | https://api.airtable.com |
| Porta | 443 |
| token | {{token}} |

- **Host** não inclui o `/v0`. O prefixo de versão faz parte do caminho de cada operação.
- **token** é um **Personal Access Token (PAT)**, criado em [airtable.com/create/tokens](https://airtable.com/create/tokens). Ao criar o token, escolha os **escopos** e as **bases ou workspaces** a que ele terá acesso; uma operação sobre uma base fora dessa lista retorna erro, mesmo que o usuário tenha acesso a ela no Airtable.
- O token age como o próprio usuário que o criou. Para integrações de produção em planos Enterprise, prefira um token de **conta de serviço**, criado pelo administrador.
- As antigas **API keys** do Airtable deixaram de funcionar em fevereiro de 2024 e não servem para este conector.
- O Airtable também oferece **OAuth 2.0 com PKCE**, mas este conector usa PAT: a Sync API e o HyperDB só aceitam token pessoal.

### Escopos do token

Conceda apenas os escopos das operações que o fluxo vai usar.

| Escopo | Operações |
| ------ | --------- |
| `data.records:read` | Records (leitura) |
| `data.records:write` | Records (escrita, exclusão e Sync CSV) |
| `data.recordComments:read` / `data.recordComments:write` | Comments |
| `schema.bases:read` | Bases - List bases, Get base schema |
| `schema.bases:write` | Bases - Create base, Tables, Fields, Records - Sync CSV data |
| `workspacesAndBases:read` | Bases - Get base collaborators, Views - List views e Get view metadata, Workspaces - Get workspace collaborators, Interfaces - Get interface, Block Installations - List, Base Collaborators - List base portal collaborators |
| `workspacesAndBases:write` | Colaboradores, convites e portais de workspace, base e interface; Views - Delete view; Block Installations - Manage e Delete |
| `workspacesAndBases:manage` | Bases - Delete base; Workspaces - Create, Delete, Move base e Move workspaces |
| `workspacesAndBases.shares:manage` | Shares |
| `webhook:manage` | Webhooks |
| `user.email:read` | Adiciona o e-mail à resposta de User - Get current user |
| `enterprise.account:read` / `enterprise.account:write` | Enterprise - Get enterprise, Create descendant enterprise, Workspaces - Update workspace AI allowlist |
| `enterprise.user:read` / `enterprise.user:write` | Enterprise Users |
| `enterprise.groups:read` / `enterprise.groups:manage` | Enterprise Groups |
| `enterprise.auditLogs:read` | Audit Logs (exceto change events) |
| `enterprise.changeEvents:read` | Audit Logs - Get change events |
| `enterprise.exports:manage` | eDiscovery |
| `enterprise.scim.usersAndGroups:manage` | SCIM Groups, SCIM Users, Enterprise Users - Delete user by id |
| `hyperDB.records:read` / `hyperDB.records:write` | HyperDB |

---

## Convenções deste conector

- **Corpo das requisições.** Toda operação de escrita recebe um único parâmetro `body`, do tipo objeto, com o JSON completo na sintaxe da própria API do Airtable. O `sample` de cada operação traz um exemplo mínimo válido.
- **Upsert não é uma operação à parte.** Para criar ou atualizar conforme o valor de campos, use **Records - Update multiple records** (ou **Replace multiple records**) com `performUpsert: {"fieldsToMergeOn": ["Campo"]}` no corpo. São aceitos de 1 a 3 campos de correspondência; se mais de um registro casar, a requisição falha.
- **PATCH atualiza, PUT substitui.** As operações **Update** alteram só os campos enviados. As operações **Replace** limpam todos os campos que não estiverem no corpo.
- **Parâmetros de lista na query.** Chaves como `fields[]`, `records[]`, `include[]`, `email[]`, `id[]` e `recordMetadata[]` aceitam vários valores, mas cada operação traz **uma** linha para elas. Para enviar mais de um valor, duplique a linha na query da operação no Studio.
- **Ordenação em Records - List records.** Os parâmetros `sort_field` e `sort_direction` preenchem `sort[0][field]` e `sort[0][direction]`. Para mais critérios, duplique as duas linhas trocando o índice para `1`, `2` e assim por diante.
- **Listagens longas.** URLs acima de 16.000 caracteres são recusadas. Se a fórmula de `filter_by_formula` ou a lista de campos for grande, use **Records - List records (POST)**, que envia os mesmos parâmetros no corpo.
- **`cell_format=string` exige fuso e localidade.** Ao pedir células como texto, informe também `time_zone` e `user_locale`.
- **Paginação.** Registros e comentários usam `offset` como cursor: repita a chamada passando o `offset` da resposta até ele não vir mais (até 100 itens por página). **Bases - List bases** devolve até 1000 por página. Payloads de webhook usam `cursor` e `mightHaveMore` (até 50 por chamada). **Get audit log events** pagina com `next` e `previous`. O SCIM usa `startIndex` e `count`.
- **SCIM tem outro host.** As 12 operações **SCIM Groups** e **SCIM Users** apontam para `https://airtable.com/scim/v2` com URL completa e não dependem do Host da conta conectada. Usam o mesmo token.
- **Sync CSV envia o arquivo bruto.** **Records - Sync CSV data** manda o CSV como corpo, com o cabeçalho `Content-Type` vindo do parâmetro `content_type` (`text/csv`). Marque **"Forçar bufferização da requisição"** nas opções avançadas dessa operação no Studio; essa opção não existe no IAC e precisa ser ativada manualmente.
- **Plano exigido.** A descrição de cada operação indica quando ela exige plano Enterprise, Enterprise Scale, Enterprise Hub ou Business ou superior. Fora desses planos, a chamada retorna erro de permissão.

## Limitações conhecidas

- **Limite de requisições.** São 5 requisições por segundo por base e 50 por segundo somando todo o tráfego de um mesmo usuário ou conta de serviço. Ao passar do limite, a API responde `429` e **todas** as chamadas falham por 30 segundos. Em laços de paginação ou de escrita em lote, espace as chamadas.
- **Sync CSV** tem limite próprio: 20 requisições a cada 5 minutos por base, até 10 mil linhas, 500 colunas e 2 MB por requisição. Exige plano Pro ou superior.
- **Webhooks expiram em 7 dias.** Webhooks criados com PAT ou OAuth deixam de existir se não forem renovados. Chame **Webhooks - Refresh webhook** ou **List webhook payloads** periodicamente. Cada base aceita até 10 webhooks, e os payloads ficam disponíveis por uma semana.
- **`macSecretBase64` aparece uma vez só.** Guarde o segredo devolvido por **Webhooks - Create webhook**: ele é necessário para validar as notificações e não volta em nenhuma outra chamada.
- **Iteração expirada.** Uma paginação de registros que demora demais retorna `422 LIST_RECORDS_ITERATOR_NOT_AVAILABLE`. Recomece a listagem do início.
- **Base vazia na listagem.** Se **Bases - List bases** responder com sucesso mas sem nenhuma base, verifique se o token tem acesso às bases e se a organização não bloqueou o acesso via API.
- **Audit log legado.** **List**, **Create** e **Get audit log request** são recursos legados que o Airtable desencoraja. Prefira **Get audit log events**.
- **Resposta do HyperDB.** A documentação oficial das operações de exclusão e upsert do HyperDB descreve um formato de resposta inconsistente. Valide a resposta real antes de depender dela no fluxo.

---

## Operações

### User — 1 operação

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **User - Get current user** | **GET** | Retorna o ID do usuário do token, os escopos concedidos e o e-mail quando o escopo user.email:read está presente. |

### Records — 11 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Records - List records** | **GET** | Lista registros de uma tabela com filtro, ordenação, view e paginação por offset (até 100 por página). |
| **Records - List records (POST)** | **POST** | Lista registros enviando os parâmetros no corpo JSON; use quando fórmulas ou listas de campos excedem o limite de URL. |
| **Records - Get record** | **GET** | Retorna um registro pelo ID. Campos vazios não aparecem na resposta. |
| **Records - Create records** | **POST** | Cria um ou vários registros na tabela. |
| **Records - Update multiple records** | **PATCH** | Atualiza vários registros alterando só os campos enviados. Com performUpsert, cria ou atualiza pelos campos de correspondência. |
| **Records - Replace multiple records** | **PUT** | Substitui vários registros: campos não enviados são limpos. Aceita performUpsert para upsert destrutivo. |
| **Records - Update record** | **PATCH** | Atualiza um registro alterando só os campos enviados. |
| **Records - Replace record** | **PUT** | Substitui um registro: campos não enviados são limpos. |
| **Records - Delete multiple records** | **DELETE** | Exclui vários registros pelos IDs. |
| **Records - Delete record** | **DELETE** | Exclui um registro pelo ID. |
| **Records - Sync CSV data** | **POST** | Envia CSV bruto para uma tabela da Sync API. Só com token pessoal; até 10 mil linhas e 2 MB por requisição. |

### Comments — 4 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Comments - List comments** | **GET** | Lista os comentários de um registro, do mais recente ao mais antigo. |
| **Comments - Create comment** | **POST** | Cria um comentário em um registro, opcionalmente como resposta a outro. |
| **Comments - Update comment** | **PATCH** | Altera o texto de um comentário criado pelo próprio usuário do token. |
| **Comments - Delete comment** | **DELETE** | Exclui um comentário de um registro. |

### Bases — 5 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Bases - List bases** | **GET** | Lista as bases acessíveis pelo token, até 1000 por página. |
| **Bases - Create base** | **POST** | Cria uma base em um workspace com as tabelas informadas. |
| **Bases - Get base collaborators** | **GET** | Retorna informações da base e, conforme include, colaboradores, links de convite, interfaces e pacotes. |
| **Bases - Get base schema** | **GET** | Retorna o schema da base: tabelas, campos e views. |
| **Bases - Delete base** | **DELETE** | Exclui uma base. Exige plano Enterprise e administrador. |

### Tables — 2 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Tables - Create table** | **POST** | Cria uma tabela na base com os campos informados. |
| **Tables - Update table** | **PATCH** | Altera nome, descrição ou configurações de dependência de datas de uma tabela. |

### Fields — 2 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Fields - Create field** | **POST** | Cria um campo na tabela; as opções variam conforme o tipo. |
| **Fields - Update field** | **PATCH** | Altera nome, descrição ou opções de um campo. |

### Views — 3 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Views - List views** | **GET** | Lista as views da base. |
| **Views - Get view metadata** | **GET** | Retorna os metadados de uma view. |
| **Views - Delete view** | **DELETE** | Exclui uma view. Exige plano Enterprise. |

### Webhooks — 6 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Webhooks - List webhooks** | **GET** | Lista os webhooks da base. |
| **Webhooks - Create webhook** | **POST** | Cria um webhook na base. O macSecretBase64 da resposta só é exibido uma vez; expira em 7 dias sem renovação. |
| **Webhooks - Delete webhook** | **DELETE** | Exclui um webhook. |
| **Webhooks - Enable or disable notifications** | **POST** | Liga ou desliga os avisos enviados à notificationUrl do webhook. |
| **Webhooks - Refresh webhook** | **POST** | Estende a expiração do webhook por mais 7 dias. |
| **Webhooks - List webhook payloads** | **GET** | Lista os payloads do webhook a partir do cursor, até 50 por chamada; também estende a validade do webhook. |

### Workspaces — 11 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Workspaces - Get workspace collaborators** | **GET** | Retorna informações do workspace e, conforme include, colaboradores e links de convite. |
| **Workspaces - Create workspace** | **POST** | Cria um workspace na conta Enterprise. |
| **Workspaces - Delete workspace** | **DELETE** | Exclui um workspace. Exige plano Enterprise e administrador. |
| **Workspaces - Move base** | **POST** | Move uma base para outro workspace. Exige plano Enterprise. |
| **Workspaces - Add workspace collaborator** | **POST** | Adiciona um colaborador (usuário ou grupo) ao workspace, um por requisição. Exige plano Enterprise. |
| **Workspaces - Update workspace collaborator** | **PATCH** | Altera o nível de permissão de um colaborador do workspace. Exige plano Enterprise. |
| **Workspaces - Delete workspace collaborator** | **DELETE** | Remove um colaborador do workspace. Exige plano Enterprise. |
| **Workspaces - Delete workspace invite** | **DELETE** | Exclui um convite pendente do workspace. Exige plano Enterprise. |
| **Workspaces - Update workspace restrictions** | **POST** | Define quem pode criar convites e compartilhamentos no workspace. Exige plano Enterprise. |
| **Workspaces - Move workspaces** | **POST** | Move workspaces entre unidades da organização (até 100). Exige Enterprise Hub. |
| **Workspaces - Update workspace AI allowlist** | **POST** | Adiciona ou remove workspaces da lista de permissão de IA, até 10 por requisição. Exige plano Enterprise. |

### Shares — 3 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Shares - List shares** | **GET** | Lista os compartilhamentos da base. Exige plano Enterprise. |
| **Shares - Manage share** | **PATCH** | Ativa ou desativa um compartilhamento. Exige plano Enterprise. |
| **Shares - Delete share** | **DELETE** | Exclui definitivamente um compartilhamento, sem recuperação. Exige plano Enterprise. |

### Base Collaborators — 6 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Base Collaborators - Add base collaborator** | **POST** | Adiciona um colaborador (usuário ou grupo) à base, um por requisição. Exige plano Enterprise. |
| **Base Collaborators - Update base collaborator** | **PATCH** | Altera o nível de permissão de um colaborador na base. Exige plano Enterprise. |
| **Base Collaborators - Delete base collaborator** | **DELETE** | Remove um colaborador da base. Exige plano Enterprise. |
| **Base Collaborators - Delete base invite** | **DELETE** | Exclui um convite pendente da base. Exige plano Enterprise. |
| **Base Collaborators - List base portal collaborators** | **GET** | Lista usuários do portal da base e convites de portal pendentes. Exige plano Enterprise. |
| **Base Collaborators - Delete base portal collaborator** | **DELETE** | Remove um usuário do portal da base ou cancela o convite dele. Exige plano Enterprise. |

### Interfaces — 8 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Interfaces - Get interface** | **GET** | Retorna informações da interface e, conforme include, colaboradores e links de convite. |
| **Interfaces - Add interface collaborator** | **POST** | Adiciona um colaborador à interface, um por requisição. Exige plano Enterprise. |
| **Interfaces - Update interface collaborator** | **PATCH** | Altera a permissão de um colaborador da interface (read, comment ou edit). Exige plano Enterprise. |
| **Interfaces - Delete interface collaborator** | **DELETE** | Remove um colaborador da interface. Exige plano Enterprise. |
| **Interfaces - Delete interface invite** | **DELETE** | Exclui um convite pendente da interface. Exige plano Enterprise. |
| **Interfaces - Add interface portal collaborators** | **POST** | Adiciona até 100 usuários externos ao portal da interface por e-mail, todos com o mesmo nível. Exige plano Enterprise. |
| **Interfaces - Update interface portal collaborator** | **PATCH** | Altera a permissão de um usuário do portal da interface. Exige plano Enterprise. |
| **Interfaces - Delete interface portal collaborator** | **DELETE** | Remove um usuário do portal da interface. Exige plano Enterprise. |

### Block Installations — 3 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Block Installations - List block installations** | **GET** | Lista as extensões instaladas na base. |
| **Block Installations - Manage block installation** | **PATCH** | Ativa ou desativa uma extensão instalada. Exige plano Enterprise. |
| **Block Installations - Delete block installation** | **DELETE** | Exclui uma extensão instalada; a exclusão pode ser revertida. Exige plano Enterprise. |

### Enterprise — 2 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Enterprise - Get enterprise** | **GET** | Retorna informações da conta Enterprise e, conforme include, dados agregados e unidades descendentes. |
| **Enterprise - Create descendant enterprise** | **POST** | Cria uma unidade da organização sob a conta Enterprise. Exige Enterprise Hub. |

### Enterprise Users — 11 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Enterprise Users - Get users by id or email** | **GET** | Busca usuários da conta Enterprise por ID ou e-mail; informe ao menos um dos dois. |
| **Enterprise Users - Get user by id** | **GET** | Retorna um usuário da conta Enterprise pelo ID. |
| **Enterprise Users - Delete users by email** | **DELETE** | Exclui usuários da conta Enterprise pelo e-mail. |
| **Enterprise Users - Manage user** | **PATCH** | Altera estado (provisioned ou deactivated), e-mail, nome ou sobrenome de um usuário. |
| **Enterprise Users - Manage users batched** | **PATCH** | Altera vários usuários de uma vez; recomenda-se até 10 por requisição para evitar timeout. |
| **Enterprise Users - Manage user membership** | **POST** | Define usuários como gerenciados ou não gerenciados pela conta Enterprise. |
| **Enterprise Users - Grant admin access** | **POST** | Concede acesso de administrador aos usuários informados. |
| **Enterprise Users - Revoke admin access** | **POST** | Revoga o acesso de administrador atribuído diretamente aos usuários informados. |
| **Enterprise Users - Delete user by id** | **DELETE** | Exclui um usuário da conta Enterprise pelo ID. |
| **Enterprise Users - Logout user** | **POST** | Encerra as sessões ativas de um usuário. |
| **Enterprise Users - Remove user from enterprise** | **POST** | Remove o compartilhamento do usuário de tudo na conta Enterprise; aceita simulação com isDryRun. |

### Enterprise Groups — 2 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Enterprise Groups - Get user group** | **GET** | Retorna um grupo de usuários e, com include, as colaborações dele. |
| **Enterprise Groups - Move user groups** | **POST** | Move grupos de usuários entre unidades da organização (até 100). Exige Enterprise Hub. |

### Audit Logs — 5 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Audit Logs - Get audit log events** | **GET** | Lista eventos do log de auditoria dos últimos 180 dias, com filtros e paginação por next e previous. |
| **Audit Logs - List audit log requests** | **GET** | Lista as solicitações de log de auditoria (recurso legado; prefira Get audit log events). |
| **Audit Logs - Create audit log request** | **POST** | Cria uma solicitação de log de auditoria (recurso legado). |
| **Audit Logs - Get audit log request** | **GET** | Retorna o status e o resultado de uma solicitação de log de auditoria (recurso legado). |
| **Audit Logs - Get change events** | **GET** | Lista eventos de alteração das bases dos últimos 14 dias. Exige Enterprise Scale e o recurso habilitado. |

### eDiscovery — 3 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **eDiscovery - List eDiscovery exports** | **GET** | Lista as exportações de eDiscovery, com filtro por estado. Exige Enterprise Scale. |
| **eDiscovery - Create eDiscovery export** | **POST** | Cria uma exportação de eDiscovery de uma base. Exige Enterprise Scale. |
| **eDiscovery - Get eDiscovery export** | **GET** | Retorna o status de uma exportação de eDiscovery e as URLs de download. Exige Enterprise Scale. |

### SCIM Groups — 6 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **SCIM Groups - List groups** | **GET** | Lista grupos via SCIM, com filtro por displayName. Exige plano Enterprise. |
| **SCIM Groups - Create group** | **POST** | Cria um grupo sem membros via SCIM. Exige plano Enterprise. |
| **SCIM Groups - Get group** | **GET** | Retorna um grupo via SCIM. Exige plano Enterprise. |
| **SCIM Groups - Patch group** | **PATCH** | Aplica operações SCIM de patch a um grupo, como incluir ou remover membros. Exige plano Enterprise. |
| **SCIM Groups - Put group** | **PUT** | Substitui um grupo via SCIM, incluindo nome e membros. Exige plano Enterprise. |
| **SCIM Groups - Delete group** | **DELETE** | Exclui um grupo via SCIM. Exige plano Enterprise. |

### SCIM Users — 6 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **SCIM Users - List users** | **GET** | Lista usuários via SCIM, com filtro por userName. Exige plano Business ou superior. |
| **SCIM Users - Create user** | **POST** | Cria um usuário via SCIM, para cenários com SSO. Exige plano Business ou superior. |
| **SCIM Users - Get user** | **GET** | Retorna um usuário via SCIM. Exige plano Business ou superior. |
| **SCIM Users - Patch user** | **PATCH** | Aplica operações SCIM de patch a um usuário, como desativá-lo. Exige plano Business ou superior. |
| **SCIM Users - Put user** | **PUT** | Substitui um usuário via SCIM, com o mesmo corpo da criação. Exige plano Business ou superior. |
| **SCIM Users - Delete user** | **DELETE** | Exclui um usuário via SCIM; não vale para a própria conta nem para o único dono de workspace compartilhado. |

### HyperDB — 3 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **HyperDB - Read records** | **POST** | Lê registros de uma tabela HyperDB, com cursor e filtro por chaves primárias. Exige Enterprise Scale e token pessoal. |
| **HyperDB - Delete records by primary keys** | **POST** | Exclui registros de uma tabela HyperDB pelas chaves primárias. Exige Enterprise Scale e token pessoal. |
| **HyperDB - Upsert records by primary keys** | **PUT** | Cria ou atualiza registros de uma tabela HyperDB pela chave primária. Exige Enterprise Scale e token pessoal. |

---

## Documentação oficial

- [Airtable Web API](https://airtable.com/developers/web/api/introduction)
- [Escopos dos tokens](https://airtable.com/developers/web/api/scopes)
- [Limites de requisição](https://airtable.com/developers/web/api/rate-limits)
