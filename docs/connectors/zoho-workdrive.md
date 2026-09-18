# Zoho WorkDrive

## Contexto

A API do **Zoho WorkDrive** é REST sobre HTTPS e segue a convenção **JSON:API** — todo corpo de requisição e de resposta é embalado em `{"data": {"type": "<recurso>", "attributes": {…}}}`, com o `Content-Type` `application/vnd.api+json`. Ela expõe o armazenamento colaborativo da Zoho: arquivos e pastas, pastas de equipe, compartilhamento interno e externo, versionamento, comentários e a administração de equipes, membros e grupos.

**Conceitos fundamentais**

- **Equipe (`team_id`)** — a unidade de topo do WorkDrive, equivalente à organização. Pastas de equipe, membros, grupos e bibliotecas de modelos pertencem a uma equipe.
- **Membro da equipe (`team_member_id`) e ZUID** — o membro é a identidade do usuário *dentro* da equipe e é o que a maioria das listagens pessoais pede. O ZUID é o identificador global do usuário no Zoho Accounts, usado apenas para listar as equipes de um usuário.
- **Pasta de equipe (`teamfolder_id`)** — o espaço compartilhado por um grupo de pessoas. É onde o trabalho colaborativo vive, com seus próprios membros, configurações, lixeira e rascunhos.
- **Minhas pastas (`myfolder_id`)** — a área privada de cada membro. Tem endpoints próprios (`privatespace`), separados dos de pasta de equipe.
- **Recurso (`resource_id`)** — arquivo **ou** pasta. O WorkDrive não separa os dois: a mesma operação de atualização renomeia um arquivo, move uma pasta ou envia qualquer um dos dois para a lixeira, conforme o atributo informado.
- **Compartilhamento interno (`permissions`) e externo (`links`)** — `permissions` concede acesso a pessoas, grupos ou à equipe dentro do WorkDrive; `links` gera URLs públicas, com senha, prazo de validade e limite de download.
- **Grupo (`group_id`)** — um conjunto nomeado de membros, usado para compartilhar em bloco em vez de pessoa por pessoa.
- **Biblioteca de modelos (`library_id`)** — coleção de arquivos-modelo, com escopo público, da equipe ou do usuário.
- **Sessão de upload em partes (`upload_id`)** — o mecanismo para arquivos grandes: cria-se a sessão, enviam-se as partes e confirma-se (*commit*) no fim.
- **Zia** — a camada de IA da Zoho. No conector aparece em duas operações: o resumo de arquivo e a consulta ao conteúdo do arquivo em linguagem natural.
- **Datacenter** — a conta Zoho vive em um datacenter específico (`.com`, `.eu`, `.in`, `.com.au`, `.jp`, `.ca`, `.sa`), e o host da API muda junto com ele.

**Escopo deste conector**

Este módulo cobre **arquivos e equipe**: o ciclo de vida de arquivos e pastas (criar, listar, mover, renomear, copiar, favoritar, lixeira, restaurar, excluir), envio de conteúdo (multipart e sessão em partes), versões, ZIP, comentários, compartilhamento interno e externo, navegação por pastas de equipe, Minhas pastas e bibliotecas de modelos, e a administração de equipes, membros, grupos e membros de grupo. São **99 operações**.

Ficam **fora** do escopo:

- **Workflow** (`workflowinstances`, `workflows`, `transitions`, ações de workflow) — 11 operações que formam um produto de aprovação à parte e exigem o escopo `WorkDrive.workflow`.
- **Metadados customizados e modelos de dados** (`custommetadata`, `customfields`, `datatemplates`) — 12 operações de modelagem de metadados.
- **Classificação** (`labels`, `category`, `collections`, `submissions`, `libraries/categories`) — 22 operações de rotulagem e curadoria de conteúdo.
- **Mudanças e configurações avulsas** (`changes`, `settings`, `actions`) — 5 operações.
- **Download de conteúdo, upload em stream e acompanhamento de progresso** — 5 operações que **rodam em hosts próprios** (`download.zoho.<dc>` e `upload.zohoapis.<dc>`), incompatíveis com o Host único de uma conta conectada. Veja "Limitações conhecidas".

---

## Autenticação

**Tipo:** OAuth 2.0

