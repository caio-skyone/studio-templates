# Zoho Analytics

## Contexto

A API REST do **Zoho Analytics** (v2) expõe a plataforma de BI da Zoho: criação e administração de workspaces, importação e exportação de dados, modelagem (tabelas, colunas, fórmulas, tabelas de consulta SQL), criação de relatórios e dashboards, compartilhamento e publicação de visualizações, agendamento de envio por e-mail e AutoML. Toda chamada é autenticada pelo Zoho Accounts e endereçada a uma organização específica pelo cabeçalho `ZANALYTICS-ORGID`.

**Conceitos fundamentais**

- **Organização (`ZANALYTICS-ORGID`)** — a unidade de faturamento e de administração. Usuários, papéis, assinatura e limites de recursos pertencem à organização, e o ID dela vai em **todo** cabeçalho de requisição. Descubra o seu com **Organization - Get organizations**.
- **Workspace (`workspace_id`)** — o contêiner de dados e de análises, equivalente a um banco de dados. Tabelas, relatórios, dashboards, pastas, tags, variáveis e formulários vivem dentro de um workspace.
- **View (`view_id`)** — o termo que a API usa para **qualquer** objeto do workspace: tabela, relatório, dashboard, tabela de consulta, formulário ou apresentação de slides. Por isso a mesma operação de renomear serve para todos, e a maioria dos caminhos é `/workspaces/{workspace_id}/views/{view_id}/…`.
- **`CONFIG`** — o parâmetro que carrega a configuração de praticamente toda chamada, como um JSON. Nos `GET` ele vai na query string; nos `POST`/`PUT`/`DELETE`, no corpo `form-urlencoded`. É o que substitui a longa lista de parâmetros que outras APIs usariam.
- **Importação e exportação síncrona × assíncrona** — as operações do domínio **Data** respondem na própria chamada e servem volumes pequenos; as do domínio **Bulk Data** criam um *job* (`job_id`), que é consultado em laço até o `JOBCODE` indicar conclusão. Arquivos de até 100 MB por lote.
- **Fórmulas** — colunas de fórmula (`customformulas`, avaliadas linha a linha) e fórmulas agregadas (`aggregateformulas`, avaliadas sobre o conjunto). São objetos de primeira classe, com dependentes rastreáveis.
- **Variável (`variable_id`)** — valor parametrizável reutilizado em filtros e fórmulas, o que permite um mesmo relatório atender vários recortes.
- **Publicação** — uma view pode ser exposta por URL pública, por *private link* (chave de acesso sem login) ou embutida via *embed*, cada modo com suas permissões e critérios de filtro.
- **AutoML** — a camada de machine learning: uma análise treina modelos, um modelo é publicado como *deployment* e o *deployment* pode ser executado ou consultado em modo *what-if*.
- **Datacenter** — a conta Zoho vive em um datacenter específico (`.com`, `.eu`, `.in`, `.com.au`, `.jp`, `.ca`, `.sa`) e o host da API muda junto com ele.

**Escopo deste conector**

Este módulo cobre a **API v2 inteira**: **176 operações** em 19 domínios.

