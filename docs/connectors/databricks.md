# Databricks

## Contexto

A API REST do **Databricks Workspace** expõe operações de nível de workspace para administrar e automatizar recursos da plataforma de dados unificada: clusters Spark, jobs, pipelines Delta Live Tables, SQL warehouses, Unity Catalog (catálogos, schemas, tabelas, volumes, grants), MLflow (experimentos, modelos registrados), Lakeflow, secrets, identidade (usuários, grupos, service principals), DBFS, repos Git, vector search, serving endpoints, entre outros.

As requisições usam a URL base do workspace (por exemplo `https://{workspace-id}.cloud.databricks.com`) e paths sob `/api/2.0/` ou `/api/2.1/`, conforme cada operação. A autenticação é feita com 

---

## Autenticação

**Tipo:** Bearer Token

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| host | {{host}} |
| token | {{token}} |
| porta | 443 |

O **host** é a URL do workspace Databricks (ex.: `https://dbc-a1b2345c-d6e7.cloud.databricks.com`)

O **token** é o access token da plataforma, para obter:

1. No seu workspace, clique na foto de perfil
2. Acesse **Settings**
3. Em Settings, acesse a seção **Developer**
4. Em **Access Tokens**, clique em Manage
5. Em **Generate new token**, crie um token com os escopos necess�rios que planeja usar no Skyone Studio
6. Insira o token gerado na conta do Skyone Studio.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Clusters - List** | **GET** | Lista todos os clusters ativos e encerrados nos últimos 30 dias |
| **Clusters - Get** | **GET** | Retorna informações de um cluster pelo seu ID |
| **Clusters - Create** | **POST** | Cria um novo cluster Spark |
| **Clusters - Start** | **POST** | Inicia um cluster existente que está parado |
| **Clusters - Restart** | **POST** | Reinicia um cluster em execução |
| **Clusters - Delete** | **POST** | Termina permanentemente um cluster |
| **Clusters - Edit** | **POST** | Edita a configuração de um cluster existente |
| **Clusters - Resize** | **POST** | Redimensiona o número de workers de um cluster |
| **Clusters - Pin** | **POST** | Fixa um cluster na lista para não ser removido após 30 dias |
| **Clusters - Unpin** | **POST** | Remove a fixação de um cluster |
| **Clusters - List Events** | **POST** | Lista o histórico de eventos de atividade de um cluster |
| **Clusters - List Spark Versions** | **GET** | Lista todas as versões Spark disponíveis |
| **Clusters - List Node Types** | **GET** | Lista todos os tipos de instância disponíveis para clusters |
| **Clusters - Get Permissions** | **GET** | Retorna as permissões de um cluster |
| **Clusters - Set Permissions** | **PUT** | Define as permissões de um cluster |
| **Clusters - Update Permissions** | **PATCH** | Atualiza parcialmente as permissões de um cluster |
| **Cluster Policies - List** | **GET** | Lista todas as políticas de cluster disponíveis |
| **Cluster Policies - Get** | **GET** | Retorna detalhes de uma política de cluster pelo ID |
| **Cluster Policies - Create** | **POST** | Cria uma nova política de cluster |
| **Cluster Policies - Edit** | **POST** | Atualiza uma política de cluster existente |
| **Cluster Policies - Delete** | **POST** | Remove uma política de cluster |
| **Instance Pools - List** | **GET** | Lista todos os pools de instâncias do workspace |
| **Instance Pools - Get** | **GET** | Retorna informações de um pool de instâncias pelo ID |
| **Instance Pools - Create** | **POST** | Cria um novo pool de instâncias |
| **Instance Pools - Edit** | **POST** | Edita um pool de instâncias existente |
| **Instance Pools - Delete** | **POST** | Remove um pool de instâncias |
| **Jobs - List** | **GET** | Lista todos os jobs do workspace com paginação |
| **Jobs - Get** | **GET** | Retorna detalhes de um job pelo ID |
| **Jobs - Create** | **POST** | Cria um novo job com as configurações fornecidas |
| **Jobs - Update** | **POST** | Atualiza parcialmente as configurações de um job |
| **Jobs - Reset** | **POST** | Substitui todas as configurações de um job (reset completo) |
| **Jobs - Delete** | **POST** | Remove permanentemente um job |
| **Jobs - Run Now** | **POST** | Dispara uma execução imediata de um job existente |
| **Jobs - Submit Run** | **POST** | Cria e dispara uma execução avulsa (one-time run) |
| **Jobs - List Runs** | **GET** | Lista as execuções de um job com filtros e paginação |
| **Jobs - Get Run** | **GET** | Retorna detalhes de uma execução específica de job |
| **Jobs - Get Run Output** | **GET** | Retorna a saída de uma task de execução de job |
| **Jobs - Export Run** | **GET** | Exporta e recupera resultados de uma execução de job |
| **Jobs - Cancel Run** | **POST** | Cancela uma execução em andamento de um job |
| **Jobs - Cancel All Runs** | **POST** | Cancela todas as execuções ativas de um job |
| **Jobs - Delete Run** | **POST** | Remove permanentemente uma execução de job |
| **Jobs - Repair Run** | **POST** | Reexecuta tasks falhas ou ignoradas em uma execução de job |
| **Pipelines - List** | **GET** | Lista todos os pipelines Spark Declarative do workspace |
| **Pipelines - Get** | **GET** | Retorna detalhes de um pipeline pelo ID |
| **Pipelines - Create** | **POST** | Cria um novo pipeline Spark Declarative |
| **Pipelines - Update** | **PUT** | Atualiza as configurações de um pipeline existente |
| **Pipelines - Delete** | **DELETE** | Remove permanentemente um pipeline |
| **Pipelines - Start Update** | **POST** | Inicia uma atualização de pipeline (execução) |
| **Pipelines - Get Update** | **GET** | Retorna o estado de uma atualização de pipeline |
| **Pipelines - List Updates** | **GET** | Lista as atualizações recentes de um pipeline |
| **Pipelines - Stop** | **POST** | Para a execução de um pipeline |
| **DBFS - Get Status** | **GET** | Retorna informações de um arquivo ou diretório no DBFS |
| **DBFS - List** | **GET** | Lista o conteúdo de um diretório no DBFS |
| **DBFS - Mkdirs** | **POST** | Cria um diretório e seus pais no DBFS |
| **DBFS - Create** | **POST** | Abre um stream de escrita para criar um arquivo no DBFS |
| **DBFS - Add Block** | **POST** | Adiciona um bloco de dados a um stream DBFS aberto |
| **DBFS - Close** | **POST** | Fecha um stream de escrita no DBFS |
| **DBFS - Put** | **POST** | Envia um arquivo pequeno diretamente para o DBFS |
| **DBFS - Read** | **GET** | Lê o conteúdo de um arquivo no DBFS (base64) |
| **DBFS - Delete** | **POST** | Remove um arquivo ou diretório do DBFS |
| **DBFS - Move** | **POST** | Move um arquivo ou diretório dentro do DBFS |
| **Files - Upload** | **PUT** | Envia um arquivo de até 5 GiB para um volume Unity Catalog |
| **Files - Download** | **GET** | Baixa o conteúdo de um arquivo de um volume Unity Catalog |
| **Files - Delete** | **DELETE** | Remove um arquivo de um volume Unity Catalog |
| **Files - List Directory** | **GET** | Lista o conteúdo de um diretório em um volume Unity Catalog |
| **Files - Create Directory** | **PUT** | Cria um diretório em um volume Unity Catalog |
| **Files - Delete Directory** | **DELETE** | Remove um diretório de um volume Unity Catalog |
| **Libraries - Cluster Status** | **GET** | Retorna o status das bibliotecas instaladas em um cluster |
| **Libraries - Install** | **POST** | Instala bibliotecas em um cluster |
| **Libraries - Uninstall** | **POST** | Desinstala bibliotecas de um cluster |
| **Libraries - All Cluster Statuses** | **GET** | Retorna o status de bibliotecas em todos os clusters ativos |
| **Experiments - List** | **GET** | Lista experimentos MLflow com filtros e paginação |
| **Experiments - Get** | **GET** | Retorna detalhes de um experimento pelo ID |
| **Experiments - Get by Name** | **GET** | Retorna detalhes de um experimento pelo nome |
| **Experiments - Create** | **POST** | Cria um novo experimento MLflow |
| **Experiments - Update** | **POST** | Atualiza nome ou artefatos de um experimento |
| **Experiments - Delete** | **POST** | Marca um experimento como deletado |
| **Experiments - Restore** | **POST** | Restaura um experimento deletado |
| **Experiments - Search** | **POST** | Busca experimentos por filtros e ordenação |
| **Experiments - Set Tag** | **POST** | Define uma tag em um experimento |
| **Experiments - Delete Runs by Time** | **POST** | Remove execuções criadas antes de uma data |
| **Experiments - Restore Runs by Time** | **POST** | Restaura execuções deletadas após uma data |
| **Runs - Create** | **POST** | Cria uma nova execução MLflow em um experimento |
| **Runs - Get** | **GET** | Retorna detalhes de uma execução MLflow |
| **Runs - Update** | **POST** | Atualiza status ou endtime de uma execução |
| **Runs - Delete** | **POST** | Marca uma execução como deletada |
| **Runs - Restore** | **POST** | Restaura uma execução deletada |
| **Runs - Search** | **POST** | Busca execuções por filtros MLflow |
| **Runs - Log Metric** | **POST** | Registra uma métrica em uma execução |
| **Runs - Log Param** | **POST** | Registra um parâmetro em uma execução |
| **Runs - Log Batch** | **POST** | Registra métricas, parâmetros e tags em lote |
| **Runs - Set Tag** | **POST** | Define uma tag em uma execução |
| **Runs - Delete Tag** | **POST** | Remove uma tag de uma execução |
| **Runs - Get Metric History** | **GET** | Retorna o histórico de uma métrica em uma execução |
| **Registered Models - List** | **GET** | Lista modelos registrados no Unity Catalog |
| **Registered Models - Get** | **GET** | Retorna detalhes de um modelo registrado pelo nome completo |
| **Registered Models - Create** | **POST** | Cria um modelo registrado no Unity Catalog |
| **Registered Models - Update** | **PATCH** | Atualiza metadados de um modelo registrado |
| **Registered Models - Delete** | **DELETE** | Remove um modelo registrado do Unity Catalog |
| **Registered Models - Set Alias** | **PUT** | Define um alias para uma versão de modelo registrado |
| **Registered Models - Delete Alias** | **DELETE** | Remove um alias de um modelo registrado |
| **Model Versions - List** | **GET** | Lista versões de um modelo registrado no Unity Catalog |
| **Model Versions - Get** | **GET** | Retorna detalhes de uma versão específica de modelo |
| **Model Versions - Get by Alias** | **GET** | Retorna uma versão de modelo por alias |
| **Model Versions - Update** | **PATCH** | Atualiza metadados de uma versão de modelo |
| **Model Versions - Delete** | **DELETE** | Remove uma versão de modelo registrado |
| **Serving Endpoints - List** | **GET** | Lista todos os endpoints de serving do workspace |
| **Serving Endpoints - Get** | **GET** | Retorna detalhes de um endpoint de serving pelo nome |
| **Serving Endpoints - Create** | **POST** | Cria um novo endpoint de serving de modelo |
| **Serving Endpoints - Update Config** | **PUT** | Atualiza a configuração de um endpoint de serving |
| **Serving Endpoints - Delete** | **DELETE** | Remove um endpoint de serving |
| **Serving Endpoints - Update AI Gateway** | **PUT** | Atualiza as configurações do AI Gateway de um endpoint |
| **Serving Endpoints - Get Metrics** | **GET** | Retorna métricas de uso de um endpoint de serving |
| **Serving Endpoints - Update Rate Limits** | **PATCH** | Atualiza limites de taxa de um endpoint de serving |
| **Serving Endpoints - Get Build Logs** | **GET** | Retorna logs de build de um modelo servido |
| **Serving Endpoints - Get Served Model Logs** | **GET** | Retorna os últimos logs de um modelo servido |
| **Serving Endpoints - Query** | **POST** | Envia uma requisição de inferência para um endpoint de serving |
| **Apps - List** | **GET** | Lista todos os apps Databricks do workspace |
| **Apps - Get** | **GET** | Retorna detalhes de um app pelo nome |
| **Apps - Create** | **POST** | Cria um novo app Databricks |
| **Apps - Update** | **PATCH** | Atualiza a configuração de um app existente |
| **Apps - Delete** | **DELETE** | Remove um app Databricks |
| **Apps - Create Deployment** | **POST** | Cria um novo deployment de app a partir do source code |
| **Apps - Get Deployment** | **GET** | Retorna o estado de um deployment de app |
| **Vector Search Endpoints - List** | **GET** | Lista todos os endpoints de Vector Search |
| **Vector Search Endpoints - Get** | **GET** | Retorna detalhes de um endpoint de Vector Search |
| **Vector Search Endpoints - Create** | **POST** | Cria um novo endpoint de Vector Search |
| **Vector Search Endpoints - Delete** | **DELETE** | Remove um endpoint de Vector Search |
| **Vector Search Endpoints - Get Metrics** | **GET** | Retorna métricas de uso de um endpoint de Vector Search |
| **Vector Search Indexes - List** | **GET** | Lista índices de Vector Search de um endpoint |
| **Vector Search Indexes - Get** | **GET** | Retorna detalhes de um índice de Vector Search |
| **Vector Search Indexes - Create** | **POST** | Cria um novo índice de Vector Search |
| **Vector Search Indexes - Delete** | **DELETE** | Remove um índice de Vector Search |
| **Vector Search Indexes - Upsert Data** | **POST** | Insere ou atualiza dados em um índice de Vector Search |
| **Vector Search Indexes - Delete Data** | **DELETE** | Remove dados de um índice de Vector Search por IDs |
| **Vector Search Indexes - Query** | **POST** | Executa uma busca por similaridade em um índice |
| **Vector Search Indexes - Sync** | **POST** | Dispara sincronização de um índice Delta Sync |
| **Users - List** | **GET** | Lista usuários do workspace via SCIM |
| **Users - Get** | **GET** | Retorna detalhes de um usuário pelo ID SCIM |
| **Users - Create** | **POST** | Cria um novo usuário no workspace |
| **Users - Replace** | **PUT** | Substitui completamente os atributos de um usuário |
| **Users - Update** | **PATCH** | Atualiza parcialmente os atributos de um usuário |
| **Users - Delete** | **DELETE** | Remove um usuário do workspace |
| **Groups - List** | **GET** | Lista grupos do workspace via SCIM |
| **Groups - Get** | **GET** | Retorna detalhes de um grupo pelo ID SCIM |
| **Groups - Create** | **POST** | Cria um novo grupo no workspace |
| **Groups - Replace** | **PUT** | Substitui completamente os atributos de um grupo |
| **Groups - Update** | **PATCH** | Atualiza parcialmente os atributos de um grupo |
| **Groups - Delete** | **DELETE** | Remove um grupo do workspace |
| **Service Principals - List** | **GET** | Lista service principals do workspace via SCIM |
| **Service Principals - Get** | **GET** | Retorna detalhes de um service principal pelo ID |
| **Service Principals - Create** | **POST** | Cria um novo service principal no workspace |
| **Service Principals - Replace** | **PUT** | Substitui completamente os atributos de um service principal |
| **Service Principals - Update** | **PATCH** | Atualiza parcialmente um service principal |
| **Service Principals - Delete** | **DELETE** | Remove um service principal do workspace |
| **Current User - Get** | **GET** | Retorna informações do usuário autenticado atual |
| **Permissions - Get** | **GET** | Retorna as permissões de um objeto (cluster, job, notebook, etc.) |
| **Permissions - Set** | **PUT** | Define as permissões de um objeto substituindo as existentes |
| **Permissions - Update** | **PATCH** | Atualiza parcialmente as permissões de um objeto |
| **Permissions - Get Permission Levels** | **GET** | Retorna os níveis de permissão disponíveis para um tipo de objeto |
| **Tokens - List** | **GET** | Lista os tokens de acesso pessoal do usuário |
| **Tokens - Create** | **POST** | Cria um novo token de acesso pessoal |
| **Tokens - Delete** | **POST** | Revoga um token de acesso pessoal |
| **Secrets - List Scopes** | **GET** | Lista todos os escopos de segredos do workspace |
| **Secrets - Create Scope** | **POST** | Cria um novo escopo de segredos |
| **Secrets - Delete Scope** | **POST** | Remove um escopo de segredos e todos seus segredos |
| **Secrets - List** | **GET** | Lista os segredos em um escopo (sem revelar os valores) |
| **Secrets - Put** | **POST** | Cria ou atualiza um segredo em um escopo |
| **Secrets - Delete** | **POST** | Remove um segredo de um escopo |
| **Secrets - List ACLs** | **GET** | Lista as ACLs de acesso a um escopo de segredos |
| **Secrets - Get ACL** | **GET** | Retorna a ACL de um principal em um escopo de segredos |
| **Secrets - Put ACL** | **POST** | Cria ou substitui a ACL de um principal em um escopo |
| **Secrets - Delete ACL** | **POST** | Remove a ACL de um principal em um escopo de segredos |
| **SQL Warehouses - List** | **GET** | Lista todos os SQL warehouses do workspace |
| **SQL Warehouses - Get** | **GET** | Retorna detalhes de um SQL warehouse pelo ID |
| **SQL Warehouses - Create** | **POST** | Cria um novo SQL warehouse |
| **SQL Warehouses - Edit** | **POST** | Atualiza as configurações de um SQL warehouse |
| **SQL Warehouses - Delete** | **DELETE** | Remove um SQL warehouse |
| **SQL Warehouses - Start** | **POST** | Inicia um SQL warehouse parado |
| **SQL Warehouses - Stop** | **POST** | Para um SQL warehouse em execução |
| **SQL Warehouses - Get Workspace Config** | **GET** | Retorna a configuração SQL do workspace |
| **SQL Warehouses - Set Workspace Config** | **PUT** | Define a configuração SQL do workspace |
| **SQL Statement Execution - Execute** | **POST** | Executa um statement SQL em um warehouse |
| **SQL Statement Execution - Get Status** | **GET** | Retorna o status e resultado de um statement SQL |
| **SQL Statement Execution - Cancel** | **POST** | Cancela a execução de um statement SQL |
| **SQL Statement Execution - Get Result Chunk** | **GET** | Retorna um chunk específico do resultado de um statement |
| **SQL Alerts - List** | **GET** | Lista todos os alertas SQL do workspace |
| **SQL Alerts - Get** | **GET** | Retorna detalhes de um alerta SQL pelo ID |
| **SQL Alerts - Create** | **POST** | Cria um novo alerta SQL |
| **SQL Alerts - Update** | **PUT** | Atualiza um alerta SQL existente |
| **SQL Alerts - Delete** | **DELETE** | Remove um alerta SQL |
| **SQL Queries - List** | **GET** | Lista as queries SQL salvas do workspace |
| **SQL Queries - Get** | **GET** | Retorna detalhes de uma query SQL salva |
| **SQL Queries - Create** | **POST** | Cria uma nova query SQL |
| **SQL Queries - Update** | **PATCH** | Atualiza uma query SQL existente |
| **SQL Queries - Delete** | **DELETE** | Remove uma query SQL |
| **Lakeview Dashboards - List** | **GET** | Lista os dashboards AI/BI (Lakeview) do workspace |
| **Lakeview Dashboards - Get** | **GET** | Retorna detalhes de um dashboard AI/BI pelo ID |
| **Lakeview Dashboards - Create** | **POST** | Cria um novo dashboard AI/BI |
| **Lakeview Dashboards - Update** | **PATCH** | Atualiza um dashboard AI/BI existente |
| **Lakeview Dashboards - Delete** | **DELETE** | Remove um dashboard AI/BI |
| **Lakeview Dashboards - Publish** | **POST** | Publica um dashboard AI/BI para uso geral |
| **Catalogs - List** | **GET** | Lista catálogos do Unity Catalog acessíveis ao usuário |
| **Catalogs - Get** | **GET** | Retorna detalhes de um catálogo pelo nome |
| **Catalogs - Create** | **POST** | Cria um novo catálogo no Unity Catalog |
| **Catalogs - Update** | **PATCH** | Atualiza os metadados de um catálogo |
| **Catalogs - Delete** | **DELETE** | Remove um catálogo do Unity Catalog |
| **Schemas - List** | **GET** | Lista schemas de um catálogo no Unity Catalog |
| **Schemas - Get** | **GET** | Retorna detalhes de um schema pelo nome completo |
| **Schemas - Create** | **POST** | Cria um novo schema no Unity Catalog |
| **Schemas - Update** | **PATCH** | Atualiza os metadados de um schema |
| **Schemas - Delete** | **DELETE** | Remove um schema do Unity Catalog |
| **Tables - List** | **GET** | Lista tabelas de um schema no Unity Catalog |
| **Tables - Get** | **GET** | Retorna detalhes de uma tabela pelo nome completo |
| **Tables - Delete** | **DELETE** | Remove uma tabela do Unity Catalog |
| **Tables - Update** | **PATCH** | Atualiza os metadados de uma tabela no Unity Catalog |
| **Tables - Exists** | **GET** | Verifica se uma tabela existe no Unity Catalog |
| **Volumes - List** | **GET** | Lista volumes de um schema no Unity Catalog |
| **Volumes - Get** | **GET** | Retorna detalhes de um volume pelo nome completo |
| **Volumes - Create** | **POST** | Cria um novo volume no Unity Catalog |
| **Volumes - Update** | **PATCH** | Atualiza os metadados de um volume |
| **Volumes - Delete** | **DELETE** | Remove um volume do Unity Catalog |
| **Functions - List** | **GET** | Lista funções de um schema no Unity Catalog |
| **Functions - Get** | **GET** | Retorna detalhes de uma função pelo nome completo |
| **Functions - Create** | **POST** | Cria ou substitui uma função no Unity Catalog |
| **Functions - Delete** | **DELETE** | Remove uma função do Unity Catalog |
| **External Locations - List** | **GET** | Lista external locations do Unity Catalog |
| **External Locations - Get** | **GET** | Retorna detalhes de uma external location pelo nome |
| **External Locations - Create** | **POST** | Cria uma nova external location no Unity Catalog |
| **External Locations - Update** | **PATCH** | Atualiza uma external location |
| **External Locations - Delete** | **DELETE** | Remove uma external location do Unity Catalog |
| **Storage Credentials - List** | **GET** | Lista storage credentials do Unity Catalog |
| **Storage Credentials - Get** | **GET** | Retorna detalhes de uma storage credential pelo nome |
| **Storage Credentials - Create** | **POST** | Cria uma nova storage credential no Unity Catalog |
| **Storage Credentials - Update** | **PATCH** | Atualiza uma storage credential existente |
| **Storage Credentials - Delete** | **DELETE** | Remove uma storage credential do Unity Catalog |
| **Connections - List** | **GET** | Lista conexões externas do Unity Catalog |
| **Connections - Get** | **GET** | Retorna detalhes de uma conexão pelo nome |
| **Connections - Create** | **POST** | Cria uma nova conexão externa no Unity Catalog |
| **Connections - Update** | **PATCH** | Atualiza uma conexão externa |
| **Connections - Delete** | **DELETE** | Remove uma conexão externa do Unity Catalog |
| **Grants - Get** | **GET** | Retorna as permissões Unity Catalog para um objeto segurável |
| **Grants - Update** | **PATCH** | Concede ou revoga permissões Unity Catalog em um objeto |
| **Grants - Get Effective** | **GET** | Retorna as permissões efetivas (herdadas) de um objeto |
| **Metastores - List** | **GET** | Lista todos os metastores Unity Catalog acessíveis |
| **Metastores - Get Current** | **GET** | Retorna o metastore atribuído ao workspace atual |
| **Metastores - Get** | **GET** | Retorna detalhes de um metastore pelo ID |
| **Metastores - Create** | **POST** | Cria um novo metastore Unity Catalog |
| **Metastores - Update** | **PATCH** | Atualiza os metadados de um metastore |
| **Metastores - Delete** | **DELETE** | Remove um metastore Unity Catalog |
| **Metastores - Assign to Workspace** | **PUT** | Atribui um metastore a um workspace |
| **Online Tables - Get** | **GET** | Retorna detalhes de uma online table pelo nome |
| **Online Tables - Create** | **POST** | Cria uma online table a partir de uma tabela Delta existente |
| **Online Tables - Delete** | **DELETE** | Remove uma online table |
| **Delta Sharing - Shares List** | **GET** | Lista todos os shares Delta Sharing do metastore |
| **Delta Sharing - Shares Get** | **GET** | Retorna detalhes de um share pelo nome |
| **Delta Sharing - Shares Create** | **POST** | Cria um novo share Delta Sharing |
| **Delta Sharing - Shares Update** | **PATCH** | Atualiza os objetos ou metadados de um share |
| **Delta Sharing - Shares Delete** | **DELETE** | Remove um share Delta Sharing |
| **Delta Sharing - Recipients List** | **GET** | Lista recipientes Delta Sharing do metastore |
| **Delta Sharing - Recipients Get** | **GET** | Retorna detalhes de um recipiente pelo nome |
| **Delta Sharing - Recipients Create** | **POST** | Cria um novo recipiente Delta Sharing |
| **Delta Sharing - Recipients Update** | **PATCH** | Atualiza os metadados de um recipiente |
| **Delta Sharing - Recipients Delete** | **DELETE** | Remove um recipiente Delta Sharing |
| **Delta Sharing - Recipients Get Permissions** | **GET** | Retorna as permissões de compartilhamento de um recipiente |
| **Delta Sharing - Providers List** | **GET** | Lista provedores Delta Sharing do metastore |
| **Delta Sharing - Providers Get** | **GET** | Retorna detalhes de um provedor pelo nome |
| **Delta Sharing - Providers Create** | **POST** | Cria um novo provedor Delta Sharing |
| **Delta Sharing - Providers Update** | **PATCH** | Atualiza um provedor Delta Sharing |
| **Delta Sharing - Providers Delete** | **DELETE** | Remove um provedor Delta Sharing |
| **Delta Sharing - Providers List Shares** | **GET** | Lista os shares disponíveis de um provedor |
| **Quality Monitor - Get** | **GET** | Retorna detalhes do monitor de qualidade de uma tabela |
| **Quality Monitor - Create** | **POST** | Cria um monitor de qualidade de dados para uma tabela Delta |
| **Quality Monitor - Update** | **PUT** | Atualiza as configurações de um monitor de qualidade |
| **Quality Monitor - Delete** | **DELETE** | Remove um monitor de qualidade de uma tabela |
| **Quality Monitor - Run Refresh** | **POST** | Dispara uma atualização manual do monitor de qualidade |
| **Workspace - List** | **GET** | Lista objetos no workspace (notebooks, diretórios, libraries, repos) |
| **Workspace - Get Status** | **GET** | Retorna informações de um objeto do workspace |
| **Workspace - Mkdirs** | **POST** | Cria um diretório e todos os pais no workspace |
| **Workspace - Import** | **POST** | Importa um notebook ou diretório para o workspace |
| **Workspace - Export** | **GET** | Exporta o conteúdo de um notebook ou diretório do workspace |
| **Workspace - Delete** | **POST** | Remove um notebook ou diretório do workspace |
| **Repos - List** | **GET** | Lista repositórios Git do workspace |
| **Repos - Get** | **GET** | Retorna detalhes de um repo Git pelo ID |
| **Repos - Create** | **POST** | Adiciona um repositório Git ao workspace |
| **Repos - Update** | **PATCH** | Atualiza o branch/tag/commit de um repo Git |
| **Repos - Delete** | **DELETE** | Remove um repositório Git do workspace |
| **Git Credentials - List** | **GET** | Lista as credenciais Git configuradas pelo usuário |
| **Git Credentials - Get** | **GET** | Retorna uma credencial Git pelo ID |
| **Git Credentials - Create** | **POST** | Cria credenciais Git para o usuário atual |
| **Git Credentials - Update** | **PATCH** | Atualiza credenciais Git existentes |
| **Git Credentials - Delete** | **DELETE** | Remove credenciais Git pelo ID |
| **Global Init Scripts - List** | **GET** | Lista todos os global init scripts do workspace |
| **Global Init Scripts - Get** | **GET** | Retorna detalhes de um global init script pelo ID |
| **Global Init Scripts - Create** | **POST** | Cria um novo global init script |
| **Global Init Scripts - Update** | **PATCH** | Atualiza um global init script existente |
| **Global Init Scripts - Delete** | **DELETE** | Remove um global init script |
| **Instance Profiles - List** | **GET** | Lista instance profiles IAM disponíveis para clusters (AWS) |
| **Instance Profiles - Add** | **POST** | Adiciona um instance profile IAM ao Databricks (AWS) |
| **Instance Profiles - Edit** | **POST** | Edita um instance profile IAM |
| **Instance Profiles - Remove** | **POST** | Remove um instance profile IAM do Databricks |
| **IP Access Lists - List** | **GET** | Lista todas as regras de lista de acesso IP do workspace |
| **IP Access Lists - Get** | **GET** | Retorna uma regra de lista de acesso IP pelo ID |
| **IP Access Lists - Create** | **POST** | Cria uma nova regra de lista de acesso IP |
| **IP Access Lists - Replace** | **PUT** | Substitui completamente uma regra de lista de acesso IP |
| **IP Access Lists - Update** | **PATCH** | Atualiza parcialmente uma regra de lista de acesso IP |
| **IP Access Lists - Delete** | **DELETE** | Remove uma regra de lista de acesso IP |
| **Policy Families - List** | **GET** | Lista todas as famílias de políticas disponíveis no workspace |
| **Policy Families - Get** | **GET** | Retorna uma família de políticas pelo ID |
| **Service Principal Secrets - List** | **GET** | Lista os secrets de credenciais de um service principal |
| **Service Principal Secrets - Create** | **POST** | Cria um novo secret para um service principal |
| **Service Principal Secrets - Delete** | **DELETE** | Remove um secret de um service principal |
| **Workspace Settings - Get Config** | **GET** | Retorna as configurações do workspace (workspace-conf) |
| **Workspace Settings - Set Config** | **PATCH** | Atualiza configurações do workspace para auditoria e conformidade |
| **Clusters - Change Owner** | **POST** | Transfere a propriedade de um cluster para outro usuário (offboarding) |
| **Query History - List** | **GET** | Lista o histórico de queries SQL executadas no workspace (FinOps/auditoria) |
| **Notification Destinations - List** | **GET** | Lista os destinos de notificação configurados (PagerDuty, Slack, Teams, Webhook) |
| **Notification Destinations - Get** | **GET** | Retorna um destino de notificação pelo ID |
| **Notification Destinations - Create** | **POST** | Cria um novo destino de notificação (PagerDuty, Slack, Teams, Webhook) |
| **Notification Destinations - Update** | **PUT** | Atualiza um destino de notificação existente |
| **Notification Destinations - Delete** | **DELETE** | Remove um destino de notificação |
| **Pipelines - Get Events** | **GET** | Lista eventos de execução de um pipeline DLT para monitoramento |
| **Apps - Start** | **POST** | Inicia uma aplicação Databricks (para rotinas de ativamento por horário) |
| **Apps - Stop** | **POST** | Para uma aplicação Databricks (para economia de custos fora do horário comercial) |
| **Lakeview Dashboards - List Schedules** | **GET** | Lista os agendamentos de envio de um dashboard Lakeview |
| **Lakeview Dashboards - Create Schedule** | **POST** | Cria um agendamento de envio automático de dashboard por e-mail |
| **Lakeview Dashboards - Get Schedule** | **GET** | Retorna um agendamento de dashboard pelo ID |
| **Lakeview Dashboards - Update Schedule** | **PUT** | Atualiza um agendamento de dashboard existente |
| **Lakeview Dashboards - Delete Schedule** | **DELETE** | Remove um agendamento de dashboard |
| **Lakeview Dashboards - List Subscriptions** | **GET** | Lista as assinaturas de envio de um dashboard Lakeview |
| **Lakeview Dashboards - Create Subscription** | **POST** | Cria uma assinatura para envio automático de dashboard (relatórios gerenciais) |
| **Lakeview Dashboards - Delete Subscription** | **DELETE** | Remove uma assinatura de dashboard |
| **Logged Models - Get** | **GET** | Retorna um modelo registrado via MLflow run pelo ID |
| **Logged Models - Search** | **POST** | Busca modelos registrados via MLflow com filtros |
| **Logged Models - Update** | **PATCH** | Atualiza metadados de um modelo registrado via MLflow |
| **Logged Models - Delete** | **DELETE** | Remove um modelo registrado via MLflow |
| **Artifacts - List** | **GET** | Lista artefatos de uma run MLflow (modelos, datasets, outputs) |
| **Artifacts - Get** | **GET** | Faz download de um artefato de uma run MLflow pelo caminho |
| **Runs - Log Model** | **POST** | Registra um modelo treinado em uma run MLflow (MLOps CI/CD) |
| **Runs - Log Inputs** | **POST** | Registra datasets de entrada usados em uma run MLflow para rastreabilidade |
| **Catalog Workspace Bindings - Get** | **GET** | Retorna os workspaces vinculados a um catálogo Unity Catalog (isolamento de projetos) |
| **Catalog Workspace Bindings - Update** | **PATCH** | Atualiza os workspaces vinculados a um catálogo (ABAC / isolamento de projetos) |
| **UC Credentials - List** | **GET** | Lista as credenciais de serviço Unity Catalog para acesso a storages externos |
| **UC Credentials - Get** | **GET** | Retorna uma credencial Unity Catalog pelo nome |
| **UC Credentials - Create** | **POST** | Cria uma credencial Unity Catalog para acesso seguro a storage externo |
| **UC Credentials - Update** | **PATCH** | Atualiza uma credencial Unity Catalog existente |
| **UC Credentials - Delete** | **DELETE** | Remove uma credencial Unity Catalog |
| **Resource Quotas - List** | **GET** | Lista o uso de cotas de recursos Unity Catalog para controle de gastos |
| **Resource Quotas - Get** | **GET** | Retorna o uso de uma cota específica de recurso Unity Catalog |
| **Pipelines - Change Owner** | **POST** | Transfere a propriedade de um pipeline DLT (offboarding de funcionários) |
| **OAuth Federation Policies - List** | **GET** | Lista politicas de federacao OAuth de um service principal (M2M sem token de pessoa fisica) |
| **OAuth Federation Policies - Get** | **GET** | Retorna uma politica de federacao OAuth pelo ID |
| **OAuth Federation Policies - Create** | **POST** | Cria politica de federacao OAuth (IdP externo → service principal Databricks) |
| **OAuth Federation Policies - Update** | **PUT** | Atualiza uma politica de federacao OAuth existente |
| **OAuth Federation Policies - Delete** | **DELETE** | Remove uma politica de federacao OAuth |
| **OAuth Custom App Integrations - List** | **GET** | Lista integracoes de app OAuth customizadas na conta (M2M corporativo) |
| **OAuth Custom App Integrations - Get** | **GET** | Retorna uma integracao de app OAuth customizada pelo ID |
| **OAuth Custom App Integrations - Create** | **POST** | Cria integracao OAuth customizada para automacao M2M |
| **OAuth Custom App Integrations - Update** | **PATCH** | Atualiza uma integracao de app OAuth customizada |
| **OAuth Custom App Integrations - Delete** | **DELETE** | Remove uma integracao de app OAuth customizada |
| **OAuth Published App Integrations - List** | **GET** | Lista integracoes com apps publicados (Databricks partners OAuth) |

---

## Documentação oficial

https://docs.databricks.com/api/workspace/introduction
