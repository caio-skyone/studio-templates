# Zoho Desk

## Contexto

A API do **Zoho Desk** é REST sobre HTTPS, com troca de dados em JSON, e expõe programaticamente o help desk da Zoho: tickets, contatos, contas, tarefas, chamadas, agentes e a estrutura organizacional que os sustenta.

**Conceitos fundamentais**

- **Organização (`orgId`)** — a unidade de topo do Zoho Desk. Um mesmo usuário pode pertencer a várias organizações, e **quase toda chamada da API exige o identificador da organização**. Neste conector ele é o parâmetro `org_id`, enviado como cabeçalho `orgId`.
- **Departamento** — a divisão interna da organização. Tickets, agentes, equipes e produtos pertencem a departamentos, e boa parte das listagens aceita `departmentId` como filtro.
- **Ticket** — o registro central do help desk. Carrega threads (as mensagens da conversa), comentários internos, anexos, tarefas, chamadas, eventos, aprovações, tags, seguidores, registros de tempo e histórico de resolução — cada um com seus próprios endpoints.
- **Thread e comentário** — a thread é a comunicação com o cliente (e-mail, formulário, chat); o comentário é a nota interna entre agentes. São coisas distintas, com endpoints distintos.
- **Contato e conta** — o contato é a pessoa que abre o ticket; a conta é a empresa a que ele pertence. Um contato pode estar associado a várias contas.
- **Agente, equipe e perfil** — o agente é quem atende. Equipes agrupam agentes para atribuição; perfis e papéis definem permissões.
- **Blueprint** — o fluxo de trabalho guiado que um ticket percorre, com transições que exigem campos e aprovações.
- **Registro de tempo (time entry)** — o apontamento de horas sobre um ticket, tarefa ou chamada, usado para faturamento e SLA.
- **Datacenter** — a conta Zoho vive em um datacenter específico (`.com`, `.eu`, `.in`, `.com.au`, `.jp`, `.ca`, `.sa`), e o host da API muda junto com ele.

**Escopo deste conector**

Este módulo cobre o **fluxo operacional de suporte**: tickets e tudo o que pende deles, contatos, contas, tarefas, agentes, departamentos, produtos, chamadas, eventos, usuários finais, organizações, contratos, equipes, grupos, modelos de e-mail e de ticket, além de utilitários transversais — busca, visualizações, upload de arquivos e o mecanismo de seguidores.

Ficam **fora** do escopo, por decisão de projeto:

- **Comunidade** (`communityTopics`, `communityUsers`, `communityCategory`, moderação) — 82 operações que formam um produto à parte dentro do Desk.
- **Base de conhecimento** (`articles`, `kbRootCategories`, `kbSections`, traduções e feedback de artigo) — 53 operações.
- **Layouts, regras de layout, campos organizacionais, validação, blueprints de configuração e demais metadados de administração** — pertencem à configuração do portal, não ao atendimento, e exigiriam escopos OAuth bem mais permissivos.
- **Deduplicação de contas e contatos** — 9 operações de merge e detecção de duplicatas, deixadas de fora do primeiro recorte.

---

## Autenticação

**Tipo:** OAuth 2.0

Toda API da Zoho autentica pelo **Zoho Accounts**, com o cabeçalho `Authorization: Zoho-oauthtoken <token>` — montado pela conta conectada, não por parâmetro de operação.

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://desk.zoho.<>seu-datacenter</>` |
| Porta | 443 |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Access Token | {{access_token}} |
| Refresh Token | {{refresh_token}} |
| Endpoint de troca de token | `https://accounts.zoho.com/oauth/v2/token` |

> **O datacenter faz parte do Host.** Substitua `<>seu-datacenter</>` pelo TLD da sua conta: `com`, `eu`, `in`, `com.au`, `jp`, `ca` ou `sa`. Uma conta do datacenter europeu não responde em `desk.zoho.com`. O endpoint de troca de token acompanha o mesmo datacenter — use `https://accounts.zoho.eu/oauth/v2/token` para o DC europeu, e assim por diante.

### Obtendo uma URL de redirect

No Skyone Studio, acesse **API Gateway**, crie um Gateway e uma rota **sem autenticação**. Essa URL será o `redirect_uri` registrado na Zoho.

### Obtendo as credenciais

