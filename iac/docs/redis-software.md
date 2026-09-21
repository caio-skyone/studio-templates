# redis-software

## Contexto

A REST API do **Redis Software** (anteriormente Redis Enterprise Software) é a
interface administrativa de um cluster Redis autogerenciado — instalado on-premises,
em máquinas virtuais ou em containers. Ela automatiza tudo o que normalmente se faz
pela UI do Cluster Manager ou pelo `rladmin`: provisionar e configurar bancos de
dados, administrar o cluster e seus nós, controlar acesso e acompanhar o estado
operacional do ambiente.

Não confunda com a **Redis Cloud API** (serviço gerenciado, `api.redislabs.com`):
esta API roda dentro do seu próprio cluster, na porta **9443**, e usa Basic Auth.

Este conector cobre **76 operações** distribuídas em **28 domínios**:

- **Bancos de dados** — `Databases` (bdbs: CRUD completo, ações como flush e
  reset de senha, criação v1 e v2), `CRDBs` (bancos Active-Active geo-distribuídos),
  `CRDB Tasks` (acompanhamento e cancelamento das tarefas assíncronas de CRDB),
  `Migrations` (status de migração Replica Of), `Shards` (shards dos bancos) e
  `Modules` (módulos Redis instalados: Search, JSON, TimeSeries, Bloom).
- **Cluster e infraestrutura** — `Cluster` (informações e configurações gerais),
  `Nodes` (nós do cluster), `Bootstrap` (criação do cluster e adesão de novos nós),
  `Proxies` (proxies de conexão), `Services` (start/stop/restart de serviços
  opcionais), `Node Master Healthcheck` (conexão do nó com o primário),
  `Suffix` e `Suffixes` (sufixos DNS do cluster).
- **Segurança e acesso** — `Users` (usuários do Cluster Manager), `Roles` (papéis
  RBAC), `Redis ACLs` (listas de controle de acesso aplicadas aos bancos),
  `LDAP Mappings` (integração com diretórios corporativos) e `OCSP` (validação
  de revogação de certificados).
- **Observabilidade e operação** — `Actions` (tarefas assíncronas em andamento,
  v1 e v2), `Logs` (log de eventos do cluster), `Metrics Config` (configuração
  de métricas), `Diagnostics` (serviço de diagnóstico), `Job Scheduler`
  (agendador de jobs internos) e `Usage Report` (relatório de uso das bases,
  formato NDJSON).
- **Administração da plataforma** — `License` (consulta e instalação de licença),
  `CM Settings` (preferências da UI do Cluster Manager) e `JSON Schema`
  (schemas dos objetos da própria API, úteis para montar payloads).

*Fora de escopo neste conector:* os domínios `debuginfo` (`/v1/debuginfo/*`) e
`endpoints/stats` (`/v1/endpoints/stats`), ambos marcados como **deprecated** na
documentação oficial — o primeiro desde a versão 7.4.2 e o segundo desde a 7.22,
substituídos por endpoints de debug por recurso e pelo metrics stream engine v2,
respectivamente.

**Notas de uso:**

- Vários endpoints de escrita aceitam o parâmetro `dry_run`, que valida o payload
  sem aplicar a alteração — útil para conferir uma configuração antes de efetivá-la.
- Operações sobre CRDBs e boa parte das ações de banco retornam **tarefas
  assíncronas**: acompanhe o resultado pelos domínios `Actions` ou `CRDB Tasks`.
- O cluster usa certificados autoassinados por padrão. Se a conta conectada
  rejeitar o certificado, será necessário instalar um certificado confiável no
  cluster ou desabilitar a verificação SSL na conta.
- As operações `Services - Operate ...` são destrutivas: pare ou reinicie apenas
  serviços opcionais, nunca os essenciais do cluster.

---

## Autenticação

**Tipo:** Autenticação básica (HTTP Basic)

As credenciais são as de um usuário do Cluster Manager. O usuário `admin` tem
acesso a todos os endpoints; para acessos mais restritos, use RBAC com roles
dedicadas (domínio `Roles`) — um usuário sem permissão recebe `403 Forbidden`.

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://<>seu-cluster</>` |
| Porta | 9443 |
| password | {{api_token}} |
| username | {{account_email}} |

