# HubSpot CRM

## Contexto

O HubSpot é uma plataforma de CRM, marketing, vendas e atendimento. Este
conector cobre o núcleo da **API de CRM** do HubSpot: os objetos e relações
usados no dia a dia de vendas e atendimento.

Domínios cobertos:

- **Contacts, Companies, Deals, Tickets** — os objetos padrão do CRM, cada um
  com CRUD completo, operações em lote (`batch`), busca (`search`), mesclagem
  (`merge`), exclusão em conformidade com GDPR e listagem de associações.
- **Associations / Association Batches / Association Labels / Association
  Definitions** — criação, remoção e configuração de associações (vínculos)
  entre registros de tipos de objeto diferentes, incluindo rótulos e tipos de
  associação personalizados.
- **Pipelines** — pipelines de negociação/objeto e seus estágios (stages),
  incluindo auditoria de alterações.
- **Owners** — proprietários (usuários) associados a registros do CRM.

Este conector foi gerado a partir dos specs OpenAPI oficiais do HubSpot
(rollout `2026-09`), publicados em
[HubSpot-public-api-spec-collection](https://github.com/HubSpot/HubSpot-public-api-spec-collection).

**Observações técnicas:**
- O objeto **Deals** usa o segmento `deals` no path das operações. A API do
  HubSpot também aceita o identificador interno `0-3` como alias, mas o path
  foi padronizado como `deals` para manter consistência com os demais objetos
  (`contacts`, `companies`, `tickets`).
- As operações **Pipelines - Retrieve pipelines** (lista, sem informar
  `pipelineId`) e **Pipelines - Retrieve pipeline** (registro único, com
  `pipelineId`) compartilham a mesma descrição na tabela abaixo — é uma
  limitação da ferramenta de geração de IAC, não um erro de dados; o
  comportamento das duas chamadas continua distinto (lista vs. item).

---

## Autenticação

**Tipo:** Bearer Token

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | https://api.hubapi.com |
| Porta | 443 |
| token | {{token}} |

O `token` corresponde ao **Private App Access Token** gerado no HubSpot
(Configurações → Integrações → Aplicativos privados), com os escopos de CRM
necessários (ex.: `crm.objects.contacts.read/write`,
`crm.objects.companies.read/write`, `crm.objects.deals.read/write`,
`crm.objects.owners.read`, etc., conforme as operações usadas).

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Association Definitions - Read All** | **GET** | Retorna todas as configurações de usuário disponíveis em um portal. |
| **Association Definitions - Read** | **GET** | Retorna configurações de usuário em todas as definições de associação entre dois tipos de objetos. |
| **Association Definitions - Create** | **POST** | Cria em lote configurações de usuário entre dois tipos de objetos. |
| **Association Definitions - Delete** | **POST** | Exclui em lote configurações de usuário entre dois tipos de objetos. |
| **Association Definitions - Update** | **POST** | Atualiza em lote configurações de usuário entre dois tipos de objetos. |
| **Association Batches - Report high usage** | **POST** | Solicita um relatório de todos os objetos no portal que têm alta utilização de associações. |
| **Association Batches - Remove associations** | **POST** | Exclui em lote associações para objetos. |
| **Association Batches - Create Default Associations** | **POST** | Cria o tipo de associação padrão (mais genérico) entre dois tipos de objetos. |
| **Association Batches - Associate records (labelled)** | **POST** | Cria em lote associações para objetos. |
| **Association Labels - Delete Specific Labels** | **POST** | Exclui em lote rótulos de associação específicos para objetos. Excluir uma associação sem rótulo também excluirá todas as associações rotuladas entre esses dois objetos. |
| **Association Batches - Retrieve associations** | **POST** | Lê em lote associações de objetos para um tipo de objeto específico. Use o campo 'after' retornado para recuperar páginas adicionais. |
| **Association Labels - Read** | **GET** | Retorna todos os tipos de associação entre dois tipos de objetos. |
| **Association Labels - Create** | **POST** | Cria uma definição de associação definida pelo usuário. |
| **Association Labels - Update** | **PUT** | Atualiza uma definição de associação definida pelo usuário. |
| **Association Labels - Delete** | **DELETE** | Exclui uma definição de associação. |
| **Companies - Retrieve companies** | **GET** | Recupera todas as empresas, usando parâmetros de consulta para controlar as informações retornadas. |
| **Companies - Create a company** | **POST** | Cria uma única empresa. Inclua um objeto `properties` para definir valores de propriedade da empresa, juntamente com um array `associations` para definir associações com outros registros do CRM. |
| **Companies - Archive a batch of companies** | **POST** | Exclui um lote de empresas por ID. Empresas excluídas podem ser restauradas dentro de 90 dias da exclusão. |
| **Companies - Create a batch of companies** | **POST** | Cria um lote de empresas. O array `inputs` pode conter um objeto `properties` para definir valores de propriedade de cada empresa, juntamente com um array `associations` para definir associações com outros registros do CRM. |
| **Companies - Retrieve a batch of companies** | **POST** | Recupera um lote de empresas por ID (`companyId`) ou por uma propriedade única (`idProperty`). Especifique o que é retornado usando o parâmetro de consulta `properties`. |
| **Companies - Update a batch of companies** | **POST** | Atualiza um lote de empresas por ID. |
| **Companies - Create or update a batch of companies by unique property values** | **POST** | Cria ou atualiza empresas identificadas por um valor de propriedade única conforme especificado pelo parâmetro de consulta `idProperty`. O parâmetro refere-se a uma propriedade cujos valores são únicos para o objeto. |
| **Companies - GDPR Delete** | **POST** | Exclui permanentemente um contato e todo conteúdo associado em conformidade com regulamentos GDPR. Permite especificar 'idProperty' como 'email' para identificar o contato. |
| **Companies - Merge two companies** | **POST** | Mesclar dois registros de empresa. Saiba mais sobre como mesclar registros. |
| **Companies - Search for companies** | **POST** | Pesquisar empresas filtrando por propriedades, pesquisando associações e classificando resultados. |
| **Companies - Retrieve a company** | **GET** | Recuperar uma empresa pelo seu ID (companyId) ou por uma propriedade única (idProperty). Você pode especificar o que é retornado usando o parâmetro de consulta properties. |
| **Companies - Update a company** | **PATCH** | Atualizar uma empresa pelo ID (companyId) ou valor de propriedade única (idProperty). Os valores fornecidos serão sobrescritos. Propriedades somente leitura e inexistentes resultarão em erro. |
| **Companies - Archive a company** | **DELETE** | Excluir uma empresa por ID. Empresas excluídas podem ser restauradas dentro de 90 dias da exclusão. |
| **Companies - List associations** | **GET** | Listar todas as associações de um objeto (identificado por objectType e objectId) com outro tipo de objeto especificado por toObjectType. Suporta recuperação de até 500 associações por chamada. |
| **Contacts - Retrieve contacts** | **GET** | Recuperar todos os contatos, usando parâmetros de consulta para especificar as informações retornadas. |
| **Contacts - Create a contact** | **POST** | Criar um único contato. Incluir um objeto properties para definir valores de propriedade e uma matriz associations para definir associações com outros registros do CRM. |
| **Contacts - Archive a batch of contacts** | **POST** | Arquivar um lote de contatos por ID. Contatos arquivados podem ser restaurados dentro de 90 dias da exclusão. |
| **Contacts - Create a batch of contacts** | **POST** | Criar um lote de contatos. A matriz inputs pode conter um objeto properties para definir valores e uma matriz associations para definir associações com outros registros. |
| **Contacts - Retrieve a batch of contacts** | **POST** | Recuperar um lote de contatos por ID (contactId) ou valor de propriedade única (idProperty). |
| **Contacts - Update a batch of contacts** | **POST** | Atualizar um lote de contatos por ID (contactId) ou valor de propriedade única (idProperty). Os valores fornecidos serão sobrescritos. Propriedades somente leitura e inexistentes resultarão em erro. |
| **Contacts - Create or update a batch of contacts** | **POST** | Fazer upsert em um lote de contatos. A matriz inputs pode conter um objeto properties para definir valores de propriedade para cada registro. |
| **Contacts - Permanently delete a contact (GDPR-compliant)** | **POST** | Excluir permanentemente um contato e todo o conteúdo associado para cumprir o GDPR. Use a propriedade opcional idProperty definida como email para identificar o contato. Se não encontrado, será adicionado a uma lista de bloqueio. |
| **Contacts - Merge two contacts** | **POST** | Mesclar dois registros de contato. Saiba mais sobre como mesclar registros. |
| **Contacts - Search for contacts** | **POST** | Pesquisar contatos filtrando por propriedades, pesquisando associações e classificando resultados. |
| **Contacts - Retrieve a contact** | **GET** | Recuperar um contato pelo seu ID (contactId) ou por uma propriedade única (idProperty). Você pode especificar o que é retornado usando o parâmetro de consulta properties. |
| **Contacts - Update a contact** | **PATCH** | Atualizar um contato existente identificado por ID ou propriedade única. Os valores fornecidos serão sobrescritos. Propriedades somente leitura e inexistentes resultarão em erro. |
| **Contacts - Archive a contact** | **DELETE** | Excluir um contato por ID. Contatos excluídos podem ser restaurados dentro de 90 dias da exclusão. |
| **Contacts - List associations** | **GET** | Listar todas as associações de um objeto específico (identificado por tipo e ID) com outro tipo de objeto especificado. Suporta paginação com até 500 resultados por chamada. |
| **Deals - List** | **GET** | Ler uma página de negócios. Controlar o que é retornado por meio do parâmetro de consulta properties. |
| **Deals - Create** | **POST** | Criar um negócio com as propriedades fornecidas e retornar uma cópia do objeto, incluindo o ID. |
| **Deals - Archive a batch of deals by ID** | **POST** | Arquivar vários negócios usando seus IDs. |
| **Deals - Create a batch of deals** | **POST** | Criar múltiplos negócios em uma única solicitação. |
| **Deals - Read a batch of deals by internal ID, or unique property values** | **POST** | Recuperar registros por ID ou usar o parâmetro idProperty para recuperar registros por um valor de propriedade único personalizado. |
| **Deals - Update a batch of deals by internal ID, or unique property values** | **POST** | Atualizar múltiplos negócios usando seus IDs internos ou valores de propriedade únicos. |
| **Deals - Create or update a batch of deals by unique property values** | **POST** | Criar ou atualizar registros identificados por um valor de propriedade única especificado por idProperty. Parâmetro refere-se a propriedade com valores únicos para o objeto. |
| **Deals - GDPR Delete** | **POST** | Excluir permanentemente um negócio e conteúdo associado em conformidade com GDPR. Use idProperty definido como 'email' para identificar por email. Se não encontrado, será adicionado a uma lista de bloqueio. |
| **Deals - Merge two deals with same type** | **POST** | Combinar dois negócios do mesmo tipo em um único negócio. |
| **Deals - Search for deals using various filters and criteria to retrieve specific records.** | **POST** | Pesquisar negócios usando critérios e filtros especificados. |
| **Deals - Read** | **GET** | Ler um negócio identificado por dealId (ID interno) ou valor único de idProperty. Controle o retorno via parâmetro properties. |
| **Deals - Update** | **PATCH** | Atualizar parcialmente um negócio identificado por dealId ou valor único de idProperty. Valores serão sobrescritos. Propriedades somente leitura causam erro. Limpe passando string vazia. |
| **Deals - Archive** | **DELETE** | Mover um negócio identificado por dealId para a lixeira. |
| **Deals - List associations** | **GET** | Listar todas as associações de um objeto especificado por tipo. Máximo de 500 associações retornadas por chamada. |
| **Tickets - List** | **GET** | Listar tickets com suporte a paginação. Controle os dados retornados especificando propriedades e incluindo IDs de objetos associados e registros arquivados. |
| **Tickets - Create** | **POST** | Criar um ticket com propriedades especificadas. Retorna uma cópia do objeto criado, incluindo seu ID. |
| **Tickets - Batch archive objects** | **POST** | Arquivar um lote de tickets identificados por seus IDs, movendo-os para a lixeira em uma única solicitação. |
| **Tickets - Batch create objects** | **POST** | Criar um lote de tickets com propriedades especificadas. Retorna uma cópia de cada objeto criado, incluindo seus IDs. |
| **Tickets - Read batch objects** | **POST** | Recuperar um lote de tickets por IDs internos ou valores únicos de propriedades. Opcionalmente inclua objetos arquivados nos resultados. |
| **Tickets - Update batch objects** | **POST** | Atualizar um lote de tickets fornecendo seus detalhes no corpo da solicitação. Útil para atualizações em massa de múltiplos objetos simultaneamente. |
| **Tickets - Upsert batch objects** | **POST** | Criar ou atualizar um lote de tickets por valores de propriedade únicos. Objetos existentes são atualizados; novos são criados em uma única solicitação. |
| **Tickets - GDPR Delete** | **POST** | Excluir permanentemente um ticket e conteúdo associado em conformidade com GDPR. Use idProperty definido como 'email' para identificar por endereço de email. Se não encontrado, será adicionado a uma lista de bloqueio. |
| **Tickets - Merge objects** | **POST** | Combinar dois tickets do mesmo tipo em um único objeto, consolidando suas propriedades e associações. |
| **Tickets - Search objects** | **POST** | Pesquisar tickets usando filtros, critérios, grupos de filtros e opções de classificação especificados. |
| **Tickets - Read** | **GET** | Ler um ticket identificado por objectId (ID interno) ou valor único de idProperty. Controle o retorno via parâmetro properties. Inclui propriedades, associações e histórico. |
| **Tickets - Update** | **PATCH** | Atualizar parcialmente um ticket identificado por objectId ou valor único de idProperty. Valores serão sobrescritos. Propriedades somente leitura são ignoradas. Limpe passando string vazia. |
| **Tickets - Archive** | **DELETE** | Mover um objeto identificado por `{objectId}` para a lixeira. Esta operação permite arquivar um objeto CRM específico por ID, removendo-o do uso ativo enquanto o retém no sistema para potencial restauração futura. |
| **Tickets - List associations** | **GET** | Listar todas as associações de um objeto especificado pelo seu tipo. Este endpoint permite recuperar associações entre objetos, com limite de 500 associações por chamada. É útil para entender as relações entre diferentes objetos CRM. |
| **Associations - Create Association** | **PUT** | Criar o tipo de associação padrão entre dois tipos de objeto especificados no HubSpot. Este endpoint é usado para estabelecer uma relação genérica entre dois objetos, identificados por seus tipos e IDs respectivos. |
| **Associations - Create** | **PUT** | Definir rótulos de associação entre dois registros no CRM, especificando a relação entre os tipos de objeto, para organizar as conexões entre registros na conta HubSpot. |
| **Associations - Delete** | **DELETE** | Deletar todas as associações entre dois registros especificados na sua conta HubSpot. Esta operação remove a ligação entre os dois objetos identificados pelos seus IDs respectivos. |
| **Owners - List owners** | **GET** | Recuperar proprietários da sua conta HubSpot com filtro por email e paginação. Suporta especificar o número máximo de resultados por página e inclua proprietários arquivados na resposta. |
| **Owners - Retrieve a specific owner by ID** | **GET** | Recuperar detalhes de um proprietário específico usando seu 'id' ou 'userId'. |
| **Pipelines - Retrieve pipelines** | **GET** | Recupera pipelines de um tipo de objeto do CRM: sem informar o ID do pipeline, retorna a lista completa; informando o ID, retorna os dados detalhados de um pipeline específico, incluindo seus estágios. |
| **Pipelines - Create pipeline** | **POST** | Criar um novo pipeline para um tipo de objeto na sua conta HubSpot. Requer corpo JSON com rótulo, ordem de exibição e estágios. |
| **Pipelines - Retrieve pipeline** | **GET** | Recupera pipelines de um tipo de objeto do CRM: sem informar o ID do pipeline, retorna a lista completa; informando o ID, retorna os dados detalhados de um pipeline específico, incluindo seus estágios. |
| **Pipelines - Update pipeline (Replace)** | **PUT** | Atualizar um pipeline existente especificando seu ID e tipo de objeto. Modifique propriedades como rótulo, ordem e estágios. |
| **Pipelines - Update pipeline (Partial)** | **PATCH** | Atualizar propriedades específicas de um pipeline existente, como rótulo, ordem de exibição ou status de arquivo, mantendo os dados de pipeline atualizados na conta HubSpot. |
| **Pipelines - Delete pipeline** | **DELETE** | Deletar um pipeline específico na sua conta HubSpot identificado por seu tipo de objeto e ID. Esta operação pode validar opcionalmente referências e uso de estágios de negócio antes da exclusão para garantir a integridade dos dados. |
| **Pipelines - Retrieve audit logs** | **GET** | Recuperar registros de auditoria de um pipeline específico na sua conta HubSpot. Fornece detalhes sobre alterações feitas no pipeline para rastrear modificações e entender seu histórico. |
| **Pipelines - List stages** | **GET** | Recuperar todos os estágios de um pipeline específico. Útil para obter informações detalhadas sobre cada estágio, que podem ser usadas para análise ou integração com outros sistemas. |
| **Pipelines - Create Stage** | **POST** | Criar um novo estágio dentro de um pipeline especificado. Permite rastreamento e gerenciamento mais granular de objetos através de diferentes estágios de um processo. |
| **Pipelines - Retrieve stage** | **GET** | Recuperar detalhes de um estágio específico dentro de um pipeline incluindo seu rótulo, ordem de exibição e metadados. |
| **Pipelines - Update stage** | **PUT** | Atualizar um estágio específico dentro de um pipeline modificando seu rótulo, ordem e metadados. |
| **Pipelines - Update stage (Partial)** | **PATCH** | Atualizar um estágio específico dentro de um pipeline modificando suas propriedades como rótulo, ordem e metadados. |
| **Pipelines - Delete stage** | **DELETE** | Deletar um estágio específico de um pipeline na sua conta HubSpot. Útil para gerenciar e manter seus estágios de pipeline removendo os desnecessários. |
| **Pipelines - Retrieve stage audit** | **GET** | Recuperar informações de auditoria para um estágio específico dentro de um pipeline. Fornece detalhes sobre ações tomadas para rastrear alterações e entender o histórico. |

---

## Documentação oficial

https://developers.hubspot.com/docs/api-reference/latest/overview