1. Acesse o [Zoho API Console](https://api-console.zoho.com/) e clique em **Add client**, do tipo **Server-based Application**.
2. Informe um nome identificável, uma homepage URL qualquer que seja válida e, em **Authorized Redirect URIs**, a URL gerada no passo anterior.
3. Na aba **Client Secret** do client criado, anote o **Client ID** e o **Client Secret**.

### Obtendo os tokens

1. Crie no Studio um fluxo com gatilho de **API Gateway** apontando para a rota criada, com um parâmetro de query chamado `code`.
2. Acesse a URL de autorização da Zoho no navegador:

```
https://accounts.zoho.com/oauth/v2/auth?scope={escopos}&client_id={client_id}&response_type=code&access_type=offline&redirect_uri={redirect_uri}
```

3. Troque o `code` recebido pelos tokens no endpoint de troca de token e preencha **Access Token** e **Refresh Token** na conta conectada.

> `access_type=offline` é obrigatório para receber o `refresh_token`. Se ele não vier depois de autenticações sucessivas, acrescente `prompt=consent` à URL de autorização.

### Obtendo o `orgId`

No Zoho Desk, acesse **Setup → Developer Space → API**. O identificador da organização aparece ali. Ele é obrigatório em **todas as 339 operações** deste conector.

### Escopos OAuth necessários

Os escopos vão no parâmetro `scope` da URL de autorização, separados por vírgula. As 339 operações deste módulo exigem, somadas, **49 escopos distintos** — o conjunto abaixo é a união exata:

| Família | Escopos | Cobre |
| ------- | ------- | ----- |
| `Desk.tickets` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | tickets, threads, comentários, anexos, aprovações, resolução, blueprint, transições, seguidores e tags |
| `Desk.contacts` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | contatos, contas, produtos associados, convites de usuário final e contratos |
| `Desk.tasks` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | tarefas e seus comentários, anexos e registros de tempo |
| `Desk.calls` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | chamadas e seus comentários |
| `Desk.events` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | eventos e seus comentários |
| `Desk.activities` | `.tasks.*`, `.calls.*`, `.events.*` (READ/CREATE/UPDATE/DELETE) | as mesmas atividades acessadas pela rota de atividades |
| `Desk.products` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | produtos e suas associações com contas e contatos |
| `Desk.basic` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | agentes, equipes, grupos, usuários finais, organizações e disponibilidade de agente |
| `Desk.settings` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | departamentos, modelos de e-mail e de ticket, visualizações, logotipos e favicon |
| `Desk.search` | `.READ` | busca por módulo e entre módulos |
| `Desk.articles` | `.READ`, `.CREATE`, `.UPDATE` | sugestão de artigo no ticket e registro de uso de artigo |
| `Desk.custommodule` | `.READ` | leitura de módulos customizados pelo mecanismo de seguidores |

> **Conceda só o que for usar.** Quanto mais estreito o conjunto de escopos, menos permissiva precisa ser a aplicação OAuth. Se o seu fluxo só lê e atualiza tickets, `Desk.tickets.READ,Desk.tickets.UPDATE,Desk.basic.READ` já resolve — não é preciso autorizar as 49.

---

## Convenções deste conector

- **`orgId` é um cabeçalho obrigatório, não um parâmetro de consulta.** Toda operação recebe `org_id` e o envia como cabeçalho `orgId`. A especificação OpenAPI oficial da Zoho declara esse campo como *query param* em 692 dos seus endpoints, mas a API real só o aceita como cabeçalho — os exemplos da própria documentação usam `-H "orgId:2389290"`. O conector segue a API, não a especificação.
- **Corpo das requisições.** O parâmetro `body` é um texto JSON único, preenchido com um exemplo derivado do schema da operação. Informe o objeto completo na sintaxe da própria API do Zoho Desk.
- **Uploads são multipart.** As nove operações de envio de arquivo usam `multipart/form-data` no formato granular `campo:<>parâmetro</>:mime:tipo:arquivo`. Para enviar conteúdo binário, informe o arquivo em **base64** e marque **"Forçar bufferização da requisição"** na operação — sem isso o corpo é truncado.
- **O caminho carrega `/api/v1`.** O Host da conta conectada é apenas `https://desk.zoho.<>seu-datacenter</>`; o prefixo de versão faz parte do caminho de cada operação.
- **Uma operação por forma de caminho.** Onde a API oferece a versão em lote e a individual sob o mesmo nome — convite de usuário final e busca — as duas existem como operações separadas, com descrições distintas.
- **Paginação.** As listagens aceitam `from` (deslocamento) e `limit`. Não há cursor: para percorrer tudo, incremente `from`. Os limites **não são uniformes** — a especificação declara máximo de `limit` variando entre 50, 99, 100 e 200 conforme o recurso, e o índice inicial de `from` ora é 0, ora 1. Confira o teto do recurso que você está usando antes de fixar o tamanho de página.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Accounts - List accounts** | GET | Lista um número específico de contas, com base no limite especificado. |
| **Accounts - Create Account** | POST | Cria uma conta no seu portal de help desk. |
| **Accounts - Delete Accounts** | POST | Move as contas especificadas para a Lixeira. |
| **Accounts - Search Accounts** | GET | Busca contas no help desk. Forneça múltiplos valores separados por vírgulas para buscar usando qualquer um deles. |
| **Accounts - Update many accounts** | POST | Atualiza múltiplas contas simultaneamente. |
| **Accounts - Get Account** | GET | Obtém uma conta do seu portal de help desk. |
| **Accounts - Update Account** | PATCH | Atualiza os detalhes de uma conta existente. |
| **Accounts - Add account followers** | POST | Adiciona um ou mais usuários à lista de seguidores de uma conta. |
| **Accounts - Associate products with an account** | POST | Associa produtos com uma conta. Máximo de 10 produtos por requisição. |
| **Accounts - List Account attachments** | GET | Lista os arquivos anexados a uma conta. |
| **Accounts - Create Account attachment** | POST | Anexa um arquivo a uma conta. |
| **Accounts - Delete Account attachment** | DELETE | Remove um anexo de uma conta. |
| **Accounts - List all account comments** | GET | Lista um número específico de comentários registrados em uma conta, com base no limite especificado. |
| **Accounts - Create an account comment** | POST | Adiciona um comentário a uma conta. |
| **Accounts - Get an account comment** | GET | Obtém um comentário da conta no portal. |
| **Accounts - Update an account comment** | PUT | Atualiza um comentário existente da conta. |
| **Accounts - Delete an account comment** | DELETE | Remove um comentário existente da conta. |
| **Accounts - List Associated contacts** | GET | Lista os contatos associados a uma conta. |
| **Accounts - Get contract** | GET | Obtém os contratos de uma conta. |
| **Accounts - Get account followers** | GET | Obtém a lista de usuários que seguem uma conta. |
| **Accounts - Get account history** | GET | Obtém o histórico de tickets de uma conta. |
| **Accounts - Merge Accounts** | POST | Mescla duas ou mais contas. |
| **Accounts - List products by account** | GET | Lista os produtos associados a uma conta específica. |
| **Accounts - Remove account followers** | POST | Remove um ou mais usuários da lista de seguidores de uma conta. |
| **Accounts - List account SLAs** | GET | Lista um número específico de SLAs associados a uma conta, com base no limite definido. |
| **Accounts - Associate or dissociate SLA from account** | POST | Associa ou desassocia um SLA de uma conta. |
| **Accounts - Get account statistics** | GET | Obtém as estatísticas gerais de uma conta. |
| **Accounts - List tickets by account** | GET | Lista os tickets recebidos de uma conta específica. |
| **Accounts - List Account Time Entries** | GET | Lista os registros de tempo para tickets ou tarefas relacionados a uma conta. |
| **Accounts - Get summation of Account Time Entries** | GET | Obtém a soma dos registros de tempo para uma conta do seu help desk. |
| **Activities - Delete spam activities** | POST | Remove todas as atividades de spam. |
| **Activities - Search Activities** | GET | Busca atividades no portal de help desk. Forneça valores separados por vírgulas para buscar usando qualquer um deles. |
| **Agentavailability - Get Current Availability** | GET | Lista a disponibilidade atual dos agentes em um departamento específico. |
| **Agentavailabilityconfig - Get Agent Availability Configuration** | GET | Obtém a configuração de disponibilidade de agentes no seu portal de help desk. |
| **Agentavailabilityconfig - Update Agent Availability Configuration** | POST | Atualiza a configuração de disponibilidade de agentes no seu portal de help desk. |
| **Agents - List agents** | GET | Lista um número específico de agentes, com base no limite especificado. |
| **Agents - Add agent** | POST | Adiciona um agente ao seu help desk. Requer emailId, lastName, departmentIds e rolePermissionType. |
| **Agents - Activate agents** | POST | Ativa agentes no seu help desk. |
| **Agents - Get agents count** | GET | Lista a contagem de agentes por status, confirmados e incluindo light. |
| **Agents - Delete unconfirmed agents** | POST | Remove agentes não confirmados do seu help desk. |
| **Agents - Reinvite unconfirmed agents** | POST | Envia e-mails de reinvitação para agentes não confirmados. |
| **Agents - Get agent** | GET | Obtém os detalhes de um agente no seu help desk. |
| **Agents - Update agent** | PATCH | Atualiza os detalhes de um agente. |
| **Agents - Deactivate agent** | POST | Desativa um agente no seu help desk. |
| **Agents - Map Skills in a Department with an Agent** | POST | Modifica as habilidades mapeadas para um agente em um departamento. |
| **Agents - Get agent photo** | GET | Obtém a foto de perfil para o ID do agente fornecido. |
| **Agents - Schedule reassignment for deactivated or deleted agents** | POST | Agenda a reatribuição de tickets, tarefas e automações de um agente deletado/desativado para outro agente. |
| **Agents - Get signatures of agent** | GET | Obtém as diferentes assinaturas configuradas por um agente. |
| **Agents - Update signatures of agent** | PATCH | Atualiza as assinaturas existentes de um agente. |
| **Agents - Get Skills of an Agent** | GET | Retorna as habilidades mapeadas com um agente por departamento. |
| **Agents - List associated teams of agent** | GET | Obtém os detalhes de todos os times aos quais um agente pertence. |
| **Agents - List Agent Time Entries** | GET | Lista os registros de tempo associados a um agente. |
| **Agents - Get an Agent Time Entry** | GET | Obtém um registro de tempo relacionado a um agente. |
| **Agents - Get summation of Agent Time Entries** | GET | Obtém a soma dos registros de tempo associados a um agente. |
| **Agents - Update customized signatures of agent** | POST | Atualiza as assinaturas personalizadas de um agente. |
| **Agents - Auto Display an Entity** | POST | Instrui o navegador de um agente a abrir e exibir uma entidade automaticamente, sem ação manual. |
| **Agentsbyids - Get agent details by agentId** | GET | Obtém os detalhes dos agentes através dos IDs passados na requisição. |
| **Agentsticketscount - List all agentsTicketsCount** | GET | Retorna o número de tickets atribuídos a múltiplos agentes. |
| **Associatedtickets - List all associated tickets** | GET | Lista um número específico de tickets associados a você do seu help desk, conforme o limite especificado. |
| **Calls - List calls** | GET | Obtém um número específico de chamadas, conforme o limite especificado. |
| **Calls - Create call** | POST | Adiciona uma entrada de chamada ao seu portal de help desk. |
| **Calls - Delete spam calls** | POST | Deleta as chamadas de spam fornecidas. |
| **Calls - Empty spam calls** | POST | Deleta todas as chamadas de spam. |
| **Calls - Delete calls** | POST | Move as entradas de chamada para a Lixeira do seu portal de help desk. |
| **Calls - Search Calls** | GET | Pesquisa chamadas em seu portal de help desk. Você pode fornecer múltiplos valores separados por vírgulas. |
| **Calls - Update many calls** | POST | Atualiza múltiplas chamadas de uma vez. |
| **Calls - Get call** | GET | Obtém os detalhes de uma chamada. |
| **Calls - Update call** | PATCH | Atualiza os detalhes de uma chamada. |
| **Calls - Clear live call mapping from an activity** | POST | Limpa o mapeamento de chamada ao vivo de uma atividade. |
| **Calls - Create a call comment** | POST | Adiciona um comentário a uma chamada. |
| **Calls - Get a call comment** | GET | Obtém um comentário de chamada do portal. |
| **Calls - Update a call comment** | PUT | Atualiza um comentário de chamada existente. |
| **Calls - List all call comments** | GET | Lista um número específico de comentários registrados em uma chamada, conforme o limite especificado. |
| **Closetickets - Closed many tickets** | POST | Fecha múltiplos tickets de uma vez. |
| **Contacts - List Contacts** | GET | Lista um número específico de contatos, conforme o limite especificado. |
| **Contacts - Create Contact** | POST | Cria um contato em seu portal de help desk. |
| **Contacts - List Contacts By Ids** | GET | Lista detalhes de contatos específicos, conforme os IDs fornecidos na requisição. |
| **Contacts - Get contacts count** | GET | Exibe a contagem do número de contatos em uma visualização personalizada. |
| **Contacts - Delete spam contacts** | POST | Deleta os contatos de spam fornecidos. |
| **Contacts - Invite multiple contacts to help center** | POST | Convida múltiplos contatos como usuários finais para seu centro de ajuda. |
| **Contacts - Mark contact as spam** | POST | Marca contatos como spam. |
| **Contacts - Delete Contacts** | POST | Move os contatos especificados para a Lixeira. |
| **Contacts - Search Contacts** | GET | Pesquisa contatos em seu help desk. Você pode fornecer múltiplos valores separados por vírgulas. |
| **Contacts - Update many contacts** | POST | Atualiza múltiplos contatos de uma vez. |
| **Contacts - Get Contact** | GET | Obtém um único contato do seu portal de help desk. |
| **Contacts - Update Contact** | PATCH | Atualiza detalhes de um contato existente. |
| **Contacts - List accounts of contact** | GET | Lista as contas associadas a um contato específico. |
| **Contacts - Dissociate account from contact** | PATCH | Desassocia uma conta específica de um contato. |
| **Contacts - Add contact followers** | POST | Adiciona um ou mais usuários à lista de seguidores de um contato. |
| **Contacts - Approve contact for help center** | POST | Aprova um contato específico como usuário final para seu centro de ajuda. |
| **Contacts - Associate accounts with contact** | POST | Associa múltiplas contas a um contato específico. |
| **Contacts - Associate products with a contact** | POST | Associa produtos a um contato. Máximo de 10 produtos por requisição. |
| **Contacts - List Contact Attachments** | GET | Lista os arquivos anexados a um contato. |
| **Contacts - Create Contact Attachment** | POST | Anexa um arquivo a um contato. |
| **Contacts - Delete Contact attachment** | DELETE | Remove um anexo de um contato. |
| **Contacts - List all contact comments** | GET | Lista um número específico de comentários registrados em um contato, conforme o limite especificado. |
| **Contacts - Create a contact comment** | POST | Adiciona um comentário a um contato. |
| **Contacts - Get a contact comment** | GET | Obtém um comentário de contato do portal. |
| **Contacts - Update a contact comment** | PUT | Atualiza um comentário de contato existente. |
| **Contacts - Delete a contact comment** | DELETE | Deleta um comentário de contato existente. |
| **Contacts - Dissociate accounts from contact** | POST | Desassocia múltiplas contas de um contato específico. |
| **Contacts - Get contact followers** | GET | Obtém a lista de usuários que seguem um contato. |
| **Contacts - Get status of contact in help centers** | GET | Obtém o status de ativação de um contato em todos os centros de ajuda dos quais faz parte. |
| **Contacts - Get contact history** | GET | Obtém o histórico de tickets de um contato. |
| **Contacts - Invite contact to help center** | POST | Convida um contato específico como usuário final para seu centro de ajuda. |
| **Contacts - Merge Contacts** | POST | Mescla dois ou mais contatos. Registros de usuários do portal não podem ser mesclados. |
| **Contacts - Delete contact photo** | DELETE | Deleta a foto de exibição de um contato. |
| **Contacts - List products by contact** | GET | Lista produtos associados a um contato específico. |
| **Contacts - Get Contact Profiles** | GET | Obtém a lista de perfis de um contato de vários canais. |
| **Contacts - Reject contact for help center** | POST | Rejeita um contato específico de ser adicionado como usuário final para seu centro de ajuda. |
| **Contacts - Remove contact followers** | POST | Remove um ou mais usuários da lista de seguidores de um contato. |
| **Contacts - Get contact statistics** | GET | Obtém as estatísticas gerais de um contato. |
| **Contacts - List tickets by contact** | GET | Lista tickets recebidos de um contato específico. |
| **Contacts - List Contact Time Entries** | GET | Lista entradas de tempo registradas para um ticket ou tarefa de um contato. |
| **Contacts - Get summation of Contact Time Entries** | GET | Esta API busca a soma de lançamentos de tempo de um contato do seu help desk. |
| **Contracts - List all contracts** | GET | Obtém uma lista de contratos. |
| **Contracts - Create a contract** | POST | Esta API cria um contrato no seu help desk. |
| **Contracts - Get contract count by custom view and department** | GET | Retorna a contagem de contratos com base na exibição personalizada e departamento especificados. Se ownerId for especificado, retorna a contagem de contratos que pertencem ao proprietário no departamento especificado. |
| **Contracts - Update many contracts** | POST | Esta API atualiza vários contratos de uma vez. |
| **Contracts - Get a contract** | GET | Esta API busca um único contrato do seu help desk. |
| **Contracts - Update a contract** | PATCH | Esta API atualiza detalhes de um contato existente. |
| **Deletedagents - Anonymize deleted agent** | POST | Esta API remove os detalhes de identificação de um agente excluído. |
| **Departments - List departments** | GET | Esta API lista um número específico de departamentos, com base no limite especificado. |
| **Departments - Add department** | POST | Esta API adiciona um departamento ao seu portal help desk. |
| **Departments - Check for duplicate departments** | GET | Esta API verifica se vários departamentos têm o mesmo nome. |
| **Departments - Get department count** | GET | Esta API retorna o número de departamentos configurados no seu portal help desk. |
| **Departments - Get department** | GET | Esta API busca os detalhes de um departamento do seu help desk. |
| **Departments - Update department** | PATCH | Esta API atualiza os detalhes de um departamento existente. |
| **Departments - List agents in department** | GET | Esta API lista os agentes em um departamento. |
| **Departments - Associate agents to department** | POST | Esta API associa agentes a um departamento. |
| **Departments - Disable department** | POST | Esta API desabilita um departamento no seu portal help desk. |
| **Departments - Dissociate agents from department** | POST | Esta API desassocia agentes de um departamento. |
| **Departments - Enable department** | POST | Esta API habilita um departamento no seu portal help desk. |
| **Departments - Get department logo** | GET | Esta API busca o logotipo definido para um departamento. |
| **Departments - Upload department logo** | POST | Esta API atualiza o logotipo definido para um departamento. |
| **Departments - Delete department logo** | DELETE | Esta API remove o logotipo definido para um departamento. |
| **Departments - List teams in department** | GET | Esta API busca detalhes de todas as equipes em um departamento específico. |
| **Events - List events** | GET | Esta API lista um número específico de eventos, com base no limite especificado. |
| **Events - Create event** | POST | Esta API adiciona uma entrada de evento ao seu portal help desk. |
| **Events - Delete spam events** | POST | Esta API deleta os eventos de spam fornecidos. |
| **Events - Empty spam events** | POST | Esta API deleta todos os eventos de spam. |
| **Events - Delete events** | POST | Esta API move entradas de eventos para a Lixeira do seu portal help desk. |
| **Events - Search Events** | GET | Pesquisa eventos no seu portal help desk. Você pode fornecer múltiplos valores separados por vírgulas e a pesquisa será realizada usando qualquer um dos valores fornecidos. |
| **Events - Update many events** | POST | Esta API atualiza vários eventos de uma vez. |
| **Events - Get event** | GET | Esta API busca os detalhes de um evento. |
| **Events - Update an event** | PATCH | Esta API atualiza os detalhes de um evento. |
| **Events - List all event comments** | GET | Esta API lista um número específico de comentários registrados em um evento, com base no limite especificado. |
| **Events - Create a event comment** | POST | Esta API adiciona um comentário a um evento. |
| **Events - Get a event comment** | GET | Esta API busca um comentário de evento no portal. |
| **Events - Update a event comment** | PUT | Esta API atualiza um comentário de evento existente. |
| **Groups - List helpcenter groups** | GET | Esta API lista um número específico de grupos, com base no limite definido. |
| **Groups - Create user groups** | POST | Esta API cria um grupo de usuários no seu centro de ajuda. |
| **Groups - Get details of group** | GET | Esta API busca os detalhes de um grupo de usuários específico. |
| **Groups - Update group** | PATCH | Esta API ajuda a atualizar os detalhes de um grupo de usuários. |
| **Groups - Delete helpcenter user group** | DELETE | Esta API deleta um grupo de usuários do seu centro de ajuda. |
| **Groups - List users in a group** | GET | Esta API lista um número específico de usuários em um grupo, com base no limite definido. |
| **Groups - Add users to group** | POST | Esta API adiciona usuários a um grupo específico. |
| **Groups - Remove users from group** | POST | Esta API remove usuários específicos de um grupo. |
| **Lastaccessedview - Get Last Accessed View** | GET | Esta API busca a exibição acessada por último pelo usuário no módulo e departamento especificados na solicitação. |
| **Lastaccessedview - Update Last Accessed View** | PUT | Esta API atualiza a exibição acessada por último pelo usuário no módulo e departamento especificados na solicitação. |
| **Lightagentprofile - Get light agent profile** | GET | Esta API busca as diferentes permissões configuradas para o perfil de agente leve. |
| **Offlineagents - Get Offline Agents** | GET | Esta API lista os agentes que estão atualmente offline em um departamento específico. |
| **Onlineagents - Get Online Agents** | GET | Esta API lista os agentes que estão atualmente online em um departamento específico. |
| **Organizations - Get Organizations** | GET | Esta API lista todas as organizações às quais o usuário atual pertence. |
| **Organizations - Update Default Organizaion** | POST | Esta API atualiza a organização padrão para o usuário atual no Zoho Desk. |
| **Organizations - Get Organization** | GET | Esta API busca os detalhes de uma organização do seu help desk. |
| **Organizations - Update Organization** | PATCH | Esta API atualiza os detalhes de uma organização. |
| **Organizations - Get Organization Favicon** | GET | Esta API busca o favicon definido para uma organização/portal no seu help desk. |
| **Organizations - Update Organization Favicon** | POST | Esta API atualiza o favicon definido para uma organização/portal no seu help desk. |
| **Organizations - Delete Organization Favicon** | DELETE | Esta API atualiza o favicon definido para uma organização/portal no seu help desk. |
| **Organizations - Get Organization Logo** | GET | Esta API busca o logotipo definido para uma organização/portal no seu help desk. |
| **Organizations - Update Organization Logo** | POST | Atualiza o logotipo da organização/portal do help desk. Exige OAuthToken com o escopo Desk.settings.UPDATE,profile.orglogo.UPDATE ou Desk.basic.UPDATE,profile.orglogo.UPDATE. |
| **Organizations - Delete Organization Logo** | DELETE | Esta API exclui o logotipo definido para uma organização/portal no seu help desk. |
| **Products - List Products** | GET | Esta API lista um número específico de produtos do seu portal de help desk, com base no limite definido. Nota: a chave departmentIds em breve será descontinuada. |
| **Products - Create product** | POST | Esta API adiciona um produto ao seu helpdesk. |
| **Products - Move Products to trash** | POST | Esta API move produtos para a Lixeira do seu portal de help desk. |
| **Products - Search Products** | GET | Esta API busca produtos no seu portal de help desk. Você pode fornecer múltiplos valores separados por vírgulas para a busca. |
| **Products - Search for duplicate records** | GET | Esta API busca registros duplicados de um produto. |
| **Products - Get product** | GET | Esta API obtém um único produto do seu helpdesk. |
| **Products - Update product** | PATCH | Esta API atualiza detalhes de um produto no seu portal de help desk. |
| **Products - List accounts associated with product** | GET | Esta API lista as contas associadas a um produto. |
| **Products - Associate accounts with a product** | POST | Esta API associa contas a um produto. Um máximo de 10 contas pode ser associado por solicitação de API. |
| **Products - Associate contacts with a product** | POST | Esta API associa contatos a um produto. Um máximo de 10 contatos pode ser associado por solicitação de API. |
| **Products - List all product attachments** | GET | Esta API lista todos os anexos em um produto. |
| **Products - Create an product attachment** | POST | Esta API anexa um arquivo a um produto. |
| **Products - Delete an product attachment** | DELETE | Esta API exclui um anexo de um produto. |
| **Products - List contacts associated with product** | GET | Esta API lista os contatos associados a um produto. |
| **Products - List tickets by products** | GET | Esta API lista tickets recebidos de produtos específicos. |
| **Recenttickettags - List recent tags** | GET | Esta API lista as cinco tags mais recentes associadas a tickets. |
| **Recenttickettags - Update recent tags** | POST | Esta API adiciona uma tag à lista de tags visualizadas recentemente. tag_id é um parâmetro obrigatório. |
| **Search - Search across modules** | GET | Esta API retorna informações de todos os módulos ou de um módulo específico, com base no parâmetro de query do módulo. |
| **Starredviews - List Starred Views** | GET | Esta API lista as visualizações destacadas em um módulo. O número de recursos é exibido apenas para o módulo de Tickets. |
| **Starredviews - Update Starred View order - Reorder** | PUT | Esta API ajuda a reordenar as visualizações destacadas em um módulo. |
| **Starredviews - Remove Starred View** | POST | Esta API remove a marcação de destaque de uma visualização, desabilitando o acesso rápido. |
| **Tasks - List tasks** | GET | Esta API obtém um número específico de tarefas, com base no limite especificado. |
| **Tasks - Create task** | POST | Esta API cria uma tarefa no seu portal de help desk. |
| **Tasks - List all tasks count** | GET | Esta API retorna o número de tarefas no seu help desk. |
| **Tasks - Delete spam tasks** | POST | Esta API exclui as tarefas de spam fornecidas. |
| **Tasks - Empty spam tasks** | POST | Esta API exclui todas as tarefas de spam. |
| **Tasks - Delete tasks** | POST | Esta API move entradas de tarefas para a Lixeira do seu portal de help desk. |
| **Tasks - Search Tasks** | GET | Esta API busca tarefas no seu help desk. Você pode fornecer múltiplos valores separados por vírgulas para a busca. |
| **Tasks - Update many tasks** | POST | Esta API atualiza múltiplas tarefas simultaneamente. |
| **Tasks - Get Task Timer** | GET | Esta API obtém o tempo decorrido no cronômetro da tarefa, juntamente com o estado atual. |
| **Tasks - List task timers** | GET | Esta API obtém os detalhes dos cronômetros atualmente ativos em uma tarefa. |
| **Tasks - List all task comments** | GET | Esta API lista um número específico de comentários registrados em uma tarefa, com base no limite especificado. |
| **Tasks - Create a task comment** | POST | Esta API adiciona um comentário a uma tarefa. |
| **Tasks - Get a task comment** | GET | Esta API obtém um comentário de tarefa do portal. |
| **Tasks - Update a task comment** | PUT | Esta API atualiza um comentário de tarefa existente. |
| **Tasks - Get task** | GET | Esta API obtém uma tarefa do seu portal de help desk. |
| **Tasks - Update a task** | PATCH | Esta API ajuda a atualizar os detalhes de uma tarefa. |
| **Tasks - List Task attachments** | GET | Esta API lista os arquivos anexados a uma tarefa. |
| **Tasks - Create Task attachment** | POST | Esta API anexa um arquivo a uma tarefa. |
| **Tasks - Delete Task attachment** | DELETE | Esta API remove um anexo de uma tarefa. |
| **Tasks - List Task Time Entries** | GET | Esta API lista os registros de tempo associados a uma tarefa. |
| **Tasks - Add a Task Time Entry** | POST | Esta API cria um registro de tempo no seu help desk. |
| **Tasks - Get a Task Time Entry** | GET | Esta API obtém um registro de tempo registrado para uma tarefa. |
| **Tasks - Update a Task Time Entry** | PATCH | Esta API atualiza detalhes de um registro de tempo existente. |
| **Tasks - Get summation of Task Time Entries** | GET | Esta API obtém a soma dos registros de tempo associados a uma tarefa. |
| **Tasks - Performs Task Timer actions** | POST | Esta API realiza ações relacionadas ao cronômetro, como START, STOP, PAUSE e RESUME. |
| **Teams - List teams from all associated departments** | GET | Esta API obtém detalhes de todas as equipes criadas em todos os departamentos aos quais o usuário atual pertence. |
| **Teams - Create team** | POST | Esta API cria uma equipe no seu portal de help desk. |
| **Teams - Get team** | GET | Esta API obtém os detalhes de uma equipe. |
| **Teams - List associable teams** | GET | Esta API lista as outras equipes que podem ser adicionadas como sub-equipes à equipe atual. |
| **Teams - Update team** | PATCH | Esta API atualiza detalhes de uma equipe existente. |
| **Teams - Delete team** | POST | Esta API exclui uma equipe existente do seu portal de help desk. Para reatribuir tickets e tarefas, passe os parâmetros ticketNewTeam, taskNewTeam, ticketNewAgent e taskNewAgent. |
| **Teams - List details of team members** | GET | Esta API obtém detalhes de todos os membros de uma equipe específica. |
| **Templates - Listing Templates** | GET | Lista todos os modelos. |
| **Templates - Add Template** | POST | Adiciona um novo modelo. |
| **Templates - Fetching placeholders** | GET | Listar os espaços reservados suportados em modelos de email |
| **Templates - View Template** | GET | Visualizar um modelo particular |
| **Templates - Update Template** | PUT | Atualizar um modelo existente |
| **Templates - Delete Template** | DELETE | Excluir um modelo |
| **Templates - Cloning a Email Template Attachments** | POST | Clonar os anexos de um modelo existente |
| **Templates - Rendering a Template** | POST | Renderizar um modelo existente em resposta |
| **Ticketqueueview - List all ticketQueueView count** | GET | Esta API retorna o número de tickets em uma visualização particular. |
| **Tickettags - List tickets tags** | GET | Esta API lista as tags de ticket adicionadas no seu portal de helpdesk. |
| **Tickettemplates - List ticket templates** | GET | Esta API lista um número particular de modelos de ticket, com base no limite especificado. |
| **Tickettemplates - Create ticket template** | POST | Esta API ajuda a criar um modelo de ticket no seu portal de helpdesk. |
| **Tickettemplates - Delete ticket template** | POST | Esta API exclui um modelo de ticket do seu portal de helpdesk. |
| **Tickettemplates - Get ticket template** | GET | Esta API obtém os detalhes de um modelo de ticket particular. |
| **Tickettemplates - Update ticket template** | PATCH | Esta API ajuda a atualizar os detalhes de um modelo de ticket particular. |
| **Tickets - List all tickets** | GET | Esta API lista um número particular de tickets, com base no limite especificado. |
| **Tickets - Create a ticket** | POST | Esta API cria um ticket no seu helpdesk. |
| **Tickets - Get Archived Ticket List** | GET | Esta API obtém a lista de tickets arquivados no departamento fornecido. |
| **Tickets - Delete spam tickets** | POST | Esta API exclui os tickets de spam fornecidos. |
| **Tickets - Empty spam tickets** | POST | Esta API exclui todos os tickets de spam. |
| **Tickets - Mark ticket as spam** | POST | Esta API marca tickets como spam. |
| **Tickets - Move Tickets to trash** | POST | Esta API move tickets para a Lixeira. |
| **Tickets - Search Tickets** | GET | Esta API pesquisa tickets no seu helpdesk. Você pode fornecer múltiplos valores separados por vírgulas, e a pesquisa será realizada usando qualquer um dos valores fornecidos. |
| **Tickets - Bulk update tickets** | POST | Esta API atualiza múltiplos tickets de uma vez. |
| **Tickets - List Ticket Time Entries** | GET | Esta API lista os registros de tempo associados a um ticket. |
| **Tickets - Get Ticket Timer** | GET | Esta API obtém o tempo decorrido no cronômetro do ticket, junto com o estado atual. |
| **Tickets - Performs Ticket Timer actions** | POST | Esta API executa ações relacionadas ao cronômetro, como INICIAR, PARAR, PAUSAR e RETOMAR. |
| **Tickets - List ticket timers** | GET | Esta API obtém os detalhes dos cronômetros atualmente ativos em um ticket. |
| **Tickets - Get Original Mail Content** | GET | Esta API obtém o conteúdo do email original, incluindo cabeçalhos de email. |
| **Tickets - Get a ticket** | GET | Esta API obtém um único ticket do seu helpdesk. |
| **Tickets - Update a ticket** | PATCH | Esta API atualiza os detalhes de um ticket existente. |
| **Tickets - Get ticket history** | GET | Esta API obtém detalhes de todas as ações — chamadas eventos — realizadas em um ticket e nas abas secundárias na página de detalhes. |
| **Tickets - List ticket activities** | GET | Esta API lista um número particular de atividades associadas a um ticket, com base no limite especificado. |
| **Tickets - Add ticket followers** | POST | Esta API adiciona um ou mais usuários à lista de seguidores de um ticket. |
| **Tickets - List approvals** | GET | Esta API lista as aprovações enviadas no seu helpdesk. |
| **Tickets - Create approval** | POST | Esta API cria uma aprovação no seu helpdesk. |
| **Tickets - Get approval** | GET | Esta API obtém os detalhes de uma aprovação. |
| **Tickets - Update approval** | PATCH | Esta API atualiza os detalhes de uma aprovação de ticket existente. |
| **Tickets - Suggest relevant articles for ticket** | GET | Esta API sugere artigos de ajuda que possam ser relevantes para resolver um ticket. |
| **Tickets - Associate Ticket Tags** | POST | Esta API adiciona uma ou múltiplas tags a um ticket. |
| **Tickets - List ticket attachments** | GET | Esta API lista os arquivos anexados a um ticket. |
| **Tickets - Create Ticket attachment** | POST | Esta API anexa um arquivo a um ticket. |
| **Tickets - Update Ticket attachment** | PATCH | Esta API atualiza um anexo existente. |
| **Tickets - Delete Ticket attachment** | DELETE | Esta API exclui um anexo de um ticket. |
| **Tickets - List calls by ticket** | GET | Esta API lista um número particular de chamadas associadas a um ticket, com base no limite especificado. |
| **Tickets - List all ticket comments** | GET | Esta API lista um número particular de comentários registrados em um ticket, com base no limite especificado. |
| **Tickets - Create ticket comment** | POST | Esta API adiciona um comentário a um ticket. Para incluir uma menção@, siga este formato: zsu[@user:{zuid}]zsu. |
| **Tickets - Get ticket comment** | GET | Esta API obtém um comentário de ticket do seu portal de helpdesk. |
| **Tickets - Update ticket comment** | PATCH | Esta API modifica um comentário existente. Para incluir uma menção@, siga este formato: zsu[@user:{zuid}]zsu. |
| **Tickets - Delete ticket comment** | DELETE | Esta API exclui um comentário. |
| **Tickets - Get a ticket comment history** | GET | Esta API obtém o histórico de comentários registrados em um ticket, incluindo instâncias de adição e edição. |
| **Tickets - Dissociate Ticket Tags** | POST | Esta API remove uma ou múltiplas tags de um ticket. |
| **Tickets - Draft Email Reply** | POST | Esta API redige uma resposta de email. O endereço de envio deve ser um endereço configurado no seu portal de helpdesk. |
| **Tickets - Update Draft** | PATCH | Esta API atualiza um rascunho de thread criado através do canal @EMAIL@, @FACEBOOK@ ou @FORUM@. |
| **Tickets - List events by ticket** | GET | Esta API lista um número particular de eventos associados a um ticket, com base no limite especificado. |
| **Tickets - Execute Skill Based Assignment** | POST | Esta API atribui tickets a agentes de acordo com suas habilidades designadas e preferências de roteamento. |
| **Tickets - Get ticket followers** | GET | Esta API obtém a lista de usuários seguindo um ticket. Seguidores de contato ou conta podem se tornar seguidores de ticket indiretamente se associados. |
| **Tickets - Mark as read** | POST | Esta API marca um ticket como lido pelo usuário. |
| **Tickets - Mark as unread** | POST | Esta API marca um ticket como não lido pelo usuário. |
| **Tickets - Merge two tickets** | POST | Esta API mescla dois tickets diferentes. |
| **Tickets - Get ticket metrics** | GET | Esta API obtém detalhes relacionados aos tempos de resposta e resolução de um ticket. |
| **Tickets - Move ticket** | POST | Esta API ajuda a mover um ticket de um departamento para outro. O parâmetro de query departmentId será descontinuado em breve. Portanto, a partir de agora, o atributo departmentId deve ser passado no corpo da requisição. |
| **Tickets - Map articles to tickets** | POST | Esta API mapeia tickets com artigos de ajuda para sugerir automaticamente os mesmos artigos para tickets semelhantes que chegam depois. |
| **Tickets - Get pins of a ticket** | GET | Esta API obtém a lista de pins de um ticket específico. |
| **Tickets - Create a pin on the ticket** | POST | Esta API cria um novo pin no ticket. |
| **Tickets - Unpin a ticket's pin** | POST | Esta API exclui um ou mais pins de um ticket. |
| **Tickets - Recalculate Skills for a ticket** | POST | Esta API remove skills existentes e reaaplica as obrigatórias com base nas circunstâncias atuais do ticket. |
| **Tickets - Remove ticket followers** | POST | Esta API remove um ou mais usuários da lista de seguidores de um ticket. |
| **Tickets - Get ticket resolution** | GET | Esta API obtém detalhes relacionados à resolução de um ticket. |
| **Tickets - Update ticket resolution** | PATCH | Esta API atualiza o campo de resolução de um ticket. |
| **Tickets - Delete ticket resolution** | DELETE | Esta API exclui uma resolução adicionada a um ticket. |
| **Tickets - Get resolution history** | GET | Esta API obtém o histórico de resolução de um ticket. |
| **Tickets - Send Email Reply** | POST | Esta API envia uma resposta por email. O endereço de origem no email deve ser um endereço configurado no seu portal de help desk. |
| **Tickets - List tags in a ticket** | GET | Esta API lista tags associadas a um ticket. |
| **Tickets - List tasks by ticket** | GET | Esta API lista todas as tarefas associadas a um ticket específico. |
| **Tickets - List all threads** | GET | Esta API lista todas as threads do seu helpdesk. |
| **Tickets - Delete attachment** | DELETE | Esta API exclui um anexo de uma thread de rascunho. |
| **Tickets - Split tickets** | POST | Esta API divide uma thread de ticket de entrada em um novo ticket. |
| **Tickets - Add Ticket Time Entry** | POST | Esta API adiciona uma entrada de tempo no seu help desk. |
| **Tickets - Update Ticket Time Entry** | PUT | Esta API atualiza uma entrada de tempo de ticket existente. |
| **Tickets - Get Ticket Time Entry** | GET | Esta API obtém uma entrada de tempo registrada para um ticket. |
| **Tickets - Delete Ticket Time Entry** | DELETE | Esta API exclui uma entrada de tempo registrada para um ticket. |
| **Tickets - Get Ticket Time Entries by Billing Type** | GET | Esta API obtém entradas de tempo para um ticket criado após o tempo de modificação recente do tipo de cobrança fornecido do seu help desk. |
| **Tickets - Get summation of Ticket Time Entries** | GET | Esta API obtém a soma das entradas de tempo associadas a um ticket. |
| **Tickets - Delete the during actions transition draft** | POST | Para excluir o rascunho de transição durante ações. |
| **Tickets - Save the during actions transition draft** | POST | Para salvar o rascunho de transição durante ações. |
| **Tickets - Get Applied Blueprint details of ticket for a user** | GET | Para obter os detalhes do blueprint aplicado de um ticket. |
| **Tickets - Revoke Blueprint at Entity Level** | POST | Para revogar blueprint de uma entidade. |
| **Tickets - Delete attachment of a transition draft** | DELETE | Exclui um anexo específico adicionado a um rascunho de transição. |
| **Tickets - View a specific attachment added to a transition draft** | GET | Obtém anexo de um rascunho de transição. |
| **Ticketscount - Get tickets count** | GET | Esta API retorna a contagem de tickets do seu help desk. |
| **Ticketscountbyfieldvalues - Get ticket count by field** | GET | Esta API retorna a contagem de tickets do seu help desk, filtrada por um campo específico. |
| **Uploads - Upload file** | POST | Esta API envia um arquivo. |
| **Users - Get Users** | GET | Esta API lista um número específico de usuários do help center, com base no limite definido. Também ajuda você a pesquisar usuários específicos. |
| **Users - Get User Details** | GET | Esta API obtém os detalhes de um usuário específico do help center. |
| **Users - Update User Details** | PATCH | Esta API ajuda a atualizar os detalhes de um usuário específico do help center. |
| **Users - Delete End User** | POST | Esta API exclui permanentemente todas as informações de identificação sobre um usuário do seu help center. |
| **Users - List User badges** | GET | Esta API lista badges padrão e personalizadas do usuário, com base no limite definido. |
| **Users - Add Badges to a user** | POST | Esta API adiciona badges especificadas ao usuário. |
| **Users - Remove Badges from user** | POST | Esta API remove badges especificadas dos usuários. |
| **Users - Get User Groups** | GET | Esta API lista um número específico de grupos de usuários em um help center, com base no limite definido. |
| **Users - Associate Groups To Users** | POST | Esta API adiciona um usuário aos grupos especificados. |
| **Users - Delete Groups From Users** | POST | Esta API remove um usuário dos grupos especificados. |
| **Users - Get User Labels** | GET | Esta API lista um número específico de labels associados a um usuário, com base no limite definido. |
| **Users - Assign Labels To User** | POST | Esta API atribui os labels que você especifica a um usuário específico. |
| **Users - Remove Labels From User** | POST | Esta API remove os labels que você especifica de um usuário específico. |
| **Views - List Views** | GET | Esta API lista as diferentes views configuradas para um módulo específico ou para todos os módulos no seu portal de help desk. |
| **Views - Add Starred View** | POST | Esta API marca uma view como favorita, permitindo acesso rápido à view. |
| **Follow - Follow the Entity** | POST | Esta API segue a entidade solicitada pelo usuário solicitado. |
| **Followers - Get Entity followers details** | GET | Esta API obtém a lista de detalhes de seguidores com base no filtro fornecido. |
| **Followerscount - Get Entity followers count** | GET | Esta API obtém a contagem de lista de seguidores com base no filtro fornecido. |
| **Unfollow - UnFollow the entity** | POST | Esta API deixa de seguir a entidade solicitada pelo usuário solicitado. |
| **Search - Search  Records** | GET | Esta API pesquisa registros no seu help desk. Você pode fornecer múltiplos valores separados por vírgulas, e a pesquisa será realizada no campo usando qualquer um dos valores fornecidos. |

---

## Documentação oficial

- [Zoho Desk REST API v1](https://desk.zoho.com/DeskAPIDocument)
- [Escopos OAuth do Zoho Desk](https://desk.zoho.com/DeskAPIDocument#OauthTokens#OauthScopes)
- [Especificação OpenAPI oficial](https://github.com/zoho/zohodesk-oas)