Toda API da Zoho autentica pelo **Zoho Accounts**, com o cabeçalho `Authorization: Zoho-oauthtoken <token>` — montado pela conta conectada, não por parâmetro de operação.

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://www.zohoapis.<>seu-datacenter</>` |
| Porta | 443 |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Access Token | {{access_token}} |
| Refresh Token | {{refresh_token}} |
| Endpoint de troca de token | `https://accounts.zoho.com/oauth/v2/token` |

> **O datacenter faz parte do Host.** Substitua `<>seu-datacenter</>` pelo TLD da sua conta: `com`, `eu`, `in`, `com.au`, `jp`, `ca` ou `sa`. Uma conta do datacenter europeu não responde em `www.zohoapis.com`. O endpoint de troca de token acompanha o mesmo datacenter — use `https://accounts.zoho.eu/oauth/v2/token` para o DC europeu, e assim por diante.

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

### Descobrindo o `team_id` e o `team_member_id`

Comece por **Users - Get User Info** (`/users/me`), que não exige nenhum ID. A resposta traz o ZUID do usuário autenticado. Com ele, **Users - Get All Teams of User** devolve as equipes e seus `team_id`; **Teams - Get Current Team Member** devolve o `team_member_id` do usuário na equipe escolhida. A partir daí, **Users - Get My Folders Id** dá o `myfolder_id` da área privada e **Teams - Get Team Folders in a Team** lista as pastas de equipe.

### Escopos OAuth necessários

Os escopos vão no parâmetro `scope` da URL de autorização, separados por vírgula. As 99 operações deste módulo exigem, somadas, **39 escopos distintos** — o conjunto abaixo é a união exata:

| Família | Escopos | Cobre |
| ------- | ------- | ----- |
| `WorkDrive.files` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | arquivos e pastas, versões, ZIP, resumo e consulta Zia, upload, propriedades e estatísticas |
| `WorkDrive.files.sharing` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | compartilhamento interno de arquivos e pastas (`permissions`) |
| `WorkDrive.links` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | links de compartilhamento externo |
| `WorkDrive.comments` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | comentários e respostas em arquivos |
| `WorkDrive.teamfolders` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | pastas de equipe e sua navegação |
| `WorkDrive.teamfolders.admin` | `.READ` | lixeira e configurações administrativas da pasta de equipe |
| `WorkDrive.teamfolders.sharing` | `.CREATE`, `.UPDATE`, `.DELETE` | membros e grupos colaboradores da pasta de equipe |
| `WorkDrive.team` | `.READ`, `.UPDATE` | dados e atualização da equipe, busca de registros |
| `WorkDrive.team.admin` | `.READ` | configurações de administrador da equipe |
| `WorkDrive.users` | `.READ`, `.CREATE`, `.UPDATE` | membros da equipe, convites, listagens pessoais e Minhas pastas |
| `WorkDrive.groups` | `.READ`, `.CREATE`, `.UPDATE`, `.DELETE` | grupos e membros de grupo |
| `WorkDrive.libraries` | `.READ`, `.CREATE`, `.UPDATE` | bibliotecas de modelos e seus arquivos |
| `WorkDrive.libraries.sharing` | `.READ` | permissões da biblioteca de modelos |
| `ZohoSearch.securesearch` | `.READ` | **Teams - Search Records** — a busca roda no Zoho Search, não no WorkDrive |

> **Conceda só o que for usar.** Quanto mais estreito o conjunto de escopos, menos permissiva precisa ser a aplicação OAuth. Um fluxo que só lê e envia arquivos resolve com `WorkDrive.files.READ,WorkDrive.files.CREATE,WorkDrive.users.READ` — não é preciso autorizar os 39.

---

## Convenções deste conector

