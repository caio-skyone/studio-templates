# Jira

## Contexto

O **Jira Cloud** é a plataforma de rastreamento de trabalho da Atlassian. Tudo nela gira em torno da **issue** — uma unidade de trabalho que vive dentro de um **projeto**, tem um **tipo** (Bug, Story, Task, Epic, Subtask), percorre um **fluxo de trabalho** de status e carrega **campos** padrão e customizados. Em torno disso a API expõe comentários, anexos, registros de trabalho, vínculos entre issues, versões, componentes, usuários, grupos, permissões, filtros salvos e painéis.

Este template cobre **467 operações** de duas APIs distintas, ambas na mesma instância e sob a mesma credencial:

**[Jira Cloud platform REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)** — 406 operações em `/rest/api/{version}`. É a base do produto: issues, projetos, campos, usuários, busca JQL, filtros, painéis, versões, componentes e a configuração de instância de uso corrente.

**[Jira Software Cloud API](https://developer.atlassian.com/cloud/jira/software/rest/intro/)** — 61 operações do lado ágil: 51 em `/rest/agile/1.0` (quadros, sprints, épicos, backlog) e 10 em `/rest/software/1.0`, que são variantes aprimoradas das listagens de issues de quadro, épico e sprint, com paginação por token.

As operações foram geradas a partir das especificações OpenAPI oficiais publicadas pela Atlassian, não de uma coleção de terceiros.

## Conceitos Fundamentais

### Issue: id ou chave, os dois servem

A maior parte das operações de issue aceita tanto o **id numérico** (`10002`) quanto a **chave** (`PROJ-123`) no mesmo parâmetro — daí o nome `issue_id_or_key`. A chave é legível e é o que aparece na interface, mas ela **muda** quando a issue é movida de projeto. Em automações de longa duração, o id é a referência estável. O mesmo vale para `project_id_or_key`.

### O usuário é identificado por accountId

O Jira Cloud não expõe nome de usuário nem e-mail como identificador de API — desde a adequação ao GDPR, o identificador é o **accountId**, uma string opaca como `5b10ac8d82e05b22cc7d4ef5`. É ele que vai em `account_id`, em atribuição de issue e em busca de usuário.

### JQL é a linguagem de consulta

Praticamente toda listagem interessante passa por **JQL** (`project = PROJ AND status = "In Progress" ORDER BY created DESC`). O domínio **Search** executa a consulta; o domínio **JQL** trata de autocomplete, validação, parsing e sanitização das consultas.

Há duas gerações de busca no template: as operações `/search` clássicas e as `/search/jql` aprimoradas. As aprimoradas paginam por **token** (`next_page_token`), não por deslocamento, e são as recomendadas pela Atlassian para volumes grandes.

### Duas formas de paginar

A maioria dos endpoints pagina por deslocamento, com `start_at` e `max_results`. Os endpoints mais novos — busca aprimorada, listagens de quadro em `/rest/software/1.0`, changelogs em lote — paginam por cursor, com `next_page_token`. Na paginação por cursor a última página simplesmente não traz o token.

### Permissões vêm do usuário, não da API

Toda chamada roda com as permissões da conta cujo token está na conta conectada. A API não eleva privilégio: se o usuário não enxerga o projeto, a operação devolve 404 em vez de 403, para não revelar a existência do recurso. Operações administrativas exigem a permissão global *Administer Jira*.

### Propriedades de entidade

Issues, projetos, comentários, usuários, quadros e sprints aceitam **propriedades** — pares chave/valor com JSON arbitrário, usados para guardar metadados de integração junto ao recurso. Aparecem no template como operações *Get / Set / Delete property* em vários domínios.

---

## Autenticação

**Tipo:** Autenticação básica (HTTP Basic)

O Jira Cloud aceita Basic com **e-mail da conta Atlassian** como usuário e um **API token** como senha. A credencial fica na conta conectada — nenhuma operação deste template carrega parâmetro de token.

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://{{seu_site}}.atlassian.net` |
| Porta | 443 |
| username | {{email_da_conta}} |
| password | {{api_token}} |

### Host

É a URL do seu site Atlassian, a mesma que você usa no navegador:

```
https://{seu-site}.atlassian.net
```

### API token

1. Acesse **[id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)**.
2. Clique em **Create API token**, dê um rótulo que identifique a integração e copie o valor — ele só aparece uma vez.
3. Use o **e-mail da conta** que criou o token como `username`, e o token como `password`.

O token herda todas as permissões do usuário que o criou. Para integrações, crie uma conta de serviço com o acesso mínimo necessário em vez de usar uma conta pessoal.

### Por que não OAuth 2.0

O Jira Cloud também suporta OAuth 2.0 (3LO), mas nesse fluxo a URL base deixa de ser o site e passa a ser `https://api.atlassian.com/ex/jira/{cloudId}`, com o `cloudId` no caminho. Isso quebraria o prefixo comum exigido pelo IAC — todas as operações de um conector precisam compartilhar o mesmo nível de prefixo. Por isso o template é Basic.

---

## Convenções do template

### A versão da API é um parâmetro em 406 operações

O Jira Cloud publica a mesma coleção de operações da plataforma em duas versões, `/rest/api/2` e `/rest/api/3`. Este template não fixa nenhuma das duas: o segmento é o parâmetro obrigatório **`version`**, com sample `3`.

A diferença entre elas é o formato de texto rico:

| Valor | Comportamento |
| :--- | :--- |
| `3` | campos de texto rico em **ADF** (Atlassian Document Format), um JSON estruturado |
| `2` | campos de texto rico em **wiki markup**, string simples |
| `latest` | alias que a Atlassian aponta para a versão corrente |

A escolha importa em toda operação que escreve descrição, comentário ou qualquer campo de texto formatado. Montar ADF à mão é trabalhoso; se o seu fluxo só precisa gravar texto simples, `2` costuma ser o caminho mais curto. Para leitura, `3` devolve a estrutura completa.

**As 61 operações ágeis não têm o parâmetro**: `/rest/agile/1.0` e `/rest/software/1.0` só existem na versão `1.0`, e o único alias disponível (`latest`) aponta para ela mesma. Parametrizar ali não daria escolha alguma.

### O parâmetro `body` — um objeto, não campos soltos

As 143 operações com corpo JSON expõem um único parâmetro `body` do tipo objeto, com o payload inteiro. Não há um parâmetro por campo. O motivo é a profundidade dos corpos do Jira: o corpo de **Issues - Create issue** carrega `fields`, que contém um objeto por campo do projeto, incluindo campos customizados que variam por instância.

Cada operação traz no `sample` do `body` um exemplo do formato esperado — use-o como ponto de partida.

### Path e query são exaustivos

Todo segmento variável do caminho e todo parâmetro de query documentado na spec estão mapeados, obrigatórios e opcionais. Um parâmetro de query deixado em branco é descartado pelo Studio antes do envio, então não custa nada deixá-lo vazio.

Parâmetros que a API recebe repetidos aparecem com `[]` na chave — `expand[]`, `fields[]`, `id[]`. O caso mais comum é `expand`, presente em 66 operações, que controla quais blocos extras a resposta traz.

### Headers só onde a API exige

Nenhum header opcional entrou no template: no Studio, um header deixado em branco é enviado mesmo assim, com valor vazio, e algumas APIs rejeitam isso. Só quatro operações carregam header, todas por exigência do Jira:

| Operação | Header | Valor |
| :--- | :--- | :--- |
| **Issues - Add attachment** | `X-Atlassian-Token` | `no-check` (fixo) |
| **Issue Types - Load issue type avatar** | `Content-Type` | parâmetro `content_type` |
| **Projects - Load project avatar** | `Content-Type` | parâmetro `content_type` |
| **Avatars - Load avatar** | `Content-Type` | parâmetro `content_type` |

### Uploads de arquivo

São dois formatos diferentes, com exigências diferentes de configuração:

**Multipart — `Issues - Add attachment`.** O conteúdo vai na linha de corpo `file:<>file</>:mime:application/octet-stream:anexo.pdf`. Ajuste o mime e o nome do arquivo diretamente na linha do corpo da operação, conforme o arquivo que você envia. O header `X-Atlassian-Token: no-check` já está posto — sem ele o Jira recusa o upload.

**Binário cru — os três uploads de avatar.** Aqui o arquivo vai sozinho no corpo, e o `Content-Type` da requisição é o próprio mime da imagem (`image/png`, `image/jpeg`), não `multipart/form-data`. Nesse formato:

- o conteúdo do arquivo deve ser informado em **base64** no parâmetro `image_data`;
- a opção **"Forçar bufferização da requisição"** precisa estar **marcada** na operação.

Sem as duas coisas o corpo chega corrompido do outro lado. Vale para **Issue Types - Load issue type avatar**, **Projects - Load project avatar** e **Avatars - Load avatar**.

### Propriedades de entidade usam `property_value`

As nove operações *Set property* recebem um JSON arbitrário como corpo, sem schema na spec. Elas expõem o parâmetro `property_value`, que aceita qualquer valor JSON válido e não vazio — um objeto, um array, um número ou uma string entre aspas.

### As operações em lote de propriedade de issue

**Issues - Bulk set issue property** e **Issues - Bulk delete issue property** não seguem o padrão acima: em vez de um valor solto, recebem um `body` com o filtro que seleciona as issues afetadas. O bulk delete é o único DELETE do template com corpo — sem o filtro, a operação não tem o que apagar.

### Operações sem corpo

Nove operações de escrita não levam corpo nenhum, porque a própria API não espera um: o efeito está inteiro no caminho. São ações como **Projects - Archive project**, **Issues - Add vote**, **Tasks - Cancel task**, **Filters - Add filter as favorite** e **Versions - Merge versions**.

### Query de tipo objeto: o que varia é a chave

Dois parâmetros de query são do tipo objeto — `state` e `type`. Neles o que muda de uma chamada para outra é a **chave** da query, não o valor. Para usar uma variante, edite a chave do parâmetro na operação.

---

## Fora do escopo

Do total de 796 operações publicadas nas três specs do Jira Cloud, 329 ficaram de fora:

**Jira Service Management** (74 operações, `/rest/servicedeskapi`) — service desks, solicitações de cliente, organizações e base de conhecimento. É um produto à parte, com modelo próprio, e merece um conector dedicado.

**Administração pesada de esquemas** (211 operações) — workflow schemes, issue security schemes, notification schemes, priority schemes, permission schemes, issue type schemes, field configuration schemes, telas e screen schemes, templates de projeto e o Advanced Roadmaps (`/plans`). São tarefas de configuração de instância, normalmente feitas uma vez pela interface, não em fluxo automatizado.

**Endpoints exclusivos de app** (28 operações) — `/rest/atlassian-connect`, `/rest/forge`, `/rest/internal/api`, `/rest/api/{version}/app` e as UI modifications. Exigem credencial de app Connect ou Forge, não de usuário.

**Ingestão DevOps** (44 operações) — `devinfo`, `deployments`, `builds`, `featureflags`, `remotelinks`, `devopscomponents`, `security` e `operations`. São APIs pelas quais integrações como Bitbucket e GitHub *empurram* dados para o Jira; três delas nem aceitam autenticação básica, só escopos OAuth de app.

---

## Operações

### Issues e trabalho

*108 operações.*

#### Issues

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Issues - Add attachment** | **POST** | Adiciona um ou mais anexos a uma issue como multipart/form-data com cabeçalho X-Atlassian-Token: no-check. Exige permissões de Procurar projetos e Criar anexos. |
| **Issues - Add comment** | **POST** | Adiciona um comentário a uma issue. Exige permissões de Procurar projetos e Adicionar comentários. |
| **Issues - Add vote** | **POST** | Adiciona o voto do usuário a uma issue. Requer permissão Procurar projetos e visualizar issue se houver segurança em nível de issue. |
| **Issues - Add watcher** | **POST** | Adiciona um usuário como observador de uma issue especificando o ID da conta do usuário. |
| **Issues - Add worklog** | **POST** | Adiciona um registro de tempo de trabalho a uma issue. |
| **Issues - Archive issue(s) by JQL** | **POST** | Arquiva até 100 mil issues usando JQL em uma operação assíncrona. Requer permissão de administrador global e licença Premium ou Enterprise. |
| **Issues - Archive issue(s) by issue ID/key** | **PUT** | Arquiva até 1 mil issues por ID ou chave. Requer permissão de administrador global e licença Premium ou Enterprise. |
| **Issues - Assign issue** | **PUT** | Atribui uma issue a um usuário ou ao atribuído padrão do projeto, ou remove a atribuição. Exige permissões de Procurar projetos e Atribuir issues. |
| **Issues - Bulk create issue** | **POST** | Cria até 50 issues ou subtarefas com transições e propriedades opcionais. Exige permissões de Procurar projetos e Criar issues. |
| **Issues - Bulk delete issue property** | **DELETE** | Deleta propriedade de múltiplas issues usando critérios de filtro, de forma transacional e assíncrona. |
| **Issues - Bulk delete worklogs** | **DELETE** | Deleta uma lista de registros de tempo de trabalho de uma issue. Máximo 5.000 registros de uma vez. |
| **Issues - Bulk fetch issues** | **POST** | Retorna detalhes de até 100 issues por ID ou chave, em ordem crescente, com busca de case-insensitive para issues movidas. |
| **Issues - Bulk move worklogs** | **POST** | Move uma lista de registros de tempo de trabalho entre issues. Máximo 5.000 registros de uma vez. |
| **Issues - Bulk set issue properties by issue** | **POST** | Define ou atualiza até 10 propriedades por issue em até 100 issues, de forma não-transacional e assíncrona. |
| **Issues - Bulk set issue property** | **PUT** | Define valor de propriedade em múltiplas issues usando filtro e expressão Jira opcional, de forma transacional e assíncrona. |
| **Issues - Bulk set issues properties by list** | **POST** | Define ou atualiza lista de até 10 propriedades em até 10 mil issues, de forma transacional e assíncrona. |
| **Issues - Create issue** | **POST** | Cria uma issue ou subtarefa com transição de fluxo de trabalho opcional. Exige permissões de Procurar projetos e Criar issues. |
| **Issues - Create or update remote issue link** | **POST** | Cria ou atualiza um link de issue remota para uma issue. Requer que a vinculação de issues esteja ativa. |
| **Issues - Delete comment** | **DELETE** | Deleta um comentário. Exige permissão de Deletar todos os comentários ou Deletar comentários próprios. |
| **Issues - Delete issue** | **DELETE** | Deleta uma issue, com opção de deletar também as subtarefas. Exige permissões de Procurar projetos e Deletar issues. |
| **Issues - Delete issue property** | **DELETE** | Deleta uma propriedade de issue. |
| **Issues - Delete remote issue link by ID** | **DELETE** | Deleta link de issue remota de uma issue. Requer que a vinculação de issues esteja ativa. |
| **Issues - Delete remote issue link by global ID** | **DELETE** | Deleta link de issue remota de uma issue usando o ID global do link. Requer que a vinculação de issues esteja ativa. |
| **Issues - Delete vote** | **DELETE** | Remove o voto do usuário de uma issue. Requer permissão Procurar projetos e visualizar issue se houver segurança em nível de issue. |
| **Issues - Delete watcher** | **DELETE** | Remove um usuário como observador de uma issue. |
| **Issues - Delete worklog** | **DELETE** | Deleta um registro de tempo de trabalho de uma issue. |
| **Issues - Delete worklog property** | **DELETE** | Deleta uma propriedade de um registro de tempo de trabalho. |
| **Issues - Edit issue** | **PUT** | Edita uma issue, atualizando campos e propriedades. Exige permissões de Procurar projetos e Editar issues. |
| **Issues - Export archived issue(s)** | **PUT** | Permite que administradores exportem detalhes de todas as issues arquivadas em arquivo CSV por e-mail. |
| **Issues - Get changelogs** | **GET** | Retorna lista paginada de todos os registros de alteração de uma issue, ordenada por data. |
| **Issues - Get changelogs by IDs** | **POST** | Retorna registros de alteração de uma issue especificada por lista de IDs de registro. |
| **Issues - Get comment** | **GET** | Retorna um comentário de uma issue. |
| **Issues - Get comments** | **GET** | Retorna todos os comentários de uma issue. |
| **Issues - Get create field metadata for a project and issue type id** | **GET** | Retorna página de metadados de campos para um projeto e tipo de issue especificados. |
| **Issues - Get create issue metadata** | **GET** | Retorna detalhes de projetos, tipos de issue e campos de tela de criação para preenchimento de requisições de criar issue. |
| **Issues - Get create metadata issue types for a project** | **GET** | Retorna página de metadados de tipos de issue para um projeto especificado. |
| **Issues - Get edit issue metadata** | **GET** | Retorna campos de tela de edição de uma issue visíveis e editáveis pelo usuário, com opções de sobrescrita para aplicações Connect. |
| **Issues - Get is watching issue bulk** | **POST** | Retorna status de monitoramento de issues para o usuário a partir de uma lista. Requer opção Permitir monitoramento de issues ativa. |
| **Issues - Get issue** | **GET** | Retorna detalhes de uma issue identificada por ID ou chave, com busca de case-insensitive para issues movidas. |
| **Issues - Get issue adf limit report** | **GET** | Retorna issues cujos campos ADF (texto rico) excedem o limite de tamanho universal, com contagem de entidades violadoras por campo. |
| **Issues - Get issue limit report** | **GET** | Retorna issues que violam ou se aproximam dos limites por issue. Exige permissões de Procurar projetos e Administrar Jira. |
| **Issues - Get issue picker suggestions** | **GET** | Retorna listas de issues correspondentes a uma cadeia de consulta para sugestões de autocompletar no seletor de issues. |
| **Issues - Get issue property** | **GET** | Retorna chave e valor de uma propriedade de issue. |
| **Issues - Get issue property keys** | **GET** | Retorna URLs e chaves das propriedades de uma issue. |
| **Issues - Get issue watchers** | **GET** | Retorna os observadores de uma issue. Requer permissão Procurar projetos e visualizar issue se houver segurança em nível de issue. |
| **Issues - Get issue worklogs** | **GET** | Retorna os registros de tempo de trabalho de uma issue, começando do mais antigo ou a partir de data e hora especificadas. |
| **Issues - Get remote issue link by ID** | **GET** | Retorna um link de issue remota para uma issue. Requer que a vinculação de issues esteja ativa. |
| **Issues - Get remote issue links** | **GET** | Retorna links de issue remota para uma issue. Requer que a vinculação de issues esteja ativa. |
| **Issues - Get transitions** | **GET** | Retorna transições que podem ser realizadas pelo usuário em uma issue, baseadas no seu status. |
| **Issues - Get votes** | **GET** | Retorna detalhes sobre votos de uma issue. Requer que a opção Permitir usuários votarem em issues esteja ativa. |
| **Issues - Get worklog** | **GET** | Retorna um registro de tempo de trabalho. |
| **Issues - Get worklog property** | **GET** | Retorna o valor de uma propriedade de um registro de tempo de trabalho. |
| **Issues - Get worklog property keys** | **GET** | Retorna as chaves de todas as propriedades de um registro de tempo de trabalho. |
| **Issues - Send notification for issue** | **POST** | Cria notificação por e-mail para uma issue e a adiciona à fila de envio. Exige permissão de Procurar projetos. |
| **Issues - Set issue property** | **PUT** | Define o valor de uma propriedade de issue para armazenar dados personalizados. |
| **Issues - Set worklog property** | **PUT** | Define o valor de uma propriedade de um registro de tempo de trabalho. Aceita um blob JSON válido e não vazio. |
| **Issues - Transition issue** | **POST** | Realiza transição de issue, atualizando campos da tela de transição se necessário. Exige permissões de Procurar projetos e Transicionar issues. |
| **Issues - Unarchive issue(s) by issue keys/ID** | **PUT** | Desarquiva até 1 mil issues por ID ou chave. Requer permissão de administrador global e licença Premium ou Enterprise. |
| **Issues - Update comment** | **PUT** | Atualiza um comentário. Exige permissão de Editar todos os comentários ou Editar comentários próprios. |
| **Issues - Update remote issue link by ID** | **PUT** | Atualiza um link de issue remota para uma issue. Requer que a vinculação de issues esteja ativa. |
| **Issues - Update worklog** | **PUT** | Atualiza um registro de tempo de trabalho. |

#### Comments

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Comments - Delete comment property** | **DELETE** | Exclui uma propriedade de comentário. Requer permissão de edição de comentários. |
| **Comments - Get comment property** | **GET** | Retorna o valor de uma propriedade de comentário. Requer permissão de navegação do projeto. |
| **Comments - Get comment property keys** | **GET** | Retorna as chaves de todas as propriedades de um comentário. Requer permissão de navegação do projeto. |
| **Comments - Get comments by IDs** | **POST** | Retorna lista paginada de comentários pelos seus IDs. Requer permissão de navegação do projeto. |
| **Comments - Set comment property** | **PUT** | Cria ou atualiza uma propriedade de comentário com dados JSON (máx. 32.768 caracteres). Requer permissão de edição de comentários. |

#### Worklogs

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Worklogs - Get IDs of deleted worklogs** | **GET** | Retorna IDs e timestamps de worklogs deletados após uma data. |
| **Worklogs - Get IDs of updated worklogs** | **GET** | Retorna IDs e timestamps de worklogs atualizados após uma data. |
| **Worklogs - Get worklogs** | **POST** | Retorna detalhes de worklogs para uma lista de IDs. |

#### Attachments

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Attachments - Delete attachment** | **DELETE** | Exclui um anexo de uma issue. Requer permissão de exclusão de anexos. |
| **Attachments - Get Jira attachment settings** | **GET** | Retorna as configurações de anexo (ativado, tamanho máximo). Sem permissões necessárias. |
| **Attachments - Get all metadata for an expanded attachment** | **GET** | Retorna metadados do conteúdo de um anexo (arquivo/ZIP) e do próprio anexo. Requer permissão de navegação do projeto. |
| **Attachments - Get attachment content** | **GET** | Retorna o conteúdo de um anexo. Suporta intervalo de bytes via header Range. Requer permissão de navegação do projeto. |
| **Attachments - Get attachment metadata** | **GET** | Retorna os metadados de um anexo. Requer permissão de navegação do projeto. |
| **Attachments - Get attachment thumbnail** | **GET** | Retorna a miniatura de um anexo. Requer permissão de navegação do projeto. |
| **Attachments - Get contents metadata for an expanded attachment** | **GET** | Retorna metadados do conteúdo de um anexo (arquivo/ZIP). Requer permissão de navegação do projeto. |

#### Issue Links

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Issue Links - Create issue link** | **POST** | Cria um vínculo entre duas issues. Requer permissões Procurar projeto, Vincular issues. |
| **Issue Links - Delete issue link** | **DELETE** | Deleta um vínculo de issue. |
| **Issue Links - Get issue link** | **GET** | Retorna um vínculo de issue. |

#### Issue Link Types

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Issue Link Types - Create issue link type** | **POST** | Cria um tipo de vínculo de issue com nomes e descrições para as relações de entrada e saída. |
| **Issue Link Types - Delete issue link type** | **DELETE** | Deleta um tipo de vínculo de issue. Substitui todos os usos pelo tipo alternativo. |
| **Issue Link Types - Get issue link type** | **GET** | Retorna um tipo de vínculo de issue. |
| **Issue Link Types - Get issue link types** | **GET** | Retorna uma lista de todos os tipos de vínculo de issue. |
| **Issue Link Types - Update issue link type** | **PUT** | Atualiza um tipo de vínculo de issue. |

#### Issue Types

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Issue Types - Create issue type** | **POST** | Cria um novo tipo de issue. |
| **Issue Types - Delete issue type** | **DELETE** | Deleta um tipo de issue. Substitui todos os usos pelo tipo alternativo especificado. |
| **Issue Types - Delete issue type property** | **DELETE** | Deleta uma propriedade de tipo de issue. |
| **Issue Types - Get all issue types for user** | **GET** | Retorna todos os tipos de issue com base nas permissões do usuário. |
| **Issue Types - Get alternative issue types** | **GET** | Retorna tipos de issue que podem substituir um tipo especificado. |
| **Issue Types - Get issue type** | **GET** | Retorna um tipo de issue. |
| **Issue Types - Get issue type property** | **GET** | Retorna a chave e valor de uma propriedade de tipo de issue. |
| **Issue Types - Get issue type property keys** | **GET** | Retorna todas as chaves de propriedade do tipo de issue. |
| **Issue Types - Get issue types for project** | **GET** | Retorna os tipos de issue para um projeto. |
| **Issue Types - Load issue type avatar** | **POST** | Carrega um avatar para o tipo de issue. Deve ser JPEG, GIF ou PNG. |
| **Issue Types - Set issue type property** | **PUT** | Cria ou atualiza o valor de uma propriedade de tipo de issue. Aceita um blob JSON válido e não vazio. |
| **Issue Types - Update issue type** | **PUT** | Atualiza um tipo de issue. |

#### Changelogs

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Changelogs - Bulk fetch changelogs** | **POST** | Obtém registros de alterações em lote para até 1.000 issues filtrados por até 10 IDs de campo. Requer permissão de navegação. |

#### Bulk Operations

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Bulk Operations - Bulk delete issues** | **POST** | Envia solicitação de exclusão em lote de até 1.000 issues. Requer permissão de exclusão em todos os projetos. |
| **Bulk Operations - Bulk edit issues** | **POST** | Envia solicitação de edição em lote de até 1.000 issues com até 200 campos. Requer permissão de edição em todos os projetos. |
| **Bulk Operations - Bulk move issues** | **POST** | Envia solicitação de movimentação em lote de até 1.000 issues para um mesmo projeto/tipo/pai. Requer permissão apropriada. |
| **Bulk Operations - Bulk transition issue statuses** | **POST** | Envia solicitação de transição de status em lote de até 1.000 issues. Requer permissão de transição em todos os projetos. |
| **Bulk Operations - Bulk unwatch issues** | **POST** | Envia solicitação de parar de acompanhar até 1.000 issues em uma operação. Requer permissão de mudança em lote. |
| **Bulk Operations - Bulk watch issues** | **POST** | Envia solicitação de acompanhar até 1.000 issues em uma operação. Requer permissão de mudança em lote. |
| **Bulk Operations - Get available transitions** | **GET** | Obtém lista de transições disponíveis para operações em lote de até 1.000 issues. Retorna 50 fluxos por vez. |
| **Bulk Operations - Get bulk editable fields** | **GET** | Obtém lista de campos editáveis visíveis para operações em lote de até 1.000 issues. Retorna 50 campos por vez. |
| **Bulk Operations - Get bulk issue operation progress** | **GET** | Obtém o estado de progresso de uma operação em lote pelo `taskId`. Requer permissão de mudança em lote. |

#### Redaction

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Redaction - Get redaction status** | **GET** | Retorna o status atual de um trabalho de redação (IN_PROGRESS, COMPLETED ou PENDING). |
| **Redaction - Redact** | **POST** | Submete um trabalho para remover dados de campos de issue. A remoção ocorre assincronamente. |

### Busca

*18 operações.*

#### Search

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Search - Count issues using JQL** | **POST** | Fornece contagem estimada de issues que correspondem à consulta JQL. Requer permissão Procurar projetos. |
| **Search - Currently being removed. Search for issues using JQL (GET)** | **GET** | Pesquisa issues usando JQL. Este endpoint está sendo removido; use a versão POST para consultas grandes. Requer permissão Procurar projetos. |
| **Search - Currently being removed. Search for issues using JQL (POST)** | **POST** | Pesquisa issues usando JQL via POST. Este endpoint está sendo removido. Requer permissão Procurar projetos. |
| **Search - Search for issues using JQL enhanced search (GET)** | **GET** | Pesquisa issues com JQL aprimorado. Use POST para consultas grandes. Requer permissão Procurar projetos. |
| **Search - Search for issues using JQL enhanced search (POST)** | **POST** | Pesquisa issues com JQL aprimorado via POST. Requer permissão Procurar projetos. |

#### JQL

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **JQL - Check issues against JQL** | **POST** | Verifica se uma ou mais issues seriam retornadas por uma ou mais consultas JQL. |
| **JQL - Convert user identifiers to account IDs in JQL queries** | **POST** | Converte consultas JQL com identificadores de usuário para equivalentes com IDs de conta. |
| **JQL - Get field auto complete suggestions** | **GET** | Retorna sugestões de autopreenchimento de busca JQL para um campo. |
| **JQL - Get field reference data (GET)** | **GET** | Retorna dados de referência para buscas JQL com campos, funções e palavras reservadas. |
| **JQL - Get field reference data (POST)** | **POST** | Retorna dados de referência para buscas JQL, opcionalmente filtrados por projeto. |
| **JQL - Get precomputations (apps)** | **GET** | Retorna a lista de pré-computações de uma função com informações de criação e uso. |
| **JQL - Get precomputations by ID (apps)** | **POST** | Retorna pré-computações de função por IDs com informações de criação e uso. |
| **JQL - Parse JQL query** | **POST** | Analisa e valida consultas JQL no contexto do usuário atual. |
| **JQL - Sanitize JQL queries** | **POST** | Sanitiza consultas JQL convertendo detalhes legíveis em IDs quando apropriado. |
| **JQL - Update precomputations (apps)** | **POST** | Atualiza o valor de pré-computação de uma função criada por um app. |

#### Jira Expressions

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Jira Expressions - Analyse Jira expression** | **POST** | Analisa e valida expressões do Jira, com verificação de tipo experimental. |
| **Jira Expressions - Currently being removed. Evaluate Jira expression** | **POST** | Avalia uma expressão do Jira e retorna seu valor. Este endpoint está em processo de remoção. |
| **Jira Expressions - Evaluate Jira expression using enhanced search API** | **POST** | Avalia uma expressão do Jira retornando seu valor, usando API de busca aprimorada para melhor desempenho e escalabilidade. |

### Projetos

*84 operações.*

#### Projects

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Projects - Add actors to project role** | **POST** | Adiciona atores a uma função de projeto. Para substituir todos, use Set actors. |
| **Projects - Archive project** | **POST** | Arquiva um projeto. |
| **Projects - Assign permission scheme** | **PUT** | Associa um esquema de permissão a um projeto. Requer permissão Administer Jira. |
| **Projects - Create project** | **POST** | Cria um projeto baseado em um modelo de tipo de projeto. |
| **Projects - Delete actors from project role** | **DELETE** | Deleta atores de uma função de projeto. |
| **Projects - Delete project** | **DELETE** | Exclui um projeto. Projetos arquivados não podem ser excluídos; restaure-o primeiro. |
| **Projects - Delete project asynchronously** | **POST** | Exclui um projeto de forma assíncrona e transacional. Acompanhe o status na resposta. |
| **Projects - Delete project avatar** | **DELETE** | Exclui um avatar customizado do projeto. Avatares do sistema não podem ser excluídos. |
| **Projects - Delete project property** | **DELETE** | Deleta uma propriedade de um projeto. Requer permissão Administer Jira ou Administer Projects. |
| **Projects - Get accessible project type by key** | **GET** | Retorna um tipo de projeto se acessível ao usuário. |
| **Projects - Get all project avatars** | **GET** | Retorna todos os avatares do projeto agrupados por avatares de sistema e personalizados. |
| **Projects - Get all project types** | **GET** | Retorna todos os tipos de projeto, com ou sem licença válida. |
| **Projects - Get all projects** | **GET** | Retorna todos os projetos visíveis ao usuário. Descontinuado; use Obter projetos paginados. |
| **Projects - Get all statuses for project** | **GET** | Retorna os status válidos para um projeto agrupados por tipo de issue. |
| **Projects - Get assigned permission scheme** | **GET** | Retorna o esquema de permissão associado ao projeto. |
| **Projects - Get fields for projects** | **GET** | Retorna uma lista paginada de campos para os projetos e tipos de trabalho solicitados. |
| **Projects - Get licensed project types** | **GET** | Retorna todos os tipos de projeto com licença válida. |
| **Projects - Get project** | **GET** | Retorna os detalhes do projeto. |
| **Projects - Get project components** | **GET** | Retorna todos os componentes do projeto. |
| **Projects - Get project components paginated** | **GET** | Retorna uma lista paginada de todos os componentes do projeto. |
| **Projects - Get project features** | **GET** | Retorna a lista de recursos do projeto. |
| **Projects - Get project issue security levels** | **GET** | Retorna todos os níveis de segurança de issue do projeto acessíveis ao usuário. |
| **Projects - Get project issue security scheme** | **GET** | Retorna o esquema de segurança de issue associado ao projeto. |
| **Projects - Get project issue type hierarchy** | **GET** | Retorna a hierarquia de tipos de issue para um projeto next-gen (Epic, Stories/Tasks/Bugs, Subtasks). |
| **Projects - Get project notification scheme** | **GET** | Retorna o esquema de notificação associado ao projeto. |
| **Projects - Get project property** | **GET** | Retorna o valor de uma propriedade do projeto. Requer permissão Browse Projects. |
| **Projects - Get project property keys** | **GET** | Retorna todas as chaves de propriedade do projeto. |
| **Projects - Get project role details** | **GET** | Retorna todas as funções de projeto com seus detalhes. A lista é compartilhada por todos os projetos. |
| **Projects - Get project role for project** | **GET** | Retorna os detalhes de uma função de projeto e os atores associados, ordenados por nome de exibição. |
| **Projects - Get project roles for project** | **GET** | Retorna uma lista de funções de projeto com seus nomes e URLs. Requer permissão Administer Projects ou Administer Jira. |
| **Projects - Get project type by key** | **GET** | Retorna um tipo de projeto. |
| **Projects - Get project versions** | **GET** | Retorna todas as versões em um projeto sem paginação. |
| **Projects - Get project versions paginated** | **GET** | Retorna uma lista paginada de todas as versões em um projeto. |
| **Projects - Get project's sender email** | **GET** | Retorna o endereço de email do remetente do projeto. |
| **Projects - Get projects paginated** | **GET** | Retorna uma lista paginada de projetos visíveis ao usuário. |
| **Projects - Get recent projects** | **GET** | Retorna uma lista de até 20 projetos recentemente visualizados pelo usuário. |
| **Projects - Get the classification configuration for a project** | **GET** | Retorna a configuração de classificação consolidada para a página de configurações do projeto. |
| **Projects - Get the default data classification level of a project** | **GET** | Retorna a classificação de dados padrão do projeto. |
| **Projects - Load project avatar** | **POST** | Carrega um avatar para o projeto com tipos de imagem JPEG, GIF ou PNG. |
| **Projects - Remove the default data classification level from a project** | **DELETE** | Remove o nível de classificação de dados padrão do projeto. |
| **Projects - Restore deleted or archived project** | **POST** | Restaura um projeto arquivado ou no lixo do Jira. |
| **Projects - Set actors for project role** | **PUT** | Define os atores de uma função de projeto, substituindo todos os existentes. Para adicionar sem sobrescrever, use Add actors. |
| **Projects - Set project avatar** | **PUT** | Define o avatar exibido para o projeto. |
| **Projects - Set project feature state** | **PUT** | Define o estado de um recurso do projeto. |
| **Projects - Set project property** | **PUT** | Define o valor de uma propriedade do projeto. O corpo deve ser um JSON válido não vazio, máximo 32768 caracteres. |
| **Projects - Set project's sender email** | **PUT** | Define o endereço de email do remetente do projeto. Uma string vazia restaura o endereço padrão. |
| **Projects - Update project** | **PUT** | Atualiza os detalhes do projeto. Todos os parâmetros são opcionais. |
| **Projects - Update the default data classification level of a project** | **PUT** | Atualiza o nível de classificação de dados padrão do projeto. |

#### Project Categories

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Project Categories - Create project category** | **POST** | Cria uma categoria de projeto. Requer permissão Administer Jira. |
| **Project Categories - Delete project category** | **DELETE** | Deleta uma categoria de projeto. Requer permissão Administer Jira. |
| **Project Categories - Get all project categories** | **GET** | Retorna todas as categorias de projeto. |
| **Project Categories - Get project category by ID** | **GET** | Retorna uma categoria de projeto por ID. |
| **Project Categories - Update project category** | **PUT** | Atualiza uma categoria de projeto. Requer permissão Administer Jira. |

#### Project Roles

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Project Roles - Add default actors to project role** | **POST** | Adiciona atores padrão (grupos ou usuários) a uma função de projeto. Alterar os atores padrão não afeta membros já associados. Requer permissão Administrador do Jira. |
| **Project Roles - Create project role** | **POST** | Cria uma nova função de projeto sem atores padrão. Use Add default actors para adicionar atores depois. |
| **Project Roles - Delete default actors from project role** | **DELETE** | Remove atores padrão (grupos ou usuários) de uma função de projeto. Alterar os atores padrão não afeta membros já associados. Requer permissão Administrador do Jira. |
| **Project Roles - Delete project role** | **DELETE** | Deleta uma função de projeto. Deve-se especificar uma função substituta se em uso. |
| **Project Roles - Fully update project role** | **PUT** | Atualiza o nome e descrição de uma função de projeto. Ambos devem estar presentes. |
| **Project Roles - Get all project roles** | **GET** | Retorna uma lista de todas as funções de projeto com seus detalhes e atores padrão. |
| **Project Roles - Get default actors for project role** | **GET** | Retorna os atores padrão para uma função de projeto. |
| **Project Roles - Get project role by ID** | **GET** | Retorna os detalhes de uma função de projeto e seus atores padrão, ordenados por nome. |
| **Project Roles - Partial update project role** | **POST** | Atualiza o nome ou descrição de uma função de projeto. Não é possível atualizar ambos simultaneamente. |

#### Project Validation

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Project Validation - Get valid project key** | **GET** | Valida a chave de um projeto e gera uma chave aleatória válida se for inválida ou em uso. |
| **Project Validation - Get valid project name** | **GET** | Verifica se o nome do projeto não está em uso. Se estiver, tenta gerar um válido adicionando um número. |
| **Project Validation - Validate project key** | **GET** | Valida a chave de um projeto confirmando se é válida e não está em uso. |

#### Components

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Components - Create component** | **POST** | Cria um componente. Requer permissão de administração de projetos ou administrador do Jira. |
| **Components - Delete component** | **DELETE** | Exclui um componente. Requer permissão de administração de projetos ou administrador do Jira. |
| **Components - Find components for projects** | **GET** | Retorna lista paginada de componentes do projeto, incluindo globais. Requer permissão de navegação do projeto. |
| **Components - Get component** | **GET** | Retorna um componente. Requer permissão de navegação do projeto. |
| **Components - Get component issues count** | **GET** | Retorna a quantidade de issues atribuídas ao componente. Sem permissões necessárias. |
| **Components - Update component** | **PUT** | Atualiza um componente. Pode remover líder definindo `leadAccountId` como vazio. Requer permissão apropriada. |

#### Versions

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Versions - Create related work** | **POST** | Cria um item de trabalho relacionado à versão. |
| **Versions - Create version** | **POST** | Cria uma versão do projeto. |
| **Versions - Delete and replace version** | **POST** | Remove uma versão do projeto e substitui em issues com versão alternativa. |
| **Versions - Delete related work** | **DELETE** | Remove um item de trabalho relacionado à versão. |
| **Versions - Delete version** | **DELETE** | Remove uma versão do projeto, opcionalmente substituindo em issues. |
| **Versions - Get related work** | **GET** | Retorna itens de trabalho relacionados à versão. |
| **Versions - Get version** | **GET** | Retorna uma versão do projeto. |
| **Versions - Get version's related issues count** | **GET** | Retorna contagens de issues relacionadas: corrigidas, afetadas e em campos customizados. |
| **Versions - Get version's unresolved issues count** | **GET** | Retorna contagem de issues não resolvidas da versão. |
| **Versions - Merge versions** | **PUT** | Mescla duas versões do projeto, movendo issues de uma para outra. |
| **Versions - Move version** | **POST** | Modifica a sequência da versão no projeto, alterando sua ordem de exibição. |
| **Versions - Update related work** | **PUT** | Atualiza um item de trabalho relacionado à versão. |
| **Versions - Update version** | **PUT** | Atualiza uma versão do projeto. |

### Campos, status e prioridades

*78 operações.*

#### Fields

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Fields - Add issue types to context** | **PUT** | Adiciona tipos de issues a um contexto de campo personalizado. Não é permitido a partir de abril de 2026. Requer permissão Administrar Jira. |
| **Fields - Assign custom field context to projects** | **PUT** | Atribui um contexto de campo personalizado a projetos. Requer permissão *Administrar Jira*. |
| **Fields - Create associations** | **PUT** | Associa campos a projetos e tipos de issues. Até 50 campos e 100 projetos por solicitação. Requer permissão Administrar Jira. |
| **Fields - Create custom field** | **POST** | Cria um campo personalizado. Requer permissão Administrar Jira. |
| **Fields - Create custom field context** | **POST** | Cria um contexto de campo personalizado. Se nenhum projeto for especificado, cria um contexto global. Requer permissão Administrar Jira. |
| **Fields - Create custom field options (context)** | **POST** | Cria opções de campos personalizados de seleção. Máximo 1000 opções por solicitação e 10000 por campo. Requer permissão Administrar Jira. |
| **Fields - Create issue field option** | **POST** | Cria uma opção para um campo de seleção. Funciona apenas com opções adicionadas por aplicativos Connect. Máximo 10000 opções por campo. Requer *Administrar Jira*. |
| **Fields - Delete custom field** | **DELETE** | Remove um campo personalizado. Operação assíncrona. Requer permissão *Administrar Jira*. |
| **Fields - Delete custom field context** | **DELETE** | Deleta um contexto de campo personalizado. O contexto global não pode ser removido a partir de abril de 2026. Requer permissão Administrar Jira. |
| **Fields - Delete custom field options (context)** | **DELETE** | Deleta uma opção de campo personalizado. As opções em cascata não podem ser deletadas sem deletar suas sub-opções. Requer permissão Administrar Jira. |
| **Fields - Delete issue field option** | **DELETE** | Remove uma opção de um campo de seleção. Funciona apenas com opções adicionadas por aplicativos Connect. Requer permissão *Administrar Jira*. |
| **Fields - Get all issue field options** | **GET** | Obtém uma lista paginada de todas as opções de um campo de seleção. Funciona apenas com opções adicionadas por aplicativos Connect. Requer permissão *Administrar Jira*. |
| **Fields - Get contexts for a field** | **GET** | Obtém uma lista paginada dos contextos em que um campo é usado. Operação descontinuada. |
| **Fields - Get custom field contexts** | **GET** | Retorna uma lista paginada de contextos para um campo personalizado. Requer permissão Administrar Jira ou Editar Fluxo de Trabalho. |
| **Fields - Get custom field contexts default values** | **GET** | Retorna uma lista paginada de valores padrão para um campo personalizado. API descontinuada; será removida em outubro de 2026. Requer permissão Administrar Jira. |
| **Fields - Get custom field contexts for projects and issue types** | **POST** | Retorna uma lista paginada de mapeamentos de projetos e tipos de issues com seus contextos de campo personalizado. Requer permissão Administrar Jira. |
| **Fields - Get custom field options (context)** | **GET** | Retorna uma lista paginada de todas as opções de campo personalizado para um contexto. Requer permissão Administrar Jira ou Editar Fluxo de Trabalho. |
| **Fields - Get default values for a custom field grouped by context and issue type** | **GET** | Retorna uma lista paginada de valores padrão agrupados por contexto de campo personalizado e tipo de issue. Requer permissão Administrar Jira. |
| **Fields - Get field project associations** | **GET** | Retorna uma lista paginada de associações de projetos para um campo personalizado. Requer permissão Administrar Jira. |
| **Fields - Get fields** | **GET** | Retorna campos de issues do sistema e personalizados de acordo com regras de visibilidade, configuração global e permissão. |
| **Fields - Get fields in trash paginated** | **GET** | Retorna uma lista paginada de campos personalizados na lixeira. Requer permissão Administrar Jira. |
| **Fields - Get fields paginated** | **GET** | Retorna uma lista paginada de campos de projetos Classic do Jira, podendo ser filtrados por ID, nome ou descrição. |
| **Fields - Get issue field option** | **GET** | Obtém uma opção de um campo de seleção. Funciona apenas com opções adicionadas por aplicativos Connect. Requer permissão *Administrar Jira*. |
| **Fields - Get issue types for custom field context** | **GET** | Retorna uma lista paginada de mapeamentos de contexto para tipos de issues. Requer permissão Administrar Jira. |
| **Fields - Get project mappings for custom field context** | **GET** | Retorna uma lista paginada de mapeamentos de contexto para projetos de um campo personalizado. Requer permissão Administrar Jira. |
| **Fields - Get screens for a field** | **GET** | Obtém uma lista paginada das telas em que um campo é usado. Requer permissão *Administrar Jira*. |
| **Fields - Get selectable issue field options** | **GET** | Obtém uma lista paginada de opções de um campo de seleção que o usuário pode visualizar e selecionar. Funciona apenas com opções adicionadas por aplicativos Connect. |
| **Fields - Get visible issue field options** | **GET** | Obtém uma lista paginada de opções de um campo de seleção que o usuário pode visualizar. Funciona apenas com opções adicionadas por aplicativos Connect. |
| **Fields - Move custom field to trash** | **POST** | Move um campo personalizado para a lixeira. Requer permissão *Administrar Jira*. |
| **Fields - Remove associations** | **DELETE** | Desassocia campos de projetos e tipos de issues. Até 50 campos e 100 projetos por solicitação. Requer permissão Administrar Jira. |
| **Fields - Remove custom field context from projects** | **POST** | Remove um contexto de campo personalizado de projetos. Requer permissão *Administrar Jira*. |
| **Fields - Remove issue types from context** | **POST** | Remove tipos de issues de um contexto de campo personalizado. Requer permissão Administrar Jira. |
| **Fields - Reorder custom field options (context)** | **PUT** | Altera a ordem das opções de campo personalizado ou opções em cascata em um contexto. Requer permissão Administrar Jira. |
| **Fields - Replace custom field options** | **DELETE** | Substitui as opções de um campo personalizado. Requer permissão Administrar Jira. |
| **Fields - Replace issue field option** | **DELETE** | Remove uma opção de um campo de seleção de todas as issues. Operação assíncrona. Funciona apenas com opções adicionadas por aplicativos Connect. Requer *Administrar Jira*. |
| **Fields - Restore custom field from trash** | **POST** | Restaura um campo personalizado da lixeira. Requer permissão *Administrar Jira*. |
| **Fields - Set custom field contexts default values** | **PUT** | Define valores padrão para contextos de um campo personalizado. API descontinuada; será removida em outubro de 2026. Requer permissão Administrar Jira. |
| **Fields - Update custom field** | **PUT** | Atualiza um campo personalizado. Requer permissão Administrar Jira. |
| **Fields - Update custom field context** | **PUT** | Atualiza um contexto de campo personalizado. Requer permissão Administrar Jira. |
| **Fields - Update custom field options (context)** | **PUT** | Atualiza as opções de um campo personalizado. Requer permissão Administrar Jira. |
| **Fields - Update issue field option** | **PUT** | Atualiza ou cria uma opção de um campo de seleção. O ID da opção deve ser fornecido na URL e no corpo. Funciona apenas com opções adicionadas por aplicativos Connect. Requer *Administrar Jira*. |

#### Field Configurations

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Field Configurations - Create field configuration** | **POST** | Cria uma configuração de campo. Operação descontinuada; use Esquemas de Campo. Apenas para projetos gerenciados pela empresa. Requer *Administrar Jira*. |
| **Field Configurations - Delete field configuration** | **DELETE** | Remove uma configuração de campo. Operação descontinuada; use Esquemas de Campo. Apenas para projetos gerenciados pela empresa. Requer *Administrar Jira*. |
| **Field Configurations - Get all field configurations** | **GET** | Obtém uma lista paginada de configurações de campo. Operação descontinuada; use Esquemas de Campo. Apenas para projetos gerenciados pela empresa. Requer *Administrar Jira*. |
| **Field Configurations - Get field configuration items** | **GET** | Obtém uma lista paginada de campos de uma configuração. Operação descontinuada; use Esquemas de Campo. Apenas para projetos gerenciados pela empresa. Requer *Administrar Jira*. |
| **Field Configurations - Update field configuration** | **PUT** | Atualiza uma configuração de campo. Operação descontinuada; use Esquemas de Campo. Apenas para projetos gerenciados pela empresa. Requer *Administrar Jira*. |
| **Field Configurations - Update field configuration items** | **PUT** | Atualiza campos em uma configuração. Operação descontinuada; use Esquemas de Campo. Apenas para projetos gerenciados pela empresa. Requer *Administrar Jira*. |

#### Custom Field Options

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Custom Field Options - Get custom field option** | **GET** | Retorna uma opção de campo personalizado (ex: em uma lista selecionável). Requer permissão apropriada. |

#### Statuses

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Statuses - Bulk create statuses** | **POST** | Cria status para escopo global ou de projeto. Requer permissão Administrar projetos ou Administrador do Jira. |
| **Statuses - Bulk delete Statuses** | **DELETE** | Deleta status por ID. Requer permissão Administrar projetos ou Administrador do Jira. |
| **Statuses - Bulk get statuses** | **GET** | Retorna lista de status especificados por um ou mais IDs. Requer permissão Administrar projetos ou Administrador do Jira. |
| **Statuses - Bulk get statuses by name** | **GET** | Retorna lista de status especificados por um ou mais nomes. Requer permissão Administrar projetos, Administrador do Jira ou Procurar projetos. |
| **Statuses - Bulk update statuses** | **PUT** | Atualiza status por ID. Requer permissão Administrar projetos ou Administrador do Jira. |
| **Statuses - Get all statuses** | **GET** | Retorna uma lista de todos os status associados a fluxos de trabalho ativos. Requer permissão Procurar projetos. |
| **Statuses - Get issue type usages by status and project** | **GET** | Retorna uma página de tipos de issue em um projeto que usam um status fornecido. |
| **Statuses - Get project usages by status** | **GET** | Retorna uma página de projetos que usam um status fornecido. |
| **Statuses - Get status** | **GET** | Retorna um status. O status deve estar associado a um fluxo de trabalho ativo. Requer permissão Procurar projetos. |
| **Statuses - Get workflow usages by status** | **GET** | Retorna uma página de fluxos de trabalho que usam um status fornecido. |
| **Statuses - Search statuses paginated** | **GET** | Retorna lista paginada de status que correspondem a pesquisa por nome ou projeto. Requer permissão Administrar projetos ou Administrador do Jira. |

#### Status Categories

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Status Categories - Get all status categories** | **GET** | Retorna uma lista de todas as categorias de status. Requer permissão de acesso ao Jira. |
| **Status Categories - Get status category** | **GET** | Retorna uma categoria de status. Requer permissão de acesso ao Jira. |

#### Priorities

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Priorities - Create priority** | **POST** | Cria uma prioridade de issue. |
| **Priorities - Delete priority** | **DELETE** | Exclui uma prioridade de issue. Operação assíncrona; acompanhe o status no link de localização. |
| **Priorities - Get priorities** | **GET** | Retorna a lista de todas as prioridades de issues. Descontinuado; use Pesquisar prioridades. |
| **Priorities - Get priority** | **GET** | Retorna uma prioridade de issue. Para múltiplas prioridades, use Pesquisar prioridades. |
| **Priorities - Move priorities** | **PUT** | Altera a ordem das prioridades de issues. |
| **Priorities - Search priorities** | **GET** | Retorna uma lista paginada de prioridades filtradas por IDs, projetos ou configuração padrão. |
| **Priorities - Set default priority** | **PUT** | Define a prioridade padrão para issues. |
| **Priorities - Update priority** | **PUT** | Atualiza uma prioridade de issue. |

#### Resolutions

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Resolutions - Create resolution** | **POST** | Cria uma resolução de issue. Requer permissão Administer Jira. |
| **Resolutions - Delete resolution** | **DELETE** | Deleta uma resolução de issue. Esta operação é assíncrona. |
| **Resolutions - Get resolution** | **GET** | Retorna um valor de resolução de issue. |
| **Resolutions - Get resolutions** | **GET** | Retorna uma lista de todos os valores de resolução de issue. |
| **Resolutions - Move resolutions** | **PUT** | Altera a ordem das resoluções de issue. Requer permissão Administer Jira. |
| **Resolutions - Search resolutions** | **GET** | Retorna uma lista paginada de resoluções filtrada por IDs e configuração padrão. |
| **Resolutions - Set default resolution** | **PUT** | Define a resolução padrão de issue. Requer permissão Administer Jira. |
| **Resolutions - Update resolution** | **PUT** | Atualiza uma resolução de issue. Requer permissão Administer Jira. |

#### Labels

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Labels - Get all labels** | **GET** | Retorna uma lista paginada de rótulos. |

### Usuários, grupos e permissões

*46 operações.*

#### Users

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Users - Bulk get users** | **GET** | Retorna lista paginada de usuários especificados por um ou mais IDs de conta. Requer permissão de acesso ao Jira. |
| **Users - Create user** | **POST** | Cria um usuário. Requer permissão Administrador do Jira e ser administrador da organização. |
| **Users - Delete user** | **DELETE** | Deleta um usuário de Jira. A conta Atlassian não é deletada. Requer associação ao grupo site-admin. |
| **Users - Delete user property** | **DELETE** | Remove uma propriedade do usuário. |
| **Users - Find user keys by query** | **GET** | Encontra usuários com consulta estruturada e retorna lista paginada de chaves. |
| **Users - Find users** | **GET** | Retorna lista paginada de usuários ativos que correspondem à string de busca. |
| **Users - Find users assignable to issues** | **GET** | Retorna usuários que podem ser atribuídos a uma issue. Requer permissão Procurar usuários e grupos ou Atribuir issues. |
| **Users - Find users assignable to projects** | **GET** | Retorna usuários que podem ser atribuídos a issues em um ou mais projetos. Requer permissão Procurar projetos. |
| **Users - Find users by query** | **GET** | Encontra usuários com consulta estruturada e retorna lista paginada de detalhes. |
| **Users - Find users for picker** | **GET** | Retorna usuários cujos atributos correspondem ao termo de consulta. Requer permissão Procurar usuários e grupos. |
| **Users - Find users with browse permission** | **GET** | Retorna usuários cujos atributos correspondem à busca e têm permissão para visualizar issues. |
| **Users - Find users with permissions** | **GET** | Retorna usuários que têm permissões específicas em um projeto ou issue. Requer permissão Administrador do Jira ou Administrar projetos. |
| **Users - Get account IDs for users** | **GET** | Retorna os IDs de conta dos usuários especificados. Requer permissão de acesso ao Jira. |
| **Users - Get all users** | **GET** | Retorna lista de todos os usuários, incluindo ativos, inativos e deletados. |
| **Users - Get all users default** | **GET** | Retorna lista de todos os usuários, incluindo ativos, inativos e deletados. |
| **Users - Get user** | **GET** | Retorna um usuário. Controles de privacidade são aplicados na resposta. Requer permissão Procurar usuários e grupos. |
| **Users - Get user default columns** | **GET** | Retorna as colunas padrão de tabela de issues para o usuário. Requer permissão Administrador do Jira ou de acesso ao Jira. |
| **Users - Get user email** | **GET** | Retorna o endereço de e-mail de um usuário independentemente da configuração de visibilidade do perfil. |
| **Users - Get user email bulk** | **GET** | Retorna endereços de e-mail de usuários independentemente de configurações de visibilidade do perfil. |
| **Users - Get user groups** | **GET** | Retorna os grupos aos quais um usuário pertence. Requer permissão Procurar usuários e grupos. |
| **Users - Get user property** | **GET** | Retorna o valor de uma propriedade do usuário. |
| **Users - Get user property keys** | **GET** | Retorna as chaves de todas as propriedades de um usuário. Requer permissão Administrador do Jira ou de acesso ao Jira. |
| **Users - Reset user default columns** | **DELETE** | Redefine as colunas padrão de tabela de issues do usuário para o padrão do sistema. Requer permissão Administrador do Jira ou de acesso ao Jira. |
| **Users - Set user default columns** | **PUT** | Define as colunas padrão de tabela de issues para o usuário. Requer permissão Administrador do Jira ou de acesso ao Jira. |
| **Users - Set user property** | **PUT** | Define o valor de uma propriedade do usuário para armazenar dados customizados. |

#### Groups

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Groups - Add user to group** | **POST** | Adiciona um usuário a um grupo. Requer administração do site. |
| **Groups - Bulk get groups** | **GET** | Obtém uma lista paginada de grupos. Requer permissão de navegação de usuários e grupos. |
| **Groups - Create group** | **POST** | Cria um grupo. Requer administração do site. |
| **Groups - Find groups** | **GET** | Retorna lista de grupos cujos nomes contêm a cadeia de consulta, com correspondência destacada para sugestões do seletor de grupos. |
| **Groups - Get group** | **GET** | Obtém todos os usuários de um grupo. Operação descontinuada. Requer permissão de navegação ou administração. |
| **Groups - Get users from group** | **GET** | Obtém uma lista paginada de usuários de um grupo. Requer permissão de navegação ou administração. |
| **Groups - Remove group** | **DELETE** | Remove um grupo. Requer administração do site. |
| **Groups - Remove user from group** | **DELETE** | Remove um usuário de um grupo. Requer administração do site. |

#### Group and User Picker

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Group and User Picker - Find users and groups** | **GET** | Retorna lista de usuários e grupos correspondentes a uma cadeia de caracteres, com opção de refinar a busca por projetos e tipos de issue. |

#### Myself

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Myself - Get current user** | **GET** | Retorna os detalhes do usuário atual. |

#### My Permissions

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **My Permissions - Get my permissions** | **GET** | Retorna uma lista de permissões do usuário em contextos globais, de projetos, issues e comentários. |

#### My Preferences

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **My Preferences - Delete preference** | **DELETE** | Exclui uma preferência do usuário e restaura o valor padrão das configurações do sistema. |
| **My Preferences - Get locale** | **GET** | Retorna a localidade do usuário, ou a localidade detectada pelo navegador se nenhuma preferência estiver definida. |
| **My Preferences - Get preference** | **GET** | Retorna o valor de uma preferência do usuário atual, como localidade, fuso horário e configurações de notificação. |
| **My Preferences - Set locale** | **PUT** | Define a localidade do usuário. A localidade deve ser suportada pela instância de Jira. |
| **My Preferences - Set preference** | **PUT** | Cria ou atualiza uma preferência do usuário ao enviar uma sequência de texto simples com até 255 caracteres. |

#### Permissions

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Permissions - Get all permissions** | **GET** | Retorna todas as permissões globais, de projeto e adicionadas por plugins. |
| **Permissions - Get bulk permissions** | **POST** | Retorna as permissões globais ou de projeto concedidas a um usuário em projetos e issues específicas. |
| **Permissions - Get permitted projects** | **POST** | Retorna todos os projetos onde o usuário tem as permissões de projeto concedidas. |

#### Application Roles

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Application Roles - Get all application roles** | **GET** | Retorna todas as funções da aplicação. Requer permissão de administrador do Jira. |
| **Application Roles - Get application role** | **GET** | Retorna uma função da aplicação. Requer permissão de administrador do Jira. |

### Painéis e filtros

*36 operações.*

#### Dashboards

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Dashboards - Add gadget to dashboard** | **POST** | Adiciona um gadget a um painel. |
| **Dashboards - Bulk edit dashboards** | **PUT** | Edita em lote painéis. O número máximo de painéis a serem editados simultaneamente é 100. Os painéis devem ser de propriedade do usuário ou este deve ser administrador. |
| **Dashboards - Copy dashboard** | **POST** | Copia um painel. Os valores fornecidos no parâmetro `dashboard` substituem os do painel copiado. O painel deve ser de propriedade ou estar compartilhado com o usuário. |
| **Dashboards - Create dashboard** | **POST** | Cria um painel. Sem permissões necessárias. |
| **Dashboards - Delete dashboard** | **DELETE** | Deleta um painel. O painel deve ser de propriedade do usuário. |
| **Dashboards - Delete dashboard item property** | **DELETE** | Deleta uma propriedade de item de painel. Requer permissão de edição do painel. |
| **Dashboards - Get all dashboards** | **GET** | Retorna lista de painéis do usuário (próprios ou compartilhados). Sem permissões necessárias. |
| **Dashboards - Get available gadgets** | **GET** | Retorna uma lista de todos os gadgets disponíveis que podem ser adicionados aos painéis. |
| **Dashboards - Get dashboard** | **GET** | Retorna um painel. O painel deve estar compartilhado com o usuário ou ser de sua propriedade. |
| **Dashboards - Get dashboard item property** | **GET** | Retorna a chave e o valor de uma propriedade de item de painel. Requer permissão de leitura do painel ou que este tenha sido compartilhado. |
| **Dashboards - Get dashboard item property keys** | **GET** | Retorna as chaves de todas as propriedades de um item de painel. Requer permissão de leitura do painel ou que este tenha sido compartilhado. |
| **Dashboards - Get gadgets** | **GET** | Retorna uma lista de gadgets em um painel. Retorna gadgets por IDs, chave de módulo, URIs ou todos quando nenhum parâmetro é definido. |
| **Dashboards - Remove gadget from dashboard** | **DELETE** | Remove um gadget de um painel. Outros gadgets na mesma coluna são movidos para cima para preencher a posição vazia. |
| **Dashboards - Search for dashboards** | **GET** | Retorna uma lista paginada de painéis que podem ser filtrados por atributos específicos como nome. Os painéis devolvidos dependem das permissões do usuário. |
| **Dashboards - Set dashboard item property** | **PUT** | Define o valor de uma propriedade de item de painel para armazenar dados personalizados. O valor deve ser um JSON válido com no máximo 32768 caracteres. |
| **Dashboards - Update dashboard** | **PUT** | Atualiza um painel, substituindo todos os detalhes do painel pelos fornecidos. O painel deve ser de propriedade do usuário. |
| **Dashboards - Update gadget on dashboard** | **PUT** | Altera o título, posição e cor de um gadget em um painel. |

#### Filters

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Filters - Add filter as favorite** | **PUT** | Adiciona um filtro aos favoritos do usuário. O usuário deve ter acesso ao filtro. Requer acesso ao Jira. |
| **Filters - Add share permission** | **POST** | Adiciona uma permissão de compartilhamento a um filtro. Permissão global sobrescreve outras. Requer permissão *Compartilhar painéis e filtros*. |
| **Filters - Change filter owner** | **PUT** | Altera o proprietário de um filtro. Usuário deve ser o proprietário ou ter permissão *Administrar Jira*. Requer acesso ao Jira. |
| **Filters - Create filter** | **POST** | Cria um filtro. O filtro é compartilhado de acordo com o escopo de compartilhamento padrão. Requer acesso ao Jira. |
| **Filters - Delete filter** | **DELETE** | Remove um filtro. Apenas o criador ou administrador do Jira pode deletar. Requer acesso ao Jira. |
| **Filters - Delete share permission** | **DELETE** | Remove uma permissão de compartilhamento de um filtro. O usuário deve ser o proprietário. Requer acesso ao Jira. |
| **Filters - Get columns** | **GET** | Obtém as colunas configuradas para um filtro. Operação pode ser acessada anonimamente. |
| **Filters - Get default share scope** | **GET** | Obtém as configurações de compartilhamento padrão para filtros e painéis novos de um usuário. Requer acesso ao Jira. |
| **Filters - Get favorite filters** | **GET** | Obtém os filtros favoritos visíveis do usuário. Operação pode ser acessada anonimamente. |
| **Filters - Get filter** | **GET** | Obtém um filtro. Operação pode ser acessada anonimamente. |
| **Filters - Get my filters** | **GET** | Obtém os filtros do usuário. Se includeFavourites for verdadeiro, também retorna os filtros favoritos. Requer acesso ao Jira. |
| **Filters - Get share permission** | **GET** | Obtém uma permissão de compartilhamento de um filtro. Operação pode ser acessada anonimamente. |
| **Filters - Get share permissions** | **GET** | Obtém as permissões de compartilhamento de um filtro. Operação pode ser acessada anonimamente. |
| **Filters - Remove filter as favorite** | **DELETE** | Remove um filtro dos favoritos do usuário. Requer acesso ao Jira. |
| **Filters - Reset columns** | **DELETE** | Restaura a configuração de colunas de um filtro para o padrão. O usuário deve ser o proprietário. Requer acesso ao Jira. |
| **Filters - Search for filters** | **GET** | Obtém uma lista paginada de filtros que correspondem aos critérios especificados. Operação pode ser acessada anonimamente. |
| **Filters - Set columns** | **PUT** | Define as colunas para um filtro. Apenas campos navegáveis podem ser definidos. O usuário deve ser o proprietário do filtro. Requer acesso ao Jira. |
| **Filters - Set default share scope** | **PUT** | Define o compartilhamento padrão para filtros e painéis novos de um usuário. Requer acesso ao Jira. |
| **Filters - Update filter** | **PUT** | Atualiza um filtro. O usuário deve ser o proprietário do filtro. Requer acesso ao Jira. |

### Ágil

*61 operações.*

#### Boards

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Boards - Create board** | **POST** | Cria um novo quadro com nome, tipo (scrum ou kanban) e ID do filtro. |
| **Boards - Delete board** | **DELETE** | Remove um quadro. Admins podem remover mesmo sem permissão de visualização. |
| **Boards - Delete board property** | **DELETE** | Remove uma propriedade do quadro. Requer permissão para modificar o quadro. |
| **Boards - Get all boards** | **GET** | Retorna todos os quadros aos quais o usuário tem permissão de visualizar. |
| **Boards - Get all quick filters** | **GET** | Retorna todos os filtros rápidos de um quadro. |
| **Boards - Get all sprints** | **GET** | Retorna todos os sprints de um quadro. Inclui apenas aqueles que o usuário tem permissão para visualizar. |
| **Boards - Get all versions** | **GET** | Retorna todas as versões de um quadro, ordenadas pelo nome do projeto e sequência do usuário. Requer permissão para visualizar. |
| **Boards - Get approximate issue count for backlog** | **GET** | Retorna a contagem aproximada de issues do backlog do quadro. Equivalente a contar issues em todas as páginas. |
| **Boards - Get approximate issue count for board** | **GET** | Retorna a contagem aproximada de issues do quadro. Equivalente a contar issues em todas as páginas. |
| **Boards - Get board** | **GET** | Retorna um quadro pelo seu ID. |
| **Boards - Get board by filter id** | **GET** | Retorna quadros que utilizam um ID de filtro específico. |
| **Boards - Get board issues for epic** | **GET** | Retorna issues do quadro que pertencem a um épico específico. |
| **Boards - Get board issues for epic (enhanced)** | **GET** | Retorna issues de um épico no quadro com paginação por token. Inclui apenas aquelas que o usuário tem permissão para visualizar, ordenadas por rank. |
| **Boards - Get board issues for sprint** | **GET** | Retorna as issues do sprint para o qual você tem acesso, com campos adicionais como sprint, sprints fechados e épico. Ordenadas por rank. |
| **Boards - Get board issues for sprint (enhanced)** | **GET** | Retorna issues do sprint com paginação por token e campos adicionais como sprint, sprints fechados e épico. Ordenadas por rank. |
| **Boards - Get board property** | **GET** | Retorna o valor da propriedade de um quadro para uma chave fornecida. Requer permissão para visualizar o quadro. |
| **Boards - Get board property keys** | **GET** | Retorna as chaves de todas as propriedades do quadro. Requer permissão para visualizar o quadro. |
| **Boards - Get configuration** | **GET** | Retorna a configuração do quadro: colunas, status, estimativa e ranking. |
| **Boards - Get epics** | **GET** | Retorna todos os épicos do quadro aos quais o usuário tem permissão. |
| **Boards - Get features for board** | **GET** | Retorna os recursos habilitados no quadro. |
| **Boards - Get issues for backlog** | **GET** | Retorna issues do backlog do quadro, ordenadas por rank. |
| **Boards - Get issues for backlog (enhanced)** | **GET** | Retorna issues do backlog com paginação por token. Inclui issues incompletas não atribuídas a sprints futuros ou ativos, ordenadas por rank. |
| **Boards - Get issues for board** | **GET** | Retorna issues do quadro cujo status está mapeado para coluna. |
| **Boards - Get issues for board (enhanced)** | **GET** | Retorna issues do quadro com paginação por token. Uma issue pertence ao quadro se seu status está mapeado para uma coluna. |
| **Boards - Get issues without epic for board** | **GET** | Retorna issues do quadro que não pertencem a nenhum épico. |
| **Boards - Get issues without epic for board (enhanced)** | **GET** | Retorna issues sem épico no quadro com paginação por token. Inclui apenas aquelas que o usuário tem permissão para visualizar, ordenadas por rank. |
| **Boards - Get projects** | **GET** | Retorna projetos associados ao quadro através do filtro ou issues. |
| **Boards - Get projects full** | **GET** | Retorna todos os projetos associados estaticamente ao quadro. Um projeto é associado se o filtro do quadro garante que as issues retornadas vêm do conjunto definido na JQL. |
| **Boards - Get quick filter** | **GET** | Retorna um filtro rápido pelo ID. Requer permissão para visualizar o quadro ao qual pertence. |
| **Boards - Get reports for board** | **GET** | Obtém relatórios para o quadro. |
| **Boards - Move issues to board** | **POST** | Move issues do backlog para o quadro ou faz transição para primeira coluna. |
| **Boards - Set board property** | **PUT** | Define o valor de uma propriedade do quadro. Permite armazenar dados personalizados. Requer permissão para modificar o quadro. |
| **Boards - Toggle features** | **PUT** | Habilita ou desabilita recursos no quadro. |

#### Sprints

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Sprints - Create sprint** | **POST** | Cria um novo sprint futuro. Nome e ID do quadro são obrigatórios. Data de início, fim e objetivo são opcionais. |
| **Sprints - Delete property** | **DELETE** | Remove uma propriedade do sprint. Requer permissão para modificar o sprint. |
| **Sprints - Delete sprint** | **DELETE** | Exclui um sprint. As issues abertas são movidas para o backlog. |
| **Sprints - Get issues for sprint** | **GET** | Retorna todas as issues de um sprint. Inclui apenas aquelas que o usuário tem permissão para visualizar, ordenadas por rank. |
| **Sprints - Get issues for sprint (enhanced)** | **GET** | Retorna issues de um sprint com paginação por token. Inclui apenas aquelas que o usuário tem permissão para visualizar, ordenadas por rank. |
| **Sprints - Get properties keys** | **GET** | Retorna as chaves de todas as propriedades de um sprint. Requer permissão para visualizar o sprint. |
| **Sprints - Get property** | **GET** | Retorna o valor da propriedade de um sprint para uma chave fornecida. Requer permissão para visualizar. |
| **Sprints - Get sprint** | **GET** | Retorna um sprint pelo ID. Requer permissão para visualizar o quadro ou ao menos uma issue do sprint. |
| **Sprints - Move issues to sprint and rank** | **POST** | Move issues para um sprint. Apenas sprints abertos ou ativos. Máximo 50 issues por operação. |
| **Sprints - Partially update sprint** | **POST** | Atualiza parcialmente um sprint. Sprints fechados: apenas nome e objetivo. Para iniciar: mudar estado para 'ativo' com startDate e endDate. |
| **Sprints - Set property** | **PUT** | Define o valor de uma propriedade do sprint. Permite armazenar dados personalizados. Requer permissão para modificar. |
| **Sprints - Swap sprint** | **POST** | Troca a posição de um sprint com outro sprint. |
| **Sprints - Update sprint** | **PUT** | Atualiza completamente um sprint. Campos ausentes são definidos como null. Para sprints fechados: apenas nome e objetivo são alteráveis. |

#### Epics

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Epics - Get epic** | **GET** | Retorna um épico pelo ID. Requer permissão para visualizá-lo. |
| **Epics - Get issues for epic** | **GET** | Retorna issues de um épico. Inclui apenas aquelas que o usuário tem permissão para visualizar, ordenadas por rank. |
| **Epics - Get issues for epic (enhanced)** | **GET** | Retorna issues de um épico com paginação por token. Inclui apenas aquelas que o usuário tem permissão para visualizar, ordenadas por rank. |
| **Epics - Get issues without epic** | **GET** | Retorna issues que não pertencem a nenhum épico. Inclui apenas aquelas que o usuário tem permissão para visualizar, ordenadas por rank. |
| **Epics - Get issues without epic (enhanced)** | **GET** | Retorna issues sem épico com paginação por token. Inclui apenas aquelas que o usuário tem permissão para visualizar, ordenadas por rank. |
| **Epics - Move issues to epic** | **POST** | Move issues para um épico. Uma issue só pode estar em um épico por vez. Requer permissão de edição. Máximo 50 issues. |
| **Epics - Partially update epic** | **POST** | Atualiza parcialmente um épico. Campos ausentes na JSON não são atualizados. Cores válidas: color_1 até color_9. |
| **Epics - Rank epics** | **PUT** | Move (classifica) um épico antes ou depois de outro épico. Usa o campo de classificação padrão se rankCustomFieldId não for definido. |
| **Epics - Remove issues from epic** | **POST** | Remove issues de épicos. Requer permissão de edição para cada issue. Máximo 50 issues por operação. |

#### Backlog

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Backlog - Move issues to backlog** | **POST** | Move issues para o backlog, removendo de sprints futuros e ativos. |
| **Backlog - Move issues to backlog for board** | **POST** | Move issues para backlog do quadro, removendo de sprints ou retirando do quadro. |

#### Agile Issues

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Agile Issues - Estimate issue for board** | **PUT** | Atualiza a estimativa de uma issue. boardId obrigatório. Aceita formatos como 1w, 2d, 3h, 20m ou minutos. Armazenado em segundos. |
| **Agile Issues - Get issue** | **GET** | Retorna uma issue pelo ID ou chave. Inclui campos Agile como sprint, sprints fechados, sinalizado e épico. |
| **Agile Issues - Get issue estimation for board** | **GET** | Retorna a estimativa de uma issue e o campo usado. boardId é obrigatório. Estimativa armazenada internamente em segundos. |
| **Agile Issues - Rank issues** | **PUT** | Move (classifica) issues antes ou depois de outra issue. Máximo 50 issues por operação. Usa classificação padrão se rankCustomFieldId não for definido. |

### Instância e administração

*36 operações.*

#### Configuration

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Configuration - Get all time tracking providers** | **GET** | Retorna todos os provedores de rastreamento de tempo disponíveis. Requer permissão de administrador do Jira. |
| **Configuration - Get global settings** | **GET** | Retorna configurações globais do Jira (subtarefas, rastreamento de tempo, etc.). Requer permissão para acessar Jira. |
| **Configuration - Get selected time tracking provider** | **GET** | Retorna o provedor de rastreamento de tempo selecionado. Requer permissão de administrador do Jira. |
| **Configuration - Get time tracking settings** | **GET** | Retorna as configurações de rastreamento de tempo (formato, unidade padrão, etc.). Requer permissão de administrador do Jira. |
| **Configuration - Select time tracking provider** | **PUT** | Seleciona um provedor de rastreamento de tempo. Requer permissão de administrador do Jira. |
| **Configuration - Set time tracking settings** | **PUT** | Define as configurações de rastreamento de tempo. Requer permissão de administrador do Jira. |

#### Settings

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Settings - Get issue navigator default columns** | **GET** | Retorna as colunas padrão do navegador de issues. Requer permissão Administrador do Jira. |
| **Settings - Set issue navigator default columns** | **PUT** | Define as colunas padrão do navegador de issues. Use múltiplos parâmetros columns para especificar colunas. Requer permissão Administrador do Jira. |

#### Application Properties

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Application Properties - Get advanced settings** | **GET** | Retorna as propriedades da aplicação acessíveis na página de Configurações Avançadas. Requer permissão de administrador do Jira. |
| **Application Properties - Get application property** | **GET** | Retorna todas as propriedades da aplicação ou uma propriedade específica se a chave for fornecida. |
| **Application Properties - Set application property** | **PUT** | Altera o valor de uma propriedade da aplicação. Requer permissão de administrador do Jira. |

#### Announcement Banner

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Announcement Banner - Get announcement banner configuration** | **GET** | Retorna a configuração atual do banner de anúncio. Requer permissão de administrador do Jira. |
| **Announcement Banner - Update announcement banner configuration** | **PUT** | Atualiza a configuração do banner de anúncio. Requer permissão de administrador do Jira. |

#### Auditing

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Auditing - Get audit records** | **GET** | Retorna lista de registros de auditoria filtrados por resumo, categoria, origem de evento, nome, ou data. Requer permissão de administrador do Jira. |

#### Avatars

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Avatars - Delete avatar** | **DELETE** | Deleta um avatar de um projeto, tipo de issue ou prioridade. Requer permissão Administrador do Jira. |
| **Avatars - Get avatar image by ID** | **GET** | Retorna imagem de avatar de projeto, tipo de issue ou prioridade por ID. Permissões variam conforme tipo. |
| **Avatars - Get avatar image by owner** | **GET** | Retorna a imagem de avatar para projeto, tipo de issue ou prioridade. Permissões variam conforme tipo. |
| **Avatars - Get avatar image by type** | **GET** | Retorna a imagem de avatar padrão de projeto, tipo de issue ou prioridade. Sem permissões necessárias. |
| **Avatars - Get avatars** | **GET** | Retorna avatares do sistema e personalizados para projeto, tipo de issue ou prioridade. Permissões variam conforme tipo. |
| **Avatars - Get system avatars by type** | **GET** | Retorna lista de avatares do sistema por tipo de proprietário (tipo de issue, projeto, usuário, prioridade). Sem permissões necessárias. |
| **Avatars - Load avatar** | **POST** | Carrega avatar personalizado para projeto, tipo de issue ou prioridade. Requer permissão Administrador do Jira. |

#### Classification Levels

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Classification Levels - Get all classification levels** | **GET** | Retorna todos os níveis de classificação. Sem permissões necessárias. |

#### Data Policies

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Data Policies - Get data policy for projects** | **GET** | Retorna as políticas de dados dos projetos especificados na solicitação. |
| **Data Policies - Get data policy for the workspace** | **GET** | Retorna a política de dados do espaço de trabalho. |

#### Events

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Events - Get events** | **GET** | Retorna todos os eventos de issues. Requer permissão Administrar Jira. |

#### Instance

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Instance - Get license** | **GET** | Retorna informações de licença sobre a instância do Jira. |

#### License

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **License - Get approximate application license count** | **GET** | Retorna o número aproximado total de contas de usuários para uma única licença Jira. Informação em cache com ciclo de vida de 7 dias. |
| **License - Get approximate license count** | **GET** | Retorna o número aproximado de contas de usuários em todas as licenças do Jira. Esta informação é armazenada em cache com ciclo de vida de 7 dias e pode estar desatualizada. |

#### Server Info

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Server Info - Get Jira instance info** | **GET** | Retorna informações sobre a instância do Jira. Sem permissões necessárias. |

#### Tasks

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Tasks - Cancel task** | **POST** | Cancela uma tarefa. Requer permissão Administrador do Jira ou ser o criador da tarefa. |
| **Tasks - Get task** | **GET** | Retorna o status de uma tarefa assíncrona de longa duração. Detalhes são retidos por 14 dias. Requer permissão Administrador do Jira ou ser o criador da tarefa. |

#### Webhooks

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Webhooks - Delete webhooks by ID** | **DELETE** | Remove webhooks pelo ID. Apenas webhooks do app são removidos. |
| **Webhooks - Extend webhook life** | **PUT** | Estende a vida útil dos webhooks que expiram em 30 dias. |
| **Webhooks - Get dynamic webhooks for app** | **GET** | Retorna lista paginada dos webhooks registrados pelo app. |
| **Webhooks - Get failed webhooks** | **GET** | Retorna webhooks que falharam na entrega após máximo de tentativas. |
| **Webhooks - Register dynamic webhooks** | **POST** | Registra webhooks para receber notificações de eventos do Jira. |
---

## Documentação oficial

- **Jira Cloud platform REST API v3** — [developer.atlassian.com/cloud/jira/platform/rest/v3/intro](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)
- **Jira Software Cloud API** — [developer.atlassian.com/cloud/jira/software/rest/intro](https://developer.atlassian.com/cloud/jira/software/rest/intro/)
- **Especificações OpenAPI** — [platform](https://developer.atlassian.com/cloud/jira/platform/swagger-v3.v3.json) · [software](https://developer.atlassian.com/cloud/jira/software/swagger.v3.json)
- **Sintaxe JQL** — [support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql](https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
- **Atlassian Document Format (ADF)** — [developer.atlassian.com/cloud/jira/platform/apis/document/structure](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)
