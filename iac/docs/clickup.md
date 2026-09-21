# ClickUp

## Contexto

ClickUp é uma plataforma de gestão de trabalho e produtividade (tarefas, projetos, documentos e colaboração de equipe). Sua API REST v2 organiza os recursos em uma hierarquia: **Workspace (Team)** → **Space** → **Folder** → **List** → **Task**, com conceitos transversais como comentários, checklists, campos personalizados, tags, metas (Goals com Key Results), views (exibições de lista, quadro, calendário, gantt etc.), controle de tempo (time tracking) e webhooks para notificação de eventos.

Este conector cobre os seguintes domínios: Checklist, Comment, Folder, Goal, Group (grupos de usuários), Key Result, List, Space, Task, Team (Workspace — inclui a maior parte das operações de nível de workspace, como time tracking, guests, templates e webhooks), User, View e Webhook.

**Fora do escopo:** o fluxo OAuth2 (`POST /oauth/token`), já que o conector usa autenticação por Personal API Key; e 4 operações de controle de tempo em nível de workspace (`GET`/`POST /team/{team_id}/time_entries`, `PUT /team/{team_id}/time_entries/{timer_id}`, `POST /team/{team_id}/time_entries/start`) que carregam um bug no spec oficial da ClickUp — o parâmetro de path `team_Id` colide com o parâmetro de query `team_id` após normalização de maiúsculas/minúsculas, o que impede a geração correta da operação.

---

## Autenticação

**Tipo:** Autenticação por cabeçalho customizado

**Configuração da conta conectada:**
| Variável | Valor |
| -------- | ----- |
| Host | {{host}} |
| Porta | 443 |
| token | {{token}} |