> A porta **9443** é obrigatória e não é o padrão HTTPS — ela precisa estar
> exposta ao tráfego de entrada no cluster. O `username` é o e-mail do usuário
> do Cluster Manager e o `password` é a senha desse usuário.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Actions - Get all actions (v1)** | **GET** | Lista todas as ações em execução no cluster (v1). |
| **Actions - Get all actions (v2)** | **GET** | Lista todas as ações em execução no cluster, incluindo import/export/backup (v2). |
| **Actions - Get action by id (v1)** | **GET** | Obtém detalhes de uma ação específica pelo uid (v1). |
| **Actions - Get action by id (v2)** | **GET** | Obtém detalhes de uma ação específica pelo uid (v2). |
| **Databases - Get all databases** | **GET** | Lista todos os bancos de dados do cluster. |
| **Databases - Get database** | **GET** | Obtém detalhes de um banco de dados específico. |
| **Databases - Update database** | **PUT** | Atualiza a configuração de um banco de dados existente. |
| **Databases - Update database and run action** | **PUT** | Atualiza configuração do banco de dados e executa uma ação adicional (ex.: flush, reset_admin_pass). |
| **Databases - Create database (v1)** | **POST** | Cria um novo banco de dados (v1). |
| **Databases - Create database (v2)** | **POST** | Cria um novo banco de dados, com plano de recuperação opcional (v2). |
| **Databases - Delete database** | **DELETE** | Exclui um banco de dados. |
| **Bootstrap - Get bootstrap status** | **GET** | Obtém o status de bootstrap do nó local. |
| **Bootstrap - Start bootstrap action** | **POST** | Inicia um processo de bootstrap (ex.: create_cluster, join_cluster). |
| **Cluster - Get cluster info** | **GET** | Obtém informações do cluster. |
| **Cluster - Update cluster settings** | **PUT** | Atualiza as configurações do cluster. |
| **CM Settings - Get UI settings** | **GET** | Obtém as configurações da UI do Cluster Manager. |
| **CM Settings - Update UI settings** | **PUT** | Atualiza as configurações da UI do Cluster Manager. |
| **CRDB Tasks - List tasks** | **GET** | Lista as tarefas de Active-Active em execução. |
| **CRDB Tasks - Get task status** | **GET** | Obtém o status de uma tarefa de Active-Active. |
| **CRDB Tasks - Cancel task** | **POST** | Cancela uma tarefa de Active-Active em execução. |
| **CRDBs - List Active-Active databases** | **GET** | Lista os bancos de dados Active-Active (CRDB) do cluster. |
| **CRDBs - Get Active-Active database** | **GET** | Obtém detalhes de um banco de dados Active-Active. |
| **CRDBs - Update Active-Active database** | **PATCH** | Atualiza um banco de dados Active-Active existente. |
| **CRDBs - Create Active-Active database** | **POST** | Cria um novo banco de dados Active-Active. |
| **CRDBs - Delete Active-Active database** | **DELETE** | Exclui um banco de dados Active-Active. |
| **Diagnostics - Get diagnostics configuration** | **GET** | Obtém a configuração do serviço de diagnóstico. |
| **Diagnostics - Update diagnostics configuration** | **PUT** | Atualiza a configuração do serviço de diagnóstico. |
| **Job Scheduler - Get job scheduler settings** | **GET** | Obtém as configurações do agendador de jobs. |
| **Job Scheduler - Update job scheduler settings** | **PUT** | Atualiza as configurações do agendador de jobs. |
| **JSON Schema - Get object schema** | **GET** | Obtém o schema JSON de um objeto da API (ex.: cluster, node, bdb). |
| **LDAP Mappings - List mappings** | **GET** | Lista todos os mapeamentos LDAP. |
| **LDAP Mappings - Get mapping** | **GET** | Obtém um mapeamento LDAP específico. |
| **LDAP Mappings - Update mapping** | **PUT** | Atualiza um mapeamento LDAP existente. |
| **LDAP Mappings - Create mapping** | **POST** | Cria um novo mapeamento LDAP. |
| **LDAP Mappings - Delete mapping** | **DELETE** | Exclui um mapeamento LDAP. |
| **License - Get license details** | **GET** | Obtém os detalhes da licença do cluster. |
| **License - Update license** | **PUT** | Atualiza ou instala a licença do cluster. |
| **Logs - Get cluster event log** | **GET** | Obtém o log de eventos do cluster. |
| **Metrics Config - Get metrics configuration** | **GET** | Obtém a configuração de métricas do cluster. |
| **Metrics Config - Update metrics configuration** | **PUT** | Atualiza a configuração de métricas do cluster. |
| **Migrations - Get migration status** | **GET** | Obtém o status de migração de um banco de dados (Replica Of). |
| **Modules - List modules** | **GET** | Lista os módulos Redis disponíveis no cluster. |
| **Modules - Get module** | **GET** | Obtém detalhes de um módulo Redis específico. |
| **Node Master Healthcheck - Check connection to primary node** | **GET** | Verifica a conexão do nó local com o nó primário do cluster. |
| **Nodes - List nodes** | **GET** | Lista todos os nós do cluster. |
| **Nodes - Get node** | **GET** | Obtém detalhes de um nó específico. |
| **Nodes - Update node** | **PUT** | Atualiza a configuração de um nó existente. |
| **OCSP - Get OCSP configuration** | **GET** | Obtém a configuração OCSP do cluster. |
| **OCSP - Update OCSP configuration** | **PUT** | Atualiza a configuração OCSP do cluster. |
| **Proxies - List proxies** | **GET** | Lista todos os proxies do cluster. |
| **Proxies - Get proxy** | **GET** | Obtém detalhes de um proxy específico. |
| **Proxies - Update proxy** | **PUT** | Atualiza a configuração de um proxy específico. |
| **Proxies - Update all proxies** | **PUT** | Atualiza a configuração de todos os proxies do cluster. |
| **Redis ACLs - List ACLs** | **GET** | Lista todas as ACLs Redis configuradas. |
| **Redis ACLs - Get ACL** | **GET** | Obtém detalhes de uma ACL Redis específica. |
| **Redis ACLs - Update ACL** | **PUT** | Atualiza uma ACL Redis existente. |
| **Redis ACLs - Create ACL** | **POST** | Cria uma nova ACL Redis. |
| **Redis ACLs - Delete ACL** | **DELETE** | Exclui uma ACL Redis. |
| **Roles - List roles** | **GET** | Lista todas as roles configuradas. |
| **Roles - Get role** | **GET** | Obtém detalhes de uma role específica. |
| **Roles - Update role** | **PUT** | Atualiza uma role existente. |
| **Roles - Create role** | **POST** | Cria uma nova role. |
| **Roles - Delete role** | **DELETE** | Exclui uma role. |
| **Services - List local node services** | **GET** | Lista os serviços do nó local. |
| **Services - Operate local node services** | **POST** | Executa uma operação (start, stop ou restart) em serviços opcionais do nó local. |
| **Services - Operate primary node services** | **POST** | Executa uma operação (start, stop ou restart) em serviços opcionais do nó primário. |
| **Shards - List shards** | **GET** | Lista todos os shards do cluster. |
| **Shards - Get shard** | **GET** | Obtém detalhes de um shard específico. |
| **Suffix - Get DNS suffix** | **GET** | Obtém um sufixo DNS específico pelo nome. |
| **Suffixes - List DNS suffixes** | **GET** | Lista todos os sufixos DNS configurados no cluster. |
| **Usage Report - Get database usage report** | **GET** | Obtém o relatório de uso das bases de dados do cluster (NDJSON). |
| **Users - List users** | **GET** | Lista todos os usuários do cluster. |
| **Users - Get user** | **GET** | Obtém detalhes de um usuário específico. |
| **Users - Update user** | **PUT** | Atualiza a configuração de um usuário existente. |
| **Users - Create user** | **POST** | Cria um novo usuário. |
| **Users - Delete user** | **DELETE** | Exclui um usuário. |

---

## Documentação oficial

<https://redis.io/docs/latest/operate/rs/references/rest-api/>
