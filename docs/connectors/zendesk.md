# Zendesk

## Contexto

A API do **Zendesk Support** é uma API **RESTful** para atendimento ao cliente: tickets, solicitantes, organizações, filas de trabalho e as regras de negócio que automatizam o fluxo. A comunicação é via **HTTPS**, e tanto as requisições quanto as respostas usam **JSON**.

Este template cobre **470 operações** em 50 domínios, agrupadas em cinco blocos:

**Atendimento (105 operações):** Tickets, Requests, Ticket Fields, Ticket Forms, Ticket Form Statuses, Ticket Metrics, Ticket Audits, Ticket Content Pins, Suspended Tickets, Deleted Tickets, Problems, Imports, Skips e Comment Redactions.
**Pessoas e organizações (168 operações):** Users, User Fields, End Users, Deleted Users, Organizations, Organization Fields, Organization Memberships, Organization Merges, Organization Subscriptions, Groups, Group Memberships, User Group Memberships, User Organization Memberships, Brand Agents e Custom Roles.
**Regras de negócio (105 operações):** Views, Macros, Triggers, Trigger Categories, Automations, SLAs, Group SLAs, Targets, Target Failures, Dynamic Content e Resource Collections.
**Objetos customizados (58 operações):** Custom Objects (com registros, campos, gatilhos, regras de acesso e políticas de permissão), Custom Statuses e Relationships.
**Dados e integração (34 operações):** Search, Incremental Exports, Attachments, Uploads, Job Statuses e Webhooks.

## Conceitos Fundamentais

### IDs numéricos, sem prefixo

Diferente de APIs que usam IDs com prefixo de tipo, os IDs do Zendesk são **inteiros** — `35436` pode ser um ticket ou um usuário, dependendo de onde você o usa. Não há como detectar pelo valor que o ID foi colocado no lugar errado, então confira o parâmetro antes de executar. As exceções são os objetos customizados, identificados por uma **chave textual** (`custom_object_key`, por exemplo `ativo`) e por IDs de registro no formato ULID.

### Envelope de recurso no corpo da requisição

Praticamente todo corpo de requisição vem embrulhado no nome do recurso, no singular para um item e no plural para lote:

```json
{"ticket": {"subject": "Impressora sem toner", "priority": "normal"}}
```

```json
{"tickets": [{"id": 35436, "status": "solved"}, {"id": 35437, "status": "solved"}]}
```

Enviar os campos na raiz, sem o envelope, resulta em erro de validação. O `sample` de cada parâmetro `body` deste template já traz o envelope correto do endpoint.

### Paginação por cursor

As listagens usam **paginação por cursor**: `page[size]` define o tamanho da página e `page[after]` / `page[before]` recebem os valores `meta.after_cursor` e `meta.before_cursor` da resposta anterior. Nas operações deste template esses cursores estão expostos como os parâmetros `page_size`, `page_after` e `page_before`, e o parâmetro `page` cobre a forma genérica `page[chave]`. A paginação por offset (`page=2`) ainda funciona em vários endpoints, mas é a forma legada.

### Exportações incrementais

O bloco **Incremental** existe para sincronização contínua: em vez de repaginar a base inteira, você informa `start_time` (epoch Unix UTC) e recebe apenas o que mudou desde então, junto com o `end_time` a usar na próxima chamada. É o caminho correto para manter uma cópia dos tickets ou usuários atualizada — as listagens comuns não garantem consistência sob escrita concorrente.

### Operações em lote e job status

Endpoints com `create_many`, `update_many`, `destroy_many` e similares são **assíncronos**: a resposta traz um `job_status` em vez do resultado final. O `id` desse job status é uma string alfanumérica (não um inteiro, ao contrário dos demais IDs da API) e serve para acompanhar o processamento no domínio **Job Statuses**:

| Operação | Uso |
| -------- | --- |
| **Job Statuses - Show Job Status** | acompanha um job pelo `id` devolvido pela operação em lote; traz o progresso e o resultado item a item |
| **Job Statuses - Show Many Job Statuses** | consulta vários jobs de uma vez, por lista de ids |
| **Job Statuses - List Job Statuses** | lista os jobs recentes da conta |

Um lote só está concluído quando o status chega a `completed`; até então o resultado parcial pode não refletir tudo o que foi enviado. Jobs ficam disponíveis para consulta por tempo limitado após a conclusão.

### Webhooks e assinatura das requisições

Um **webhook** é o destino HTTP que o Zendesk chama quando um evento ocorre. Ele não dispara sozinho: um webhook com `subscriptions: ["conditional_ticket_events"]` só é acionado por um **trigger** ou uma **automation** que o referencie como ação — os dois domínios estão neste template, então o fluxo completo (criar o webhook, criar o trigger que o chama) pode ser montado sem sair do conector.

Cada webhook tem um **signing secret**, usado para o sistema de destino confirmar que a requisição partiu do Zendesk. `Webhooks - Show Webhook Signing Secret` recupera o segredo atual; `Webhooks - Reset Webhook Signing Secret` gera um novo e **invalida o anterior imediatamente** — atualize o destino antes de resetar, ou as entregas passam a falhar na validação.

Para diagnóstico, `Webhooks - List Webhook Invocations` mostra o que foi enviado e `Webhooks - List Webhook Invocation Attempts` mostra cada tentativa de entrega, incluindo as que falharam e foram reenviadas. `Webhooks - Test Webhook` permite validar uma configuração **antes** de criá-la: envie apenas o corpo, sem `webhook_id`.

### Escopo por marca e por função

Boa parte das listagens respeita a **função do usuário** cujo token está sendo usado: um agente com restrição de grupo não vê os mesmos tickets que um administrador. Ao configurar a conta conectada, use um usuário com a abrangência que o seu fluxo precisa — permissão insuficiente aparece como resultado vazio, não como erro.

---

## Autenticação

**Tipo:** OAuth 2.0

### Configuração da conta conectada

| Variável | Valor |
| -------- | ----- |
| Host | https://<>seu-subdominio</>.zendesk.com |
| Porta | 443 |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Access Token | {{access_token}} |
| Endpoint de troca de token | https://<>seu-subdominio</>.zendesk.com/oauth/tokens |

O **Host** depende da conta: substitua `<>seu-subdominio</>` pelo subdomínio do seu Zendesk — o mesmo que aparece na URL do painel. Todas as operações deste template são `base-url`, ou seja, têm o caminho `/api/v2/...` anexado a esse host.

O `client_id` e o `client_secret` vêm de um **OAuth client** criado no painel do Zendesk, em **Admin Center → Apps e integrações → APIs → OAuth clients**. Para uma integração usada em uma única conta Zendesk, um client local basta; para distribuir o conector a várias contas Zendesk, é necessário um **global OAuth client**, solicitado ao Zendesk.

É necessário marcar o **Client kind** do OAuth client criado como  **Confidential**, caso contrário os fluxos de troca de token não irão funcionar.

Visto que usaremos o fluxo de **Client Credentials** de OAuth2 (preferível para comunicação server-to-server), o campo de **Refresh token** pode ser deixado vazio.

### Fluxo e escopos

O fluxo é **client_credentials** no template, caso opte por usar o fluxo de authorization code será necessário [[contexto.md|configurar um callback]].

Use no tuturial de callback: Será necessário inserir no campo de Redirect URI do OAuth client criado a URL de um webhook do Skyone Studio, crie uma conta provisória sem o campo chave valor **Parâmetros no cabeçalho da requisição após autenticação**,
não insira access token ou refresh token. Use a conta provisória no conector do Zendesk com a operação **Auth - Get tokens with authorization code**, acesse a url de autenticação do zendesk, no formato:

```text
https://{subdominio}.zendesk.com/oauth/authorizations/new?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}
```

O restante deve ser conforme o tutorial de callback.

#### Parâmetros do payload do token (para client_credentials)

Modifique o valor de grant_type e adicione o novo campo de scope:

| Chave | Valor |
| ----- | --- |
| grant_type | client_credentials |
| scope | {{scopes}} |

Mantenha os pares chave-valor de client_id e client_credentials como o padrão, remova o campo de refresh_token.

Os escopos amplos são `read`, `write` e `impersonate`. É possível refinar por recurso na forma `recurso:escopo` — por exemplo `tickets:read`, `users:read users:write`. Conceda o mínimo que o seu fluxo exige: as operações de leitura deste template precisam apenas de `read`, e os domínios de regras de negócio (Triggers, Automations, Macros, SLAs) exigem permissão de administrador no usuário que autorizou.

---

## Convenções do template

### O parâmetro `body` — JSON em um único campo de texto

As operações de escrita expõem **um único parâmetro `body`**, do tipo texto, em vez de um campo por atributo do recurso. O `sample` de cada operação traz um exemplo real e completo daquele endpoint, com o envelope correto. Para montar o seu corpo, edite o sample: o aninhamento é o JSON normal da API do Zendesk, sem sintaxe especial.

O motivo é prático: os recursos do Zendesk aninham profundamente — um `trigger` carrega `conditions.all[]` e `actions[]`, um `ticket` carrega `comment`, `custom_fields[]` e `via` — e enumerar isso campo a campo produziria centenas de parâmetros por operação, muitos deles com nomes acima do limite de 50 caracteres do Studio.

### Path e query são exaustivos

Ao contrário do corpo, os parâmetros de **path** e de **query** estão declarados **um por um e por completo** — inclusive os opcionais. Todos os filtros, ordenações e flags de cada endpoint estão disponíveis sem edição manual da URL.

### Query de tipo objeto: o que varia é a chave

Alguns parâmetros representam uma família de chaves de query, não um valor único: `page` (`page[size]`, `page[after]`), `filter` (`filter[type]`), `filter_dynamic_values` e `filter_events`. Neles, **edite a chave da query na operação**, não apenas o valor. O `sample` mostra a forma esperada.

### Operações sem corpo

22 operações de escrita **não têm parâmetro `body`**, porque o endpoint correspondente não recebe corpo — a ação está no próprio caminho ou nos parâmetros de query. É o caso de `make_default`, `make_primary`, `verify`, `make_private`, `mark_as_spam`, `clone`, `restore`, `recover`, `logout_many`, da redação de anexo de comentário e do reset do signing secret de webhook. Não é omissão do template.

### Uploads de arquivo

Quatro operações lidam com arquivo em vez de JSON:

| Operação | Como enviar |
| -------- | ----------- |
| **Uploads - Upload Files** | corpo binário do arquivo; o nome vai no parâmetro `filename` |
| **Macros - Create Macro Attachment** | `multipart/form-data`, campo `filename` |
| **Macros - Create Unassociated Macro Attachment** | `multipart/form-data`, campo `filename` |
| **Custom Objects - Create Custom Object Record Attachment** | `multipart/form-data`, campo `uploaded_data` |