- **Host:** `https://api.clickup.com/api` (fixo).
- **token:** Personal API Key gerada em ClickUp em *Settings → Apps* (formato `pk_...`). O valor deve ser enviado inteiro (com o prefixo `pk_`) no header `Authorization` — a ClickUp não usa o prefixo `Bearer` para tokens pessoais.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Checklist - Edit Checklist** | **PUT** | Renomear lista de verificação ou reordenar para aparecer acima ou abaixo de outras listas. |
| **Checklist - Delete Checklist** | **DELETE** | Deletar lista de verificação de uma tarefa. |
| **Checklist - Create Checklist Item** | **POST** | Adicionar item a uma lista de verificação de tarefa. |
| **Checklist - Edit Checklist Item** | **PUT** | Atualizar item individual em lista de verificação. Renomear, atribuir responsável, marcar como resolvido ou aninhar. |
| **Checklist - Delete Checklist Item** | **DELETE** | Deletar item de uma lista de verificação. |
| **Comment - Update Comment** | **PUT** | Substituir conteúdo, atribuir responsável ou marcar comentário como resolvido. |
| **Comment - Delete Comment** | **DELETE** | Deletar comentário de uma tarefa. |
| **Comment - Get Threaded Comments** | **GET** | Visualizar comentários em thread. O comentário pai não é incluído na resposta. |
| **Comment - Create Threaded Comment** | **POST** | Criar comentário em thread. |
| **Folder - Get Folder** | **GET** | Visualizar listas dentro de pasta. Use include_subfolders para retornar árvore completa de subpastas. |
| **Folder - Update Folder** | **PUT** | Renomear pasta. Este endpoint apenas renomeia. Para mover, use Move Folder. |
| **Folder - Delete Folder** | **DELETE** | Deletar pasta do espaço de trabalho. |
| **Folder - Get Folder Custom Fields** | **GET** | Visualizar campos personalizados da pasta. Retorna apenas campos do nível de pasta, não do nível de lista. |
| **Folder - Add Guest To Folder** | **POST** | Compartilhar pasta com convidado. Disponível apenas em planos Enterprise. |
| **Folder - Remove Guest From Folder** | **DELETE** | Revogar acesso de convidado à pasta. Disponível apenas em planos Enterprise. |
| **Folder - Get Lists** | **GET** | Visualizar listas dentro de pasta. |
| **Folder - Create List** | **POST** | Adicionar nova lista à pasta. |
| **Folder - Create List From Template in Folder** | **POST** | Criar lista a partir de modelo em pasta. Requisição executa de forma síncrona por padrão. |
| **Folder - Move Folder** | **PUT** | Mover pasta para outro local ou aninhá-la dentro de outra. Use parent_folder_id ou space_id. |
| **Folder - Get Folder Views** | **GET** | Visualizar exibições de tarefas e páginas disponíveis para pasta. |
| **Folder - Create Folder View** | **POST** | Adicionar exibição a pasta. Tipos: lista, quadro, calendário, tabela, linha do tempo, gantt, entre outros. |
| **Goal - Get Goal** | **GET** | Visualizar detalhes do objetivo, incluindo seus alvos. |
| **Goal - Update Goal** | **PUT** | Renomear objetivo, definir data de vencimento, descrição, proprietários e cor. |
| **Goal - Delete Goal** | **DELETE** | Remover objetivo do espaço de trabalho. |
| **Goal - Create Key Result** | **POST** | Adicionar alvo a um objetivo. |
| **Group - Get Groups** | **GET** | Visualizar grupos de usuários no espaço de trabalho. |
| **Group - Update Group** | **PUT** | Gerenciar grupos de usuários. Convidado com visualização se torna pago. Assento adicionado automaticamente se necessário. |
| **Group - Delete Group** | **DELETE** | Remover grupo de usuários do espaço de trabalho. |
| **Key Result - Edit Key Result** | **PUT** | Atualizar alvo. |
| **Key Result - Delete Key Result** | **DELETE** | Deletar alvo de um objetivo. |
| **List - Get List** | **GET** | Visualizar informações sobre lista. |
| **List - Update List** | **PUT** | Renomear lista, atualizar descrição, definir data, prioridade, responsável e cor. |
| **List - Delete List** | **DELETE** | Deletar lista do espaço de trabalho. |
| **List - Get List Comments** | **GET** | Visualizar comentários da lista. Retorna 25 mais recentes. Use start e start_id para paginação. |
| **List - Create List Comment** | **POST** | Adicionar um comentário a uma Lista. |
| **List - Get List Custom Fields** | **GET** | Visualize os Campos Personalizados disponíveis em uma Lista, incluindo informações sobre escopo e aplicabilidade a tipos de tarefas específicas. |
| **List - Add Guest To List** | **POST** | Compartilhe uma Lista com um convidado. Disponível apenas em Workspaces no Plano Enterprise. |
| **List - Remove Guest From List** | **DELETE** | Revogue o acesso de um convidado a uma Lista. Disponível apenas em Workspaces no Plano Enterprise. |
| **List - Get List Members** | **GET** | Obtenha membros do Workspace com acesso explícito a uma Lista, excluindo acesso herdado de Team ou contenedores pai. |
| **List - Get Tasks** | **GET** | Visualize as tarefas em uma Lista com suporte a paginação (100 por página), filtros e informações de tempo rastreado. |
| **List - Create Task** | **POST** | Crie uma nova tarefa. Valores de Campos Personalizados são salvos apenas quando aplicáveis ao tipo de tarefa. |
| **List - Add Task To List** | **POST** | Adicione uma tarefa a uma Lista adicional. Requer o ClickApp Tasks in Multiple Lists habilitado. |
| **List - Remove Task From List** | **DELETE** | Remova uma tarefa de uma Lista adicional. Você não pode removê-la de sua Lista inicial. Requer ClickApp habilitado. |
| **List - Create Task From Template** | **POST** | Crie uma tarefa usando um modelo de tarefa do workspace. Templates públicos devem ser adicionados ao workspace primeiro. |
| **List - Get List Views** | **GET** | Visualize as exibições de tarefa e página disponíveis para uma Lista. |
| **List - Create List View** | **POST** | Adicione uma exibição (Lista, Board, Calendário, Tabela, etc.) a uma Lista. |
| **Space - Get Space** | **GET** | Visualize os Spaces disponíveis em um Workspace. |
| **Space - Update Space** | **PUT** | Renomeie, defina a cor e habilite ClickApps para um Space. |
| **Space - Delete Space** | **DELETE** | Exclua um Space do seu Workspace. |
| **Space - Get Space Custom Fields** | **GET** | Visualize os Campos Personalizados disponíveis em um Space, incluindo escopo e aplicabilidade a tipos de tarefas. |
| **Space - Get Folders** | **GET** | Visualize as pastas em um Space. Subpastas estão na mesma lista que pastas de nível superior, cada uma com seu parent_folder_id. |
| **Space - Create Folder** | **POST** | Adicione uma nova pasta a um Space, opcionalmente como subpasta dentro de uma pasta existente. |
| **Space - Create Folder from template** | **POST** | Crie uma pasta usando um modelo de pasta do workspace com todos seus ativos aninhados. Pode ser criada como subpasta. |
| **Space - Get Folderless Lists** | **GET** | Visualize as listas em um Space que não estão localizadas em uma pasta. |
| **Space - Create Folderless List** | **POST** | Adicione uma nova lista a um Space. |
| **Space - Create List From Template in Space** | **POST** | Crie uma lista usando um modelo de lista do workspace. |
| **Space - Get Space Tags** | **GET** | Visualize as tags de tarefas disponíveis em um Space. |
| **Space - Create Space Tag** | **POST** | Adicione uma nova tag de tarefa a um Space. |
| **Space - Edit Space Tag** | **PUT** | Atualize uma tag de tarefa. |
| **Space - Delete Space Tag** | **DELETE** | Exclua uma tag de tarefa de um Space. |
| **Space - Get Space Views** | **GET** | Visualize as exibições de tarefa e página disponíveis para um Space. |
| **Space - Create Space View** | **POST** | Adicione uma exibição (Lista, Board, Calendário, etc.) a um Space. |
| **Task - Get Bulk Tasks' Time in Status** | **GET** | Visualize quanto tempo duas ou mais tarefas permaneceram em cada status. Requer o ClickApp Total time in Status habilitado. |
| **Task - Get Task** | **GET** | Visualize informações sobre uma tarefa, incluindo anexos e campos personalizados aplicáveis ao seu tipo. |
| **Task - Update Task** | **PUT** | Atualize uma tarefa incluindo um ou mais campos no corpo da solicitação. |
| **Task - Delete Task** | **DELETE** | Exclua uma tarefa do seu Workspace. |
| **Task - Create Task Attachment** | **POST** | Carregue um arquivo para uma tarefa como anexo. Usa multipart/form-data como tipo de conteúdo. Suporte limitado a arquivos locais. |
| **Task - Create Checklist** | **POST** | Adicione uma nova lista de verificação a uma tarefa. |
| **Task - Get Task Comments** | **GET** | Recupera comentários de uma tarefa em ordem cronológica reversa; por padrão retorna os 25 mais recentes. |
| **Task - Create Task Comment** | **POST** | Adiciona um novo comentário em uma tarefa. |
| **Task - Add Dependency** | **POST** | Define uma tarefa como dependente ou bloqueadora de outra tarefa. |
| **Task - Delete Dependency** | **DELETE** | Remove a relação de dependência entre duas ou mais tarefas. |
| **Task - Set Custom Field Value** | **POST** | Define dados de um campo customizado em uma tarefa. |
| **Task - Remove Custom Field Value** | **DELETE** | Remove dados de um campo customizado em uma tarefa. |
| **Task - Add Guest To Task** | **POST** | Compartilha uma tarefa com um convidado (disponível apenas em Plano Enterprise). |
| **Task - Remove Guest From Task** | **DELETE** | Revoga acesso de um convidado a uma tarefa (disponível apenas em Plano Enterprise). |
| **Task - Add Task Link** | **POST** | Vincula duas tarefas juntas; apenas links entre tarefas são suportados. |
| **Task - Delete Task Link** | **DELETE** | Remove a vinculação entre duas tarefas. |
| **Task - Get Task Members** | **GET** | Recupera membros do espaço de trabalho com acesso explícito à tarefa. |
| **Task - Merge Tasks** | **POST** | Mescla múltiplas tarefas em uma tarefa de destino; IDs customizados não são suportados. |
| **Task - Add Tag To Task** | **POST** | Adiciona uma tag em uma tarefa. |
| **Task - Remove Tag From Task** | **DELETE** | Remove uma tag de uma tarefa; a tag permanece disponível no espaço. |
| **Task - Get tracked time** | **GET** | Recupera tempo rastreado em uma tarefa (endpoint legado; use a API de rastreamento). |
| **Task - Track time** | **POST** | Registra tempo rastreado em uma tarefa (endpoint legado; use a API de rastreamento). |
| **Task - Edit time tracked** | **PUT** | Edita tempo rastreado em uma tarefa (endpoint legado; use a API de rastreamento). |
| **Task - Delete time tracked** | **DELETE** | Deleta tempo rastreado em uma tarefa (endpoint legado; use a API de rastreamento). |
| **Task - Get Task's Time in Status** | **GET** | Recupera o tempo que uma tarefa permaneceu em cada status (requer habilitação do ClickApp). |
| **Team - Get Authorized Workspaces** | **GET** | Recupera os espaços de trabalho disponíveis ao usuário autenticado. |
| **Team - Get Filtered Team Tasks** | **GET** | Recupera tarefas de um espaço de trabalho que atendem critérios específicos; limite de 100 por página. |
| **Team - Get Custom Task Types** | **GET** | Recupera os tipos de tarefa customizados disponíveis em um espaço de trabalho. |
| **Team - Get Custom Roles** | **GET** | Recupera as funções customizadas disponíveis em um espaço de trabalho. |
| **Team - Get Workspace Custom Fields** | **GET** | Recupera campos customizados acessíveis em um espaço de trabalho (nível de espaço). |
| **Team - Get Folder Templates** | **GET** | Recupera modelos de pasta disponíveis em um espaço de trabalho; IDs começam com prefixo t-. |
| **Team - Get Goals** | **GET** | Recupera os objetivos disponíveis em um espaço de trabalho. |
| **Team - Create Goal** | **POST** | Cria um novo objetivo em um espaço de trabalho. |
| **Team - Create Group** | **POST** | Cria um grupo de usuários em um espaço de trabalho para organizar e gerenciar usuários. |
| **Team - Invite Guest To Workspace** | **POST** | Convida um convidado a ingressar em um espaço de trabalho (disponível apenas em Plano Enterprise). |
| **Team - Get Guest** | **GET** | Recupera informações sobre um convidado (disponível apenas em Plano Enterprise). |
| **Team - Edit Guest On Workspace** | **PUT** | Configura opções para um convidado (disponível apenas em Plano Enterprise). |
| **Team - Remove Guest From Workspace** | **DELETE** | Revoga acesso de um convidado a um espaço de trabalho (disponível apenas em Plano Enterprise). |
| **Team - Get List Templates** | **GET** | Recupera modelos de lista disponíveis em um espaço de trabalho; IDs começam com prefixo t-. |
| **Team - Get Workspace Plan** | **GET** | Recupera o plano atual do espaço de trabalho especificado. |
| **Team - Get Workspace seats** | **GET** | Exibe os assentos utilizados, totais e disponíveis de membros e convidados em um Workspace. |
| **Team - Shared Hierarchy** | **GET** | Exibe as tarefas, listas e pastas compartilhadas com o usuário autenticado. |
| **Team - Get Spaces** | **GET** | Exibe os Spaces disponíveis em um Workspace. Você pode obter informações de membros apenas em Spaces privados. |
| **Team - Create Space** | **POST** | Adiciona um novo Space a um Workspace. |
| **Team - Get Task Templates** | **GET** | Exibe os templates de tarefas disponíveis em um Workspace. |
| **Team - Get running time entry** | **GET** | Exibe o registro de tempo atualmente rastreado pelo usuário autenticado. Uma duração negativa indica que o timer está em execução. |
| **Team - Stop a time Entry** | **POST** | Para um timer que está em execução para o usuário autenticado. |
| **Team - Get all tags from time entries** | **GET** | Exibe todos os rótulos aplicados aos registros de tempo em um Workspace. |
| **Team - Add tags from time entries** | **POST** | Adiciona um rótulo a um registro de tempo. |
| **Team - Change tag names from time entries** | **PUT** | Renomeia um rótulo de registro de tempo. |
| **Team - Remove tags from time entries** | **DELETE** | Remove rótulos dos registros de tempo. Isso não remove o rótulo do Workspace. |
| **Team - Get singular time entry** | **GET** | Exibe um único registro de tempo. Uma duração negativa indica que o timer está em execução. |
| **Team - Delete a time Entry** | **DELETE** | Deleta um registro de tempo de um Workspace. |
| **Team - Get time entry history** | **GET** | Exibe uma lista de alterações realizadas em um registro de tempo. |
| **Team - Invite User To Workspace** | **POST** | Convida alguém a ingressar no Workspace como membro. Disponível apenas para Workspaces no plano Enterprise. |
| **Team - Get User** | **GET** | Exibe informações sobre um usuário em um Workspace. Disponível apenas para Workspaces no plano Enterprise. |
| **Team - Edit User On Workspace** | **PUT** | Atualiza o nome e a função de um usuário. Disponível apenas para Workspaces no plano Enterprise. |
| **Team - Remove User From Workspace** | **DELETE** | Desativa um usuário de um Workspace. Disponível apenas para Workspaces no plano Enterprise. |
| **Team - Get Workspace (Everything level) Views** | **GET** | Exibe as views de tarefas e páginas disponíveis no nível Everything de um Workspace. |
| **Team - Create Workspace (Everything level) View** | **POST** | Adiciona uma view de Lista, Quadro, Calendário, Tabela, Linha do Tempo, Carga de Trabalho, Atividade, Mapa, Chat ou Gantt no nível Everything. |
| **Team - Get Webhooks** | **GET** | Exibe os webhooks criados via API para um Workspace retornados pelo usuário autenticado. |
| **Team - Create Webhook** | **POST** | Configura um webhook para monitorar eventos. Não há endereço IP dedicado; usamos domínio e endereçamento dinâmico. |
| **User - Get Authorized User** | **GET** | Exibe os detalhes da conta ClickUp do usuário autenticado. |
| **View - Get View** | **GET** | Exibe informações sobre uma view específica de tarefa ou página. As informações variam conforme o tipo de view. |
| **View - Update View** | **PUT** | Renomeia uma view e atualiza o agrupamento, ordenação, filtros, colunas e configurações. |
| **View - Delete View** | **DELETE** | Deleta uma view. |
| **View - Get Chat View Comments** | **GET** | Exibe comentários de uma Chat view. Retorna os 25 comentários mais recentes se start e start_id não forem inclusos. Use start e start_id do comentário mais antigo para obter os próximos. |
| **View - Create Chat View Comment** | **POST** | Adiciona um novo comentário a uma Chat view. |
| **View - Get View Tasks** | **GET** | Exibe todas as tarefas visíveis em uma view. |
| **Webhook - Update Webhook** | **PUT** | Atualiza um webhook para alterar os eventos a serem monitorados. |
| **Webhook - Delete Webhook** | **DELETE** | Deleta um webhook para interromper o monitoramento dos eventos e locais. |

---

## Documentação oficial

https://developer.clickup.com/reference