- **O caminho carrega `/workdrive/api/v1`.** O Host da conta conectada é apenas a origem (`https://www.zohoapis.<>seu-datacenter</>`); o prefixo do produto e a versão fazem parte do caminho de cada operação.
- **Corpo das requisições.** O parâmetro `body` é um texto JSON único, preenchido com um exemplo real extraído da especificação oficial. Informe o objeto completo no formato JSON:API: `{"data":{"type":"<recurso>","attributes":{…}}}`.
- **Uma operação, várias ações.** A API do WorkDrive concentra muitas ações no mesmo verbo e caminho, distinguidas apenas pelo atributo enviado — `Files - Update Files Folders` cobre 15 ações (mover, renomear, favoritar, lixeira, restaurar, check-in/check-out, marcar como final…). A descrição de cada operação lista o que ela cobre, e o exemplo do `body` mostra **uma** dessas ações. Para as outras, troque o atributo: `{"status":"51"}` envia para a lixeira, `{"status":"61"}` restaura, `{"favorite":true}` favorita, `{"parent_id":"…"}` move.
- **Upload é multipart.** `Upload - Upload New Version` usa `multipart/form-data` no formato granular `campo:<>parâmetro</>`. Para enviar conteúdo binário, informe o arquivo em **base64** e marque **"Forçar bufferização da requisição"** na operação — sem isso o corpo é truncado.
- **Arquivos grandes vão por sessão.** Em vez do upload direto, use `Uploadsession - Create Session…`, envie as partes e finalize com `Uploadsession - Commit Session…`. As operações de sessão recebem seus dados por **query params**, não por corpo.
- **Paginação em dois sabores.** As listagens aceitam `page[limit]` + `page[offset]` (deslocamento, 50 itens por padrão, máximo 50 por página) e, em algumas listagens de arquivos, `page[next]` (cursor, 1000 itens por padrão). Use `page[next]=0` na primeira chamada e o token devolvido nas seguintes.
- **Filtros e ordenação usam a sintaxe de chave composta.** `filter[type]=allfiles`, `filter[extension]=docx,jpeg`, `sort=-created_time`. O que varia nesses parâmetros é a **chave** da query, não só o valor — para trocar o critério, edite a chave na operação.

---

## Limitações conhecidas