| Domínio | Operações | Cobre |
| ------- | --------- | ----- |
| Workspaces | 20 | listar, criar, copiar, renomear, excluir, favoritos, padrão, lixeira, chave secreta, template, metadados, recursos e assinatura |
| Views | 20 | listar, detalhar, renomear, excluir, copiar, duplicar, mover para pasta, favoritar, dashboards, recentes, dependentes, fontes de dados, autoanálise e refetch |
| Formulas | 12 | colunas de fórmula e fórmulas agregadas: listar, criar, editar, excluir, copiar, dependentes e valor |
| Organization | 12 | organizações, administradores, usuários da org e papéis personalizados |
| Workspace Users | 12 | usuários e grupos do workspace, papéis, status e membros de grupo |
| Sharing | 11 | compartilhar views com usuários e grupos, administradores do workspace, permissões próprias e domínios white label |
| Columns | 10 | adicionar, renomear, excluir, ocultar, exibir, reordenar, lookup, dependentes e autoanálise |
| Tags | 10 | criar, atualizar, excluir tags e associá-las a uma ou várias views |
| Bulk Data | 9 | jobs assíncronos de importação e exportação, incluindo importação em lotes |
| Publishing | 9 | URL da view, embed, private link, acesso público e configurações de publicação |
| Data | 7 | importar e exportar de forma síncrona, inserir, atualizar, excluir e ordenar linhas |
| Folders | 7 | criar, renomear, excluir, hierarquia, posição e pasta padrão |
| Slides | 6 | apresentações de slides e sua URL |
| Email Schedules | 6 | criar, atualizar, excluir, ativar/desativar e disparar agendamentos de e-mail |
| Tables | 5 | criar tabela e tabelas de consulta (SQL) |
| Variables | 5 | criar, listar, detalhar, atualizar e excluir variáveis |
| AutoML | 11 | análises, modelos, deployments, execução e what-if |
| Data Sources | 2 | atualizar a conexão da fonte de dados e disparar sincronização |
| Reports | 2 | criar e atualizar relatórios |

Nada da API v2 ficou fora. A **v1** (legada, com caminho `/api/{e-mail}/{workspace}/{view}` e semântica própria) não é atendida por este módulo.

---

## Autenticação

**Tipo:** OAuth 2.0

Toda API da Zoho autentica pelo **Zoho Accounts**, com o cabeçalho `Authorization: Zoho-oauthtoken <token>` — montado pela conta conectada, não por parâmetro de operação.

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://analyticsapi.zoho.<>seu-datacenter</>` |
| Porta | 443 |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Access Token | {{access_token}} |
| Refresh Token | {{refresh_token}} |
| Endpoint de troca de token | `https://accounts.zoho.com/oauth/v2/token` |

> **O datacenter faz parte do Host.** Substitua `<>seu-datacenter</>` pelo TLD da sua conta: `com`, `eu`, `in`, `com.au`, `jp`, `ca` ou `sa`. Uma conta do datacenter europeu não responde em `analyticsapi.zoho.com`. O endpoint de troca de token acompanha o mesmo datacenter — use `https://accounts.zoho.eu/oauth/v2/token` para o DC europeu, e assim por diante.

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

### Descobrindo o `ZANALYTICS-ORGID` e os IDs

Comece por **Organization - Get organizations** — é a única operação que não depende de nenhum ID além do da própria organização, e a resposta traz o `orgId` de cada organização acessível. Com ele em mãos, **Workspaces - Get all workspaces** devolve os `workspace_id` e **Views - Get Views** os `view_id` de cada workspace. Colunas, pastas, tags, variáveis e fórmulas seguem o mesmo caminho: a operação de listagem do recurso devolve o ID que as demais pedem.

### Escopos OAuth necessários

Os escopos vão no parâmetro `scope` da URL de autorização, separados por vírgula. As 176 operações deste módulo exigem, somadas, **23 escopos distintos** — o conjunto abaixo é a união exata:

| Família | Escopos | Cobre |
| ------- | ------- | ----- |
| `ZohoAnalytics.metadata` | `.read`, `.create`, `.update` | workspaces, views, pastas, tags, slides, lixeira, favoritos, metadados e assinatura |
| `ZohoAnalytics.modeling` | `.read`, `.create`, `.update`, `.delete` | tabelas, colunas, fórmulas, tabelas de consulta, relatórios, variáveis e autoanálise |
| `ZohoAnalytics.data` | `.read`, `.create`, `.update`, `.delete` | importação e exportação (síncrona e em massa) e linhas de tabela |
| `ZohoAnalytics.share` | `.read`, `.create`, `.update`, `.delete` | compartilhamento de views, administradores do workspace e domínios white label |
| `ZohoAnalytics.embed` | `.read`, `.create`, `.update`, `.delete` | publicação: URL pública, private link, embed e configurações |
| `ZohoAnalytics.usermanagement` | `.read`, `.create`, `.update`, `.delete` | usuários e grupos da organização e do workspace, papéis e status |