Em `Uploads - Upload Files` a resposta traz um **token**, que é o que você anexa ao comentário do ticket (`comment.uploads[]`) — e é também o valor usado em **Uploads - Delete Upload**. Esse token identifica o upload; não é uma credencial.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Attachments - Show Attachment** | GET | Exibe os detalhes de um anexo. O valor de attachment_id pode ser obtido ao listar os comentários do ticket, pois cada comentário traz uma lista de anexos com o id de cada um. Permitido para agentes. |
| **Attachments - Update Attachment for Malware** | PUT | Alterna entre liberar e restringir o acesso dos agentes a anexos nos quais foi detectado malware. Permitido para administradores. |
| **Attachments - Delete Attachment** | DELETE | Exclui o anexo. Permitido para agentes. |
| **Automations - List Automations** | GET | Lista todas as automações da conta atual. Aceita filtros opcionais como active, sort_by e sort_order e retorna no máximo 100 registros por página. |
| **Automations - Create Automation** | POST | Cria uma automação, que deve ser única e conter no array all pelo menos uma condição baseada em tempo e uma condição sobre status, type, group_id, assignee_id ou requester_id. |
| **Automations - List Active Automations** | GET | Lista todas as automações ativas da conta. Aceita os filtros opcionais sort_by e sort_order. |
| **Automations - Bulk Delete Automations** | DELETE | Exclui as automações correspondentes à lista de IDs separados por vírgula informada. Algumas automações padrão podem ter a exclusão restrita; nesse caso, apenas as automações sem restrição são excluídas. |
| **Automations - Search Automations** | GET | Busca automações da conta. Usa apenas paginação por offset e aceita sideloads como app_installation, permissions e métricas de uso. |
| **Automations - Update Many Automations** | PUT | Atualiza várias automações de uma vez a partir de um objeto automations, no qual cada item traz o id obrigatório e, opcionalmente, position e active. Algumas automações padrão podem ter a atualização restrita. |
| **Automations - Show Automation** | GET | Exibe os dados da automação especificada. Disponível para agentes. |
| **Automations - Update Automation** | PUT | Atualiza a automação especificada. Ao alterar uma condição ou ação, envie todas elas, pois os arrays conditions e actions são substituídos por completo. |
| **Automations - Delete Automation** | DELETE | Exclui a automação especificada. Algumas automações padrão podem ter a exclusão restrita. |
| **Brand Agents - List Brand Agent Memberships** | GET | Retorna a lista de todas as associações entre agentes e marcas da conta, com paginação por cursor (recomendada) ou por offset, no máximo 100 registros por página. Permitido para administradores. |
| **Brand Agents - Show Brand Agent Membership** | GET | Retorna uma associação entre agente e marca da conta. Permitido para administradores. |
| **Brand Agents - Delete Brand Agent Membership** | DELETE | Exclui uma associação entre agente e marca. Permitido para administradores. |
| **Comment Redactions - Redact Ticket Comment In Agent Workspace** | PUT | Remove permanentemente palavras, textos ou anexos de um comentário de ticket, envolvendo o conteúdo em tags <redact> no html_body. A remoção é definitiva e não pode ser desfeita. |
| **Custom Objects - List Custom Objects** | GET | Lista todos os objetos personalizados não excluídos da conta. Permitido para agentes. |
| **Custom Objects - Create Custom Object** | POST | Cria um objeto que descreve todas as propriedades necessárias para criar um registro de objeto personalizado. Permitido para administradores. |
| **Custom Objects - Custom Objects Limit** | GET | Lista a contagem atual e o limite de objetos personalizados. Permitido para administradores. |
| **Custom Objects - Custom Object Records Limit** | GET | Lista a contagem atual e o limite de registros de objetos personalizados. Permitido para agentes. |
| **Custom Objects - Show Custom Object** | GET | Retorna o objeto personalizado com a chave informada. Permitido para agentes. |
| **Custom Objects - Update Custom Object** | PATCH | Atualiza um objeto personalizado individual a partir de um objeto `custom_object` com as propriedades a alterar; a propriedade `key` não pode ser atualizada. Permitido para administradores. |
| **Custom Objects - Delete Custom Object** | DELETE | Exclui permanentemente o objeto personalizado com a chave informada. Permitido para administradores. |
| **Custom Objects - List Access Rules** | GET | Retorna a lista de regras de acesso de um objeto personalizado, que definem condições restringindo quais registros uma função pode acessar. Permitido para administradores. |
| **Custom Objects - Create Access Rule** | POST | Cria uma regra de acesso para um objeto personalizado, definindo condições que restringem quais registros uma função pode acessar com base em valores de campos ou relacionamentos. |
| **Custom Objects - List Access Rule Definitions** | GET | Retorna as definições de campos e os operadores disponíveis para criar regras de acesso de um objeto personalizado, indicando quais campos podem ser filtrados e quais operadores se aplicam a cada tipo. |
| **Custom Objects - Show Access Rule** | GET | Retorna uma regra de acesso específica de um objeto personalizado. Permitido para administradores. |
| **Custom Objects - Update Access Rule** | PATCH | Atualiza uma regra de acesso existente de um objeto personalizado. Permitido para administradores. |
| **Custom Objects - Delete Access Rule** | DELETE | Exclui permanentemente uma regra de acesso de um objeto personalizado. Permitido para administradores. |
| **Custom Objects - List Custom Object Fields** | GET | Lista todos os campos personalizados não excluídos do objeto informado, com paginação por cursor (recomendada) ou por offset. Permitido para agentes. |
| **Custom Objects - Create Custom Object Field** | POST | Cria um campo personalizado dos tipos text, textarea, checkbox, currency, date, integer, decimal, regexp, dropdown, lookup, multiselect ou parent, inclusive campos de resumo roll-up. Permitido para administradores. |
| **Custom Objects - Reorder Custom Fields of an Object** | PUT | Define a ordem preferida dos campos personalizados de um objeto informando os ids dos campos na ordem desejada. Permitido para administradores. |
| **Custom Objects - Show Custom Object Field** | GET | Retorna um campo personalizado de um objeto específico a partir da chave ou do id do campo. Permitido para agentes. |
| **Custom Objects - Update Custom Object Field** | PATCH | Atualiza um campo personalizado do objeto; a propriedade `key` não pode ser alterada e, em campos padrão, somente `title`, `description` e `properties` são editáveis. Em listas suspensas, envie todas as opções existentes. |
| **Custom Objects - Delete Custom Object Field** | DELETE | Exclui o campo com a chave informada; campos padrão não podem ser excluídos. Permitido para administradores. |
| **Custom Objects - Custom Object Record Bulk Jobs** | POST | Enfileira um job em segundo plano para executar ações em massa (create, update, delete, delete_by_external_id, create_or_update_by_external_id ou create_or_update_by_name) em até 100 registros por requisição. |
| **Custom Objects - Custom Object Fields Limit** | GET | Lista a contagem atual e o limite de campos de um objeto personalizado. Permitido para agentes. |
| **Custom Objects - List Permission Policies** | GET | Retorna a lista de políticas de permissão de um objeto personalizado, que definem quais ações (criar, ler, atualizar, excluir) cada função pode executar nos registros. Permitido para administradores. |
| **Custom Objects - Show Permission Policy** | GET | Retorna a política de permissão de uma função específica em um objeto personalizado; o id da política pode ser `custom-role-{custom_role_id}` ou `end-user`. Permitido para administradores. |
| **Custom Objects - Update Permission Policy** | PATCH | Atualiza a política de permissão de uma função em um objeto personalizado, definindo quais ações (criar, ler, atualizar, excluir) a função pode executar e, opcionalmente, as regras de acesso aplicáveis. |
| **Custom Objects - List Custom Object Records** | GET | Lista todos os registros não excluídos do objeto personalizado informado, apenas com paginação por cursor. Se o objeto tiver campo pai com `cascade_permissions_enabled`, agentes não administradores recebem 403. |
| **Custom Objects - Create Custom Object Record** | POST | Cria um registro conforme a definição do objeto personalizado; com `autoincrement_enabled` o nome é gerado automaticamente e, se o objeto tiver campo de relacionamento pai, ele é obrigatório. Permitido para agentes. |
| **Custom Objects - Create or Update Custom Object Record** | PATCH | Cria ou atualiza um registro de objeto personalizado com base no id externo ou no nome informado, alterando apenas os atributos enviados; id externo e nome não podem ser usados juntos na mesma requisição. |
| **Custom Objects - Delete Custom Object Record by External Id Or Name** | DELETE | Exclui o registro com o id externo ou o nome informado, que não podem ser usados juntos na mesma requisição; se o registro for pai em um relacionamento, os registros filhos também são excluídos de forma assíncrona. |
| **Custom Objects - Autocomplete Custom Object Record Search** | GET | Retorna os registros do objeto personalizado cujo valor de campo corresponde ao informado no parâmetro `name`, apenas com paginação por cursor e limitado aos 10.000 primeiros registros ordenados por relevância. |
| **Custom Objects - Count Custom Object Records** | GET | Retorna a contagem total de registros de um objeto personalizado e o momento em que a contagem foi atualizada. Agentes não administradores recebem 403 se o objeto tiver campo pai com `cascade_permissions_enabled`. |
| **Custom Objects - Search Custom Object Records** | GET | Retorna os registros de um objeto personalizado cuja busca corresponde aos valores de campos de texto, texto multilinha e RegExp, ordenados por relevância e paginados apenas por cursor. |
| **Custom Objects - Filtered Search of Custom Object Records** | POST | Retorna os registros de um objeto personalizado que atendem aos critérios de busca e filtro, aceitando objetos de comparação e grupos lógicos $and/$or, com paginação apenas por cursor. |
| **Custom Objects - Show Custom Object Record** | GET | Retorna um registro de um objeto personalizado específico a partir do id informado. |
| **Custom Objects - Update Custom Object Record** | PATCH | Atualiza um registro individual de objeto personalizado a partir de um objeto custom_object_record, com os campos do objeto aninhados em custom_object_fields. |
| **Custom Objects - Delete Custom Object Record** | DELETE | Exclui o registro com o id informado; se ele for pai em uma relação pai-filho, os registros filhos associados também são excluídos de forma assíncrona em segundo plano. |
| **Custom Objects - List Custom Object Record Attachments** | GET | Lista todos os anexos associados a um registro de objeto personalizado. |
| **Custom Objects - Create Custom Object Record Attachment** | POST | Cria um novo anexo associado a um registro de objeto personalizado; o objeto personalizado precisa ter a configuração allows_attachments habilitada. |
| **Custom Objects - Update Custom Object Record Attachment for Malware** | PUT | Atualiza as configurações de acesso a malware do anexo informado, normalmente para liberar o acesso a anexos sinalizados como contendo malware. |
| **Custom Objects - Delete Custom Object Record Attachment** | DELETE | Exclui o anexo informado associado a um registro de objeto personalizado. |
| **Custom Objects - Download Custom Object Record Attachment** | GET | Baixa o conteúdo do anexo informado, retornando um redirecionamento para a URL do conteúdo; o acesso a anexos maliciosos é controlado pela configuração malware_access_override. |
| **Custom Objects - List Object Triggers** | GET | Lista todos os gatilhos do objeto personalizado informado. |
| **Custom Objects - Create Object Trigger** | POST | Cria um novo gatilho de objeto para o objeto informado. |
| **Custom Objects - List Active Object Triggers** | GET | Lista todos os gatilhos de objeto ativos, com paginação por cursor ou por offset e no máximo 100 registros por página. |
| **Custom Objects - List Object Trigger Action and Condition Definitions** | GET | Lista as condições e as ações de todos os gatilhos do objeto personalizado informado. |
| **Custom Objects - Delete Many Object Triggers** | DELETE | Exclui os gatilhos de objeto correspondentes à lista de ids separados por vírgula; a exclusão em massa só é possível para gatilhos de um único objeto, indicado pelo custom_object_key da requisição. |
| **Custom Objects - Search Object Triggers** | GET | Retorna a lista de gatilhos de objeto que atendem aos critérios de busca ou de filtro informados, com paginação apenas por offset. |
| **Custom Objects - Update Many Object Triggers** | PUT | Atualiza a posição ou o status ativo de vários gatilhos de objeto, ignorando outras propriedades; a atualização em massa só vale para gatilhos de um único objeto, indicado pelo custom_object_key. |
| **Custom Objects - Show Object Trigger** | GET | Retorna os detalhes de um gatilho de objeto específico. |
| **Custom Objects - Update Object Trigger** | PUT | Atualiza o gatilho de objeto informado; alterar uma condição ou ação substitui os arrays de conditions e actions por completo, então envie todas as condições e ações desejadas. |
| **Custom Objects - Delete Object Trigger** | DELETE | Exclui o gatilho de objeto informado. |
| **Custom Roles - List Custom Roles** | GET | Lista as funções personalizadas da conta. Disponível apenas para contas no plano Enterprise ou superior e permitido para agentes. |
| **Custom Roles - Create Custom Role** | POST | Cria uma função personalizada. Disponível apenas para contas no plano Enterprise ou superior e permitido para administradores e agentes com a permissão manage_roles. |
| **Custom Roles - Show Custom Role** | GET | Exibe uma função personalizada específica. Disponível apenas para contas no plano Enterprise ou superior e permitido para administradores e agentes com a permissão manage_roles. |
| **Custom Roles - Update Custom Role** | PUT | Atualiza uma função personalizada. Disponível apenas para contas no plano Enterprise ou superior e permitido para administradores e agentes com a permissão manage_roles. |
| **Custom Roles - Delete Custom Role** | DELETE | Exclui uma função personalizada. Disponível apenas para contas no plano Enterprise ou superior e permitido para administradores e agentes com a permissão manage_roles. |
| **Custom Status - Bulk Update Default Custom Ticket Status** | PUT | Atualiza de uma só vez os valores padrão de vários status de ticket personalizados. |
| **Custom Statuses - List Custom Ticket Statuses** | GET | Lista todos os status de ticket personalizados não excluídos da conta; este endpoint não oferece paginação. |
| **Custom Statuses - Create Custom Ticket Status** | POST | Cria um status de ticket personalizado a partir de um objeto custom_status com as propriedades desejadas. |
| **Custom Statuses - Show Custom Ticket Status** | GET | Retorna o objeto do status de ticket personalizado informado. |
| **Custom Statuses - Update Custom Ticket Status** | PUT | Atualiza um status de ticket personalizado a partir de um objeto custom_status com as propriedades a serem alteradas. |
| **Custom Statuses - Delete Custom Ticket Status** | DELETE | Exclui o status de ticket personalizado; antes disso, o status precisa ser removido de todos os tickets ativos (não fechados). |
| **Custom Statuses - Create Ticket Form Statuses for a Custom Status** | POST | Cria uma ou várias associações de status de formulário de ticket para um status personalizado. |
| **Deleted Tickets - List Deleted Tickets** | GET | Lista os tickets excluídos e ainda não arquivados dos últimos 30 dias, ordenados por data de criação do mais antigo para o mais recente, retornando no máximo 100 registros por página. |
| **Deleted Tickets - Delete Multiple Tickets Permanently** | DELETE | Exclui permanentemente até 100 tickets já removidos de forma reversível, a partir de uma lista de ids separados por vírgula. Enfileira um job em segundo plano e retorna o job_status; a operação não pode ser desfeita. |
| **Deleted Tickets - Restore Previously Deleted Tickets in Bulk** | PUT | Restaura em lote tickets excluídos anteriormente. Disponível para agentes. |
| **Deleted Tickets - Delete Ticket Permanently** | DELETE | Exclui permanentemente um ticket já removido de forma reversível. Enfileira um job de exclusão em segundo plano e retorna o job_status; a operação não pode ser desfeita. |
| **Deleted Tickets - Restore a Previously Deleted Ticket** | PUT | Restaura um ticket excluído anteriormente. Disponível para agentes. |
| **Deleted Users - List Deleted Users** | GET | Retorna os usuários excluídos, incluindo os excluídos permanentemente, cujos dados pessoais como email e phone vêm nulos. Paginação por cursor ou offset, no máximo 100 registros por página. |
| **Deleted Users - Count Deleted Users** | GET | Retorna a contagem aproximada de usuários excluídos, incluindo os excluídos permanentemente; acima de 100.000 o valor é atualizado a cada 24 horas e count[refreshed_at] indica a última atualização. Permitido para agentes. |
| **Deleted Users - Show Deleted User** | GET | Retorna um usuário que foi excluído, mas ainda não de forma permanente. Permitido para agentes. |
| **Deleted Users - Permanently Delete User** | DELETE | Exclui permanentemente um usuário já excluído antes, apagando todas as suas informações de forma irrecuperável. O limite é de 700 exclusões permanentes a cada 10 minutos. |
| **Dynamic Content - List Items** | GET | Retorna a lista de todos os itens de conteúdo dinâmico da conta, quando acessado por administradores ou por agentes com permissão para gerenciar conteúdo dinâmico. |
| **Dynamic Content - Create Item** | POST | Cria um item de conteúdo dinâmico com uma ou mais variantes no array variants; os valores de default_locale_id e locale_id devem ser locales ativos na conta. |
| **Dynamic Content - Show Many Items** | GET | Exibe vários itens de conteúdo dinâmico em uma única requisição. Endpoint em estágio de desenvolvimento. |
| **Dynamic Content - Show Item** | GET | Exibe o item de conteúdo dinâmico especificado. Disponível para administradores e agentes. |
| **Dynamic Content - Update Item** | PUT | Atualiza o item de conteúdo dinâmico especificado; o único atributo que pode ser alterado é o nome. Para incluir, atualizar ou excluir variantes, use a API de variantes do item. |
| **Dynamic Content - Delete Item** | DELETE | Exclui o item de conteúdo dinâmico especificado. Disponível para administradores e agentes. |
| **Dynamic Content - List Variants** | GET | Retorna todas as variantes do item de conteúdo dinâmico especificado. Disponível para administradores e para agentes com permissão para gerenciar conteúdo dinâmico. |
| **Dynamic Content - Create Variant** | POST | Cria uma variante do item de conteúdo dinâmico. É possível criar apenas uma variante por locale; se já existir uma variante para o locale, a requisição é rejeitada. |
| **Dynamic Content - Create Many Variants** | POST | Cria várias variantes do item de conteúdo dinâmico em uma única requisição. Disponível para administradores e agentes. |
| **Dynamic Content - Update Many Variants** | PUT | Atualiza uma ou mais variantes do item de conteúdo dinâmico. As variantes devem ser identificadas pelo id no corpo da requisição. |
| **Dynamic Content - Show Variant** | GET | Exibe a variante especificada do item de conteúdo dinâmico. Disponível para administradores e agentes. |
| **Dynamic Content - Update Variant** | PUT | Atualiza a variante especificada, sem necessidade de enviar todas as propriedades. Não é possível alterar o estado ativo da variante padrão do item nem definir seu campo default como false. |
| **Dynamic Content - Delete Variant** | DELETE | Exclui a variante especificada do item de conteúdo dinâmico. Disponível para administradores e agentes. |
| **End Users - List End User Identities** | GET | Retorna a lista de identidades do usuário final informado; usuários finais só conseguem listar identidades de email e de telefone. Paginação por cursor ou offset, até 100 registros por página no cursor. |
| **End Users - Create End User Identity** | POST | Adiciona uma identidade ao perfil de um usuário final; os tipos suportados são email e phone_number. Permitido para usuários finais verificados. |
| **End Users - Show End User Identity** | GET | Exibe a identidade com o id informado de um usuário final; usuários finais só podem visualizar identidades de email ou de telefone. Permitido para usuários finais verificados. |
| **End Users - Delete End User Identity** | DELETE | Exclui a identidade de um usuário final; em certos casos o número de telefone associado à identidade continua visível no perfil do usuário após a exclusão pela API. |
| **End Users - Make End User Identity Primary** | PUT | Define a identidade informada como principal do usuário final; por ser uma operação de coleção, recarregue toda a coleção depois. Uma identidade de email só pode se tornar principal se o email estiver verificado. |
| **End Users - Request End User Verification** | PUT | Envia ao usuário final um email de verificação com um link para confirmar a posse do endereço de email. Permitido para usuários finais verificados. |
| **Group Memberships - List Memberships** | GET | Lista as associações entre agentes e grupos, com paginação por cursor (recomendada) ou por offset, no máximo 100 registros por página. Permitido para agentes. |
| **Group Memberships - Create Membership** | POST | Atribui um agente a um grupo informado. Permitido para administradores e para agentes com função personalizada que permita gerenciar associações de grupo (apenas Enterprise). |
| **Group Memberships - List Assignable Memberships** | GET | Lista as associações de grupo que podem receber atribuição de tickets, com paginação por cursor (recomendada) ou por offset, no máximo 100 registros por página. Permitido para agentes. |
| **Group Memberships - Bulk Create Memberships** | POST | Atribui até 100 agentes a grupos informados. Retorna um objeto job_status e enfileira um job em segundo plano; use Show Job Status para acompanhar a conclusão. |
| **Group Memberships - Bulk Delete Memberships** | DELETE | Remove imediatamente usuários dos grupos e agenda um job para desatribuir todos os tickets em andamento vinculados às combinações de usuário e grupo informadas. |
| **Group Memberships - Show Membership** | GET | Exibe uma associação de grupo específica. O id informado é o id da associação de grupo, não o id do grupo. Permitido para agentes. |
| **Group Memberships - Delete Membership** | DELETE | Remove imediatamente um usuário de um grupo e agenda um job para desatribuir todos os tickets em andamento vinculados àquela combinação de usuário e grupo. |
| **Group SLAs - List Group SLA Policies** | GET | Lista as políticas de SLA de grupo da conta. Disponível para administradores. |
| **Group SLAs - Create Group SLA Policy** | POST | Cria uma política de SLA de grupo. Disponível para administradores. |
| **Group SLAs - Retrieve Supported Filter Definition Items** | GET | Retorna os itens de definição de filtro suportados nas políticas de SLA de grupo. Disponível para administradores. |
| **Group SLAs - Reorder Group SLA Policies** | PUT | Reordena as políticas de SLA de grupo conforme a lista de IDs informada. Disponível para administradores. |
| **Group SLAs - Show Group SLA Policy** | GET | Exibe a política de SLA de grupo especificada. Disponível para administradores. |
| **Group SLAs - Update Group SLA Policy** | PUT | Atualiza a política de SLA de grupo especificada. Disponível para administradores. |
| **Group SLAs - Delete Group SLA Policy** | DELETE | Exclui a política de SLA de grupo especificada. Disponível para administradores. |
| **Groups - List Groups** | GET | Lista os grupos da conta, com paginação por cursor (recomendada) ou por offset, no máximo 100 registros por página. Permitido para administradores e agentes. |
| **Groups - Create Group** | POST | Cria um grupo. Permitido para administradores e para agentes com função personalizada que permita gerenciar grupos (apenas Enterprise). |
| **Groups - List Assignable Groups** | GET | Lista os grupos que podem receber atribuição de tickets, com paginação por cursor (recomendada) ou por offset, no máximo 100 registros por página. Permitido para administradores e agentes. |
| **Groups - Autocomplete Groups** | GET | Retorna a lista de grupos cujo nome começa com o valor informado no parâmetro name. Permitido para administradores e agentes. |
| **Groups - List Available Agents** | GET | Retorna a lista de todos os agentes disponíveis para serem adicionados a grupos; o usuário atual precisa de permissão para editar associações de grupo. Paginação por cursor, até 1000 registros por página. |
| **Groups - Count Groups** | GET | Retorna a contagem aproximada de grupos; acima de 100.000 o valor é atualizado a cada 24 horas e a propriedade refreshed_at indica a última atualização. Permitido para administradores e agentes. |
| **Groups - Show Default Group** | GET | Exibe o grupo padrão da conta. Permitido para administradores e agentes. |
| **Groups - Show Group** | GET | Exibe um grupo específico. Permitido para administradores e agentes. |
| **Groups - Update Group** | PUT | Atualiza um grupo existente. Permitido para administradores. |
| **Groups - Delete Group** | DELETE | Exclui um grupo. Permitido para administradores e para agentes com função personalizada que permita gerenciar grupos (apenas Enterprise). |
| **Groups - List Memberships By Group** | GET | Retorna a lista de todas as associações de um grupo específico, com paginação por cursor (recomendada) ou por offset, no máximo 100 registros por página. Permitido para agentes. |
| **Groups - List Assignable Memberships By Group** | GET | Retorna a lista de associações de um grupo específico que podem receber atribuição, com paginação por cursor (recomendada) ou por offset, no máximo 100 registros por página. Permitido para agentes. |
| **Groups - List Users By Group** | GET | Lista os usuários de um grupo específico, com paginação por cursor (recomendada) ou por offset, no máximo 100 registros por página. Permitido para administradores, agentes e light agents. |
| **Groups - Count Users By Group** | GET | Retorna a contagem aproximada de usuários do grupo informado; acima de 100.000 o valor é atualizado a cada 24 horas e refreshed_at indica a última atualização. Permitido para administradores, agentes e light agents. |
| **Imports - Ticket Import** | POST | Importa um ticket já existente, com seu histórico, para o Zendesk. Disponível para administradores. |
| **Imports - Ticket Bulk Import** | POST | Importa tickets em lote, aceitando um array de até 100 objetos de ticket. Disponível para administradores. |
| **Incremental - Incremental Custom Object Record Export, Cursor Based** | GET | Retorna os registros de objetos personalizados alterados desde o start_time, usando exportação incremental baseada em cursor. Aceita somente paginação por cursor e permite até 10 requisições por minuto. |
| **Incremental - Incremental Organization Export** | GET | Exportação incremental de organizações: retorna as organizações alteradas a partir do horário informado. Permitido para administradores e compatível com sideload de organizações. |
| **Incremental - Incremental Attributes Values Export** | GET | Retorna o fluxo de alterações ocorridas nos valores de atributos de roteamento. Permitido para administradores. |
| **Incremental - Incremental Attributes Export** | GET | Retorna o fluxo de alterações ocorridas nos atributos de roteamento. Permitido para administradores. |
| **Incremental - Incremental Instance Values Export** | GET | Retorna o fluxo de alterações ocorridas nos valores de instância de roteamento, agrupadas por attribute_value_id. Permitido para administradores. |
| **Incremental - Incremental Ticket Event Export** | GET | Retorna o fluxo de alterações ocorridas em tickets, excluindo eventos do último minuto. Cada evento está ligado a uma atualização de ticket e traz os campos alterados. Permitido para administradores. |
| **Incremental - List Ticket Metric Events** | GET | Retorna os eventos de métricas de tickets ocorridos a partir do start_time, em ordem cronológica. Com paginação por cursor, retorna no máximo 100 registros por página. Permitido para administradores. |
| **Incremental - Incremental Ticket Export, Time Based** | GET | Retorna os tickets alterados desde o start_time usando exportação incremental baseada em tempo. Os resultados incluem tickets atualizados pelo sistema. Permitido para administradores. |
| **Incremental - Incremental Ticket Export, Cursor Based** | GET | Retorna os tickets alterados desde o start_time usando exportação incremental baseada em cursor, abordagem recomendada por oferecer desempenho e tamanho de resposta mais consistentes. Permitido para administradores. |
| **Incremental - Incremental User Export, Time Based** | GET | Exportação incremental de usuários baseada em tempo: retorna os usuários alterados a partir do horário informado. Permitido para administradores e compatível com sideload de usuários. |
| **Incremental - Incremental User Export, Cursor Based** | GET | Exportação incremental de usuários baseada em cursor: retorna os usuários alterados usando paginação por cursor. Permitido para administradores e compatível com sideload de usuários. |
| **Incremental - Incremental Sample Export** | GET | Testa o formato de exportação incremental. Tem limite mais restrito (10 requisições por 20 minutos) e retorna até 50 resultados. Use incremental_resource para indicar o recurso. Permitido para administradores. |
| **Macros - List Macros** | GET | Lista todas as macros compartilhadas e pessoais disponíveis para o usuário atual; para administradores, retorna todas as macros da conta, incluindo as macros pessoais de agentes e de outros administradores. |
| **Macros - Create Macro** | POST | Cria uma macro. Disponível para agentes. |
| **Macros - List Supported Actions for Macros** | GET | Lista as ações suportadas em macros. Disponível para agentes. |
| **Macros - List Active Macros** | GET | Lista todas as macros ativas, compartilhadas e pessoais, disponíveis para o usuário atual. |
| **Macros - Create Unassociated Macro Attachment** | POST | Envia um anexo que pode ser associado a uma macro posteriormente. Associe o anexo a uma macro o quanto antes, pois anexos antigos sem macro associada são removidos periodicamente. |
| **Macros - Show Macro Attachment** | GET | Exibe as propriedades do anexo de macro especificado. Disponível para agentes. |
| **Macros - List Macro Categories** | GET | Lista todas as categorias de macro disponíveis para o usuário atual. Permitido para agentes. |
| **Macros - List Macro Action Definitions** | GET | Retorna as definições das ações que uma macro pode executar, incluindo título, tipo e valores possíveis de cada ação. Permitido para agentes. |
| **Macros - Bulk Delete Macros** | DELETE | Exclui as macros correspondentes à lista de IDs separados por vírgula informada. Permitido para agentes. |
| **Macros - Show Macro Replica** | GET | Retorna uma representação de macro não persistida derivada de um ticket ou de uma macro. Informe `macro_id` ou `ticket_id`; se ambos forem enviados, `macro_id` é usado. Permitido para agentes. |
| **Macros - Search Macros** | GET | Pesquisa macros da conta. Suporta apenas paginação por offset. Permitido para agentes. |
| **Macros - Update Many Macros** | PUT | Atualiza as macros informadas com as alterações especificadas. Permitido para agentes. |
| **Macros - Show Macro** | GET | Retorna os detalhes da macro especificada. Permitido para agentes. |
| **Macros - Update Macro** | PUT | Atualiza a macro especificada. Permitido para agentes. |
| **Macros - Delete Macro** | DELETE | Exclui a macro especificada. Permitido para agentes, com restrições aplicáveis a determinadas ações. |
| **Macros - Show Changes to Ticket** | GET | Retorna apenas os campos do ticket que a macro alteraria, sem alterar o ticket de fato. Os dados da resposta podem ser usados em uma chamada posterior ao endpoint de tickets. Permitido para agentes. |
| **Macros - List Macro Attachments** | GET | Lista os anexos associados a uma macro. Permitido para agentes. |
| **Macros - Create Macro Attachment** | POST | Permite enviar um anexo e associá-lo a uma macro na mesma chamada. Uma macro pode ter no máximo cinco anexos associados. Permitido para agentes. |
| **Organization Fields - List Organization Fields** | GET | Retorna a lista de campos personalizados de organização da conta, na ordem definida na configuração do Zendesk Support. Paginação por cursor (recomendada) ou por offset, no máximo 100 registros por página. |
| **Organization Fields - Create Organization Field** | POST | Cria um campo personalizado de organização de um dos tipos: text (padrão quando o tipo não é informado), textarea, checkbox, date, integer, decimal, regexp, dropdown, lookup ou multiselect. Permitido para administradores. |
| **Organization Fields - Reorder Organization Field** | PUT | Reordena os campos personalizados de organização da conta. Permitido para administradores. |
| **Organization Fields - Show Organization Field** | GET | Retorna os detalhes de um campo de organização específico. Permitido para agentes. |
| **Organization Fields - Update Organization Field** | PUT | Atualiza um campo de organização. Em campos dropdown (tagger) ou multiselect, envie todas as opções em `custom_field_options`, pois as omitidas são removidas. Permitido para administradores. |
| **Organization Fields - Delete Organization Field** | DELETE | Exclui um campo de organização. Permitido para administradores. |
| **Organization Memberships - List Memberships** | GET | Retorna a lista de vínculos de organização da conta, do usuário ou da organização em questão. Para um usuário, a organização padrão vem primeiro e as demais são ordenadas por nome. Retorna no máximo 100 registros por página. |
| **Organization Memberships - Create Membership** | POST | Atribui um usuário a uma organização. Retorna erro com status 422 se o usuário já estiver atribuído à organização. Permitido para administradores e para agentes ao criar vínculo de um usuário final. |
| **Organization Memberships - Create Many Memberships** | POST | Aceita um array de até 100 objetos de vínculo de organização. Retorna um objeto `job_status` e enfileira um job em background; use Show Job Status para verificar a conclusão. Permitido para administradores e agentes. |
| **Organization Memberships - Bulk Delete Memberships** | DELETE | Remove imediatamente os usuários das organizações e agenda um job para desatribuir os tickets em andamento dessa combinação, definindo o `organization_id` deles como null. Retorna um objeto `job_status`. Permitido para agentes. |
| **Organization Memberships - Show Membership** | GET | Retorna os detalhes de um vínculo de organização específico. Permitido para agentes. |
| **Organization Memberships - Delete Membership** | DELETE | Remove imediatamente o usuário da organização e agenda um job para desatribuir todos os tickets em andamento dessa combinação, definindo o `organization_id` deles como null. Permitido para administradores e agentes. |
| **Organization Merges - Show Organization Merge** | GET | Recupera os detalhes de uma operação de mesclagem de organizações, incluindo os IDs da organização vencedora e da perdedora, o status da mesclagem e as URLs associadas. Permitido para administradores. |
| **Organization Subscriptions - List Organization Subscriptions** | GET | Lista as inscrições em organizações, com no máximo 100 registros por página. Permitido para agentes e usuários finais; para usuários finais, apenas as inscrições criadas por quem faz a requisição. |
| **Organization Subscriptions - Create Organization Subscription** | POST | Cria uma inscrição em uma organização. Permitido para agentes e usuários finais; usuários finais só podem se inscrever em organizações compartilhadas das quais são membros. |
| **Organization Subscriptions - Show Organization Subscription** | GET | Retorna os detalhes de uma inscrição em organização específica. Permitido para agentes e usuários finais; para usuários finais, apenas as inscrições criadas por quem faz a requisição. |
| **Organization Subscriptions - Delete Organization Subscription** | DELETE | Exclui uma inscrição em organização. Permitido para agentes e usuários finais. |
| **Organizations - List Organizations** | GET | Lista as organizações da conta, com no máximo 100 registros por página. Permitido para agentes com restrições: se o papel customizado do agente limitar o acesso à própria organização, retorna erro 403 Forbidden. |
| **Organizations - Create Organization** | POST | Cria uma organização; o `name` deve ser único. Espaços no início e no fim do nome são removidos antes da validação, de modo que nomes que diferem apenas por espaços são tratados como duplicados. |
| **Organizations - Autocomplete Organizations** | GET | Retorna um array de organizações cujo nome começa com o valor informado no parâmetro `name`. Usa apenas paginação por offset. Permitido para agentes. |
| **Organizations - Count Organizations** | GET | Retorna uma contagem aproximada de organizações; acima de 100.000 ela é atualizada a cada 24 horas. A propriedade `refreshed_at` do objeto `count` indica a última atualização e pode vir nula nesse caso. |
| **Organizations - Create Many Organizations** | POST | Aceita um array de até 100 objetos de organização. Retorna um objeto `job_status` e enfileira um job em background; use Show Job Status para verificar a conclusão. Permitido para agentes, com restrições em certas ações. |
| **Organizations - Create Or Update Organization** | POST | Cria a organização se ela ainda não existir ou atualiza a existente. Informe o id ou o external id ao atualizar para evitar erro de duplicidade; o nome não serve como critério de correspondência. |
| **Organizations - Bulk Delete Organizations** | DELETE | Aceita uma lista separada por vírgulas de até 100 ids ou external ids de organizações. Retorna um objeto `job_status` e enfileira um job em background para executar o trabalho. Permitido para administradores. |
| **Organizations - Search Organizations** | GET | Retorna as organizações que correspondem ao critério. É possível buscar pelo `external_id` ou pelo `name`, mas não por ambos; a correspondência deve ser exata, sem diferenciar maiúsculas de minúsculas. |
| **Organizations - Show Many Organizations** | GET | Aceita uma lista separada por vírgulas de até 100 ids ou external ids de organizações. Permitido para administradores e agentes. |
| **Organizations - Update Many Organizations** | PUT | Atualiza até 100 organizações em massa (mesma alteração para todas, via `ids`) ou em lote (alterações diferentes por organização). Retorna um objeto `job_status` e enfileira um job em background. |
| **Organizations - Show Organization** | GET | Retorna os detalhes de uma organização específica. Permitido para administradores e agentes. |
| **Organizations - Update Organization** | PUT | Atualiza uma organização. Atualizar `domain_names` sobrescreve todos os valores existentes, portanto envie a lista completa. Agentes sem restrições de permissão só podem atualizar "notes". |
| **Organizations - Delete Organization** | DELETE | Exclui uma organização. Permitido para administradores e para agentes com papel customizado com permissão para gerenciar organizações (apenas Enterprise). |
| **Organizations - Merge Organization With Another Organization** | POST | Mescla duas organizações, movendo usuários, tickets e nomes de domínio da organização indicada em `{organization_id}` para a definida em `winner_id`. A organização perdedora é excluída. Operação irreversível. |
| **Organizations - List Organization Merges** | GET | Lista todas as operações de mesclagem associadas a uma organização, com o id da mesclagem, os IDs das organizações vencedora e perdedora, o status atual e a URL do registro. Até 100 registros por página. |
| **Organizations - List Organization Memberships by Organization** | GET | Retorna a lista de vínculos de organização da organização em questão, com no máximo 100 registros por página. Permitido para agentes e usuários finais. |
| **Organizations - Show Organization's Related Information** | GET | Retorna as informações relacionadas a uma organização específica. Permitido para agentes. |
| **Organizations - List Organization Requests** | GET | Retorna a lista de requisições de uma organização específica. Permitido para usuários finais. |
| **Organizations - List Subscriptions By Organization** | GET | Retorna a lista de inscrições de uma organização específica, com no máximo 100 registros por página. Para usuários finais, são listadas apenas as inscrições criadas por quem faz a requisição. |
| **Organizations - List Organization Tags** | GET | Lista as tags de uma organização. Permitido para agentes. |
| **Organizations - Set Organization Tags** | POST | Define as tags de uma organização. Permitido para agentes. |
| **Organizations - Add Organization Tags** | PUT | Adiciona tags a uma organização. Permitido para agentes. |
| **Organizations - Remove Organization Tags** | DELETE | Remove tags de uma organização. Permitido para agentes. |
| **Organizations - List Organization Tickets** | GET | Retorna a lista de tickets de uma organização específica. Permitido para agentes. |
| **Organizations - Count Organization Tickets** | GET | Retorna uma contagem aproximada de tickets de uma organização; acima de 100.000 ela é atualizada a cada 24 horas. `count[refreshed_at]` indica a última atualização e pode vir nula nesse caso. |
| **Organizations - List Organization Users** | GET | Retorna a lista de usuários de uma organização específica, com no máximo 100 registros por página. Permitido para administradores, agentes e light agents. |
| **Organizations - Count Organization Users** | GET | Retorna uma contagem aproximada de usuários de uma organização; acima de 100.000 ela é atualizada a cada 24 horas. A propriedade `refreshed_at` do objeto `count` indica a última atualização. |
| **Problems - List Ticket Problems** | GET | Lista os tickets do tipo problema. A resposta é sempre ordenada por updated_at em ordem decrescente. |
| **Problems - Autocomplete Problems** | POST | Retorna os tickets do tipo "problem" cujo assunto contém o texto informado no parâmetro text, que pode ser enviado no corpo da requisição em vez da query string. |
| **Relationships - Filter Definitions** | GET | Retorna as definições de filtro do tipo de destino informado (zen:user, zen:ticket, zen:organization ou zen:custom_object:CUSTOM_OBJECT_KEY), usadas para montar o relationship_filter de um campo. |
| **Requests - List Requests** | GET | Lista as solicitações (requests) do usuário final autenticado. Para grandes volumes, use paginação por cursor com páginas menores para evitar erros intermitentes 503. |
| **Requests - Create Request** | POST | Cria uma solicitação a partir de um objeto request com uma ou mais propriedades. O comment é obrigatório e, em solicitações anônimas, o requester também. Use via_followup_source_id para criar follow-up de ticket fechado. |
| **Requests - List CCD Requests** | GET | Lista as solicitações em que o usuário final autenticado está em cópia (CC). |
| **Requests - List Open Requests** | GET | Lista as solicitações com status "open" do usuário final autenticado. |
| **Requests - Search Requests** | GET | Busca solicitações por termo, podendo filtrar por organização, CC e status. Usa apenas paginação por offset e retorna até 1.000 resultados por consulta, com no máximo 100 por página. |
| **Requests - List Solved Requests** | GET | Lista as solicitações com status "solved" do usuário final autenticado. |
| **Requests - Show Request** | GET | Retorna os dados de uma solicitação específica. Suporta o sideload users, que traz os endereços em cópia da solicitação. |
| **Requests - Update Request** | PUT | Atualiza uma solicitação com um comentário ou colaboradores em cópia, e permite ao usuário que a criou marcá-la como resolvida. Nenhum outro atributo da solicitação pode ser alterado por este endpoint. |
| **Requests - Listing Comments** | GET | Lista os comentários de uma solicitação. Por padrão são ordenados por data de criação em ordem crescente, e a ordenação pode ser alterada com sort ou com sort_by e sort_order. |
| **Requests - Getting Comments** | GET | Retorna um comentário específico de uma solicitação. Disponível para usuários finais. |
| **Resource Collections - List Resource Collections** | GET | Lista as coleções de recursos da conta. Permitido para administradores. |
| **Resource Collections - Create Resource Collection** | POST | Cria uma coleção de recursos a partir de um objeto `payload`, especificado como o conteúdo de um requirements.json de app Zendesk. A resposta inclui um job status da criação dos recursos. Permitido para administradores. |
| **Resource Collections - Show Resource Collection** | GET | Recupera os detalhes da coleção de recursos especificada. Permitido para administradores. |
| **Resource Collections - Update Resource Collection** | PUT | Atualiza uma coleção de recursos usando um objeto `payload`, especificado como o conteúdo de um requirements.json de app Zendesk. A resposta inclui um job status das atualizações. Permitido para administradores. |
| **Resource Collections - Delete Resource Collection** | DELETE | Exclui a coleção de recursos especificada. A resposta inclui um job status da exclusão dos recursos da coleção. Permitido para administradores. |
| **Search - List Search Results** | GET | Retorna os resultados da busca conforme a sintaxe do parâmetro query. Usa apenas paginação por offset, que pode gerar resultados duplicados entre páginas, e possui limite de requisições próprio. Permitido para agentes. |
| **Search - Show Results Count** | GET | Retorna a quantidade de itens que correspondem à consulta, em vez dos próprios itens. A string de busca funciona como em uma busca comum. Permitido para agentes. |
| **Search - Export Search Results** | GET | Exporta um conjunto de resultados de busca, indicado para consultas com mais de 1000 resultados. Retorna apenas um tipo de objeto (ticket, organização, usuário ou grupo), definido em filter[type], com paginação por cursor. |
| **Skips - List All Skips** | GET | Lista todos os registros de tickets ignorados (skips). Tickets arquivados não são incluídos na resposta e são retornados no máximo 100 registros por página. |
| **Skips - Record a New Skip for the Current User** | POST | Registra um novo skip de ticket para o usuário atual. Disponível para agentes. |
| **SLAs - List SLA Policies** | GET | Lista as políticas de SLA da conta. Disponível para contas nos planos Support Professional ou Suite Growth ou superiores. Permitido para administradores. |
| **SLAs - Create SLA Policy** | POST | Cria uma política de SLA. Disponível para contas nos planos Support Professional ou Suite Growth ou superiores. Permitido para administradores. |
| **SLAs - Retrieve Supported Filter Definition Items** | GET | Retorna os itens de definição de filtro suportados pelas políticas de SLA. Disponível para contas nos planos Support Professional ou Suite Growth ou superiores. Permitido para administradores. |
| **SLAs - Reorder SLA Policies** | PUT | Reordena as políticas de SLA da conta. Disponível para contas nos planos Support Professional ou Suite Growth ou superiores. Permitido para administradores. |
| **SLAs - Show SLA Policy** | GET | Retorna os detalhes da política de SLA especificada. Disponível para contas nos planos Support Professional ou Suite Growth ou superiores. Permitido para administradores. |
| **SLAs - Update SLA Policy** | PUT | Atualiza a política de SLA especificada. Disponível para contas nos planos Support Professional ou Suite Growth ou superiores. Permitido para administradores. |
| **SLAs - Delete SLA Policy** | DELETE | Exclui a política de SLA especificada. Disponível para contas nos planos Support Professional ou Suite Growth ou superiores. Permitido para administradores. |
| **Suspended Tickets - List Suspended Tickets** | GET | Lista os tickets suspensos da conta. A ordenação pode ser definida pelos parâmetros de query sort_by e sort_order, e a paginação é por cursor. |
| **Suspended Tickets - Suspended Ticket Attachments** | POST | Cria copias dos anexos de um ticket suspenso e as retorna como tokens de anexo, que podem ser incluídos no novo ticket caso a recuperação seja feita manualmente. |
| **Suspended Tickets - Bulk Recover Suspended Tickets** | PUT | Enfileira um job em lote para recuperar vários tickets suspensos e retorna um job status que pode ser acompanhado pela API de Job Statuses. Indicado para grandes volumes, por ser assíncrono. |
| **Suspended Tickets - Delete Multiple Suspended Tickets** | DELETE | Exclui vários tickets suspensos, aceitando até 100 ids (o id gerado automaticamente para o ticket suspenso, e não o id do ticket). |
| **Suspended Tickets - Export Suspended Tickets** | POST | Exporta a lista de tickets suspensos da instância, enfileirando um job que gera um arquivo CSV. Ao concluir, a Zendesk envia por e-mail ao solicitante o link do arquivo, com os tickets ordenados pela data de atualização. |
| **Suspended Tickets - Recover Multiple Suspended Tickets** | PUT | Recupera vários tickets suspensos, aceitando até 100 ids (o id gerado automaticamente, e não o id do ticket). Os tickets que falharem na recuperação também aparecem na resposta. |
| **Suspended Tickets - Show Suspended Ticket** | GET | Retorna os dados de um ticket suspenso específico. Disponível para administradores e agentes com permissão para gerenciar tickets suspensos. |
| **Suspended Tickets - Delete Suspended Ticket** | DELETE | Exclui um ticket suspenso específico. Disponível para agentes sem restrição. |
| **Suspended Tickets - Recover Suspended Ticket** | PUT | Recupera um ticket suspenso de forma sincrona. O solicitante passa a ser o agente autenticado que chamou a API, e não o solicitante original; para preservá-lo, use o endpoint de recuperação múltipla com um único ticket. |
| **Target Failures - List Target Failures** | GET | Retorna as 25 falhas de target mais recentes, por target. Estabilidade: em desenvolvimento. Permitido para administradores. |
| **Target Failures - Show Target Failure** | GET | Retorna os detalhes da falha de target especificada. Estabilidade: em desenvolvimento. Permitido para administradores. |
| **Targets - List Targets** | GET | Lista os targets da conta. Permitido para agentes. |
| **Targets - Create Target** | POST | Cria um target. Permitido para administradores. |
| **Targets - Show Target** | GET | Retorna os detalhes do target especificado. Permitido para agentes. |
| **Targets - Update Target** | PUT | Atualiza o target especificado. Permitido para administradores. |
| **Targets - Delete Target** | DELETE | Exclui o target especificado. Permitido para administradores. |
| **Ticket Audits - List All Ticket Audits** | GET | Retorna as auditorias de tickets, sem incluir tickets arquivados. Não deve ser usado para capturar dados de alteração, pois registros podem ser omitidos ao acompanhar continuamente o cursor. |
| **Ticket Content Pins - List Ticket Content Pins** | GET | Lista os content pins de um ticket específico. Content pins fixam conteúdos relacionados, como artigos, ao ticket para acesso rápido. |
| **Ticket Content Pins - Create Ticket Content Pin** | POST | Cria um novo content pin em um ticket específico, permitindo vincular artigos, publicações da comunidade ou conteúdo externo para consulta rápida. |
| **Ticket Content Pins - Delete Content Pin from Ticket** | DELETE | Remove um content pin específico de um ticket. Disponível para agentes. |
| **Ticket Fields - List Ticket Fields** | GET | Retorna a lista de todos os campos de ticket do sistema e personalizados da conta. Para usuários finais, apenas os campos com visible_in_portal igual a true são retornados. A paginação por cursor retorna no máximo 100 registros por página. |
| **Ticket Fields - Create Ticket Field** | POST | Cria um campo de ticket personalizado de qualquer um dos tipos suportados (text, textarea, checkbox, date, integer, decimal, regexp, partialcreditcard, multiselect, tagger ou lookup). Tags não podem ser reutilizadas entre campos personalizados. |
| **Ticket Fields - Count Ticket Fields** | GET | Retorna uma contagem aproximada dos campos de ticket do sistema e personalizados da conta. Acima de 100.000, o resultado vem de cache atualizado a cada 24 horas; count[refreshed_at] indica quando a contagem foi atualizada. |
| **Ticket Fields - Reorder Ticket Fields** | PUT | Reordena os campos de ticket conforme o array ticket_field_ids enviado no corpo. Não é preciso informar todos os IDs: os enviados assumem as primeiras posições e os ausentes recebem posições incrementais automaticamente. |
| **Ticket Fields - Show Many Ticket Fields** | GET | Retorna vários campos de ticket em uma única requisição. Informe ids (lista de IDs separados por vírgula) ou keys (lista de chaves separadas por vírgula), com até 100 valores. |
| **Ticket Fields - Show Ticket Field** | GET | Retorna os dados de um campo de ticket específico pelo seu ID. Restrito a agentes. |
| **Ticket Fields - Update Ticket Field** | PUT | Atualiza um campo de ticket, inclusive as opções de campos do tipo lista ou multisseleção via custom_field_options. Informe todas as opções existentes na requisição: opções omitidas são removidas do campo e dos tickets e macros que as usam. |
| **Ticket Fields - Delete Ticket Field** | DELETE | Exclui um campo de ticket pelo seu ID. Restrito a administradores. |
| **Ticket Fields - List Ticket Field Options** | GET | Retorna a lista de opções personalizadas do campo de ticket do tipo lista informado. Restrito a agentes. |
| **Ticket Fields - Create or Update Ticket Field Option** | POST | Cria ou atualiza uma opção do campo de ticket do tipo lista informado. Inclua o id dentro de custom_field_option para atualizar uma opção existente; sem id, uma nova opção é criada. Limite de 100 requisições por minuto. |
| **Ticket Fields - Show Ticket Field Option** | GET | Retorna uma opção específica de um campo de ticket pelo seu ID. Restrito a agentes. |
| **Ticket Fields - Delete Ticket Field Option** | DELETE | Exclui uma opção específica de um campo de ticket pelo seu ID. Restrito a administradores. |
| **Ticket Form Statuses - List Ticket Form Statuses** | GET | Retorna todos os status de formulário de ticket da conta. Permite filtrar por ID do formulário de ticket e por outros critérios usando parâmetros de consulta. |
| **Ticket Form Statuses - Show Many Ticket Form Statuses** | GET | Retorna os status de formulário de ticket indicados por uma lista de IDs separados por vírgula. |
| **Ticket Forms - List Ticket Forms** | GET | Retorna a lista de todos os formulários de ticket da conta quando o acesso é de administrador ou agente. Usuários finais visualizam apenas os formulários com end_user_visible igual a true. |
| **Ticket Forms - Create Ticket Form** | POST | Cria um novo formulário de ticket na conta. Restrito a administradores. |
| **Ticket Forms - Reorder Ticket Forms** | PUT | Reordena os formulários de ticket conforme o array ticket_form_ids enviado no corpo da requisição. Restrito a administradores. |
| **Ticket Forms - Show Many Ticket Forms** | GET | Retorna vários formulários de ticket a partir do parâmetro de consulta ids, que aceita uma lista de até 100 IDs separados por vírgula. Endpoint usado principalmente pelo SDK mobile e pelo Web Widget. |
| **Ticket Forms - Show Ticket Form** | GET | Retorna os dados de um formulário de ticket específico pelo seu ID. Disponível para administradores, agentes e usuários finais. |
| **Ticket Forms - Update Ticket Form** | PUT | Atualiza um formulário de ticket existente pelo seu ID. Restrito a administradores. |
| **Ticket Forms - Delete Ticket Form** | DELETE | Exclui um formulário de ticket pelo seu ID. Restrito a administradores. |
| **Ticket Forms - Clone an Already Existing Ticket Form** | POST | Cria uma cópia de um formulário de ticket já existente, informado pelo ID. Restrito a administradores. |
| **Ticket Forms - List Ticket Form Statuses of a Ticket Form** | GET | Retorna todos os status de formulário de ticket associados ao formulário de ticket informado. |
| **Ticket Forms - Create Ticket Form Statuses** | POST | Cria uma ou várias associações de status de formulário de ticket. Restrito a administradores. |
| **Ticket Forms - Bulk Update Ticket Form Statuses of a Ticket Form** | PUT | Atualiza ou remove associações de status de formulário de ticket. Operação em lote que pode adicionar e remover associações de um formulário em uma única chamada. Restrito a administradores. |
| **Ticket Forms - Delete Ticket Form Statuses** | DELETE | Exclui os status de formulário de ticket informados por id. Disponível para administradores e agentes. |
| **Ticket Forms - Update Ticket Form Status By Id** | PUT | Atualiza ou remove uma associação de status de formulário de ticket pelo seu id. Restrito a administradores. |
| **Ticket Forms - Delete Ticket Form Status By Id** | DELETE | Exclui um status de formulário de ticket pelo seu id. Restrito a administradores. |
| **Ticket Metrics - List Ticket Metrics** | GET | Retorna a lista de tickets com suas métricas, em ordem cronológica de criação do mais recente para o mais antigo. Tickets arquivados não são incluídos. Máximo de 100 registros por página. |
| **Ticket Metrics - Show Ticket Metrics** | GET | Retorna uma métrica específica ou as métricas de um ticket específico. Máximo de 100 registros por página. Restrito a agentes. |
| **Tickets - List Tickets** | GET | Lista os tickets da conta. |
| **Tickets - Create Ticket** | POST | Cria um ticket. |
| **Tickets - Count Tickets** | GET | Retorna uma contagem aproximada dos tickets da conta. Acima de 100.000, a contagem é atualizada a cada 24 horas; count[refreshed_at] indica quando a contagem foi atualizada pela última vez. Restrito a agentes. |
| **Tickets - Create Many Tickets** | POST | Cria até 100 tickets a partir de um array de objetos de ticket. Os tickets criados podem acionar suas regras de negócio, incluindo notificações por e-mail. Retorna um job_status e enfileira um job em segundo plano para executar o trabalho. |
| **Tickets - Bulk Delete Tickets** | DELETE | Exclui em lote os tickets indicados por uma lista de até 100 ids separados por vírgula. Retorna um job_status e enfileira um job em segundo plano; use Show Job Status para verificar a conclusão. |
| **Tickets - Bulk Mark Tickets as Spam** | PUT | Marca até 100 tickets como spam a partir de uma lista de ids separados por vírgula. Retorna um objeto job_status e enfileira um job em segundo plano; use Show Job Status para acompanhar a conclusão. Permitido para agentes. |
| **Tickets - Show Ticket by Messaging Conversation ID** | GET | Retorna o ticket ativo associado ao id de conversa do Sunshine Conversations informado. Um ticket é ativo enquanto estiver aberto e a sessão de mensageria em andamento. Permitido para agentes com a permissão view_private_content. |
| **Tickets - List Recent Tickets** | GET | Lista até cinco tickets que o agente que faz a requisição visualizou ou criou recentemente na interface de agente. Permitido para agentes. |
| **Tickets - Show Multiple Tickets** | GET | Retorna vários tickets a partir de uma lista de ids separados por vírgula, com no máximo 100 registros por chamada. Permitido para agentes. |
| **Tickets - Update Many Tickets** | PUT | Atualiza vários tickets de uma vez, aceitando um array de até 100 objetos de ticket ou uma lista de até 100 ids separados por vírgula. |
| **Tickets - Show Ticket** | GET | Retorna as propriedades de um ticket, sem a thread completa de comentários. O comentário inicial fica na propriedade description; para obter todos os comentários, use List Comments. Permitido para agentes. |
| **Tickets - Update Ticket** | PUT | Atualiza um ticket existente. |
| **Tickets - Delete Ticket** | DELETE | Exclui um ticket. Permitido para administradores e agentes com permissão de exclusão. O limite é de 400 tickets por minuto neste endpoint; para volumes maiores, use Bulk Delete Tickets. |
| **Tickets - List Audits for a Ticket** | GET | Lista as auditorias de um ticket específico, com paginação por cursor (recomendada) ou por offset e no máximo 100 registros por página. Auditorias de tickets arquivados não suportam paginação. Permitido para agentes. |
| **Tickets - Count Audits for a Ticket** | GET | Retorna a contagem aproximada de auditorias de um ticket. Acima de 100.000, o resultado vem de cache atualizado a cada 24 horas, e count[refreshed_at] indica quando a contagem foi atualizada. Permitido para agentes. |
| **Tickets - Show Audit** | GET | Retorna os dados de uma auditoria específica de um ticket. Permitido para agentes. |
| **Tickets - Change a Comment From Public To Private** | PUT | Altera de público para privado o comentário associado a uma auditoria do ticket. Permitido para agentes. |
| **Tickets - List Collaborators for a Ticket** | GET | Lista os colaboradores de um ticket específico. Permitido para agentes. |
| **Tickets - List Comments** | GET | Retorna os comentários adicionados ao ticket, com paginação por cursor (recomendada) ou por offset e no máximo 100 registros por página. Por padrão, os comentários são ordenados pela data de criação em ordem crescente. |
| **Tickets - Count Ticket Comments** | GET | Retorna a contagem aproximada de comentários do ticket. Acima de 100.000, o resultado vem de cache atualizado a cada 24 horas, e count[refreshed_at] indica quando a contagem foi atualizada. Permitido para agentes. |
| **Tickets - Redact Comment Attachment** | PUT | Remove permanentemente um anexo de um comentário do ticket, substituindo-o por um arquivo redacted.txt vazio. A remoção não pode ser desfeita e não é possível em tickets já fechados. |
| **Tickets - Make Comment Private** | PUT | Torna privado um comentário do ticket. Permitido para agentes. |
| **Tickets - Redact String in Comment** | PUT | Remove permanentemente palavras ou trechos de texto de um comentário do ticket. Informe o texto a ocultar na propriedade text; os caracteres são substituídos pelo símbolo ▇. A ação não pode ser desfeita. |
| **Tickets - List Conversation log for Ticket** | GET | Lista os eventos do log de conversa de um ticket específico, com paginação por cursor e no máximo 100 registros por página. Permitido para agentes. |
| **Tickets - List Email CCs for a Ticket** | GET | Retorna os usuários em cópia (CC) do ticket. Requer o recurso CCs e Followers habilitado no Zendesk Support; sem ele, use List Collaborators. Permitido para agentes. |
| **Tickets - List Followers for a Ticket** | GET | Retorna os usuários que seguem o ticket. Requer o recurso CCs e Followers habilitado no Zendesk Support. Permitido para agentes. |
| **Tickets - List Ticket Incidents** | GET | Lista os tickets de incidente vinculados a um ticket de problema, com paginação por cursor (recomendada) ou por offset. Permitido para agentes. |
| **Tickets - Show Ticket After Changes** | GET | Retorna o objeto completo do ticket como ele ficaria após a aplicação da macro, sem alterar o ticket de fato. Para obter apenas os campos que a macro mudaria, use Show Changes to Ticket. Permitido para agentes. |
| **Tickets - Mark Ticket as Spam and Suspend Requester** | PUT | Marca o ticket como spam e suspende o solicitante. Permitido para agentes. |
| **Tickets - Merge Tickets into Target Ticket** | POST | Mescla um ou mais tickets no ticket de destino informado, copiando os anexos dos tickets de origem. Retorna um objeto job_status e enfileira um job em segundo plano; use Show Job Status para acompanhar a conclusão. |
| **Tickets - Show Ticket Metrics By Ticket** | GET | Retorna as métricas de um ticket específico. Permitido para agentes. |
| **Tickets - Ticket Related Information** | GET | Retorna informações relacionadas ao ticket, como tópico associado, issues do Jira vinculadas, origens de follow-up, indicação de ticket arquivado e a contagem de incidentes relacionados. Permitido para agentes. |
| **Tickets - Create a Satisfaction Rating** | POST | Cria uma avaliação de satisfação (CSAT) para um ticket resolvido ou que foi resolvido e reaberto. Somente o usuário final solicitante do ticket pode avaliar, e o score aceita apenas os valores good e bad. |
| **Tickets - List Ticket Skips By Ticket** | GET | Retorna os skips de um ticket específico. Tickets arquivados não entram na resposta. Suporta paginação por cursor (recomendada) ou por offset, com no máximo 100 registros por página. |
| **Tickets - List Resource Tags** | GET | Lista as tags associadas ao ticket. Permitido para agentes. |
| **Tickets - Set Tags** | POST | Define as tags do ticket, substituindo as tags existentes pelas informadas. Permitido para agentes. |
| **Tickets - Add Tags** | PUT | Adiciona tags ao ticket. Para evitar perda de tags em atualizações simultâneas, envie as propriedades updated_stamp e safe_update no corpo da requisição; se os timestamps não coincidirem, a requisição retorna erro 409 Conflict. |
| **Tickets - Remove Tags** | DELETE | Remove tags do ticket. O endpoint aceita atualização segura (safe update) para evitar colisões entre atualizações simultâneas. Permitido para agentes. |
| **Tickets - Show Task List** | GET | Retorna a lista de tarefas anexada ao ticket informado. Se o ticket não tiver lista de tarefas, um array vazio é retornado. Permitido para agentes. |
| **Tickets - Create Task List** | POST | Adiciona uma lista de tarefas ao ticket informado. Permitido para agentes. |
| **Trigger Categories - List Ticket Trigger Categories** | GET | Retorna todas as categorias de gatilho de ticket da conta. Usa paginação por cursor. |
| **Trigger Categories - Create Ticket Trigger Category** | POST | Cria uma categoria de gatilho de ticket. |
| **Trigger Categories - Create Batch Job for Ticket Trigger Categories** | POST | Cria um job que executa uma operação em lote para as categorias de gatilho de ticket informadas. |
| **Trigger Categories - Show Ticket Trigger Category** | GET | Retorna a categoria de gatilho de ticket com o ID especificado. |
| **Trigger Categories - Update Ticket Trigger Category** | PATCH | Atualiza a categoria de gatilhos de tickets com o ID especificado. |
| **Trigger Categories - Delete Ticket Trigger Category** | DELETE | Exclui a categoria de gatilhos de tickets com o ID especificado. |
| **Triggers - List Ticket Triggers** | GET | Lista todos os gatilhos de tickets da conta atual, com paginação por cursor (recomendada) ou por offset, retornando no máximo 100 registros por página. Permitido para agentes. |
| **Triggers - Create Trigger** | POST | Cria um gatilho de tickets. Permitido para agentes. |
| **Triggers - List Active Ticket Triggers** | GET | Lista todos os gatilhos de tickets ativos, com paginação por cursor (recomendada) ou por offset, retornando no máximo 100 registros por página. Permitido para agentes. |
| **Triggers - List Ticket Trigger Action and Condition Definitions** | GET | Retorna as definições das ações que um gatilho de tickets pode executar e das condições sob as quais ele pode ser executado, incluindo título, tipo, valores possíveis e, nas condições, os operadores. |
| **Triggers - Bulk Delete Ticket Triggers** | DELETE | Exclui os gatilhos de tickets correspondentes à lista de IDs separados por vírgula informada. Permitido para agentes. |
| **Triggers - Reorder Ticket Triggers** | PUT | Altera a ordem de disparo dos gatilhos de tickets da conta, definida em um array trigger_ids; é preciso incluir todos os ids da conta e a conta não pode ter mais de uma categoria de gatilhos. |
| **Triggers - Search Ticket Triggers** | GET | Pesquisa gatilhos de tickets, com paginação apenas por offset; use o parâmetro filter para filtrar a busca por um ou mais atributos. Permitido para agentes. |
| **Triggers - Update Many Ticket Triggers** | PUT | Atualiza a posição ou o status ativo de vários gatilhos de tickets de uma vez; as demais propriedades são ignoradas e no máximo 100 gatilhos podem ser atualizados por requisição. |
| **Triggers - Show Ticket Trigger** | GET | Exibe o gatilho de tickets informado. O valor de Via Type é um número, e não um texto. Permitido para agentes. |
| **Triggers - Update Ticket Trigger** | PUT | Atualiza o gatilho de tickets informado. Atualizar uma condição ou ação substitui por completo os arrays de condições e de ações, portanto envie todas as suas condições e ações. |
| **Triggers - Delete Ticket Trigger** | DELETE | Exclui o gatilho de tickets informado. Permitido para agentes. |
| **Triggers - List Ticket Trigger Revisions** | GET | Lista as revisões associadas a um gatilho de tickets; o histórico de revisões está disponível apenas nos planos Enterprise. Usa paginação por cursor, com no máximo 1000 registros por requisição. |
| **Triggers - Show Ticket Trigger Revision** | GET | Busca uma revisão associada a um gatilho de tickets; o histórico de revisões de gatilhos está disponível apenas nos planos Enterprise. Permitido para agentes. |
| **Uploads - Upload Files** | POST | Envia um arquivo que pode ser anexado a um comentário de ticket, sem anexá-lo ao comentário. Exige o parâmetro filename e um Content-Type com o MIME type correto do arquivo enviado. Permitido para usuários finais. |
| **Uploads - Delete Upload** | DELETE | Exclui um upload já enviado, identificado pelo seu token. Permitido para usuários finais. |
| **User Fields - List User Fields** | GET | Retorna a lista de campos de usuário personalizados da conta, na ordem definida na configuração de campos de usuário do Zendesk Support. Retorna no máximo 100 registros por página. Permitido para agentes. |
| **User Fields - Create User Field** | POST | Cria um campo personalizado de usuário do tipo text (padrão quando nenhum "type" é informado), textarea, checkbox, date, integer, decimal, regexp, dropdown, lookup ou multiselect. Permitido para administradores. |
| **User Fields - Reorder User Field** | PUT | Reordena os campos personalizados de usuário. Permitido para administradores. |
| **User Fields - Show Many User Fields** | GET | Retorna múltiplos campos de usuário a partir de suas chaves. Permitido para agentes. |
| **User Fields - Show User Field** | GET | Retorna um campo personalizado de usuário específico. Permitido para agentes. |
| **User Fields - Update User Field** | PUT | Atualiza um campo personalizado de usuário. Em campos dropdown ou multiselect, envie todas as opções em `custom_field_options`: as omitidas são removidas, e a ordem do array define a ordem exibida. Permitido para administradores. |
| **User Fields - Delete User Field** | DELETE | Exclui um campo personalizado de usuário. Permitido para administradores. |
| **User Fields - List User Field Options** | GET | Retorna a lista de opções de um campo personalizado de usuário do tipo dropdown. Suporta paginação por cursor (recomendada) ou por offset, com no máximo 100 registros por página. Permitido para agentes. |
| **User Fields - Create or Update a User Field Option** | POST | Cria uma opção ou atualiza uma existente em um campo de usuário do tipo dropdown. Informe o `id` dentro de `custom_field_option` para atualizar; sem `id`, uma nova opção é criada. Permitido para administradores. |
| **User Fields - Show a User Field Option** | GET | Retorna uma opção específica de um campo personalizado de usuário. Permitido para agentes. |
| **User Fields - Delete User Field Option** | DELETE | Exclui uma opção de um campo personalizado de usuário. Permitido para administradores. |
| **Users - List Users** | GET | Lista os usuários da conta. Suporta paginação por cursor (recomendada) ou por offset, com no máximo 100 registros por página. Permitido para administradores, agentes e light agents. |
| **Users - Create User** | POST | Cria um usuário. |
| **Users - Autocomplete Users** | GET | Retorna os usuários cujo nome começa com o valor informado no parâmetro `name`. Retorna apenas usuários sem identidades externas. Permitido para agentes. |
| **Users - Autocomplete Users by Request Body** | POST | Retorna os usuários cujo nome começa com o valor da propriedade `name` enviada no corpo da requisição. Aceita os mesmos parâmetros do método GET, mas no corpo. Retorna apenas usuários sem identidades externas. |
| **Users - Count Users** | GET | Retorna uma contagem aproximada de usuários, com o campo `refreshed_at` indicando a última atualização. Acima de 100.000, o valor é atualizado a cada 24 horas e fica limitado a 100.000 até concluir a atualização. |
| **Users - Create Many Users** | POST | Aceita um array de até 100 usuários e enfileira um job em segundo plano, retornando um objeto `job_status`. A importação em massa não vem habilitada por padrão na conta; sem ela, o retorno é 403 Forbidden. |
| **Users - Create Or Update User** | POST | Cria o usuário caso não exista ou atualiza o usuário existente identificado por e-mail ou external ID. Sem o parâmetro de role, o novo usuário recebe end user; use `"skip_verify_email": true` para não enviar e-mail de verificação. |
| **Users - Create Or Update Many Users** | POST | Aceita até 100 usuários, criando cada um que não exista e atualizando os existentes, identificados por `email` ou `external_id`. Retorna um objeto `job_status` e enfileira um job em segundo plano. Requer importação em massa habilitada. |
| **Users - Bulk Delete Users** | DELETE | Exclui usuários em massa a partir de uma lista de até 100 ids separados por vírgula, informada no parâmetro `ids` ou `external_ids`. Retorna um objeto `job_status` e enfileira um job em segundo plano. Permitido para administradores. |
| **Users - Logout many users** | POST | Encerra as sessões de vários usuários a partir de uma lista de até 100 ids separados por vírgula. Permitido para administradores. |
| **Users - Show Self** | GET | Retorna as informações do usuário autenticado e um `authenticity_token`, que deve ser enviado no header HTTP `X-CSRF-Token` nas chamadas feitas por usuários finais a partir do help center. |
| **Users - Delete the Authenticated Session** | DELETE | Exclui a sessão atual. Na prática só funciona com autenticação por sessão, como em requisições feitas do lado do cliente por um app Zendesk; com OAuth ou basic não há sessão atual e o endpoint não tem efeito. |
| **Users - List Current User's Clients** | GET | Retorna os clientes OAuth pertencentes ao usuário atual. Suporta paginação por cursor (recomendada) ou por offset, com no máximo 100 registros por página. Permitido para administradores. |
| **Users - Show the Currently Authenticated Session** | GET | Retorna a sessão atualmente autenticada. Permitido para administradores, agentes e usuários finais. |
| **Users - Renew the current session** | GET | Renova a sessão atual. Permitido para administradores, agentes e usuários finais. |
| **Users - Show Current User Settings** | GET | Retorna as configurações do usuário autenticado, incluindo preferências de interface para onboarding, tooltips, atalhos de teclado, tema e outros feature toggles. Permitido para agentes. |
| **Users - Update Current User Settings** | PUT | Atualiza as configurações do usuário autenticado, agrupadas em Support, admin_center, shared_views_order e agent_home_pinned_views (máximo de 8 visões). Apenas as configurações enviadas são alteradas; as demais permanecem inalteradas. |
| **Users - Request User Create** | POST | Envia ao proprietário da conta um e-mail de lembrete para atualizar a assinatura e permitir a criação de mais agentes. Permitido para agentes. |
| **Users - Search Users** | GET | Retorna os usuários que atendem aos critérios de busca. Suporta apenas paginação por offset, com até 100 registros por página e no máximo 10.000 registros por consulta. Permitido para agentes. |
| **Users - Show Many Users** | GET | Retorna vários usuários a partir de uma lista de até 100 ids ou external ids separados por vírgula. Permitido para agentes. |
| **Users - Update Many Users** | PUT | Atualiza vários usuários. |
| **Users - Show User** | GET | Retorna um usuário específico. Permitido para agentes. |
| **Users - Update User** | PUT | Atualiza um usuário. |
| **Users - Delete User** | DELETE | Exclui o usuário e os registros associados da conta; usuários excluídos não podem ser recuperados. Para atender ao GDPR é necessário um passo adicional, com a exclusão permanente do usuário. |
| **Users - List Brand Agent Memberships By User** | GET | Retorna todas as associações de agente a marcas de um usuário específico. Suporta paginação por cursor (recomendada) ou por offset, com no máximo 100 registros por página. Permitido para administradores. |
| **Users - Show Brand Agent Membership By User** | GET | Retorna uma associação específica de agente a marca de um usuário. Permitido para administradores. |
| **Users - Show Compliance Deletion Statuses** | GET | Retorna o status de GDPR do usuário por área de compliance, normalmente um produto como "support/explore", podendo ser mais granular. Se o usuário não estiver na conta, a requisição retorna 404. Permitido para agentes, com restrições. |
| **Users - Get Full User Entitlements** | GET | Retorna os entitlements completos do usuário informado em todos os produtos Zendesk (Explore, Voice, Knowledge, Live Chat), com nome do papel e status. Um entitlement só é ativo se o usuário tem acesso e o produto está ativo na conta. |
| **User Group Memberships - List Group Memberships by User** | GET | Lista as associações a grupos de um usuário. Suporta paginação por cursor (recomendada) ou por offset, com no máximo 100 registros por página. Permitido para agentes. |
| **User Group Memberships - Create Group Membership for User** | POST | Atribui um agente a um determinado grupo. Permitido para administradores e para agentes em papel personalizado com permissão para gerenciar associações a grupos (apenas Enterprise). |
| **User Group Memberships - Show User's Group Membership** | GET | Retorna uma associação a grupo específica de um usuário. Permitido para agentes. |
| **User Group Memberships - Delete User's Group Membership** | DELETE | Remove imediatamente um usuário de um grupo e agenda um job para desatribuir todos os tickets em andamento associados àquela combinação de usuário e grupo. Permitido para administradores e agentes com permissão (apenas Enterprise). |
| **User Group Memberships - Set Membership as Default** | PUT | Define a associação de grupo informada como a padrão do usuário. Permitido para agentes. |
| **Users - List User Groups** | GET | Retorna a lista de grupos do usuário informado. Suporta paginação por cursor (recomendada) ou por offset, com no máximo 100 registros por página. Permitido para administradores e agentes. |
| **Users - Count User Groups** | GET | Retorna a contagem aproximada de grupos do usuário informado. Acima de 100.000, o valor é atualizado a cada 24 horas e `refreshed_at` indica a última atualização. Permitido para administradores e agentes. |
| **Users - List Identities** | GET | Retorna a lista de identidades do usuário informado. Usuários finais só listam identidades de e-mail e telefone. Suporta paginação por cursor (recomendada) ou offset, com até 100 registros por página. |
| **Users - Create Identity** | POST | Adiciona uma identidade ao perfil de um usuário. Tipos aceitos: email, twitter, facebook, google, agent_forwarding e phone_number. Use `skip_verify_email: true` para não enviar o e-mail de verificação. |
| **Users - Show Identity** | GET | Exibe a identidade com o id informado para um usuário. Usuários finais só podem visualizar identidades de e-mail ou telefone. Permitido para agentes e usuários finais verificados. |
| **Users - Update Identity** | PUT | Atualiza a identidade informada: marca como verificada, remove a verificação ou altera o campo `value`. O atributo `primary` não pode ser alterado aqui — use a operação Make Identity Primary. |
| **Users - Delete Identity** | DELETE | Exclui a identidade de um usuário. O telefone pode continuar visível no perfil — limpe o atributo `phone` do usuário. Excluir identidades do tipo `messaging` pode quebrar a funcionalidade de mensagens. |
| **Users - Make Identity Primary** | PUT | Define a identidade informada como primária. É uma operação de coleção, portanto recarregue a coleção completa em seguida. Usuários finais só podem tornar primária uma identidade de e-mail verificada. |
| **Users - Request User Verification** | PUT | Envia ao usuário um e-mail de verificação com um link para confirmar a propriedade do endereço de e-mail. Permitido para agentes. |
| **Users - Verify Identity** | PUT | Marca a identidade informada como verificada. Por segurança, não é possível usar esta operação na identidade de e-mail do proprietário da conta. Permitido para agentes. |
| **Users - Merge End Users** | PUT | Mescla o usuário final indicado no caminho no usuário final informado no corpo da requisição. O usuário do caminho deve ser solicitante de 10.000 tíquetes ou menos; agentes e administradores não podem ser mesclados. |
| **User Organization Memberships - List Organization Memberships by User** | GET | Retorna as associações de organização do usuário informado, ordenadas com a organização padrão primeiro e depois pelo nome. Suporta paginação por cursor ou offset, com até 100 registros por página. |
| **User Organization Memberships - Create Organization Membership for User** | POST | Atribui um usuário a uma organização. Retorna erro com status 422 se o usuário já estiver atribuído à organização. Permitido para administradores e para agentes ao vincular um usuário final. |
| **User Organization Memberships - Show Organization Membership by User** | GET | Exibe a associação de organização informada de um usuário. Permitido para agentes. |
| **User Organization Memberships - Delete Organization Membership for User** | DELETE | Remove imediatamente o usuário da organização e agenda um job que desatribui todos os tíquetes em andamento dessa combinação de usuário e organização, definindo `organization_id` como null. |
| **User Organization Memberships - Set Membership as Default** | PUT | Define a associação de organização padrão de um usuário. Permitido para administradores e para agentes quando o padrão é definido para um usuário final. |
| **Users - List User's Organization Subscriptions** | GET | Retorna a lista de assinaturas de organização de um usuário específico. Suporta paginação por cursor ou offset, com até 100 registros por página. Usuários finais veem apenas as assinaturas que criaram. |
| **Users - List User Organizations** | GET | Retorna a lista de organizações associadas ao usuário informado, com paginação por cursor ou offset e até 100 registros por página. Agentes com acesso restrito à própria organização recebem erro 403. |
| **Users - Count User's Organizations** | GET | Retorna a contagem aproximada de organizações de um usuário específico. Acima de 100.000, o valor é atualizado a cada 24 horas e `refreshed_at` indica quando a contagem foi atualizada pela última vez. |
| **Users - Unassign Organization** | DELETE | Remove imediatamente o usuário da organização e agenda um job que desatribui todos os tíquetes em andamento dessa combinação de usuário e organização, definindo `organization_id` como null. |
| **Users - Set Organization as Default** | PUT | Define a associação de organização padrão de um usuário. Permitido para agentes. |
| **Users - Set a User's Password** | POST | Define a senha de um usuário. Só funciona se a configuração estiver habilitada em Zendesk Support, em Settings > Security > Global; ela vem desativada e apenas o proprietário da conta pode alterá-la. |
| **Users - Change Your Password** | PUT | Altera a sua própria senha, exigindo a senha atual. Não é possível alterar a senha de outro usuário por aqui; um administrador pode definir uma nova senha para outro usuário com a operação Set a User's Password. |
| **Users - List password requirements** | GET | Lista os requisitos de senha aplicáveis ao usuário informado. Permitido para agentes e usuários finais. |
| **Users - Show User Related Information** | GET | Exibe as informações relacionadas ao usuário informado. |
| **Users - List User Requests** | GET | Lista as solicitações do usuário informado. Permitido para usuários finais. |
| **Users - List Sessions for User** | GET | Lista todas as sessões de um usuário específico. Suporta paginação por cursor (recomendada) ou por offset. Permitido para administradores, agentes e usuários finais. |
| **Users - Bulk Delete Sessions** | DELETE | Exclui todas as sessões de um usuário. Permitido para administradores, agentes e usuários finais. |
| **Users - Show Session** | GET | Exibe a sessão informada de um usuário. Permitido para administradores, agentes e usuários finais. |
| **Users - Delete Session** | DELETE | Exclui a sessão informada de um usuário. Permitido para administradores, agentes e usuários finais. |
| **Users - List Ticket Skips** | GET | Lista os skips de tíquetes do usuário informado; tíquetes arquivados não são retornados. Suporta paginação por cursor ou offset, com até 100 registros por página. |
| **Users - List User Tags** | GET | Lista as tags do usuário informado. Permitido para agentes. |
| **Users - Set User Tags** | POST | Define as tags do usuário informado, substituindo as existentes pelas enviadas. Permitido para agentes. |
| **Users - Add User Tags** | PUT | Adiciona tags ao usuário informado, mantendo as já existentes. Permitido para agentes. |
| **Users - Remove User Tags** | DELETE | Remove as tags informadas do usuário. Permitido para agentes. |
| **Users - List User Assigned Tickets** | GET | Lista os tíquetes atribuídos ao usuário informado. |
| **Users - Count User Assigned Tickets** | GET | Retorna a contagem aproximada de tíquetes atribuídos ao usuário informado. Acima de 100.000, o valor é atualizado a cada 24 horas e `count[refreshed_at]` indica a última atualização. |
| **Users - List User CCD Tickets** | GET | Lista os tíquetes em que o usuário informado está em cópia (CC). |
| **Users - Count User CCD Tickets** | GET | Retorna a contagem aproximada de tíquetes em que o usuário informado está em cópia (CC). Acima de 100.000, o valor é atualizado a cada 24 horas e `count[refreshed_at]` indica a última atualização. |
| **Users - List User Followed Tickets** | GET | Lista os tíquetes que o usuário informado está seguindo. |
| **Users - List User Requested Tickets** | GET | Lista os tíquetes solicitados pelo usuário informado. |
| **Views - List Views** | GET | Lista as visualizações compartilhadas e pessoais disponíveis para o usuário atual, com paginação por cursor (recomendada) ou por offset, retornando no máximo 100 registros por página. |
| **Views - Create View** | POST | Cria uma visualização a partir de um objeto view com os valores desejados; é obrigatório informar title e ao menos uma condição no array all sobre status, type, group_id, assignee_id ou requester_id. |
| **Views - List Active Views** | GET | Lista as visualizações compartilhadas e pessoais ativas disponíveis para o usuário atual, com paginação por offset e no máximo 100 registros por página. Permitido para agentes. |
| **Views - List Views - Compact** | GET | Retorna uma lista compacta das visualizações compartilhadas e pessoais disponíveis para o usuário atual; nunca retorna mais de 32 registros e não respeita a opção per_page. |
| **Views - Count Views** | GET | Retorna uma contagem aproximada das visualizações compartilhadas e pessoais disponíveis para o usuário atual; acima de 100.000, o resultado vem de um cache atualizado a cada 24 horas. |
| **Views - Count Tickets in Views** | GET | Retorna a contagem de tickets de cada visualização de uma lista, aceitando até 20 ids por requisição; contagens ainda em cálculo podem vir nulas. Limitado a 6 requisições por minuto. |
| **Views - List View Filter Definitions** | GET | Retorna as definições das condições e ações que uma visualização pode executar, incluindo condições, colunas de saída e campos que podem ser agrupados e ordenados. Permitido para agentes. |
| **Views - Bulk Delete Views** | DELETE | Exclui as visualizações correspondentes à lista de IDs informada. Permitido para agentes. |
| **Views - Preview Views** | POST | Pré-visualiza uma visualização montando as condições sob a propriedade view; a saída pode ser controlada pelas propriedades columns, group_by, group_order, sort_by e sort_order sob output. |
| **Views - Preview Ticket Count** | POST | Retorna a contagem de tickets de uma única pré-visualização. Permitido para agentes. |
| **Views - Search Views** | GET | Pesquisa visualizações, com paginação apenas por offset. Permitido para agentes. |
| **Views - List Views By ID** | GET | Lista as visualizações correspondentes aos IDs informados. Permitido para agentes. |
| **Views - Update Many Views** | PUT | Atualiza várias visualizações de uma vez por meio de um objeto views, no qual cada item informa o id e, opcionalmente, a nova posição e o status ativo. Permitido para agentes. |
| **Views - Show View** | GET | Exibe a visualização informada; além de IDs numéricos, o parâmetro de caminho view_id aceita os apelidos "incoming", "my" e "my_groups" para as visualizações internas correspondentes. |
| **Views - Update View** | PUT | Atualiza a visualização informada por meio de um objeto view cujas propriedades são todas opcionais; atualizar uma condição substitui todo o array, então envie todas as suas condições. |
| **Views - Delete View** | DELETE | Exclui a visualização informada. Permitido para agentes. |
| **Views - Count Tickets in View** | GET | Retorna a contagem de tickets de uma única visualização, limitada a 5 requisições por minuto por visualização e por agente; a contagem é mais fortemente armazenada em cache conforme a visualização cresce. |
| **Views - Execute View** | GET | Retorna os títulos das colunas e as linhas da visualização informada; limitado a 5 requisições por minuto por visualização e por agente, e o resultado pode ter sido calculado nos últimos 10 minutos. |
| **Views - Export View** | GET | Retorna o anexo csv da visualização informada quando possível, enfileirando um job para gerar o csv se necessário. Permitido para agentes. |
| **Views - List Tickets From a View** | GET | Lista os tickets de uma visualização, com paginação por cursor (recomendada) ou por offset. Permitido para agentes. |
| **Job Statuses - List Job Statuses** | GET | Lista os status dos jobs em segundo plano, ordenados primeiro pela data de conclusão e depois pela data de criação, em ordem decrescente. Permitido para agentes. |
| **Job Statuses - Show Many Job Statuses** | GET | Exibe vários status de job a partir de uma lista de ids separados por vírgula. Permitido para agentes. |
| **Job Statuses - Show Job Status** | GET | Exibe o status de um job em segundo plano, incluindo o progresso e os resultados por item. Permitido para agentes. |
| **Webhooks - List Webhooks** | GET | Lista os webhooks da conta, com filtros opcionais por parte do nome e por status. Permitido para administradores. |
| **Webhooks - Create or Clone Webhook** | POST | Cria um webhook a partir do corpo informado, ou clona um webhook existente quando clone_webhook_id é informado. Permitido para administradores. |
| **Webhooks - Test Webhook** | POST | Envia uma requisição de teste para um webhook. Informe webhook_id para testar um webhook existente, ou apenas o corpo para testar uma configuração antes de criá-la. Permitido para administradores. |
| **Webhooks - Show Webhook** | GET | Exibe as propriedades do webhook informado. Permitido para administradores. |
| **Webhooks - Update Webhook** | PUT | Substitui o webhook informado pelo objeto enviado no corpo. Todos os campos precisam ser informados, pois os omitidos são sobrescritos. Permitido para administradores. |
| **Webhooks - Patch Webhook** | PATCH | Atualiza apenas os campos informados do webhook, mantendo os demais como estão. Permitido para administradores. |
| **Webhooks - Delete Webhook** | DELETE | Exclui o webhook informado. Permitido para administradores. |
| **Webhooks - List Webhook Invocations** | GET | Lista as invocações do webhook informado, permitindo auditar o que foi enviado ao endpoint de destino. Permitido para administradores. |
| **Webhooks - List Webhook Invocation Attempts** | GET | Lista as tentativas de entrega das invocações do webhook informado, úteis para diagnosticar falhas e reenvios. Permitido para administradores. |
| **Webhooks - Show Webhook Signing Secret** | GET | Exibe o segredo de assinatura do webhook, usado para validar no destino que a requisição partiu do Zendesk. Permitido para administradores. |
| **Webhooks - Reset Webhook Signing Secret** | POST | Gera um novo segredo de assinatura para o webhook e invalida o anterior. Atualize o destino antes de usar, pois as requisições passam a ser assinadas com o novo segredo. Permitido para administradores. |

