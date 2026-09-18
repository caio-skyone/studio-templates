# Zoho CRM

## Contexto

A API do **Zoho CRM** é REST sobre HTTPS, com troca de dados em JSON, e expõe programaticamente o CRM da Zoho: registros comerciais, usuários, metadados de configuração e operações em lote.

**Conceitos fundamentais**

- **Módulo** — a unidade central do CRM. Cada módulo (`Leads`, `Contacts`, `Accounts`, `Deals`, `Tasks`, `Calls`, `Products`, além dos customizados) é uma coleção de registros com seus próprios campos e layouts. Quase toda operação deste conector recebe o **nome de API do módulo** como parâmetro, o que faz uma única operação servir a todos eles.
- **Registro** — uma instância dentro de um módulo, identificada por um ID numérico longo. É sobre registros que agem criação, atualização, exclusão, clonagem, mesclagem e conversão.
- **Lista relacionada** — a coleção de registros vinculados a um registro pai, por exemplo os contatos de um negócio. Tem endpoints próprios de leitura, associação e desassociação.
- **Ações em massa** — trabalhos assíncronos (atualização, exclusão, troca de proprietário, conversão de leads) que retornam um `job_id` e são consultados depois.
- **COQL** — linguagem de consulta própria do Zoho, em sintaxe parecida com SQL, para buscar registros com filtros que a listagem simples não expressa.
- **Bulk Read / Bulk Write** — leitura e escrita de grandes volumes via arquivos CSV compactados, também assíncronas.
- **Organização e datacenter** — a conta Zoho vive em um datacenter específico (`.com`, `.eu`, `.in`, `.com.au`, `.jp`, `.ca`, `.sa`), e o host da API muda junto com ele.
- **Versão da API** — a Zoho mantém **oito versões ativas ao mesmo tempo**: `v2`, `v2.1`, `v3`, `v4`, `v5`, `v6`, `v7` e `v8`, cada uma em seu próprio caminho. A versão não é fixada no conector: é um parâmetro de cada operação.

**Escopo deste conector**

Este módulo cobre o uso operacional do CRM — registros, listas relacionadas, notas, anexos, fotos, e-mails, usuários, territórios, consultas e ações em massa — e a parte de configuração estritamente necessária para operá-lo: metadados de módulo, layouts e visualizações personalizadas.

Ficam **fora** do escopo, por decisão de projeto, os demais endpoints de `settings/*` — automação, perfis, papéis, regras de atribuição, portais, tags, variáveis, horários comerciais, lixeira, campos, moedas, entre outros. São administração do CRM, exigiriam escopos OAuth bem mais permissivos e cabem melhor em um módulo próprio.

---

## Autenticação

**Tipo:** OAuth 2.0

Toda API da Zoho autentica pelo **Zoho Accounts**, com o cabeçalho `Authorization: Zoho-oauthtoken <token>` — montado pela conta conectada, não por parâmetro de operação.

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://zohoapis.<>seu-datacenter</>/crm` |
| Porta | 443 |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Access Token | {{access_token}} |
| Refresh Token | {{refresh_token}} |
| Endpoint de troca de token | `https://accounts.zoho.com/oauth/v2/token` |

> **O datacenter faz parte do Host.** Substitua `<>seu-datacenter</>` pelo TLD da sua conta: `com`, `eu`, `in`, `com.au`, `jp`, `ca` ou `sa`. Uma conta do datacenter europeu não responde em `zohoapis.com`. O endpoint de troca de token acompanha o mesmo datacenter — use `https://accounts.zoho.eu/oauth/v2/token` para o DC europeu, e assim por diante.

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

### Escopos OAuth necessários

Os escopos vão no parâmetro `scope` da URL de autorização, separados por vírgula. O conjunto abaixo é a união exata do que as 170 operações deste módulo exigem:

| Escopo | Cobre |
| ------ | ----- |
| `ZohoCRM.modules.ALL` | registros de todos os módulos, listas relacionadas, notas, anexos, fotos, e-mails, rascunhos, compromissos, serviços e bloqueio de registro |
| `ZohoCRM.users.ALL` | usuários e territórios de usuário |
| `ZohoCRM.settings.modules.ALL` | metadados de módulo |
| `ZohoCRM.settings.territories.ALL` | atribuição e remoção de territórios |
| `ZohoCRM.settings.layouts.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | layouts |
| `ZohoCRM.settings.custom_views.READ`, `.UPDATE` | visualizações personalizadas |
| `ZohoCRM.settings.fields.READ` | leitura de campos, exigida pela exclusão de layout |
| `ZohoCRM.notifications.ALL` | canais de notificação |
| `ZohoCRM.bulk.READ`, `ZohoCRM.bulk.CREATE` | leitura e escrita em massa |
| `ZohoCRM.coql.READ` | consultas COQL |
| `ZohoCRM.files.READ`, `ZohoCRM.files.CREATE` | arquivos no Zoho File System |
| `ZohoCRM.change_owner.READ`, `.CREATE` | troca de proprietário |
| `ZohoCRM.mass_update.READ`, `.UPDATE` | atualização em massa |
| `ZohoCRM.mass_delete.READ`, `.DELETE` | exclusão em massa |
| `ZohoCRM.mass_convert.leads.READ`, `.CREATE` | conversão de leads em massa |
| `ZohoCRM.send_mail.all.CREATE` | envio de e-mail a partir do registro |
| `ZohoSearch.securesearch.READ` | **escopo de outro produto Zoho** |

> **Atenção ao escopo de terceiro.** Duas operações — **Search - Search Records by Criteria, Word, Email, or Phone** e **Actions - Get Record Count in a Module** — exigem `ZohoSearch.securesearch.READ`, que pertence ao Zoho Search, não ao CRM. Ele precisa ser autorizado na mesma aplicação OAuth. Se você não pretende usar essas duas operações, pode omiti-lo dos escopos concedidos.

---

## Convenções deste conector

- **A versão da API é um parâmetro.** Toda operação recebe `version` como primeiro segmento do caminho, com `v8` como valor sugerido. Isso existe porque a Zoho serve `v2`, `v2.1`, `v3`, `v4`, `v5`, `v6`, `v7` e `v8` simultaneamente — fixar a versão no Host prenderia o conector a uma delas e obrigaria a criar outra conta conectada para falar com as demais.
- **O módulo é um parâmetro.** As operações do domínio `Records` e boa parte das de `Actions` recebem `module` (ou `module_api_name`) no caminho. Informe o **nome de API** do módulo — `Leads`, `Contacts`, `Deals`, `Tasks` ou o nome de API de um módulo customizado. Uma única operação serve, assim, a todo o CRM.
- **Corpo das requisições.** O parâmetro `body` é um texto JSON único. Informe o objeto completo na sintaxe da própria API do Zoho; na maioria das operações de escrita, os registros vão dentro do array `data`.
- **Uploads são multipart.** As três operações de envio de arquivo — **Files - Uploads a file to ZFS**, **Attachments - Upload an attachment** e **Photo - Upload a photo** — usam `multipart/form-data` no formato granular `file:<>file</>:mime:tipo:arquivo`. Não exigem base64 nem bufferização forçada.
- **Trabalhos assíncronos.** Bulk Read, Bulk Write, atualização, exclusão e conversão em massa e troca de proprietário em massa retornam um `job_id`. A consulta de situação é uma operação separada.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Appointments  S - GET /Appointments__s** | GET | Recupera os registros do módulo Appointments. |
| **Appointments  S - POST /Appointments__s** | POST | Cria registros no módulo Appointments. |
| **Appointments  S - PUT /Appointments__s** | PUT | Atualiza registros do módulo Appointments. |
| **Appointments  S - DELETE /Appointments__s/{ids}** | DELETE | Exclui registros do módulo Appointments. |
| **Appointments  S - GET /Appointments__s/{appointmentId}** | GET | Recupera um registro do módulo Appointments pelo seu identificador. |
| **Appointments  S - PUT /Appointments__s/{id}** | PUT | Atualiza um registro do módulo Appointments pelo identificador do compromisso. |
| **Appointments  S - DELETE /Appointments__s/id** | DELETE | Exclui um registro do módulo Appointments pelo seu identificador. |
| **Contacts - Link Emails to Deals** | POST | Vincula os e-mails aos negócios indicados no CRM. |
| **Contacts - Unlink Emails from Records** | DELETE | Desvincula os e-mails dos registros indicados no CRM. |
| **Contacts - Link Email to Record** | POST | Vincula um e-mail a um registro específico do CRM. |
| **Contacts - Unlink Email from Record** | DELETE | Desvincula um e-mail de um registro específico do CRM. |
| **Events - Cancel Meeting** | POST | Envia o e-mail de cancelamento da reunião. |
| **Leads - Get mass convert job status** | GET | Recupera a situação e as contagens de um trabalho de conversão em massa já agendado, usando o parâmetro de consulta job_id. |
| **Leads - Mass convert leads** | POST | Agenda um trabalho de conversão em massa que converte vários leads em outros módulos (Deals, Contacts, Accounts) conforme as opções informadas. Máximo de 50 IDs de lead por requisição. |
| **Leads - Get Lead Conversion Options** | GET | Recupera as opções de conversão disponíveis para um lead, incluindo contatos e contas correspondentes, mapeamento de campos e preferências de layout, antes de executar a conversão. |
| **Leads - Convert a Lead** | POST | Converte um registro de Lead em registros de Contact, Account e/ou Deal, permitindo configurar sobrescrita, notificações, atribuição de proprietário e transferência de tags. |
| **Notes - Get Notes** | GET | Recupera uma lista de notas. |
| **Notes - Create Notes** | POST | Cria um ou mais registros de nota. |
| **Notes - Update Notes** | PUT | Atualiza um ou mais registros de nota existentes. Para cada nota é obrigatório informar ao menos o conteúdo ou o título. |
| **Notes - Delete Notes** | DELETE | Exclui permanentemente uma ou mais notas, informando os IDs separados por vírgula. |
| **Notes - Get a Specific Note** | GET | Recupera os detalhes de uma nota específica pelo seu ID. |
| **Notes - Update a Specific Note** | PUT | Atualiza uma nota específica pelo seu ID. É obrigatório informar ao menos o conteúdo ou o título da nota. |
| **Notes - Delete a Specific Note** | DELETE | Exclui permanentemente uma nota específica pelo seu ID. |
| **Services  S - GET /services_s** | GET | Recupera os registros do módulo Services. |
| **Services  S - POST /services_s** | POST | Cria registros no módulo Services. |
| **Services  S - PUT /services_s** | PUT | Atualiza registros do módulo Services. |
| **Services  S - DELETE /services_s** | DELETE | Exclui registros do módulo Services. |
| **Services  S - GET /services_s/{id}** | GET | Recupera um registro do módulo Services pelo seu identificador. |
| **Services  S - PUT /services_s/{id}** | PUT | Atualiza um registro do módulo Services pelo seu identificador. |
| **Services  S - DELETE /services_s/{id}** | DELETE | Exclui um registro do módulo Services pelo seu identificador. |
| **Actions - List active notification channels** | GET | Recupera a lista de todos os canais de notificação ativos do usuário. |
| **Actions - Create notification channels** | POST | Cria um ou mais canais de notificação. |
| **Actions - Update full notification details** | PUT | Substitui todos os detalhes de um canal de notificação existente, sobrescrevendo a configuração anterior. |
| **Actions - Update specific notification information** | PATCH | Atualiza parcialmente propriedades selecionadas de um canal de notificação: URL, eventos, expiração, condições e token. |
| **Actions - Disable notification channels** | DELETE | Desativa um ou mais canais de notificação identificados pelo parâmetro de consulta channel_ids. |
| **Contacts - Get Contact Roles** | GET | Recupera uma lista de papéis de contato. |
| **Contacts - Create Contact Roles** | POST | Cria um ou mais papéis de contato. |
| **Contacts - Update Contact Roles** | PUT | Atualiza um ou mais papéis de contato. |
| **Contacts - Delete Contact Roles** | DELETE | Exclui um ou mais papéis de contato pelos seus IDs. |
| **Contacts - Get Role** | GET | Recupera um papel de contato específico pelo seu ID. |
| **Contacts - Update Role** | PUT | Atualiza um papel de contato específico pelo seu ID. |
| **Contacts - Delete Role** | DELETE | Exclui um papel de contato específico pelo seu ID. |
| **Coql - Execute COQL query** | POST | Executa uma consulta COQL do tipo select para buscar dados de registros. |
| **Files - Retrieves a file from ZFS** | GET | Recupera o conteúdo binário de um arquivo armazenado no Zoho File System (ZFS) pelo parâmetro de consulta obrigatório "id". Se o arquivo não existir no ZFS, a resposta é 204 No Content. |
| **Files - Uploads a file to ZFS** | POST | Envia um arquivo ao Zoho File System (ZFS) via multipart e retorna os metadados, incluindo o ID usado para associá-lo a registros do CRM. Até 10 arquivos por requisição, no máximo 20 MB cada. |
| **Read - Createbulkreadjob** | POST | Cria um trabalho de leitura em massa (bulk read). |
| **Read - Getbulkreadjobdetails** | GET | Recupera os detalhes de um trabalho de leitura em massa. |
| **Read - Downloadresult** | GET | Baixa o resultado de um trabalho de leitura em massa. |
| **Settings - To get the Call preferences of the user** | GET | Retorna as preferências de chamada do usuário, usadas para exibir os campos de número de origem e de destino no CRM. |
| **Settings - Updating Call preference** | PUT | Atualiza as preferências de chamada do usuário. |
| **Settings - Get All Custom Views** | GET | Recupera todas as visualizações personalizadas de um módulo. |
| **Settings - Change Sort Order** | PUT | Altera a ordem de classificação de uma visualização personalizada. |
| **Settings - Get Custom View By Id** | GET | Recupera uma visualização personalizada específica de um módulo pelo seu ID. |
| **Settings - Change Sort Order of a Specific Custom View** | PUT | Altera a ordem de classificação de uma visualização personalizada específica, identificada pelo seu ID. |
| **Settings - Get all layouts metadata for a module** | GET | Recupera os detalhes de todos os layouts de um módulo, incluindo seções, campos, perfis e permissões, em uma única resposta sem paginação. O array "profiles" vem nulo sem a permissão de personalização de módulo. |
| **Settings - Get a specific layout metadata by ID** | GET | Recupera os detalhes de um layout específico de um módulo pelo seu identificador, incluindo seções, campos, perfis e permissões. O array "profiles" vem nulo sem a permissão de personalização de módulo. |
| **Settings - Update a Layout** | PATCH | Atualiza um layout customizado: renomeia, altera permissões de perfil, habilita o cartão de visita e cria, atualiza, exclui ou move seções e campos. Limite de 5 seções e 5 campos no total por requisição. |
| **Settings - Delete a custom layout** | DELETE | Exclui um layout customizado de um módulo. Se o layout tiver registros associados, é preciso informar em "transfer_to" o layout de destino. O layout padrão não pode ser excluído. |
| **Settings - Activate layout with profile associations** | POST | Ativa um layout desativado, tornando-o disponível no módulo, e opcionalmente adiciona ou remove associações de perfil. Apenas um layout por requisição; ativar um layout já ativo retorna erro. |
| **Settings - Deactivate layout with configuration transfer** | DELETE | Desativa um layout ativo e transfere sua configuração — associações de perfil, permissões e mapeamento de campos — para outro layout ativo do mesmo módulo. Ao menos um layout ativo precisa permanecer. |
| **Settings - Retrieve CRM module metadata** | GET | Recupera os metadados dos módulos do CRM, incluindo configuração, capacidades e informações estruturais. Permite filtrar por nome de funcionalidade ou por status; informando os dois, o módulo precisa atender a ambos. |
| **Settings - Create a custom CRM module** | POST | Cria um módulo customizado no CRM. Exige a permissão Crm_Implied_Customize_Zoho_CRM, cria apenas um módulo por requisição e não é idempotente: repetir o mesmo api_name gera erro de validação. |
| **Settings - Update CRM modules** | PUT | Atualiza módulos existentes do CRM, permitindo alterar rótulos e atribuições de perfil. É idempotente e aceita vários módulos por requisição, retornando 207 quando parte deles falha. |
| **Settings - Get module metadata by API name** | GET | Recupera os metadados completos de um módulo do CRM pelo seu nome de API, incluindo campos, layouts, perfis, listas relacionadas, visualizações personalizadas e capacidades. |
| **Settings - Update module labels and profiles** | PUT | Atualiza parcialmente os rótulos de exibição de um módulo, no singular e no plural, e as permissões de perfil associadas, sem afetar o restante da configuração. A operação é idempotente. |
| **Settings - Retrieve service preference settings for the organization** | GET | Recupera a configuração de preferências de serviço da organização. |
| **Settings - Update service preference settings for the organization** | PUT | Atualiza a configuração de preferências de serviço da organização. |
| **Settings - List territory users** | GET | Retorna os usuários de um território. |
| **Settings - Add users** | PUT | Adiciona usuários a um território. |
| **Settings - Remove users** | DELETE | Remove usuários de um território. |
| **Settings - Get user details** | GET | Retorna um usuário específico de um território. |
| **Settings - Add specific user** | PUT | Adiciona um usuário específico a um território. |
| **Settings - Remove user** | DELETE | Remove um usuário específico de um território. |
| **Users - Get users** | GET | Recupera todos os usuários conforme os parâmetros informados. |
| **Users - Create User** | POST | Cria um novo usuário na organização. |
| **Users - Update User** | PUT | Atualiza vários usuários. |
| **Users - Get Transfer Status** | GET | Recupera a situação de uma operação de transferência de usuário pelo ID do trabalho. |
| **Users - Get Transfer and Delete Status** | GET | Recupera a situação de uma operação de transferência e exclusão de usuário pelo ID do trabalho. |
| **Users - Transfer and Delete User** | POST | Transfere os registros, atribuições e critérios de um usuário para outro e exclui o usuário de origem. |
| **Users - Transfer a Specific User** | POST | Transfere os registros, atribuições e critérios de um usuário específico para outro usuário. |
| **Users - Transfer and Delete a Specific User** | POST | Transfere os registros, atribuições e critérios de um usuário específico para outro usuário e exclui o usuário de origem. |
| **Users - Validate User Before Transfer** | GET | Valida um usuário antes da transferência, recuperando a situação da operação pelo ID do trabalho. |
| **Users - Get user** | GET | Recupera um único usuário pelo ID informado. |
| **Users - Update a Specific User** | PUT | Atualiza um único usuário pelo seu ID. |
| **Users - Delete a User** | DELETE | Exclui um usuário pelo seu ID. |
| **Users - Get Territories of User** | GET | Recupera os territórios atribuídos a um usuário. |
| **Users - Associate Territories to User** | PUT | Associa territórios a um usuário. |
| **Users - Remove Territories from User** | DELETE | Remove territórios de um usuário. |
| **Users - Get specific Territory of User** | GET | Recupera um território específico de um usuário. |
| **Users - Remove Territory from User** | DELETE | Remove um território específico de um usuário. |
| **Write - Create Bulk Write Job** | POST | Cria um trabalho de escrita em massa para inserir ou atualizar registros em lote. |
| **Write - Get Bulk Write Job Details** | GET | Recupera os detalhes de um trabalho de escrita em massa. A resposta traz o file_id do CSV em ZIP enviado, usado na requisição de escrita em massa. |
| **Actions - Get Record Count in a Module** | GET | Recupera o total de registros de um módulo, com filtro por cvid ou por um dos parâmetros de busca (criteria, phone, email, word) — nunca os dois juntos, sob pena de erro. Exige também o escopo ZohoSearch.securesearch.READ. |
| **Actions - Fetch full data for multiple records** | GET | Recupera o conteúdo completo dos campos de texto rico de vários registros. O parâmetro "fields" é obrigatório e aceita no máximo 8 campos de texto rico. |
| **Actions - Share Emails in Bulk** | POST | Compartilha os e-mails de vários registros com outros usuários da sua organização. |
| **Actions - Unshare Emails in Bulk** | POST | Remove o compartilhamento dos e-mails de vários registros com outros usuários da sua organização. |
| **  Emails Sharing Details - Get Email Shared Details** | GET | Recupera os detalhes dos usuários com quem os e-mails do registro podem ser compartilhados e o tipo de compartilhamento. |
| **Actions - Convert an inventory record** | POST | Converte o registro em outro módulo de inventário conforme o módulo de origem: Quotes para Sales Orders ou Invoices, e Sales Orders para Invoices. |
| **Actions - Fetch full data for a single record** | GET | Recupera o conteúdo completo dos campos de texto rico de um registro específico. Sem o parâmetro "fields", todos os campos de texto rico do módulo são retornados. |
| **Actions - Share Emails of a record** | POST | Compartilha os e-mails de um registro específico com outros usuários da sua organização. |
| **Actions - Unshare Emails of a record** | POST | Remove o compartilhamento dos e-mails de um registro específico com outros usuários da sua organização. |
| **Attachments - Retrieve all attachments associated with a specific record** | GET | Recupera todos os anexos associados a um registro específico. |
| **Attachments - Upload an attachment** | POST | Envia um anexo informando um arquivo ou uma URL válida. O corpo da requisição pode ter no máximo 100 MB. |
| **Attachments - Download a specific attachment file** | GET | Baixa o conteúdo de um anexo específico pelo seu ID, retornando o arquivo em si — imagem, PDF, documento. Anexos do tipo link retornam erro, pois não podem ser baixados. |
| **Attachments - Delete Link Attachment** | DELETE | Exclui um anexo do tipo link associado a um registro de um módulo. |
| **Actions - Get Related Records Count** | POST | Recupera a contagem de registros relacionados a um registro pai, com filtro por critérios como situação de aprovação, situação de conversão e campos customizados, sem trazer os registros em si. |
| **Actions - Send an email to a record** | POST | Envia um e-mail para um registro de um módulo, usando modelos específicos ou conteúdo personalizado. |
| **Locking Information  S - To retrieve the locking information details of locked records** | GET | Recupera os detalhes das informações de bloqueio de registros bloqueados em diferentes módulos. |
| **Locking Information  S - To lock a record of a module** | POST | Bloqueia registros em diferentes módulos. |
| **Locking Information  S - To update the locking reason of a locked record** | PUT | Altera as informações de bloqueio de registros bloqueados em diferentes módulos. |
| **Locking Information  S - Remove Lock from Locked Records** | DELETE | Remove o bloqueio de registros bloqueados em diferentes módulos. |
| **Actions - Asssign Territories To Records** | POST | Atribui territórios a vários registros do módulo. |
| **Actions - Change owner for multiple records** | POST | Altera o proprietário de vários registros do módulo. |
| **Actions - Enroll records into cadences** | POST | Inscreve registros em uma cadência manual. |
| **Actions - Check mass change owner job status** | GET | Consulta a situação de um trabalho de troca de proprietário em massa pelo ID do trabalho. |
| **Actions - Mass change owner of records** | POST | Altera em massa o proprietário dos registros de um módulo, com base em uma visualização personalizada. |
| **Actions - Retrieve mass delete job status** | GET | Recupera a situação e os resultados de uma exclusão em massa já agendada, pelo ID do trabalho. |
| **Actions - Mass delete with record ids and custom view id** | POST | Exclui registros em massa informando os IDs dos registros ou o ID de uma visualização personalizada. |
| **Actions - Retrieve the status of a mass update job** | GET | Recupera a situação atual e as métricas de progresso de um trabalho assíncrono de atualização em massa, com as contagens de registros e o estado do trabalho. |
| **Actions - Mass Update API** | POST | Atualiza o valor de um campo específico em vários registros de um módulo do CRM. |
| **Actions - Remove Territories To Records** | POST | Remove territórios de vários registros do módulo. |
| **Actions - Unenroll records from cadences** | POST | Cancela a inscrição de registros nas cadências. |
| **Deleted - Get deleted records from a module** | GET | Recupera os registros excluídos de um módulo, tanto os excluídos permanentemente quanto os que estão na lixeira. |
| **Search - Search Records by Criteria, Word, Email, or Phone** | GET | Busca registros de um módulo por critérios, palavra, e-mail ou telefone; ao menos um parâmetro de busca é obrigatório. Limite de 2.000 registros e 15 condições. Exige também o escopo ZohoSearch.securesearch.READ. |
| **Upsert - To insert a new or update an existing record based on duplicate check field** | POST | Insere um novo registro ou atualiza um existente, com base nos valores do campo de verificação de duplicidade. |
| **Contact Roles - Get Associated Contact Roles** | GET | Recupera os papéis de contato associados a um negócio. |
| **Contact Roles - Add Or Update Contact Role Relations** | PUT | Adiciona papéis de contato a um negócio ou atualiza em lote as relações de papel já existentes. |
| **Contact Roles - Delete Contact Role Relations** | DELETE | Remove uma ou mais associações de papel de contato de um negócio, usando os IDs das relações. |
| **Contact Roles - Get Contact Role For Contact** | GET | Recupera a relação de papel de contato de um contato específico associado a um negócio. |
| **Contact Roles - Associate Contact Role To Deal** | PUT | Atribui ou atualiza o papel de um contato específico em um negócio. |
| **Contact Roles - Delete Contact Role Relation** | DELETE | Remove uma relação específica entre contato e negócio, usando o identificador do contato no caminho. |
| **Actions - Get Merge Job Status** | GET | Recupera a situação dos trabalhos de mesclagem, para localizar e acompanhar operações de mesclagem de registros nos módulos do Zoho CRM. |
| **Actions - Merge Records** | POST | Mescla registros duplicados nos módulos do Zoho CRM, com mapeamento de campos e validação. Suporta mesclagem síncrona e assíncrona. |
| **Actions - To clone a record in a module** | POST | Clona um registro de um módulo. |
| **Emails - Get Download Attachments Details** | GET | Recupera o conteúdo binário de um anexo de e-mail de um registro específico. |
| **Emails - Download inline images embedded in an email related to a record** | GET | Baixa as imagens embutidas em um e-mail relacionado a um registro. |
| **  Timeline - Get Timelines** | GET | Recupera as linhas do tempo do registro. |
| **Actions - Associate Email** | POST | Associa e-mails a um registro específico de um módulo. |
| **  Email Drafts - Get email drafts for a record** | GET | Recupera a lista de rascunhos de e-mail associados ao registro informado no módulo indicado. |
| **  Email Drafts - Create email drafts for a record** | POST | Cria um ou mais rascunhos de e-mail associados ao registro informado no módulo indicado. |
| **  Email Drafts - Get email draft** | GET | Recupera o rascunho de e-mail indicado, do registro informado no módulo. |
| **  Email Drafts - Update email draft** | PUT | Atualiza o rascunho de e-mail indicado, do registro informado no módulo. |
| **  Email Drafts - Delete an email draft** | DELETE | Exclui o rascunho de e-mail indicado do registro informado. |
| **Actions - Asssign Territories To Record** | POST | Atribui territórios a um registro do módulo. |
| **Actions - Change owner for a single record** | POST | Altera o proprietário de um registro específico do módulo. |
| **Actions - Remove Territories To Record** | POST | Remove territórios de um registro do módulo. |
| **Photo - Get a photo** | GET | Recupera a foto de um registro. |
| **Photo - Upload a photo** | POST | Envia a foto de um registro. |
| **Photo - Delete a photo** | DELETE | Exclui a foto de um registro. |
| **Deleted - List Deleted Related Records** | GET | Recupera a lista de registros que estavam relacionados a um registro pai e foram excluídos, útil para trilha de auditoria e recuperação de dados. |
| **Notes - List Notes for a Record** | GET | Recupera, de forma paginada, as notas associadas a um registro pai de um módulo do CRM. |
| **Notes - Create Notes for a Record** | POST | Cria uma ou mais notas associadas a um registro pai. É obrigatório informar ao menos o conteúdo ou o título da nota. |
| **Notes - Update Multiple Notes for a Record** | PUT | Atualiza uma ou mais notas associadas a um registro pai. Para cada nota é obrigatório informar ao menos o conteúdo ou o título. |
| **Notes - Delete Note(s) for a Record** | DELETE | Exclui uma ou mais notas associadas a um registro pai, informando os IDs separados por vírgula no parâmetro de consulta. |
| **Notes - Get a Specific Note for a Record** | GET | Recupera os detalhes de uma nota específica associada a um registro pai de um módulo do CRM. |
| **Notes - Update a Note** | PUT | Atualiza uma nota existente associada a um registro pai. É obrigatório informar ao menos o conteúdo ou o título da nota. |
| **Notes - Delete a Specific Note for a Record** | DELETE | Exclui uma nota específica associada a um registro pai, usando o ID da nota no caminho. |
| **Records - Get Records for a specific module** | GET | Recupera os registros de um módulo do CRM, com filtros por campos, território, IDs, visualização personalizada, paginação e ordenação. |
| **Records - Create a Record in a specific module** | POST | Cria um ou mais registros em um módulo do CRM. |
| **Records - To update existing entities or records in a specified module** | PUT | Atualiza registros existentes em um módulo do CRM, informando o ID de cada um no corpo da requisição. |
| **Records - Delete multiple records from a module** | DELETE | Exclui vários registros de um módulo do CRM, informando os IDs no parâmetro de consulta. |
| **Records - Get Record for a specific module with RecordId** | GET | Recupera um registro específico de um módulo do CRM pelo seu ID. |
| **Records - To update existing entities or records in a specified module with the recordID** | PUT | Atualiza um registro específico de um módulo do CRM, identificado pelo seu ID no caminho. |
| **Records - Delete a single record by ID** | DELETE | Exclui um único registro de um módulo do CRM pelo seu ID. |
| **Records - List Related Records** | GET | Recupera os registros de uma lista relacionada de um registro pai, com paginação, ordenação e filtro por IDs. |
| **Records - Update Related Records** | PUT | Atualiza ou associa registros de uma lista relacionada de um registro pai. |
| **Records - Remove Related Records by IDs** | DELETE | Desassocia registros de uma lista relacionada de um registro pai, informando os IDs no parâmetro de consulta. |
| **Records - Get Specific Related Record** | GET | Recupera um registro específico de uma lista relacionada de um registro pai. |
| **Records - Update Specific Related Record** | PUT | Atualiza um registro específico de uma lista relacionada de um registro pai. |
| **Records - Delink Specific Related Record** | DELETE | Desassocia um registro específico de uma lista relacionada do seu registro pai. |

---

## Documentação oficial

- [Zoho CRM REST API v8](https://www.zoho.com/crm/developer/docs/api/v8/)
- [Escopos OAuth do Zoho CRM](https://www.zoho.com/crm/developer/docs/api/v8/scopes.html)
- [Especificação OpenAPI oficial](https://github.com/zoho/crm-oas)