- **Download de conteúdo não está no conector.** `GET /v1/workdrive/download/{resource_id}` roda em `download.zoho.<dc>`, um host diferente do da conta conectada, e o mesmo vale para o upload em stream (`upload.zohoapis.<dc>`) e para os três endpoints de progresso (`downloadprogress`, `uploadprogress`, `zipprogress`). Como uma conta conectada tem um único Host, essas cinco operações ficaram de fora. Para baixar conteúdo, gere um link externo com `Links - Create External Share` ou trate o download em uma operação avulsa configurada com URL completa.
- **Quatro operações de sessão de upload sem corpo.** `Uploadsession - Create/Commit Session` (normal e de revisão) não declaram corpo na especificação oficial: seus dados vão em query params. Isso é o comportamento da API, não uma lacuna do conector.
- **Duas operações de sessão compartilham a mesma descrição.** As variantes "normal" e "de revisão" de criar e confirmar sessão reduzem à mesma chave de operação no gerador, então recebem um texto que serve às duas. Os caminhos são distintos: a variante de revisão carrega `resource_id`.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Comments - Create Comments** | POST | Cria um comentário em um arquivo ou uma resposta a um comentário existente. |
| **Comments - Get Comment Info** | GET | Recupera as informações detalhadas de um comentário específico. |
| **Comments - Update Comments** | PATCH | Atualiza um comentário: cobre resolver, editar e reabrir o comentário. |
| **Comments - Delete Comment** | DELETE | Exclui um comentário ou uma resposta existente. |
| **Createzip - Create Multiple Files/Folders as ZIP** | POST | Compacta vários arquivos e pastas em um ZIP e salva o resultado na pasta de destino informada. |
| **Files - Create Zoho format files** | POST | Cria arquivos em formato Zoho: documentos no Zoho Writer, planilhas no Zoho Sheet e apresentações no Zoho Show. |
| **Files - Update Multiple Files Folders** | PATCH | Atualiza vários arquivos e pastas de uma vez: cobre mover para a lixeira, marcar e desmarcar como favorito, mover, restaurar e excluir definitivamente. |
| **Files - List Files/Folders inside a Folder** | GET | Lista todos os arquivos e pastas dentro de uma pasta específica. |
| **Files - Save File as Template** | POST | Salva um arquivo como modelo reutilizável na biblioteca de modelos informada. |
| **Files - Fetch Files Folders** | GET | Busca um arquivo ou pasta: cobre as informações do recurso e a URL da miniatura. |
| **Files - Update Files Folders** | PATCH | Atualiza um arquivo ou pasta: cobre mover, renomear, excluir definitivamente, favoritar, restaurar, enviar para a lixeira, liberar edição, check-out, check-in, marcar como final, incluir ou remover da visão de índice e atualizar link. |
| **Files - Get File/Folder Breadcrumbs** | GET | Busca a localização e a hierarquia de pastas de um arquivo ou pasta. |
| **Files - Get File Comments** | GET | Busca todos os comentários de um arquivo. |
| **Files - Copy Files Folders** | POST | Copia um ou vários arquivos e pastas para o destino informado. |
| **Files - Get File Query** | GET | Consulta o conteúdo do arquivo com o Zia e devolve respostas contextuais. Na primeira requisição o Zia indexa o arquivo antes de gerar respostas; acompanhe pelo status da resposta: 1 = indexação concluída, 2 = em andamento, 3 ou mais = falha. |
| **Files - Convert File to Zoho Format** | POST | Converte arquivos que não são do Zoho para os formatos do Zoho Office, como Writer, Sheet e Show. |
| **Files - Create Link file** | POST | Cria um arquivo de link, que permite guardar URLs da web e organizar arquivos e pastas de uso frequente em um só lugar. |
| **Files - Get File/Folder External Share Links** | GET | Busca todos os links de compartilhamento externo de um arquivo ou pasta. |
| **Files - Get Shared Users of File** | GET | Busca todos os usuários com quem um arquivo ou pasta está compartilhado. |
| **Files - Get Preview Meta Data** | GET | Recupera os metadados de prévia de um arquivo, incluindo URLs e tamanho. |
| **Files - Get File/Folder statistics** | GET | Busca as estatísticas de acesso de um arquivo ou pasta, com a atividade dos usuários, como visualizações e downloads. |
| **Files - Unzip File** | POST | Extrai o conteúdo de um arquivo ZIP para a pasta informada no WorkDrive. |
| **Files - Get File Versions** | GET | Recupera todas as versões disponíveis de um arquivo. |
| **Filesummary - Generate File Summary** | POST | Gera um resumo do arquivo informado com inteligência artificial. |
| **Filesummary - Get File Summary** | GET | Retorna o status do resumo de um arquivo: disponível, em geração ou não criado. |
| **Groupmembers - Add Multiple Members to Group** | POST | Adiciona vários membros a um grupo e retorna os dados dos membros criados. |
| **Groupmembers - Get Group Member Info** | GET | Recupera as informações detalhadas de um membro de grupo específico. |
| **Groupmembers - Update Group Member Role** | PATCH | Atualiza o papel de um membro existente do grupo. |
| **Groupmembers - Remove Group Member** | DELETE | Remove um membro do grupo informado. |
| **Groups - Create Group** | POST | Cria um grupo na equipe ou organização informada. |
| **Groups - Get Group Info** | GET | Recupera as informações detalhadas de um grupo específico. |
| **Groups - Update Groups** | PATCH | Atualiza um grupo: cobre renomear o grupo e alterar sua descrição. |
| **Groups - Delete Group** | DELETE | Exclui um grupo e remove todos os membros associados a ele. |
| **Groups - Get List of Group Members** | GET | Recupera a lista de todos os membros de um grupo específico. |
| **Libraries - Get Public Templates Library ID** | GET | Recupera as bibliotecas públicas de modelos conforme os filtros informados. |
| **Libraries - Get Template Library Info** | GET | Recupera os detalhes de uma biblioteca de modelos pelo ID da biblioteca. |
| **Libraries - Change Sort Type and Order** | PATCH | Atualiza as preferências de visualização do usuário para a biblioteca de modelos informada. |
| **Libraries - Get all Templates from a Template Library** | GET | Recupera a lista de arquivos de modelo da biblioteca informada, conforme os filtros aplicados. |
| **Libraries - Get Template Library Permissions** | GET | Recupera as permissões de compartilhamento configuradas para uma biblioteca de modelos. |
| **Links - Create External Share** | POST | Cria um compartilhamento externo: cobre o link personalizado e o link de download. |
| **Links - Get External Share Link Info** | GET | Recupera as informações detalhadas de um link de compartilhamento externo. |
| **Links - Update External Share** | PATCH | Atualiza um compartilhamento externo: cobre as configurações de download, de expiração e de senha do link. |
| **Links - Revoke External Share Link** | DELETE | Revoga um link de compartilhamento externo existente de um recurso. |
| **Members - Create Team Folder Members** | POST | Adiciona membros ou grupos como colaboradores de uma pasta de equipe. |
| **Members - Update Member Role in Team Folder** | PATCH | Atualiza o papel de acesso de um membro compartilhado na pasta de equipe informada. |
| **Members - Delete Member from Team Folder** | DELETE | Remove o usuário ou grupo informado da lista de colaboração da pasta de equipe. |
| **Multizip - Download Multiple Files/Folders as ZIP** | POST | Compacta vários arquivos e pastas em um ZIP e retorna uma chave WMS para acompanhar os metadados do ZIP. |
| **Permissions - Create Files Folders Share** | POST | Compartilha arquivos e pastas: cobre o compartilhamento com membros individuais, com a equipe, com membros de grupo, com todos na internet e a geração de código de incorporação. |
| **Permissions - Get File/Folder Collaboration Info** | GET | Retorna os dados de colaboração correspondentes ao ID de compartilhamento informado. |
| **Permissions - Update Files Folders Share** | PATCH | Atualiza um compartilhamento de arquivo ou pasta: cobre as permissões e a data de expiração. |
| **Permissions - Delete File/Folder Share Access** | DELETE | Remove o acesso a um arquivo ou pasta compartilhado. |
| **Privatespace - Get Files in My Folders** | GET | Recupera os arquivos das suas Minhas pastas. |
| **Privatespace - Get Folders in My Folders** | GET | Recupera as pastas das suas Minhas pastas. |
| **Privatespace - Get My Folders Links** | GET | Retorna a lista de links compartilhados do recurso de Minhas pastas informado. |
| **Privatespace - Get Trashed Files in My Folders** | GET | Retorna a lista de arquivos na lixeira do recurso de Minhas pastas informado. |
| **Resourceproperty - Get File/Folder ResourceProperty** | GET | Busca propriedades adicionais de um arquivo ou pasta. |
| **Teamfolders - Create Team Folder** | POST | Cria uma pasta de equipe no local pai informado. |
| **Teamfolders - Get Team Folder Info** | GET | Retorna os metadados detalhados da pasta de equipe informada, incluindo configurações de compartilhamento, atributos do espaço de trabalho e status atual. |
| **Teamfolders - Update Team Folder** | PATCH | Atualiza uma pasta de equipe: cobre fixar e desafixar, arquivar e desarquivar, renomear e alterar a descrição. |
| **Teamfolders - Delete Team Folder** | DELETE | Exclui a pasta de equipe informada e atualiza o estado do espaço de trabalho relacionado. |
| **Teamfolders - Get Team Folder Files and Folders** | GET | Retorna os arquivos e pastas da pasta de equipe informada, com filtros, ordenação, seleção de campos e paginação. |
| **Teamfolders - Get list of Sub Folders** | GET | Retorna as subpastas disponíveis na pasta de equipe informada, com paginação e ordenação. |
| **Teamfolders - Get Team Folder Links** | GET | Retorna os links compartilhados criados para recursos da pasta de equipe informada, com filtro por tipo e paginação. |
| **Teamfolders - Get Team Folder Members** | GET | Retorna os membros e grupos compartilhados na pasta de equipe informada, com filtros, busca e paginação. |
| **Teamfolders - Get Team Folder MyDraft Files** | GET | Retorna os arquivos de rascunho criados pelo usuário atual na pasta de equipe informada. |
| **Teamfolders - Get Team Folder Settings** | GET | Recupera as configurações atuais da pasta de equipe informada, incluindo compartilhamento externo, conversão de arquivos, permissão de download para visualizadores e acesso por dispositivo. |
| **Teamfolders - Get Team Folder Trashed Files** | GET | Retorna os arquivos na lixeira da pasta de equipe informada, para administradores com acesso à lixeira. |
| **Teamfolders - Get Team Folder Unread Files** | GET | Retorna os arquivos não lidos da pasta de equipe informada, com filtro opcional por tipo de recurso. |
| **Teams - Get Team Info** | GET | Retorna os dados de perfil e configuração da equipe informada, incluindo nome, descrição, quantidade de membros e configurações de compartilhamento. |
| **Teams - Update Teams** | PATCH | Atualiza uma equipe: cobre alterar o nome, a descrição e definir a equipe preferida. |
| **Teams - Get Current Team Member** | GET | Retorna os dados de participação do usuário autenticado na equipe informada. |
| **Teams - Get Groups in a Team** | GET | Retorna todos os grupos da equipe informada, com filtro por tipo de grupo e paginação. |
| **Teams - Get Org Templates Library ID** | GET | Recupera os detalhes da biblioteca de modelos da equipe informada. |
| **Teams - Search Records** | GET | Busca registros: cobre a busca em Minhas pastas, em uma pasta de equipe, em uma pasta, em toda a equipe, por modelo de dados e em Compartilhados comigo. |
| **Teams - Get Team Settings** | GET | Recupera as configurações de administrador da equipe informada, incluindo permissões, políticas de compartilhamento, restrições de armazenamento e configurações de recursos. |
| **Teams - Get Team Folders in a Team** | GET | Retorna todas as pastas de equipe da equipe informada, com filtro opcional por tipo e paginação. |
| **Teams - Get Team Members** | GET | Retorna os membros da equipe informada, com filtros e busca opcionais. |
| **Upload - Upload New Version** | POST | Envia uma nova versão de um arquivo existente. |
| **Uploadsession - Upload Session Progress** | GET | Retorna os dados de progresso de uma sessão de upload em partes em andamento. |
| **Uploadsession - Commit Session (Normal Upload)** | POST | Conclui a sessão de upload em partes depois de todas as partes enviadas, criando o novo arquivo ou a nova versão após validar a atividade da sessão, a expiração, os limites de armazenamento e as permissões. |
| **Uploadsession - Create Session (Normal Upload)** | POST | Cria uma sessão de upload em partes, para enviar um arquivo novo ou uma nova versão de um arquivo existente. |
| **Uploadsession - Commit Session for Revision Upload** | POST | Conclui a sessão de upload em partes depois de todas as partes enviadas, criando o novo arquivo ou a nova versão após validar a atividade da sessão, a expiração, os limites de armazenamento e as permissões. |
| **Uploadsession - Create Session for Revision Upload** | POST | Cria uma sessão de upload em partes, para enviar um arquivo novo ou uma nova versão de um arquivo existente. |
| **Users - Invite New Member to Team** | POST | Convida um ou mais usuários para entrar na equipe pelo endereço de e-mail. |
| **Users - Get User Info** | GET | Retorna os dados do usuário autenticado. |
| **Users - Get Team Member Info** | GET | Retorna as informações de perfil e papel do membro da equipe informado. |
| **Users - Update users** | PATCH | Atualiza um membro da equipe: cobre excluir, suspender e alterar o papel do membro. |
| **Users - Get Team Member Collaborators** | GET | Retorna a lista de usuários e grupos com quem o membro da equipe informado compartilhou arquivos ou pastas. |
| **Users - Get Favorited Files** | GET | Retorna a lista de arquivos marcados como favoritos pelo membro da equipe informado. |
| **Users - Get Team Member's Groups** | GET | Retorna todos os grupos a que o membro da equipe informado pertence dentro da equipe. |
| **Users - Get Files in Shared with Me** | GET | Retorna os arquivos da aba Compartilhados comigo, ou seja, os arquivos que outros membros da equipe compartilharam com o usuário. |
| **Users - Get Folders in Shared with Me** | GET | Retorna a lista de pastas compartilhadas com o membro da equipe informado. |
| **Users - Get My Templates Library ID** | GET | Recupera os detalhes da biblioteca de modelos do membro da equipe informado. |
| **Users - Get My Folders Id** | GET | Retorna o ID de Minhas pastas do membro da equipe informado. |
| **Users - Get Recent Files** | GET | Retorna a lista de arquivos acessados recentemente pelo membro da equipe informado. |
| **Users - Get Suggested Files** | GET | Retorna a lista de arquivos sugeridos para o membro da equipe informado. |
| **Users - Get All Teams of User** | GET | Busca todas as equipes associadas a um usuário. |
| **Versions - Restore as Top Version** | POST | Restaura uma versão selecionada do arquivo como a versão mais recente. |
| **Versions - Delete Version** | DELETE | Exclui uma versão específica de um arquivo. O ID da versão é criado quando um usuário cria uma nova versão do arquivo. |

---

## Documentação oficial

- [Zoho WorkDrive API](https://workdrive.zoho.com/apidocs/v1/)
- [Escopos OAuth do Zoho WorkDrive](https://workdrive.zoho.com/apidocs/v1/oauth)
- [Especificação OpenAPI oficial](https://github.com/zoho/zohoworkdrive-oas)
