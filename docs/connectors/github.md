# GitHub

## Contexto

O GitHub é a plataforma de hospedagem de código e colaboração da Microsoft. A REST API (`https://api.github.com`) expõe recursos em JSON para automação de repositórios, organizações, usuários, segurança, CI/CD e integrações de terceiros.

Este conector cobre **337 operações** nos vários domínios do Github.

**Convenções da API usadas pelo módulo:**

- **Cabeçalho de versão:** `X-GitHub-Api-Version` (parâmetro `x_github_api_version` nas operações), determina a versão da api github usada, insira exatamente o termo da versão, por exemplo, `2026-03-10`. Para mais informações, consulte [esta página](https://docs.github.com/pt/rest/about-the-rest-api/api-versions).

---

## Autenticação

**Tipo:** Bearer Token

**Configuração da conta conectada:**

| Variável | Valor                    |
| -------- | ------------------------ |
| host     | `https://api.github.com` |
| token    | {{token}}                |
| porta    | 443 |

A API GitHub aceita o token no cabeçalho `Authorization: Bearer <token>`. É possível neste template usar um PAT (recomendado pelo Github) ou Classic token.

Documentação: [Authenticating to the REST API](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api).

---

## Operações

| Nome da Operação                                     | Método     | Descrição da Função                                                |
| ---------------------------------------------------- | ---------- | ------------------------------------------------------------------ |
| **Repos - List for authenticated user**              | **GET**    | Lista repositórios do usuário autenticado                          |
| **Repos - List for a user**                          | **GET**    | Lista repositórios de um usuário específico                        |
| **Repos - List for org**                             | **GET**    | Lista repositórios de uma organização                              |
| **Repos - Create for authenticated user**            | **POST**   | Cria um repositório para o usuário autenticado                     |
| **Repos - Create for org**                           | **POST**   | Cria um repositório em uma organização                             |
| **Repos - Get**                                      | **GET**    | Obtém informações de um repositório                                |
| **Repos - Update**                                   | **PATCH**  | Atualiza configurações de um repositório                           |
| **Repos - Delete**                                   | **DELETE** | Exclui um repositório                                              |
| **Repos - List topics**                              | **GET**    | Lista tópicos de um repositório                                    |
| **Repos - Replace topics**                           | **PUT**    | Substitui os tópicos de um repositório                             |
| **Repos - Get content**                              | **GET**    | Obtém conteúdo de um arquivo ou diretório do repositório           |
| **Repos - Create or update file**                    | **PUT**    | Cria ou atualiza um arquivo no repositório                         |
| **Repos - Delete file**                              | **DELETE** | Exclui um arquivo do repositório                                   |
| **Repos - Get README**                               | **GET**    | Obtém o README de um repositório                                   |
| **Repos - List contributors**                        | **GET**    | Lista os contribuidores de um repositório                          |
| **Repos - List languages**                           | **GET**    | Lista as linguagens usadas em um repositório                       |
| **Repos - List tags**                                | **GET**    | Lista as tags de um repositório                                    |
| **Repos - List forks**                               | **GET**    | Lista os forks de um repositório                                   |
| **Repos - Create fork**                              | **POST**   | Cria um fork de um repositório                                     |
| **Repos - Transfer**                                 | **POST**   | Transfere um repositório para outro usuário ou organização         |
| **Repos - List watchers**                            | **GET**    | Lista os observadores de um repositório                            |
| **Repos - Get traffic referrers**                    | **GET**    | Obtém os principais referenciadores de tráfego do repositório      |
| **Repos - Get clones**                               | **GET**    | Obtém estatísticas de clones do repositório                        |
| **Repos - Get views**                                | **GET**    | Obtém estatísticas de visualizações do repositório                 |
| **Issues - List for authenticated user**             | **GET**    | Lista issues do usuário autenticado                                |
| **Issues - List for repo**                           | **GET**    | Lista issues de um repositório                                     |
| **Issues - Create**                                  | **POST**   | Cria uma issue em um repositório                                   |
| **Issues - Get**                                     | **GET**    | Obtém uma issue específica                                         |
| **Issues - Update**                                  | **PATCH**  | Atualiza uma issue                                                 |
| **Issues - Lock**                                    | **PUT**    | Bloqueia a conversa de uma issue                                   |
| **Issues - Unlock**                                  | **DELETE** | Desbloqueia a conversa de uma issue                                |
| **Issues - List comments**                           | **GET**    | Lista comentários de uma issue                                     |
| **Issues - Create comment**                          | **POST**   | Cria um comentário em uma issue                                    |
| **Issues - Get comment**                             | **GET**    | Obtém um comentário de issue                                       |
| **Issues - Update comment**                          | **PATCH**  | Atualiza um comentário de issue                                    |
| **Issues - Delete comment**                          | **DELETE** | Exclui um comentário de issue                                      |
| **Issues - List events**                             | **GET**    | Lista eventos de uma issue                                         |
| **Issues - Add assignees**                           | **POST**   | Adiciona assignees a uma issue                                     |
| **Issues - Remove assignees**                        | **DELETE** | Remove assignees de uma issue                                      |
| **Pull Requests - List**                             | **GET**    | Lista pull requests de um repositório                              |
| **Pull Requests - Create**                           | **POST**   | Cria um pull request                                               |
| **Pull Requests - Get**                              | **GET**    | Obtém um pull request específico                                   |
| **Pull Requests - Update**                           | **PATCH**  | Atualiza um pull request                                           |
| **Pull Requests - List commits**                     | **GET**    | Lista commits de um pull request                                   |
| **Pull Requests - List files**                       | **GET**    | Lista arquivos de um pull request                                  |
| **Pull Requests - Check if merged**                  | **GET**    | Verifica se um pull request foi mergeado                           |
| **Pull Requests - Merge**                            | **PUT**    | Mergeia um pull request                                            |
| **Pull Requests - List requested reviewers**         | **GET**    | Lista revisores solicitados de um pull request                     |
| **Pull Requests - Request reviewers**                | **POST**   | Solicita revisores para um pull request                            |
| **Pull Requests - Remove requested reviewers**       | **DELETE** | Remove revisores solicitados de um pull request                    |
| **Pull Requests - List reviews**                     | **GET**    | Lista reviews de um pull request                                   |
| **Pull Requests - Create review**                    | **POST**   | Cria um review em um pull request                                  |
| **Pull Requests - Submit review**                    | **POST**   | Submete um review de pull request                                  |
| **Pull Requests - List review comments**             | **GET**    | Lista comentários de review de um pull request                     |
| **Actions - List workflows**                         | **GET**    | Lista workflows de um repositório                                  |
| **Actions - Get workflow**                           | **GET**    | Obtém um workflow específico                                       |
| **Actions - Trigger workflow**                       | **POST**   | Aciona um workflow manualmente                                     |
| **Actions - List workflow runs**                     | **GET**    | Lista execuções de workflow de um repositório                      |
| **Actions - Get workflow run**                       | **GET**    | Obtém uma execução de workflow                                     |
| **Actions - Cancel workflow run**                    | **POST**   | Cancela uma execução de workflow                                   |
| **Actions - Re-run workflow run**                    | **POST**   | Reexecuta um workflow                                              |
| **Actions - Delete workflow run**                    | **DELETE** | Exclui uma execução de workflow                                    |
| **Actions - List workflow run jobs**                 | **GET**    | Lista jobs de uma execução de workflow                             |
| **Actions - Get job**                                | **GET**    | Obtém um job de workflow                                           |
| **Actions - Download job logs**                      | **GET**    | Baixa os logs de um job de workflow                                |
| **Actions - List artifacts**                         | **GET**    | Lista artefatos de um repositório                                  |
| **Actions - Get artifact**                           | **GET**    | Obtém um artefato de workflow                                      |
| **Actions - Download artifact**                      | **GET**    | Baixa um artefato de workflow como ZIP                             |
| **Actions - Delete artifact**                        | **DELETE** | Exclui um artefato de workflow                                     |
| **Actions - List repo secrets**                      | **GET**    | Lista secrets de Actions de um repositório                         |
| **Actions - Get repo secret**                        | **GET**    | Obtém um secret de Actions de um repositório                       |
| **Actions - Create or update repo secret**           | **PUT**    | Cria ou atualiza um secret de Actions                              |
| **Actions - Delete repo secret**                     | **DELETE** | Exclui um secret de Actions de um repositório                      |
| **Actions - List repo variables**                    | **GET**    | Lista variáveis de Actions de um repositório                       |
| **Actions - Create repo variable**                   | **POST**   | Cria uma variável de Actions em um repositório                     |
| **Actions - Get repo variable**                      | **GET**    | Obtém uma variável de Actions de um repositório                    |
| **Actions - Update repo variable**                   | **PATCH**  | Atualiza uma variável de Actions de um repositório                 |
| **Actions - Delete repo variable**                   | **DELETE** | Exclui uma variável de Actions de um repositório                   |
| **Actions - List org secrets**                       | **GET**    | Lista secrets de Actions de uma organização                        |
| **Actions - List self-hosted runners**               | **GET**    | Lista runners auto-hospedados de um repositório                    |
| **Actions - Get self-hosted runner**                 | **GET**    | Obtém um runner auto-hospedado                                     |
| **Actions - Delete self-hosted runner**              | **DELETE** | Exclui um runner auto-hospedado                                    |
| **Users - Get authenticated user**                   | **GET**    | Obtém o perfil do usuário autenticado                              |
| **Users - Update authenticated user**                | **PATCH**  | Atualiza o perfil do usuário autenticado                           |
| **Users - Get a user**                               | **GET**    | Obtém o perfil de um usuário                                       |
| **Users - List users**                               | **GET**    | Lista todos os usuários do GitHub                                  |
| **Users - List followers of user**                   | **GET**    | Lista seguidores de um usuário                                     |
| **Users - List following**                           | **GET**    | Lista usuários que o usuário autenticado segue                     |
| **Users - Check if following**                       | **GET**    | Verifica se o usuário autenticado segue outro usuário              |
| **Users - Follow user**                              | **PUT**    | Segue um usuário                                                   |
| **Users - Unfollow user**                            | **DELETE** | Deixa de seguir um usuário                                         |
| **Users - List public SSH keys for user**            | **GET**    | Lista chaves SSH públicas de um usuário                            |
| **Users - List public GPG keys for user**            | **GET**    | Lista chaves GPG públicas de um usuário                            |
| **Users - List social accounts for user**            | **GET**    | Lista contas sociais de um usuário                                 |
| **Users - List emails**                              | **GET**    | Lista endereços de e-mail do usuário autenticado                   |
| **Users - Add email**                                | **POST**   | Adiciona endereços de e-mail ao usuário autenticado                |
| **Users - Delete email**                             | **DELETE** | Remove endereços de e-mail do usuário autenticado                  |
| **Users - List public keys**                         | **GET**    | Lista chaves SSH públicas do usuário autenticado                   |
| **Users - Create public SSH key**                    | **POST**   | Adiciona uma chave SSH pública ao usuário autenticado              |
| **Users - Delete public SSH key**                    | **DELETE** | Remove uma chave SSH pública do usuário autenticado                |
| **Orgs - List for authenticated user**               | **GET**    | Lista organizações do usuário autenticado                          |
| **Orgs - List for a user**                           | **GET**    | Lista organizações de um usuário específico                        |
| **Orgs - Get**                                       | **GET**    | Obtém informações de uma organização                               |
| **Orgs - Update**                                    | **PATCH**  | Atualiza configurações de uma organização                          |
| **Orgs - List members**                              | **GET**    | Lista membros de uma organização                                   |
| **Orgs - Check membership**                          | **GET**    | Verifica se um usuário é membro da organização                     |
| **Orgs - Remove member**                             | **DELETE** | Remove um membro da organização                                    |
| **Orgs - List public members**                       | **GET**    | Lista membros públicos de uma organização                          |
| **Orgs - List outside collaborators**                | **GET**    | Lista colaboradores externos de uma organização                    |
| **Orgs - Remove outside collaborator**               | **DELETE** | Remove um colaborador externo da organização                       |
| **Orgs - List invitations**                          | **GET**    | Lista convites pendentes de uma organização                        |
| **Orgs - Create invitation**                         | **POST**   | Cria um convite para uma organização                               |
| **Orgs - Cancel invitation**                         | **DELETE** | Cancela um convite de organização                                  |
| **Orgs - List memberships**                          | **GET**    | Lista associações de organizações do usuário autenticado           |
| **Orgs - Get membership for authenticated user**     | **GET**    | Obtém a associação do usuário autenticado com uma organização      |
| **Orgs - Update membership**                         | **PATCH**  | Atualiza a associação do usuário autenticado com uma organização   |
| **Orgs - List webhooks**                             | **GET**    | Lista webhooks de uma organização                                  |
| **Orgs - Create webhook**                            | **POST**   | Cria um webhook em uma organização                                 |
| **Orgs - Get webhook**                               | **GET**    | Obtém um webhook de uma organização                                |
| **Orgs - Delete webhook**                            | **DELETE** | Exclui um webhook de uma organização                               |
| **Teams - Delete**                                   | **DELETE** | Exclui um time                                                     |
| **Teams - List members**                             | **GET**    | Lista membros de um time                                           |
| **Teams - Get membership for user**                  | **GET**    | Obtém a associação de um usuário com o time                        |
| **Teams - Add or update repo permissions**           | **PUT**    | Adiciona ou atualiza permissões de repositório para um time        |
| **Teams - Remove repo**                              | **DELETE** | Remove um repositório de um time                                   |
| **Teams - List**                                     | **GET**    | Lista times de uma organização                                     |
| **Teams - Create**                                   | **POST**   | Cria um time em uma organização                                    |
| **Teams - Get**                                      | **GET**    | Obtém um time pelo slug                                            |
| **Teams - Update**                                   | **PATCH**  | Atualiza um time                                                   |
| **Teams - Add or update membership**                 | **PUT**    | Adiciona ou atualiza a associação de um usuário com o time         |
| **Teams - Remove membership**                        | **DELETE** | Remove a associação de um usuário com o time                       |
| **Teams - List repos**                               | **GET**    | Lista repositórios de um time                                      |
| **Branches - List**                                  | **GET**    | Lista branches de um repositório                                   |
| **Branches - Get**                                   | **GET**    | Obtém informações de um branch                                     |
| **Branches - Get protection**                        | **GET**    | Obtém as regras de proteção de um branch                           |
| **Branches - Update protection**                     | **PUT**    | Atualiza as regras de proteção de um branch                        |
| **Branches - Delete protection**                     | **DELETE** | Remove as regras de proteção de um branch                          |
| **Branches - Get access restrictions**               | **GET**    | Obtém as restrições de acesso de um branch protegido               |
| **Branches - Delete access restrictions**            | **DELETE** | Remove as restrições de acesso de um branch protegido              |
| **Branches - Rename**                                | **POST**   | Renomeia um branch                                                 |
| **Branches - Merge**                                 | **POST**   | Mergeia um branch em outro                                         |
| **Branches - Sync fork**                             | **POST**   | Sincroniza um fork com o repositório upstream                      |
| **Git - Create blob**                                | **POST**   | Cria um blob de conteúdo no repositório                            |
| **Git - Get blob**                                   | **GET**    | Obtém um blob pelo SHA                                             |
| **Git - Create commit**                              | **POST**   | Cria um commit no repositório                                      |
| **Git - Get commit**                                 | **GET**    | Obtém um commit do banco de dados Git                              |
| **Git - List matching refs**                         | **GET**    | Lista referências que correspondem ao prefixo                      |
| **Git - Get ref**                                    | **GET**    | Obtém uma referência Git                                           |
| **Git - Create ref**                                 | **POST**   | Cria uma referência Git                                            |
| **Git - Update ref**                                 | **PATCH**  | Atualiza uma referência Git                                        |
| **Git - Delete ref**                                 | **DELETE** | Exclui uma referência Git                                          |
| **Git - Create tag**                                 | **POST**   | Cria um objeto de tag Git                                          |
| **Git - Get tag**                                    | **GET**    | Obtém um objeto de tag Git                                         |
| **Git - Create tree**                                | **POST**   | Cria uma árvore Git                                                |
| **Commits - List**                                   | **GET**    | Lista commits de um repositório                                    |
| **Commits - Get**                                    | **GET**    | Obtém um commit específico                                         |
| **Commits - List branches where head**               | **GET**    | Lista branches cujo HEAD é o commit especificado                   |
| **Commits - List associated pull requests**          | **GET**    | Lista pull requests associados a um commit                         |
| **Commits - List comments**                          | **GET**    | Lista comentários de um commit                                     |
| **Commits - Create comment**                         | **POST**   | Cria um comentário em um commit                                    |
| **Commits - Get comment**                            | **GET**    | Obtém um comentário de commit                                      |
| **Commits - Update comment**                         | **PATCH**  | Atualiza um comentário de commit                                   |
| **Commits - Delete comment**                         | **DELETE** | Exclui um comentário de commit                                     |
| **Commits - Compare two commits**                    | **GET**    | Compara dois commits ou branches                                   |
| **Releases - List**                                  | **GET**    | Lista releases de um repositório                                   |
| **Releases - Create**                                | **POST**   | Cria uma release                                                   |
| **Releases - Get**                                   | **GET**    | Obtém uma release                                                  |
| **Releases - Update**                                | **PATCH**  | Atualiza uma release                                               |
| **Releases - Delete**                                | **DELETE** | Exclui uma release                                                 |
| **Releases - Get latest**                            | **GET**    | Obtém a última release publicada                                   |
| **Releases - Get by tag**                            | **GET**    | Obtém uma release pela tag                                         |
| **Releases - List assets**                           | **GET**    | Lista assets de uma release                                        |
| **Releases - Get asset**                             | **GET**    | Obtém um asset de release                                          |
| **Releases - Update asset**                          | **PATCH**  | Atualiza um asset de release                                       |
| **Releases - Delete asset**                          | **DELETE** | Exclui um asset de release                                         |
| **Search - Repositories**                            | **GET**    | Busca repositórios no GitHub                                       |
| **Search - Code**                                    | **GET**    | Busca código no GitHub                                             |
| **Search - Commits**                                 | **GET**    | Busca commits no GitHub                                            |
| **Search - Issues and pull requests**                | **GET**    | Busca issues e pull requests no GitHub                             |
| **Search - Users**                                   | **GET**    | Busca usuários no GitHub                                           |
| **Search - Topics**                                  | **GET**    | Busca tópicos no GitHub                                            |
| **Deployments - List**                               | **GET**    | Lista deployments de um repositório                                |
| **Deployments - Create**                             | **POST**   | Cria um deployment                                                 |
| **Deployments - Get**                                | **GET**    | Obtém um deployment                                                |
| **Deployments - Delete**                             | **DELETE** | Exclui um deployment                                               |
| **Deployments - List statuses**                      | **GET**    | Lista status de um deployment                                      |
| **Deployments - Create status**                      | **POST**   | Cria um status de deployment                                       |
| **Deployments - Get status**                         | **GET**    | Obtém um status de deployment                                      |
| **Deployments - List environments**                  | **GET**    | Lista ambientes de um repositório                                  |
| **Deployments - Create or update environment**       | **PUT**    | Cria ou atualiza um ambiente de deployment                         |
| **Deployments - Delete environment**                 | **DELETE** | Exclui um ambiente de deployment                                   |
| **Deployments - List branch policies**               | **GET**    | Lista políticas de branch de um ambiente                           |
| **Deployments - Create branch policy**               | **POST**   | Cria uma política de branch para um ambiente                       |
| **Deployments - Get branch policy**                  | **GET**    | Obtém uma política de branch de um ambiente                        |
| **Deployments - Delete branch policy**               | **DELETE** | Exclui uma política de branch de um ambiente                       |
| **Checks - Create run**                              | **POST**   | Cria um check run                                                  |
| **Checks - Get run**                                 | **GET**    | Obtém um check run                                                 |
| **Checks - Update run**                              | **PATCH**  | Atualiza um check run                                              |
| **Checks - List runs for commit**                    | **GET**    | Lista check runs de um commit                                      |
| **Checks - Create suite**                            | **POST**   | Cria um check suite                                                |
| **Checks - Get suite**                               | **GET**    | Obtém um check suite                                               |
| **Checks - Rerequest suite**                         | **POST**   | Solicita a re-execução de um check suite                           |
| **Checks - List suites for commit**                  | **GET**    | Lista check suites de um commit                                    |
| **Webhooks - List repo webhooks**                    | **GET**    | Lista webhooks de um repositório                                   |
| **Webhooks - Create repo webhook**                   | **POST**   | Cria um webhook em um repositório                                  |
| **Webhooks - Get repo webhook**                      | **GET**    | Obtém um webhook de repositório                                    |
| **Webhooks - Update repo webhook**                   | **PATCH**  | Atualiza um webhook de repositório                                 |
| **Webhooks - Delete repo webhook**                   | **DELETE** | Exclui um webhook de repositório                                   |
| **Webhooks - Ping repo webhook**                     | **POST**   | Envia um ping para um webhook de repositório                       |
| **Collaborators - List**                             | **GET**    | Lista colaboradores de um repositório                              |
| **Collaborators - Check user**                       | **GET**    | Verifica se um usuário é colaborador do repositório                |
| **Collaborators - Add**                              | **PUT**    | Adiciona um colaborador ao repositório                             |
| **Collaborators - Remove**                           | **DELETE** | Remove um colaborador do repositório                               |
| **Collaborators - Get permission level**             | **GET**    | Obtém o nível de permissão de um colaborador                       |
| **Collaborators - List invitations**                 | **GET**    | Lista convites pendentes de colaboração                            |
| **Collaborators - Update invitation**                | **PATCH**  | Atualiza um convite de colaboração                                 |
| **Collaborators - Delete invitation**                | **DELETE** | Exclui um convite de colaboração                                   |
| **Labels - List for repo**                           | **GET**    | Lista labels de um repositório                                     |
| **Labels - Create**                                  | **POST**   | Cria uma label no repositório                                      |
| **Labels - Get**                                     | **GET**    | Obtém uma label pelo nome                                          |
| **Labels - Update**                                  | **PATCH**  | Atualiza uma label                                                 |
| **Labels - Delete**                                  | **DELETE** | Exclui uma label                                                   |
| **Labels - List for issue**                          | **GET**    | Lista labels de uma issue                                          |
| **Labels - List for milestone**                      | **GET**    | Lista labels de um milestone                                       |
| **Labels - Add to issue**                            | **POST**   | Adiciona labels a uma issue                                        |
| **Labels - Set on issue**                            | **PUT**    | Define as labels de uma issue (substitui as existentes)            |
| **Labels - Remove from issue**                       | **DELETE** | Remove uma label de uma issue                                      |
| **Labels - Remove all from issue**                   | **DELETE** | Remove todas as labels de uma issue                                |
| **Milestones - List**                                | **GET**    | Lista milestones de um repositório                                 |
| **Milestones - Create**                              | **POST**   | Cria um milestone                                                  |
| **Milestones - Get**                                 | **GET**    | Obtém um milestone                                                 |
| **Milestones - Update**                              | **PATCH**  | Atualiza um milestone                                              |
| **Milestones - Delete**                              | **DELETE** | Exclui um milestone                                                |
| **Reactions - List for commit comment**              | **GET**    | Lista reações de um comentário de commit                           |
| **Reactions - Create for commit comment**            | **POST**   | Cria uma reação em um comentário de commit                         |
| **Reactions - Delete commit comment reaction**       | **DELETE** | Exclui uma reação de comentário de commit                          |
| **Reactions - List for issue**                       | **GET**    | Lista reações de uma issue                                         |
| **Reactions - Create for issue**                     | **POST**   | Cria uma reação em uma issue                                       |
| **Reactions - Delete issue reaction**                | **DELETE** | Exclui uma reação de issue                                         |
| **Reactions - List for PR review comment**           | **GET**    | Lista reações de um comentário de review de PR                     |
| **Reactions - Create for PR review comment**         | **POST**   | Cria uma reação em um comentário de review de PR                   |
| **Reactions - Delete PR review comment reaction**    | **DELETE** | Exclui uma reação de comentário de review de PR                    |
| **Activity - List public events**                    | **GET**    | Lista eventos públicos do GitHub                                   |
| **Activity - List repo events**                      | **GET**    | Lista eventos de um repositório                                    |
| **Activity - List events for user**                  | **GET**    | Lista eventos de um usuário                                        |
| **Activity - List public events for user**           | **GET**    | Lista eventos públicos de um usuário                               |
| **Activity - List org events for user**              | **GET**    | Lista eventos de organização de um usuário                         |
| **Activity - List repo notifications**               | **GET**    | Lista notificações de um repositório                               |
| **Activity - List notifications**                    | **GET**    | Lista notificações do usuário autenticado                          |
| **Activity - Mark all notifications as read**        | **PUT**    | Marca todas as notificações como lidas                             |
| **Activity - Get thread**                            | **GET**    | Obtém uma thread de notificação                                    |
| **Activity - Mark thread as read**                   | **PATCH**  | Marca uma thread de notificação como lida                          |
| **Activity - List repo stargazers**                  | **GET**    | Lista usuários que deram estrela ao repositório                    |
| **Activity - List repos starred by user**            | **GET**    | Lista repositórios marcados com estrela por um usuário             |
| **Activity - Check if repo is starred**              | **GET**    | Verifica se o usuário autenticado marcou o repositório com estrela |
| **Activity - Star a repo**                           | **PUT**    | Marca um repositório com estrela                                   |
| **Activity - Unstar a repo**                         | **DELETE** | Remove a estrela de um repositório                                 |
| **Pages - Get info**                                 | **GET**    | Obtém informações do GitHub Pages de um repositório                |
| **Pages - Create site**                              | **POST**   | Cria um site GitHub Pages                                          |
| **Pages - Update site**                              | **PUT**    | Atualiza configurações do GitHub Pages                             |
| **Pages - Delete site**                              | **DELETE** | Exclui um site GitHub Pages                                        |
| **Pages - List builds**                              | **GET**    | Lista builds do GitHub Pages                                       |
| **Pages - Get latest build**                         | **GET**    | Obtém o último build do GitHub Pages                               |
| **Pages - Request build**                            | **POST**   | Solicita um build do GitHub Pages                                  |
| **Packages - List for org**                          | **GET**    | Lista pacotes de uma organização                                   |
| **Packages - Get for org**                           | **GET**    | Obtém um pacote de uma organização                                 |
| **Packages - Delete for org**                        | **DELETE** | Exclui um pacote de uma organização                                |
| **Packages - Restore for org**                       | **POST**   | Restaura um pacote excluído de uma organização                     |
| **Packages - List versions for org**                 | **GET**    | Lista versões de um pacote de uma organização                      |
| **Packages - Delete version for org**                | **DELETE** | Exclui uma versão de pacote de uma organização                     |
| **Packages - List for authenticated user**           | **GET**    | Lista pacotes do usuário autenticado                               |
| **Packages - Get for authenticated user**            | **GET**    | Obtém um pacote do usuário autenticado                             |
| **Packages - List versions for authenticated user**  | **GET**    | Lista versões de um pacote do usuário autenticado                  |
| **Packages - Delete version for authenticated user** | **DELETE** | Exclui uma versão de pacote do usuário autenticado                 |
| **Secret Scanning - List alerts for repo**           | **GET**    | Lista alertas de secret scanning de um repositório                 |
| **Secret Scanning - Get alert**                      | **GET**    | Obtém um alerta de secret scanning                                 |
| **Secret Scanning - Update alert**                   | **PATCH**  | Atualiza um alerta de secret scanning                              |
| **Secret Scanning - List alerts for org**            | **GET**    | Lista alertas de secret scanning de uma organização                |
| **Secret Scanning - List alert locations**           | **GET**    | Lista localizações de um alerta de secret scanning                 |
| **Secret Scanning - List alerts for enterprise**     | **GET**    | Lista alertas de secret scanning de uma empresa                    |
| **Code Scanning - List alerts for repo**             | **GET**    | Lista alertas de code scanning de um repositório                   |
| **Code Scanning - Get alert**                        | **GET**    | Obtém um alerta de code scanning                                   |
| **Code Scanning - Update alert**                     | **PATCH**  | Atualiza um alerta de code scanning                                |
| **Code Scanning - List alerts for org**              | **GET**    | Lista alertas de code scanning de uma organização                  |
| **Code Scanning - List analyses**                    | **GET**    | Lista análises de code scanning de um repositório                  |
| **Code Scanning - Get analysis**                     | **GET**    | Obtém uma análise de code scanning                                 |
| **Code Scanning - Delete analysis**                  | **DELETE** | Exclui uma análise de code scanning                                |
| **Dependabot - List alerts for repo**                | **GET**    | Lista alertas do Dependabot de um repositório                      |
| **Dependabot - Get alert**                           | **GET**    | Obtém um alerta do Dependabot                                      |
| **Dependabot - Update alert**                        | **PATCH**  | Atualiza um alerta do Dependabot                                   |
| **Dependabot - List alerts for org**                 | **GET**    | Lista alertas do Dependabot de uma organização                     |
| **Dependabot - List repo secrets**                   | **GET**    | Lista secrets do Dependabot de um repositório                      |
| **Dependabot - Get repo secret**                     | **GET**    | Obtém um secret do Dependabot de um repositório                    |
| **Dependabot - Create or update repo secret**        | **PUT**    | Cria ou atualiza um secret do Dependabot                           |
| **Dependabot - Delete repo secret**                  | **DELETE** | Exclui um secret do Dependabot de um repositório                   |
| **Dependabot - List org secrets**                    | **GET**    | Lista secrets do Dependabot de uma organização                     |
| **Security Advisories - List global**                | **GET**    | Lista avisos de segurança globais do GitHub                        |
| **Security Advisories - Get global**                 | **GET**    | Obtém um aviso de segurança global                                 |
| **Security Advisories - List for repo**              | **GET**    | Lista avisos de segurança de um repositório                        |
| **Security Advisories - Create**                     | **POST**   | Cria um aviso de segurança em um repositório                       |
| **Security Advisories - Get for repo**               | **GET**    | Obtém um aviso de segurança de um repositório                      |
| **Security Advisories - Update**                     | **PATCH**  | Atualiza um aviso de segurança de um repositório                   |
| **Deploy Keys - List**                               | **GET**    | Lista deploy keys de um repositório                                |
| **Deploy Keys - Create**                             | **POST**   | Cria uma deploy key em um repositório                              |
| **Deploy Keys - Get**                                | **GET**    | Obtém uma deploy key de um repositório                             |
| **Deploy Keys - Delete**                             | **DELETE** | Exclui uma deploy key de um repositório                            |
| **Codespaces - List for authenticated user**         | **GET**    | Lista codespaces do usuário autenticado                            |
| **Codespaces - Create for authenticated user**       | **POST**   | Cria um codespace para o usuário autenticado                       |
| **Codespaces - Get**                                 | **GET**    | Obtém um codespace                                                 |
| **Codespaces - Update**                              | **PATCH**  | Atualiza um codespace                                              |
| **Codespaces - Delete**                              | **DELETE** | Exclui um codespace                                                |
| **Codespaces - Start**                               | **POST**   | Inicia um codespace                                                |
| **Codespaces - Stop**                                | **POST**   | Para um codespace                                                  |
| **Codespaces - List for repo**                       | **GET**    | Lista codespaces de um repositório                                 |
| **Codespaces - Create from pull request**            | **POST**   | Cria um codespace a partir de um pull request                      |
| **Codespaces - List for org**                        | **GET**    | Lista codespaces de uma organização                                |
| **Codespaces - List repo secrets**                   | **GET**    | Lista secrets de codespaces de um repositório                      |
| **Codespaces - List secrets for authenticated user** | **GET**    | Lista secrets de codespaces do usuário autenticado                 |
| **Copilot - Get org billing**                        | **GET**    | Obtém informações de cobrança do Copilot de uma organização        |
| **Copilot - List seat assignments**                  | **GET**    | Lista assentos do Copilot de uma organização                       |
| **Copilot - Add teams to subscription**              | **POST**   | Adiciona times à assinatura do Copilot                             |
| **Copilot - Remove teams from subscription**         | **DELETE** | Remove times da assinatura do Copilot                              |
| **Copilot - Add users to subscription**              | **POST**   | Adiciona usuários à assinatura do Copilot                          |
| **Copilot - Remove users from subscription**         | **DELETE** | Remove usuários da assinatura do Copilot                           |
| **Copilot - Get seat details for user**              | **GET**    | Obtém detalhes de assento Copilot de um membro                     |
| **Dependency Graph - Compare commits**               | **GET**    | Compara dependências entre dois commits                            |
| **Dependency Graph - Export SBOM**                   | **GET**    | Exporta o SBOM (Software Bill of Materials) do repositório         |
| **Dependency Graph - Create snapshot**               | **POST**   | Cria um snapshot de dependências do repositório                    |
| **Dependency Graph - List dependents**               | **GET**    | Lista repositórios dependentes de um pacote                        |
| **Rate Limit - Get status**                          | **GET**    | Obtém o status do limite de requisições da API                     |
| **Meta - Get info**                                  | **GET**    | Obtém meta informações sobre o GitHub                              |
| **Interactions - Get restrictions for repo**         | **GET**    | Obtém restrições de interação de um repositório                    |
| **Interactions - Set restrictions for repo**         | **PUT**    | Define restrições de interação em um repositório                   |
| **Interactions - Remove restrictions for repo**      | **DELETE** | Remove restrições de interação de um repositório                   |
| **Interactions - Get restrictions for org**          | **GET**    | Obtém restrições de interação de uma organização                   |
| **Interactions - Set restrictions for org**          | **PUT**    | Define restrições de interação em uma organização                  |
| **Interactions - Remove restrictions for org**       | **DELETE** | Remove restrições de interação de uma organização                  |


---

## Documentação oficial

[https://docs.github.com/en/rest?apiVersion=2022-11-28](https://docs.github.com/en/rest?apiVersion=2022-11-28)