---

## Documentação oficial

* [https://developer.zendesk.com/api-reference/ticketing/introduction/](https://developer.zendesk.com/api-reference/ticketing/introduction/) — referência da Support API
* [https://developer.zendesk.com/api-reference/introduction/security-and-auth/](https://developer.zendesk.com/api-reference/introduction/security-and-auth/) — métodos de autenticação e a depreciação do API token
* [https://support.zendesk.com/hc/en-us/articles/4408845965210](https://support.zendesk.com/hc/en-us/articles/4408845965210) — fluxo OAuth, endpoints e escopos
* [https://support.zendesk.com/hc/en-us/articles/7386291855386](https://support.zendesk.com/hc/en-us/articles/7386291855386) — remoção do acesso por senha nas APIs
* [https://developer.zendesk.com/api-reference/introduction/pagination/](https://developer.zendesk.com/api-reference/introduction/pagination/) — paginação por cursor
* [https://developer.zendesk.com/documentation/ticketing/managing-tickets/using-the-incremental-export-api/](https://developer.zendesk.com/documentation/ticketing/managing-tickets/using-the-incremental-export-api/) — exportações incrementais
* [https://developer.zendesk.com/api-reference/introduction/rate-limits/](https://developer.zendesk.com/api-reference/introduction/rate-limits/) — limites de requisição
* [https://developer.zendesk.com/api-reference/webhooks/webhooks-api/webhooks/](https://developer.zendesk.com/api-reference/webhooks/webhooks-api/webhooks/) — Webhooks API (referência separada da Support API)
* [https://developer.zendesk.com/api-reference/ticketing/ticket-management/job_statuses/](https://developer.zendesk.com/api-reference/ticketing/ticket-management/job_statuses/) — Job Statuses e acompanhamento de operações em lote