> **Conceda só o que for usar.** Quanto mais estreito o conjunto de escopos, menos permissiva precisa ser a aplicação OAuth. Um fluxo que só lê dados de relatórios resolve com `ZohoAnalytics.data.read,ZohoAnalytics.metadata.read` — não é preciso autorizar os 23.

---

## Convenções deste conector

- **A versão da API é um parâmetro.** Todo caminho começa em `restapi/<>version</>`, com `v2` como valor. O Host da conta conectada é apenas a origem, sem versão embutida — falar com uma versão futura é trocar o valor do parâmetro, não criar outra conta conectada.
- **`ZANALYTICS-ORGID` é obrigatório em 145 das 176 operações.** Ele é um cabeçalho, declarado como parâmetro `zanalytics_orgid` em cada operação que o exige. As operações que não pedem são as que não dependem de contexto de organização, como **Organization - Get organizations**.
- **`CONFIG` na query (`config`) e `CONFIG` no corpo (`body`).** Nos `GET`, o parâmetro `config` é o JSON de configuração que vai na query string, sob a chave `CONFIG`. Nas escritas, o parâmetro `body` é o corpo `form-urlencoded` **completo**, no formato `CONFIG={…}` — e a operação já declara `Content-Type: application/x-www-form-urlencoded`. Cada operação traz um exemplo real extraído da especificação oficial; use-o como ponto de partida.
- **Duas operações usam JSON puro.** **Data - Sort Data by Columns** e **Views - Auto Analyse View** recebem `application/json`, sem envelope `CONFIG`. O `Content-Type` correspondente já está declarado nelas.
- **Importação de arquivo é multipart.** As quatro operações de **Bulk Data** que criam job de importação enviam o arquivo no campo `FILE`: informe o conteúdo em **base64** no parâmetro `file_content`, o MIME em `content_type` (`text/csv`, `application/json`) e o nome em `file_name`, e marque **"Forçar bufferização da requisição"** na operação — sem isso o corpo é truncado.
- **A importação síncrona envia texto, não arquivo.** **Data - Import Data into a New Table** e **Data - Import Data into an Existing Table** usam o campo `DATA` do multipart, com o CSV ou o JSON em texto puro no parâmetro `data`. Para enviar um arquivo binário nesses dois endpoints, troque a linha do corpo por `FILE:<>file_content</>:mime:<>content_type</>:<>file_name</>`, como nas operações de **Bulk Data**.
- **Jobs assíncronos exigem laço de consulta.** Depois de **Bulk Data - Create Import/Export Job**, consulte **Get Import/Export Job Details** com o `job_id` até o `JOBCODE` chegar a `1004` (concluído); `1001` e `1002` pedem nova tentativa, `1003` é erro e `1005` indica `job_id` inválido. O resultado fica disponível por **1 hora** e há limite de **5 jobs simultâneos** por organização.
- **Critérios de filtro usam a sintaxe SQL da Zoho.** Dentro do `CONFIG`, o campo `criteria` recebe expressões como `"Vendas"."Regiao"='Sul'` — nome de tabela e de coluna entre aspas duplas, valor entre aspas simples.

---

## Limitações conhecidas

- **A API v1 não está no conector.** A v1 usa outro formato de caminho (`/api/{e-mail}/{workspace}/{view}` com `ZOHO_ACTION` na query) e não é compatível com as operações deste módulo. O parâmetro `version` existe para versões futuras da API REST, não para acessar a v1.
- **Um único parâmetro de corpo por operação.** Como a API concentra tudo em `CONFIG`, os campos não são parametrizados individualmente: o corpo é um texto único. A descrição e o exemplo de cada operação mostram a estrutura esperada; os campos opcionais estão na documentação oficial de cada endpoint.
- **Cópia entre organizações usa um segundo cabeçalho.** **Views - Copy Views** e **Formulas - Copy Formulas** exigem `ZANALYTICS-DEST-ORGID` (parâmetro `zanalytics_dest_orgid`), o ID da organização de destino. Na cópia dentro da mesma organização, repita o valor de `zanalytics_orgid`. **Workspaces - Copy Workspace** também aceita esse cabeçalho, mas a especificação oficial o marca como opcional e ele **não** foi emitido na operação — se a sua cópia for para outra organização, acrescente-o manualmente.
- **Download de dados exportados devolve conteúdo binário.** **Bulk Data - Download Exported Data** responde com o arquivo, não com JSON; trate a resposta como conteúdo no fluxo do Studio.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **AutoML - Get AutoML Analysis In Org** | GET | Retorna todas as análises de AutoML disponíveis na organização. |
| **AutoML - Get AutoML Analysis In Workspace** | GET | Retorna a lista de análises de AutoML do workspace informado. |
| **AutoML - Create AutoML Analysis** | POST | Cria uma nova análise de AutoML no workspace informado. |
| **AutoML - Get AutoML Analysis Details** | GET | Recupera as informações detalhadas de uma análise de AutoML específica. |
| **AutoML - Delete AutoML Analysis** | DELETE | Exclui a análise de AutoML informada do workspace. |
| **AutoML - Delete AutoML Analysis Model Deployment** | DELETE | Exclui um deployment de análise de AutoML. |
| **AutoML - Run AutoML Analysis** | POST | Executa um deployment de análise de AutoML. |
| **AutoML - Delete AutoML Analysis Model** | DELETE | Exclui um modelo específico de uma análise de AutoML. |
| **AutoML - Get Deployments For A Model** | GET | Retorna os detalhes dos deployments disponíveis para um modelo de análise de AutoML. |
| **AutoML - Create AutoML Analysis Deployment** | POST | Cria um deployment para um modelo de análise de AutoML. |
| **AutoML - AutoML What If Analysis** | POST | Gera previsões usando um modelo de AutoML ja treinado. |
| **Bulk Data - Create Export Job using SQL Query (Asynchronous)** | GET | Cria um job de exportação a partir de uma consulta SQL SELECT, iniciando a exportação de dados de forma assíncrona. |
| **Bulk Data - Create Import Job for a New Table (Asynchronous)** | POST | Cria um job de importação de dados para uma nova tabela, de forma assíncrona. O arquivo pode ter no máximo 100 MB. |
| **Bulk Data - Batch Import Data into New Table** | POST | Inicia um job de importação que cria uma nova tabela e importa os dados em lotes. |
| **Bulk Data - Get Export Job Details** | GET | Retorna os detalhes do job de exportação assíncrono informado. |
| **Bulk Data - Download Exported Data** | GET | Baixa os dados do job de exportação em massa. |
| **Bulk Data - Get Import Job Details** | GET | Retorna os detalhes do job de importação assíncrono informado. |
| **Bulk Data - Create Export Job using View ID (Asynchronous)** | GET | Cria um job de exportação para iniciar a exportação dos dados da visualização informada, de forma assíncrona. |
| **Bulk Data - Create Import Job for an Existing Table (Asynchronous)** | POST | Cria um job de importação de dados para uma tabela existente, de forma assíncrona. |
| **Bulk Data - Batch Import Data into Existing Table** | POST | Inicia um job de importação que carrega, em lotes, os dados de vários arquivos para a tabela existente informada. |
| **Views - Get Dashboards** | GET | Retorna a lista de todos os dashboards acessíveis. |
| **Views - Get Owned Dashboards** | GET | Retorna a lista de dashboards de propriedade do usuário autenticado. |
| **Views - Get Shared Dashboards** | GET | Retorna a lista de dashboards compartilhados com o usuário autenticado. |
| **Workspaces - Get Meta Details** | GET | Retorna os detalhes de metadados do workspace ou da visualização informada. |
| **Organization - Get Org Admins** | GET | Retorna a lista de administradores da organização informada. |
| **Organization - Get organizations** | GET | Recupera a lista de organizações acessíveis ao usuário autenticado. |
| **Organization - Get Custom Roles** | GET | Retorna a lista de papéis personalizados da organização informada. |
| **Organization - Create Custom Role** | POST | Cria um novo papel personalizado na organização informada. |
| **Organization - Update Custom Role** | PUT | Atualiza um papel personalizado existente na organização informada. |
| **Organization - Delete Custom Role** | DELETE | Exclui da organização o papel personalizado informado. |
| **Views - Get Recent Views** | GET | Retorna a lista de visualizações acessadas recentemente. |
| **Workspaces - Get Resource Details** | GET | Retorna os detalhes de uso de recursos da organização informada. |
| **Workspaces - Get Subscription Details** | GET | Retorna os detalhes da assinatura da organização informada. |
| **Organization - Get Users** | GET | Retorna a lista de usuários da organização informada. |
| **Organization - Add Users** | POST | Adiciona usuários a organização informada. |
| **Organization - Remove Users** | DELETE | Remove usuários da organização informada. |
| **Organization - Activate Users** | PUT | Ativa usuários na organização informada. |
| **Organization - Deactivate Users** | PUT | Desativa usuários na organização informada. |
| **Organization - Change User Role** | PUT | Altera o papel dos usuários informados. |
| **Views - Get View Details** | GET | Retorna os detalhes da visualização informada. |
| **Workspaces - Get all workspaces** | GET | Recupera a lista de todos os workspaces acessíveis ao usuário autenticado. |
| **Workspaces - Create Workspace** | POST | Cria um workspace em branco na organização informada. |
| **Workspaces - Get owned workspaces** | GET | Recupera a lista de workspaces de propriedade do usuário autenticado. |
| **Workspaces - Get shared workspaces** | GET | Recupera a lista de workspaces compartilhados com o usuário autenticado. |
| **Views - Copy Views** | POST | Copia as visualizações informadas de um workspace para outro. |
| **Workspaces - Get Workspace Details** | GET | Retorna os detalhes do workspace informado. |
| **Workspaces - Copy Workspace** | POST | Copia o workspace informado para outra organização ou para a mesma organização. |
| **Workspaces - Rename Workspace** | PUT | Renomeia o workspace informado. |
| **Workspaces - Delete Workspace** | DELETE | Exclui o workspace informado. |
| **Sharing - Get Workspace Admins** | GET | Retorna a lista de administradores do workspace informado. |
| **Sharing - Add Workspace Admins** | POST | Adiciona administradores ao workspace informado. |
| **Sharing - Remove Workspace Admins** | DELETE | Remove administradores do workspace informado. |
| **Formulas - Get Aggregate Formulas In Workspace** | GET | Retorna a lista de todas as fórmulas agregadas do workspace informado. |
| **Formulas - Get Aggregate Formula Dependents** | GET | Retorna a lista de visualizações e fórmulas dependentes da fórmula agregada informada. |
| **Formulas - Get Aggregate Formula Value** | GET | Retorna o valor da fórmula agregada. |
| **Data - Import Data into a New Table (Synchronous)** | POST | Cria uma nova tabela e importa dados para ela de forma síncrona. |
| **Data Sources - Update Datasource Connection** | PUT | Atualiza os dados de conexão da fonte de dados da visualização informada. |
| **Data Sources - Sync Data** | POST | Dispara uma sincronização manual de dados da fonte de dados da visualização informada. |
| **Workspaces - Add Default Workspace** | POST | Define o workspace informado como workspace padrão. |
| **Workspaces - Remove Default Workspace** | DELETE | Remove a marcação de workspace padrão do workspace informado. |
| **Email Schedules - Get Email Schedules** | GET | Retorna a lista de agendamentos de e-mail disponíveis no workspace informado. |
| **Workspaces - Add Favorite Workspace** | POST | Marca o workspace informado como favorito. |
| **Workspaces - Remove Favorite Workspace** | DELETE | Remove o workspace informado dos favoritos. |
| **Folders - Get Folders** | GET | Retorna a lista de pastas do workspace informado. |
| **Folders - Create Folder** | POST | Cria uma pasta no workspace informado para organizar as visualizações. |
| **Folders - Rename Folder** | PUT | Renomeia uma pasta existente do workspace. |
| **Folders - Delete Folder** | DELETE | Exclui uma pasta do workspace. |
| **Folders - Make Default Folder** | POST | Define a pasta informada como pasta padrão para um tipo de visualização. |
| **Folders - Change Folder Hierarchy** | PUT | Atualiza a hierarquia da pasta, definindo sua pasta pai quando necessário. |
| **Folders - Change Folder Position** | PUT | Reordena a pasta, movendo-a em relação a outra pasta. |
| **Workspace Users - Get Groups** | GET | Retorna a lista de grupos do workspace informado. |
| **Workspace Users - Create Group** | POST | Cria um grupo no workspace informado. |
| **Workspace Users - Get Group Details** | GET | Retorna os detalhes do grupo informado. |
| **Workspace Users - Rename Group** | PUT | Renomeia o grupo informado. |
| **Workspace Users - Delete Group** | DELETE | Exclui o grupo informado. |
| **Workspace Users - Add Group Members** | POST | Adiciona usuários ao grupo informado. |
| **Workspace Users - Remove Group Members** | DELETE | Remove usuários do grupo informado. |
| **Tables - Get Query Tables** | GET | Retorna a lista de tabelas de consulta do workspace informado. |
| **Tables - Create Query Table** | POST | Cria uma tabela de consulta a partir de uma consulta SQL SELECT. |
| **Tables - Get QueryTable Details** | GET | Retorna os detalhes da tabela de consulta informada. |
| **Tables - Edit Query Table** | PUT | Atualiza uma tabela de consulta existente a partir de uma consulta SQL SELECT. |
| **Reports - Create Report** | POST | Cria um relatório (gráfico, tabela ou pivot) no workspace informado. |
| **Reports - Update Report** | PUT | Atualiza os metadados ou o desenho de um relatório existente. |
| **Workspaces - Get Workspace Secret Key** | GET | Retorna a chave secreta do workspace informado. |
| **Sharing - Get Workspace Shared Details** | GET | Retorna os detalhes de compartilhamento de todas as visualizações do workspace informado. |
| **Sharing - Get Shared Details For Views** | GET | Retorna os detalhes de compartilhamento das visualizações informadas. |
| **Slides - Get Slideshows** | GET | Retorna a lista de apresentações de slides do workspace informado. |
| **Slides - Create Slideshow** | POST | Cria uma apresentação de slides no workspace informado. |
| **Slides - Get Slideshow Details** | GET | Retorna os detalhes da apresentação de slides informada. |
| **Slides - Update Slideshow** | PUT | Atualiza os detalhes da apresentação de slides informada. |
| **Slides - Delete Slideshow** | DELETE | Exclui a apresentação de slides informada do workspace. |
| **Slides - Get Slideshow URL** | GET | Retorna a URL da apresentação de slides informada. |
| **Tables - Create Table** | POST | Cria uma tabela no workspace informado. |
| **Tags - Get Tags List** | GET | Retorna a lista de tags do workspace informado. |
| **Tags - Create Tag** | POST | Cria uma nova tag no workspace informado. |
| **Tags - Update Tag** | PUT | Atualiza a tag informada. |
| **Tags - Delete Tag** | DELETE | Exclui do workspace a tag informada. |
| **Tags - Get Tagged Views** | GET | Retorna a lista de visualizações associadas a tag informada. |
| **Tags - Add Tag To Multiple Views** | POST | Associa a tag informada a várias visualizações. |
| **Tags - Remove Tag From Multiple Views** | DELETE | Remove a tag informada de várias visualizações. |
| **Workspaces - Export as Template** | GET | Exporta o workspace informado como template. |
| **Workspaces - Get Trash Views** | GET | Retorna a lista de visualizações que estão na lixeira do workspace informado. |
| **Workspaces - Restore Trash View** | POST | Restaura uma visualização a partir da lixeira. |
| **Workspaces - Delete Trash View** | DELETE | Exclui definitivamente uma visualização da lixeira. |
| **Workspace Users - Get Workspace Users** | GET | Retorna a lista de usuários do workspace informado. |
| **Workspace Users - Add Workspace Users** | POST | Adiciona usuários ao workspace informado. |
| **Workspace Users - Delete Workspace Users** | DELETE | Remove usuários do workspace informado. |
| **Workspace Users - Change Workspace Users Role** | PUT | Atualiza o papel dos usuários no workspace do Zoho Analytics. |
| **Workspace Users - Change Workspace Users Status** | PUT | Atualiza o status de ativação dos usuários no workspace do Zoho Analytics. |
| **Variables - Get all variables in a workspace** | GET | Recupera a lista de todas as variáveis criadas no workspace informado. |
| **Variables - Create a variable** | POST | Cria uma nova variável no workspace informado a partir do JSON de CONFIG. |
| **Variables - Get details of a specific variable** | GET | Retorna os metadados e a configuração de uma variável do workspace pelo seu ID. |
| **Variables - Update a variable** | PUT | Atualiza uma variável existente do workspace informado a partir do JSON de CONFIG. |
| **Variables - Delete a variable** | DELETE | Exclui do workspace a variável informada. |
| **Views - Get Views** | GET | Retorna a lista de visualizações do workspace informado. |
| **Views - Move Views To Folder** | PUT | Move várias visualizações para a pasta informada. |
| **Sharing - Share Views** | POST | Compartilha as visualizações informadas do workspace com usuários ou grupos, com as permissões selecionadas. |
| **Sharing - Update Shared Details For View** | PUT | Atualiza a configuração de compartilhamento existente de uma visualização. |
| **Sharing - Remove Share** | DELETE | Remove o compartilhamento da visualização para os usuários ou grupos informados. |
| **Views - Rename View** | PUT | Renomeia uma visualização existente. |
| **Views - Delete View** | DELETE | Move a visualização para a lixeira. |
| **Formulas - Get Aggregate Formula List** | GET | Retorna a lista de todas as fórmulas agregadas da tabela informada. |
| **Formulas - Add Aggregate Formula** | POST | Adiciona uma coluna de fórmula agregada a visualização informada. |
| **Formulas - Edit Aggregate Formula** | PUT | Atualiza uma coluna de fórmula agregada existente na visualização. |
| **Formulas - Delete Aggregate Formula** | DELETE | Exclui uma coluna de fórmula agregada da visualização informada. |
| **Views - Auto Analyse View** | POST | Gera relatórios automaticamente para a tabela informada. |
| **Columns - Add Column** | POST | Adiciona uma nova coluna a visualização informada. |
| **Columns - Hide Columns** | PUT | Oculta as colunas informadas em uma visualização. |
| **Columns - Reorder Columns** | PUT | Atualiza a ordem das colunas da tabela. |
| **Columns - Show Columns** | PUT | Exibe as colunas ocultas informadas em uma visualização. |
| **Columns - Rename Column** | PUT | Renomeia uma coluna. |
| **Columns - Delete Column** | DELETE | Exclui de uma visualização a coluna informada. |
| **Columns - Auto Analyse Column** | POST | Gera relatórios automaticamente para a coluna informada. |
| **Columns - Get Column Dependents** | GET | Retorna as visualizações e fórmulas dependentes da coluna informada. |
| **Columns - Add Lookup** | POST | Adiciona uma relação de lookup a uma coluna. |
| **Columns - Remove Lookup** | DELETE | Remove a relação de lookup de uma coluna. |
| **Formulas - Get Custom Formula List** | GET | Retorna a lista de todas as colunas de fórmula da tabela informada. |
| **Formulas - Add Formula Column** | POST | Adiciona uma nova coluna de fórmula a visualização informada. |
| **Formulas - Edit Formula Column** | PUT | Atualiza uma coluna de fórmula existente na visualização. |
| **Formulas - Delete Formula Column** | DELETE | Exclui uma coluna de fórmula da visualização informada. |
| **Data - Export Data from a View (Synchronous)** | GET | Exporta os dados da visualização informada de forma síncrona. |
| **Data - Import Data into an Existing Table (Synchronous)** | POST | Importa dados para a tabela existente informada de forma síncrona. |
| **Data - Sort Data by Columns** | PUT | Ordena os dados da tabela pelas colunas informadas. |
| **Views - Get Datasources** | GET | Retorna as fontes de dados da visualização informada. |
| **Views - Get View Dependents** | GET | Retorna as visualizações dependentes da visualização informada. |
| **Email Schedules - Create Email Schedule** | POST | Cria um agendamento de e-mail para uma visualização. |
| **Email Schedules - Update Email Schedule** | PUT | Atualiza um agendamento de e-mail existente. |
| **Email Schedules - Delete Email Schedule** | DELETE | Exclui o agendamento de e-mail informado. |
| **Email Schedules - Change Email Schedule Status** | PUT | Ativa ou desativa o agendamento de e-mail informado. |
| **Email Schedules - Trigger Email Schedule** | POST | Dispara manualmente o agendamento de e-mail informado. |
| **Views - Add Favorite View** | POST | Marca a visualização informada como favorita. |
| **Views - Remove Favorite View** | DELETE | Remove a visualização informada dos favoritos. |
| **Formulas - Copy Formulas** | POST | Copia as fórmulas informadas de uma tabela para outra, inclusive entre workspaces. |
| **Views - Get Last Import Details** | GET | Retorna os detalhes da última importação de dados da visualização informada. |
| **Views - Get Table Metadata** | GET | Retorna os metadados da tabela informada, como as colunas disponíveis e seus atributos. |
| **Publishing - Get View URL** | GET | Retorna a URL de acesso a visualização informada. |
| **Publishing - Get Publish Configurations** | GET | Retorna as configurações de publicação da visualização informada. |
| **Publishing - Update Publish Configurations** | PUT | Atualiza as configurações de publicação da visualização informada. |
| **Publishing - Get Embed URL** | GET | Retorna a URL de incorporação (embed) da visualização informada. |
| **Publishing - Get Private URL** | GET | Retorna a URL privada de acesso a visualização informada. |
| **Publishing - Create Private URL** | POST | Cria uma URL privada para a visualização informada. |
| **Publishing - Remove Private Access** | DELETE | Remove o acesso por link privado da visualização informada. |
| **Publishing - Make Views Public** | POST | Torna a visualização informada publicamente acessível. |
| **Publishing - Remove Public Permission** | DELETE | Remove a permissão de acesso público da visualização informada. |
| **Data - Add Row** | POST | Adiciona uma linha a tabela informada. |
| **Data - Update Rows** | PUT | Atualiza linhas da tabela informada. |
| **Data - Delete Row** | DELETE | Exclui linhas da tabela informada. |
| **Views - Save As View** | POST | Cria uma nova visualização duplicando uma existente. |
| **Sharing - Get My Permissions** | GET | Retorna as permissões do usuário autenticado sobre a visualização informada. |
| **Views - Create Similar Views** | POST | Cria relatórios para a tabela informada com base em uma tabela de referência. |
| **Views - Refetch Data** | POST | Busca novamente os dados na origem da visualização informada. |
| **Tags - Get View Tags** | GET | Retorna a lista de tags associadas a visualização informada. |
| **Tags - Add Multiple Tags To View** | POST | Associa várias tags a visualização informada. |
| **Tags - Remove Multiple Tags From View** | DELETE | Remove várias tags da visualização informada. |
| **Sharing - Enable Domain Workspace** | POST | Habilita o acesso ao workspace para o domínio white label informado. |
| **Sharing - Disable Domain Workspace** | DELETE | Desabilita o acesso ao workspace para o domínio white label informado. |

---

## Documentação oficial

- [Zoho Analytics API v2](https://www.zoho.com/analytics/api/v2/introduction.html)
- [Autenticação e escopos OAuth do Zoho Analytics](https://www.zoho.com/analytics/api/v2/authentication.html)
- [Especificação OpenAPI oficial](https://github.com/zoho/analytics-oas)
