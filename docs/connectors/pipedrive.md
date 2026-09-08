# Pipedrive

## Contexto

A API REST do **Pipedrive** expõe o CRM inteiro: o pipeline de vendas (negócios, etapas, funis), a base de contatos (pessoas e organizações), leads, catálogo de produtos, atividades e agenda, projetos e tarefas, caixa de e-mail integrada, registros de chamadas, metas, arquivos, filtros e toda a administração da conta (usuários, papéis, times, conjuntos de permissões, webhooks).

**Conceitos fundamentais**

- **Deal (negócio)** — a unidade central do CRM: um negócio em andamento, que vive dentro de um **pipeline** (funil) e caminha por **stages** (etapas). Praticamente tudo no Pipedrive se conecta a um negócio.
- **Person e Organization** — a base de contatos. Uma pessoa pode pertencer a uma organização, e ambas podem ter **relacionamentos** entre organizações (matriz/filial, por exemplo).
- **Lead** — contato ainda não qualificado, antes de virar negócio. O ciclo `lead → deal` (e o inverso) tem operações próprias de conversão, cada uma com uma operação de consulta do status assíncrono da conversão.
- **Custom fields** — o Pipedrive é fortemente customizável: cada tipo de item (negócio, pessoa, organização, produto, projeto, lead, nota, atividade) tem seu próprio domínio de **Fields**, que lista, cria e altera os campos personalizados. Nos corpos de requisição, um campo personalizado é referenciado pela sua **chave hash** de 40 caracteres, não pelo nome — descubra-a pela operação de listagem de campos do item.
- **Activity** — compromisso, ligação, e-mail ou tarefa vinculada a um item, com **Activity Types** configuráveis.
- **Project** — a camada de gestão de entregas, posterior à venda: projetos têm **boards**, **phases**, **tasks** e um **plan**, e podem nascer de **templates**.
- **Follower** — usuário que acompanha um item e recebe suas notificações. Negócios, pessoas, organizações e produtos têm operações de seguidores e de *changelog* de seguidores.
- **Paginação por cursor** — os endpoints da v2 paginam com `cursor` + `limit` (máximo 500). Os da v1 usam `start` + `limit`. A resposta traz o cursor da página seguinte; repita a chamada até ele vir vazio.

**Escopo deste conector**

O módulo cobre a **API v2 inteira** e os recursos da **v1** que não têm equivalente na v2: **310 operações** em 43 domínios — 158 na v2, 150 na v1 e 2 auxiliares do fluxo OAuth.

| Domínio | Operações | Versão | Cobre |
| ------- | --------- | ------ | ----- |
| Deals | 32 | v2 + v1 | CRUD, busca, arquivados, conversão em lead, descontos, seguidores, participantes, duplicação, merge, resumo, timeline, changelog, arquivos, e-mails e usuários permitidos |
| Products | 22 | v2 + v1 | CRUD, busca, duplicação, seguidores, imagem (upload, troca, remoção), variações, negócios vinculados, arquivos e usuários permitidos |
| Persons | 20 | v2 + v1 | CRUD, busca, seguidores, foto (upload e remoção), changelog, arquivos, e-mails, merge, produtos associados e usuários permitidos |
| Projects | 16 | v2 + v1 | CRUD, busca, arquivamento, changelog, atividades, grupos, plano (com edição de atividade e tarefa) e tarefas |
| Organizations | 16 | v2 + v1 | CRUD, busca, seguidores, changelog, arquivos, e-mails, merge e usuários permitidos |
| Roles | 12 | v1 | CRUD de papéis, atribuições, visibilidade de pipelines e configurações do papel |
| Users | 10 | v2 + v1 | listar, criar, atualizar, buscar por nome, usuário atual, permissões, atribuições de papel e seguidores |
| Notes | 10 | v1 | CRUD de notas e CRUD de comentários de nota |
| Leads | 10 | v2 + v1 | CRUD, busca, arquivados, conversão em negócio e usuários permitidos |
| Product Fields | 9 | v2 + v1 | CRUD de campos, opções em massa e exclusão múltipla |
| Person Fields | 9 | v2 + v1 | CRUD de campos, opções em massa e exclusão múltipla |
| Organization Fields | 9 | v2 + v1 | CRUD de campos, opções em massa e exclusão múltipla |
| Deal Fields | 9 | v2 + v1 | CRUD de campos, opções em massa e exclusão múltipla |
| Project Fields | 8 | v2 | CRUD de campos e opções em massa |
| Pipelines | 8 | v2 + v1 | CRUD de funis, taxas de conversão, negócios do funil e movimentações |
| Legacy Teams | 8 | v1 | CRUD de times legados e gestão dos seus usuários |
| Files | 8 | v1 | listar, upload, arquivo remoto, vínculo remoto, detalhar, atualizar, excluir e download |
| Filters | 7 | v1 | CRUD de filtros, exclusão em massa e *helpers* de condição |
| Deal Products | 7 | v2 | produtos de vários negócios, anexar (um ou vários), atualizar e desanexar |
| Stages | 6 | v2 + v1 | CRUD de etapas e negócios de uma etapa |
| Mailbox | 6 | v1 | threads e mensagens da caixa de e-mail: listar, detalhar, atualizar e excluir |
| Tasks | 5 | v2 | CRUD de tarefas de projeto |
| Project Phases | 5 | v2 | CRUD de fases de projeto |
| Project Boards | 5 | v2 | CRUD de quadros de projeto |
| Organization Relationships | 5 | v1 | CRUD de relacionamentos entre organizações |
| Goals | 5 | v1 | criar, buscar, atualizar, excluir metas e consultar resultado |
| Call Logs | 5 | v1 | CRUD de registros de chamada e anexo do áudio da gravação |
| Activities | 5 | v2 | CRUD de atividades |
| Lead Labels | 4 | v1 | CRUD de etiquetas de lead |
| Deal Installments | 4 | v2 | parcelas de negócios: listar, criar, atualizar e excluir |
| Activity Types | 4 | v1 | CRUD de tipos de atividade |
| Webhooks | 3 | v1 | listar, criar e excluir webhooks |
| Permission Sets | 3 | v1 | listar conjuntos de permissão, detalhar e listar atribuições |
| Project Templates | 2 | v2 | listar templates de projeto e detalhar |
| OAuth | 2 | — | montar a URL de autorização e trocar/renovar tokens (auxiliares do setup, ver **Autenticação**) |
| Item Search | 2 | v2 | busca global entre vários tipos de item e busca por campo específico |
| Activity Fields | 2 | v2 | listar e detalhar campos de atividade |
| User Settings | 1 | v1 | configurações do usuário autenticado |
| User Connections | 1 | v1 | conexões do usuário |
| Recents | 1 | v1 | alterações recentes na conta |
| Note Fields | 1 | v1 | campos de nota |
| Lead Sources | 1 | v1 | origens de lead |
| Lead Fields | 1 | v1 | campos de lead |
| Currencies | 1 | v1 | moedas suportadas |

Ficaram fora os endpoints da v1 que a v2 já substitui — quando existe o par, apenas a versão v2 foi emitida. Também não entram os endpoints de integração de marketplace que exigem app publicado e escopo dedicado (`video-calls`, `messengers-integration`, provedores de chamada).

---

## Autenticação

**Tipo:** Header authentication

O Pipedrive aceita dois modos de autenticação: **API token** (no parâmetro de header `x-api-token`) e **OAuth 2.0** com callback. Este template usa o fluxo de API Token pela conveniência com o server-side, usando **Header authentication**.

É recomendável criar uma conta de serviço somente com as permissões necessárias para o seu uso da integração.

### O Host depende da empresa (`api_domain`)

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://<>sua-empresa</>.pipedrive.com` |
| Porta | 443 |
| Chave | x-api-token |
| Valor | {{seu-api-token}} |

> O Host termina no domínio da empresa, **sem** o prefixo de versão. A versão é o primeiro segmento do caminho de cada operação (`api/v2/...` na v2, `v1/...` na v1) — é o que permite as duas versões coexistirem sob a mesma conta conectada.

### Obtendo os tokens

1. Entre na sua conta do Pipedrive
2. Clique na sua foto de perfil
3. Selecione **Company Settings** no menu ou diretamente em **Personal Preferences**
4. Na seção de Personal Preferences, troque para a aba de API
5. Copie o seu API Token ou gere um novo e copie.

---

## Convenções deste conector

- **A versão fica no caminho, não no Host.** Operações da v2 começam em `api/v2/...`; as da v1, em `v1/...`. Não há parâmetro de versão: o par de versões não é intercambiável (métodos, formato de resposta e paginação diferem), então cada operação aponta para a versão em que aquele recurso realmente existe.
- **Corpo JSON e `x-www-form-urlencoded` é um parâmetro de texto único.** As 102 operações de escrita com corpo declaram um parâmetro `body` (`string`), com o JSON completo no *sample*. Campos personalizados entram nesse JSON pela **chave hash de 40 caracteres**, no mesmo nível dos campos nativos. Cinco operações usam `application/x-www-form-urlencoded` em vez de JSON — o `Content-Type` já vem declarado nelas: **Files - Create a remote file and link it to an item**, **Files - Link a remote file to an item**, **Files - Update file details**, **Mailbox - Update mail thread details** e **OAuth - Get or refresh the tokens**.
- **Upload de arquivo é multipart e exige base64.** Cinco operações enviam arquivo: **Files - Add file**, **Persons - Add person picture**, **Products - Upload an image for a product**, **Products - Update an image for a product** e **Call Logs - Attach an audio file to the call log**. Informe o conteúdo em **base64** no parâmetro do arquivo, ajuste o MIME e o nome na linha do corpo (`file:<>file</>:mime:application/pdf:contrato.pdf`). O corpo declara apenas os campos **obrigatórios**; campos opcionais (como `deal_id` no upload de arquivo) devem ser acrescentados manualmente conforme o uso.
- **Path e query são exaustivos.** Todos os parâmetros de caminho e de query de cada endpoint estão declarados, obrigatórios e opcionais, cada um com descrição e *sample*.
- **Paginação difere entre versões.** Na v2, `cursor` + `limit` (máximo 500); na v1, `start` + `limit`. Percorra as páginas até o cursor (ou o `more_items_in_collection`, na v1) indicar o fim.
- **Conversões são assíncronas.** **Deals - Convert a deal to a lead** e **Leads - Convert a lead to a deal** iniciam a conversão e devolvem um identificador; consulte **Get Deal conversion status** / **Get Lead conversion status** até o status indicar conclusão.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Activities - Get all activities** | GET | Retorna dados sobre todas as atividades. |
| **Activities - Add a new activity** | POST | Adiciona uma nova atividade. |
| **Activities - Get details of an activity** | GET | Retorna os detalhes de uma atividade específica. |
| **Activities - Update an activity** | PATCH | Atualiza as propriedades de uma atividade. |
| **Activities - Delete an activity** | DELETE | Marca uma atividade como deletada. Após 30 dias, a atividade será permanentemente deletada. |
| **Activity Fields - Get all activity fields** | GET | Retorna metadados sobre todos os campos de atividade da empresa. |
| **Activity Fields - Get one activity field** | GET | Retorna metadados sobre um campo de atividade específico. |
| **Project Boards - Get all project boards** | GET | Retorna todos os quadros de projeto ativos. |
| **Project Boards - Add a project board** | POST | Adiciona um novo quadro de projeto. |
| **Project Boards - Get details of a project board** | GET | Retorna os detalhes de um quadro de projeto específico. |
| **Project Boards - Update a project board** | PATCH | Atualiza as propriedades de um quadro de projeto. |
| **Project Boards - Delete a project board** | DELETE | Marca um quadro de projeto como deletado. |
| **Deal Fields - Get all deal fields** | GET | Retorna metadados sobre todos os campos de deal da empresa. |
| **Deal Fields - Create one deal field** | POST | Cria um novo campo customizado de deal. |
| **Deal Fields - Get one deal field** | GET | Retorna metadados sobre um campo de deal específico. |
| **Deal Fields - Update one deal field** | PATCH | Atualiza um campo customizado de deal. O field_code e field_type não podem ser alterados. Pelo menos um campo é obrigatório no corpo da requisição. |
| **Deal Fields - Delete one deal field** | DELETE | Marca um campo customizado como deletado. |
| **Deal Fields - Add deal field options in bulk** | POST | Adiciona novas opções a um campo customizado de deal que suporta opções (enum ou set). Esta operação é atômica; todas são adicionadas ou nenhuma é adicionada. Retorna apenas as novas opções. |
| **Deal Fields - Update deal field options in bulk** | PATCH | Atualiza opções existentes de um campo customizado de deal. Esta operação é atômica e falha se algum ID não existir. Retorna apenas as opções atualizadas. |
| **Deal Fields - Delete deal field options in bulk** | DELETE | Remove opções existentes de um campo customizado de deal. Esta operação é atômica e falha se algum ID não existir. Retorna apenas as opções removidas. |
| **Deals - Get all deals** | GET | Retorna dados sobre todos os negócios não arquivados. |
| **Deals - Add a new deal** | POST | Adiciona um novo negócio. |
| **Deals - Get all archived deals** | GET | Retorna dados sobre todos os negócios arquivados. |
| **Deal Installments - List installments added to a list of deals** | GET | Lista parcelas anexadas a uma lista de negócios. Disponível em planos Growth e superior. |
| **Deal Products - Get deal products of several deals** | GET | Retorna dados sobre produtos anexados a negociações. |
| **Deals - Search deals** | GET | Pesquisa todos os negócios por título, notas e/ou campos personalizados. Este endpoint é um wrapper de <a href="https://developers.pipedrive.com/docs/api/v1/ItemSearch#searchItem">/v1/itemSearch</a> com um escopo OAuth mais restrito. |
| **Deals - Get details of a deal** | GET | Retorna os detalhes de um negócio específico. |
| **Deals - Update a deal** | PATCH | Atualiza as propriedades de um negócio. |
| **Deals - Delete a deal** | DELETE | Marca um negócio como excluído. Após 30 dias, o negócio será permanentemente deletado. |
| **Deals - Convert a deal to a lead** | POST | Inicia uma conversão de um negócio para um cliente potencial. O valor retornado é um ID de um trabalho atribuído para executar a conversão. |
| **Deals - Get Deal conversion status** | GET | Retorna informações sobre a conversão. O status está sempre presente e seu valor (not_started, running, completed, failed, rejected) representa o estado atual da conversão. |
| **Deals - List discounts added to a deal** | GET | Lista descontos anexados a um negócio. |
| **Deals - Add a discount to a deal** | POST | Adiciona um desconto a um negócio, alterando o valor do negócio se o negócio tiver produtos únicos anexados. |
| **Deals - Update a discount added to a deal** | PATCH | Edita um desconto adicionado a um negócio, alterando o valor do negócio se o negócio tiver produtos únicos anexados. |
| **Deals - Delete a discount from a deal** | DELETE | Remove um desconto de um negócio, alterando o valor do negócio se o negócio tiver produtos únicos anexados. |
| **Deals - List followers of a deal** | GET | Lista usuários que estão seguindo o negócio. |
| **Deals - Add a follower to a deal** | POST | Adiciona um usuário como seguidor do negócio. |
| **Deals - List followers changelog of a deal** | GET | Lista changelogs sobre usuários que seguiram o negócio. |
| **Deals - Delete a follower from a deal** | DELETE | Deleta um usuário seguidor do negócio. |
| **Deal Installments - Add an installment to a deal** | POST | Adiciona uma parcela a um negócio. Apenas possível se o negócio incluir produtos únicos, não recorrentes. Disponível em planos Growth e superior. |
| **Deal Installments - Update an installment added to a deal** | PATCH | Edita uma parcela adicionada a um negócio. Disponível em planos Growth e superior. |
| **Deal Installments - Delete an installment from a deal** | DELETE | Remove uma parcela de um negócio. Disponível em planos Growth e superior. |
| **Deal Products - List products attached to a deal** | GET | Lista produtos anexados a uma negociação. |
| **Deal Products - Add a product to a deal** | POST | Adiciona um produto a uma negociação, criando um novo item chamado produto-negociação. |
| **Deal Products - Delete many products from a deal** | DELETE | Remove vários produtos de uma negociação. Se nenhuma ID de produto for especificada, até 100 produtos serão removidos. Máximo de 100 IDs de produtos pode ser fornecido por solicitação. |
| **Deal Products - Add multiple products to a deal** | POST | Adiciona vários produtos a uma negociação em uma única solicitação. Máximo de 100 produtos permitidos por solicitação. |
| **Deal Products - Update the product attached to a deal** | PATCH | Atualiza os detalhes do produto que foi anexado a uma negociação. |
| **Deal Products - Delete an attached product from a deal** | DELETE | Remove um anexo de produto de uma negociação usando o `product_attachment_id`. |
| **Item Search - Perform a search from multiple item types** | GET | Realiza uma busca a partir de tipos de itens e campos de sua escolha. |
| **Item Search - Perform a search using a specific field from an item type** | GET | Realiza uma busca a partir dos valores de um campo específico. Os resultados podem ser valores distintos do campo ou IDs de itens reais (negócios, prospectos, pessoas, organizações ou produtos). |
| **Leads - Search leads** | GET | Pesquisa leads por título, notas e/ou campos customizados. |
| **Leads - Convert a lead to a deal** | POST | Inicia a conversão de um lead em um deal, retornando o ID de um trabalho para realizar a conversão. |
| **Leads - Get Lead conversion status** | GET | Retorna dados sobre a conversão, incluindo status atual e ID do deal se concluída com sucesso. |
| **Organization Fields - Get all organization fields** | GET | Retorna metadados sobre todos os campos de organização da empresa. |
| **Organization Fields - Create one organization field** | POST | Cria um novo campo personalizado de organização. |
| **Organization Fields - Get one organization field** | GET | Retorna metadados sobre um campo de organização específico. |
| **Organization Fields - Update one organization field** | PATCH | Atualiza um campo personalizado de organização. O field_code e field_type não podem ser alterados. Pelo menos um campo deve ser fornecido no corpo da solicitação. |
| **Organization Fields - Delete one organization field** | DELETE | Marca um campo personalizado como excluído. |
| **Organization Fields - Add organization field options in bulk** | POST | Adiciona novas opções a um campo personalizado de organização que suporta opções (tipos de campo enum ou set). Esta operação é atômica - todas as opções são adicionadas ou nenhuma é adicionada. Retorna apenas as opções recém-adicionadas. |
| **Organization Fields - Update organization field options in bulk** | PATCH | Atualiza opções existentes para um campo personalizado de organização. Esta operação é atômica e falha se alguma das IDs de opção especificadas não existirem. Retorna apenas as opções atualizadas. |
| **Organization Fields - Delete organization field options in bulk** | DELETE | Remove opções existentes de um campo personalizado de organização. Esta operação é atômica e falha se alguma das IDs de opção especificadas não existirem. Retorna apenas as opções excluídas. |
| **Organizations - Get all organizations** | GET | Retorna dados sobre todas as organizações. |
| **Organizations - Add a new organization** | POST | Adiciona uma nova organização. |
| **Organizations - Search organizations** | GET | Pesquisa todas as organizações por nome, endereço, notas e/ou campos personalizados. Este endpoint é um wrapper de <a href="https://developers.pipedrive.com/docs/api/v1/ItemSearch#searchItem">/v1/itemSearch</a> com um escopo OAuth mais restrito. |
| **Organizations - Get details of a organization** | GET | Retorna os detalhes de uma organização específica. |
| **Organizations - Update a organization** | PATCH | Atualiza as propriedades de uma organização. |
| **Organizations - Delete a organization** | DELETE | Marca uma organização como deletada. Após 30 dias, a organização será permanentemente deletada. |
| **Organizations - List followers of an organization** | GET | Lista usuários que estão seguindo a organização. |
| **Organizations - Add a follower to an organization** | POST | Adiciona um usuário como seguidor da organização. |
| **Organizations - List followers changelog of an organization** | GET | Lista registros de alterações sobre usuários que seguem a organização. |
| **Organizations - Delete a follower from an organization** | DELETE | Deleta um usuário seguidor da organização. |
| **Person Fields - Get all person fields** | GET | Retorna metadados sobre todos os campos de pessoa na empresa. |
| **Person Fields - Create one person field** | POST | Cria um novo campo customizado de pessoa. |
| **Person Fields - Get one person field** | GET | Retorna metadados sobre um campo de pessoa específico. |
| **Person Fields - Update one person field** | PATCH | Atualiza um campo customizado de pessoa. O field_code e field_type não podem ser alterados. Pelo menos um campo deve ser fornecido no corpo da requisição. |
| **Person Fields - Delete one person field** | DELETE | Marca um campo customizado como deletado. |
| **Person Fields - Add person field options in bulk** | POST | Adiciona novas opções a um campo customizado de pessoa que suporta opções (tipos enum ou set). Esta operação é atômica — todas as opções são adicionadas ou nenhuma é adicionada. Retorna apenas as opções recém-adicionadas. |
| **Person Fields - Update person field options in bulk** | PATCH | Atualiza opções existentes de um campo customizado de pessoa. Esta operação é atômica e falha se qualquer ID de opção especificada não existir. Retorna apenas as opções atualizadas. |
| **Person Fields - Delete person field options in bulk** | DELETE | Remove opções existentes de um campo customizado de pessoa. Esta operação é atômica e falha se qualquer ID de opção especificada não existir. Retorna apenas as opções removidas. |
| **Persons - Get all persons** | GET | Retorna dados de todas as pessoas. Os campos `ims`, `postal_address`, `notes`, `birthday` e `job_title` são incluídos apenas se a sincronização de contatos está ativa. |
| **Persons - Add a new person** | POST | Adiciona uma nova pessoa. Se a empresa utiliza Campanhas, o endpoint aceita e retorna `marketing_status`. Os campos `im`, `postal_address`, `notes`, `birthday` e `job_title` são criados apenas ao configurar sincronização de contatos. |
| **Persons - Search persons** | GET | Pesquisa pessoas por nome, email, telefone, notas e/ou campos personalizados. Pode filtrar resultados por ID da organização. |
| **Persons - Get details of a person** | GET | Retorna os detalhes de uma pessoa específica. Os campos `ims`, `postal_address`, `notes`, `birthday` e `job_title` são incluídos apenas se a sincronização de contatos está ativa. |
| **Persons - Update a person** | PATCH | Atualiza as propriedades de uma pessoa. Se a empresa utiliza Campanhas, o endpoint aceita e retorna `marketing_status`. Os campos `im`, `postal_address`, `notes`, `birthday` e `job_title` são criados apenas ao configurar sincronização de contatos. |
| **Persons - Delete a person** | DELETE | Marca uma pessoa como deletada. Após 30 dias, será permanentemente removida. |
| **Persons - List followers of a person** | GET | Lista usuários que seguem a pessoa. |
| **Persons - Add a follower to a person** | POST | Adiciona um usuário como seguidor da pessoa. |
| **Persons - List followers changelog of a person** | GET | Lista o histórico de alterações dos seguidores da pessoa. |
| **Persons - Delete a follower from a person** | DELETE | Remove um usuário que segue a pessoa. |
| **Persons - Get picture of a person** | GET | Retorna a imagem associada à pessoa. As URLs incluem versões de 128x128 e 512x512 pixels. |
| **Project Phases - Get project phases** | GET | Retorna todas as fases de projeto ativas sob um painel específico. |
| **Project Phases - Add a project phase** | POST | Adiciona uma nova fase de projeto a um painel. |
| **Project Phases - Get details of a project phase** | GET | Retorna os detalhes de uma fase de projeto específica. |
| **Project Phases - Update a project phase** | PATCH | Atualiza as propriedades de uma fase de projeto. |
| **Project Phases - Delete a project phase** | DELETE | Marca uma fase de projeto como deletada. |
| **Pipelines - Get all pipelines** | GET | Retorna dados sobre todos os pipelines. |
| **Pipelines - Add a new pipeline** | POST | Adiciona um novo pipeline. |
| **Pipelines - Get one pipeline** | GET | Retorna dados sobre um pipeline específico. |
| **Pipelines - Update a pipeline** | PATCH | Atualiza as propriedades de um pipeline. |
| **Pipelines - Delete a pipeline** | DELETE | Marca um pipeline como excluído. |
| **Product Fields - Get all product fields** | GET | Retorna metadados sobre todos os campos de produto da empresa. |
| **Product Fields - Create one product field** | POST | Cria um novo campo customizado de produto. |
| **Product Fields - Get one product field** | GET | Retorna metadados sobre um campo de produto específico. |
| **Product Fields - Update one product field** | PATCH | Atualiza um campo customizado de produto. O field_code e field_type não podem ser alterados. Pelo menos um campo deve ser fornecido no corpo da requisição. |
| **Product Fields - Delete one product field** | DELETE | Marca um campo customizado como excluído. |
| **Product Fields - Add product field options in bulk** | POST | Adiciona novas opções a um campo customizado de produto que suporta opções (enum ou set). Esta operação é atômica - todas as opções são adicionadas ou nenhuma é. Retorna apenas as opções recém-adicionadas. |
| **Product Fields - Update product field options in bulk** | PATCH | Atualiza opções existentes para um campo customizado de produto. Esta operação é atômica e falha se algum ID de opção não existir. Retorna apenas as opções atualizadas. |
| **Product Fields - Delete product field options in bulk** | DELETE | Remove opções existentes de um campo customizado de produto. Esta operação é atômica e falha se algum ID de opção não existir. Retorna apenas as opções excluídas. |
| **Products - Get all products** | GET | Retorna dados sobre todos os produtos. |
| **Products - Add a product** | POST | Adiciona um novo produto ao inventário de produtos. Para mais informações, consulte o tutorial para <a href="https://pipedrive.readme.io/docs/adding-a-product" target="_blank" rel="noopener noreferrer">adicionar um produto</a>. |
| **Products - Search products** | GET | Busca todos os produtos por nome, código e/ou campos customizados. Este endpoint é um wrapper de <a href="https://developers.pipedrive.com/docs/api/v1/ItemSearch#searchItem">/v1/itemSearch</a> com um escopo OAuth mais restrito. |
| **Products - Get one product** | GET | Retorna dados sobre um produto específico. |
| **Products - Update a product** | PATCH | Atualiza dados do produto. |
| **Products - Delete a product** | DELETE | Marca um produto como deletado. Após 30 dias, o produto será permanentemente deletado. |
| **Products - Duplicate a product** | POST | Cria uma duplicação de um produto existente, incluindo todas as variações, preços e campos customizados. |
| **Products - List followers of a product** | GET | Lista usuários que estão seguindo o produto. |
| **Products - Add a follower to a product** | POST | Adiciona um usuário como seguidor do produto. |
| **Products - List followers changelog of a product** | GET | Lista o histórico de seguidores do produto. |
| **Products - Delete a follower from a product** | DELETE | Remove um usuário seguidor do produto. |
| **Products - Get image of a product** | GET | Recupera a imagem de um produto. A URL pública tem uma vida útil limitada de 7 dias. |
| **Products - Upload an image for a product** | POST | Carrega uma imagem para um produto. |
| **Products - Update an image for a product** | PUT | Atualiza a imagem de um produto. |
| **Products - Delete an image of a product** | DELETE | Remove a imagem de um produto. |
| **Products - Get all product variations** | GET | Retorna dados sobre todas as variações de produtos. |
| **Products - Add a product variation** | POST | Adiciona uma nova variação de produto. |
| **Products - Update a product variation** | PATCH | Atualiza dados da variação do produto. |
| **Products - Delete a product variation** | DELETE | Remove uma variação de produto. |
| **Project Fields - Get all project fields** | GET | Retorna metadados sobre todos os campos de projeto na empresa. |
| **Project Fields - Create one project field** | POST | Cria um novo campo personalizado de projeto. |
| **Project Fields - Get one project field** | GET | Retorna metadados sobre um campo de projeto específico. |
| **Project Fields - Update one project field** | PATCH | Atualiza um campo personalizado de projeto. O field_code e field_type não podem ser alterados. Pelo menos um campo deve ser fornecido no corpo da requisição. |
| **Project Fields - Delete one project field** | DELETE | Marca um campo personalizado como excluído. |
| **Project Fields - Add project field options in bulk** | POST | Adiciona novas opções a um campo personalizado de projeto que suporta opções (tipos enum ou set). Operação atômica: todas as opções são adicionadas ou nenhuma. Retorna apenas as opções recém-adicionadas. |
| **Project Fields - Update project field options in bulk** | PATCH | Atualiza opções existentes de um campo personalizado de projeto. Operação atômica: falha se qualquer ID de opção especificado não existir. Retorna apenas as opções atualizadas. |
| **Project Fields - Delete project field options in bulk** | DELETE | Remove opções existentes de um campo personalizado de projeto. Operação atômica: falha se qualquer ID de opção especificado não existir. Retorna apenas as opções deletadas. |
| **Project Templates - Get all project templates** | GET | Retorna todos os templates de projeto não deletados. |
| **Project Templates - Get details of a template** | GET | Retorna os detalhes de um template de projeto específico. |
| **Projects - Get all projects** | GET | Retorna todos os projetos não-arquivados. |
| **Projects - Add a project** | POST | Adiciona um novo projeto. Os campos personalizados devem estar envolvidos no objeto `custom_fields`. |
| **Projects - Get all archived projects** | GET | Retorna todos os projetos arquivados. |
| **Projects - Search projects** | GET | Pesquisa todos os projetos por título, descrição, notas e/ou campos personalizados com escopo OAuth restrito. Os resultados podem ser filtrados por ID de pessoa ou organização. |
| **Projects - Get details of a project** | GET | Retorna os detalhes de um projeto específico. Os campos personalizados aparecem como chaves dentro do objeto `custom_fields`. |
| **Projects - Update a project** | PATCH | Atualiza as propriedades de um projeto. |
| **Projects - Delete a project** | DELETE | Marca um projeto como excluído. |
| **Projects - Archive a project** | POST | Arquiva um projeto. |
| **Projects - List updates about project field values** | GET | Lista atualizações sobre valores de campos de um projeto. |
| **Projects - List permitted users** | GET | Lista os usuários autorizados a acessar um projeto. |
| **Stages - Get all stages** | GET | Retorna dados sobre todos os estágios. |
| **Stages - Add a new stage** | POST | Adiciona um novo estágio, retorna o ID em caso de sucesso. |
| **Stages - Get one stage** | GET | Retorna dados sobre um estágio específico. |
| **Stages - Update stage details** | PATCH | Atualiza as propriedades de um estágio. |
| **Stages - Delete a stage** | DELETE | Marca um estágio como excluído. |
| **Tasks - Get all tasks** | GET | Retorna todas as tarefas. |
| **Tasks - Add a task** | POST | Adiciona uma nova tarefa. |
| **Tasks - Get details of a task** | GET | Retorna os detalhes de uma tarefa específica. |
| **Tasks - Update a task** | PATCH | Atualiza uma tarefa. |
| **Tasks - Delete a task** | DELETE | Marca uma tarefa como deletada. Se a tarefa tiver subtarefas, elas também serão deletadas. |
| **Users - List followers of a user** | GET | Lista usuários que estão seguindo o usuário. |
| **Activity Types - Get all activity types** | GET | Retorna todos os tipos de atividade. |
| **Activity Types - Add new activity type** | POST | Adiciona um novo tipo de atividade. |
| **Activity Types - Update an activity type** | PUT | Atualiza um tipo de atividade. |
| **Activity Types - Delete an activity type** | DELETE | Marca um tipo de atividade como excluído. |
| **Call Logs - Get all call logs assigned to a particular user** | GET | Retorna todos os registros de chamada atribuídos a um usuário específico. |
| **Call Logs - Add a call log** | POST | Adiciona um novo registro de chamada. |
| **Call Logs - Get details of a call log** | GET | Retorna os detalhes de um registro de chamada específico. |
| **Call Logs - Delete a call log** | DELETE | Exclui um registro de chamada. Se houver uma gravação de áudio anexada, ela também será excluída. A atividade relacionada não será removida por esta solicitação. |
| **Call Logs - Attach an audio file to the call log** | POST | Adiciona uma gravação de áudio ao registro de chamada. O áudio pode ser reproduzido por quem tiver acesso ao objeto do registro de chamada. |
| **Currencies - Get all supported currencies** | GET | Retorna todas as moedas suportadas na conta que devem ser usadas ao salvar valores monetários com outros objetos. O parâmetro `code` dos objetos retornados é o código de moeda de acordo com ISO 4217 para todas as moedas não personalizadas. |
| **Deal Fields - Delete multiple deal fields in bulk** | DELETE | Marca vários campos de deal como deletados. |
| **Deals - Get deals summary** | GET | Retorna um resumo de todos os negócios não arquivados. |
| **Deals - Get archived deals summary** | GET | Retorna um resumo de todos os negócios arquivados. |
| **Deals - Get deals timeline** | GET | Retorna negócios abertos e ganhos não arquivados, agrupados por um intervalo de tempo definido estabelecido em um dealField do tipo data (`field_key`). |
| **Deals - Get archived deals timeline** | GET | Retorna negócios abertos e ganhos arquivados, agrupados por um intervalo de tempo definido estabelecido em um dealField do tipo data (`field_key`). |
| **Deals - List updates about deal field values** | GET | Lista atualizações sobre valores de campo de um negócio. |
| **Deals - Duplicate deal** | POST | Duplica um negócio. |
| **Deals - List files attached to a deal** | GET | Lista arquivos associados a um negócio. |
| **Deals - List updates about a deal** | GET | Lista atualizações sobre um negócio. |
| **Deals - List mail messages associated with a deal** | GET | Lista mensagens de email associadas a um negócio. |
| **Deals - Merge two deals** | PUT | Mescla um negócio com outro negócio. Para mais informações, consulte o tutorial para <a href="https://pipedrive.readme.io/docs/merging-two-deals" target="_blank" rel="noopener noreferrer">mesclar dois negócios</a>. |
| **Deals - List participants of a deal** | GET | Lista os participantes associados a um negócio. Se uma empresa usa o produto Campaigns, então esse endpoint também retornará o campo `data.marketing_status`. |
| **Deals - Add a participant to a deal** | POST | Adiciona um participante a um negócio. |
| **Deals - Delete a participant from a deal** | DELETE | Deleta um participante de um negócio. |
| **Deals - List updates about participants of a deal** | GET | Lista atualizações sobre participantes de um negócio. Este é um endpoint paginado por cursor. Para mais informações, consulte nossa documentação sobre <a href="https://pipedrive.readme. |
| **Deals - List permitted users** | GET | Lista os usuários permitidos para acessar um negócio. |
| **Files - Get all files** | GET | Retorna dados sobre todos os arquivos. |
| **Files - Add file** | POST | Permite carregar um arquivo e associá-lo a negócios, pessoas, organizações, atividades, produtos ou prospectos. |
| **Files - Create a remote file and link it to an item** | POST | Cria um novo arquivo vazio no local remoto (googledrive) que será vinculado ao item fornecido. |
| **Files - Link a remote file to an item** | POST | Vincula um arquivo remoto (googledrive) existente ao item fornecido. |
| **Files - Get one file** | GET | Retorna dados sobre um arquivo específico. |
| **Files - Update file details** | PUT | Atualiza as propriedades de um arquivo. |
| **Files - Delete a file** | DELETE | Marca um arquivo como excluído. Após 30 dias, o arquivo será excluído permanentemente. |
| **Files - Download one file** | GET | Inicia o download de um arquivo. |
| **Filters - Get all filters** | GET | Retorna dados sobre todos os filtros. |
| **Filters - Add a new filter** | POST | Adiciona um novo filtro e retorna o ID em sucesso. Apenas um grupo de condição de primeiro nível é suportado (com 'AND'), máximo dois de segundo nível (um com 'AND', outro com 'OR'). |
| **Filters - Delete multiple filters in bulk** | DELETE | Marca vários filtros como deletados. |
| **Filters - Get all filter helpers** | GET | Retorna todos os ajudantes de filtro suportados. Consulte a documentação para conhecer as condições e ajudantes disponíveis ao adicionar ou atualizar filtros. |
| **Filters - Get one filter** | GET | Retorna dados sobre um filtro específico. Inclui as linhas de condição do filtro. |
| **Filters - Update filter** | PUT | Atualiza um filtro existente. |
| **Filters - Delete a filter** | DELETE | Marca um filtro como deletado. |
| **Goals - Add a new goal** | POST | Adiciona um novo objetivo. Um relatório é criado automaticamente para acompanhar o progresso do objetivo. |
| **Goals - Find goals** | GET | Retorna dados sobre objetivos por critérios. Acrescente `{searchField}={searchValue}` à URL (p.ex., `type.params.pipeline_id`, `title`). Use `is_active=<true\\|false>` para filtrar por status. |
| **Goals - Update existing goal** | PUT | Atualiza um objetivo existente. |
| **Goals - Delete existing goal** | DELETE | Marca um objetivo como deletado. |
| **Goals - Get result of a goal** | GET | Obtém o progresso de um objetivo para o período especificado. |
| **Lead Fields - Get all lead fields** | GET | Retorna dados sobre todos os campos de leads. |
| **Lead Labels - Get all lead labels** | GET | Retorna detalhes de todos os rótulos de leads. Este endpoint não suporta paginação e todos os rótulos são sempre retornados. |
| **Lead Labels - Add a lead label** | POST | Cria um rótulo de lead. |
| **Lead Labels - Update a lead label** | PATCH | Atualiza uma ou mais propriedades de um rótulo de lead. Apenas as propriedades incluídas na solicitação serão atualizadas. |
| **Lead Labels - Delete a lead label** | DELETE | Deleta um rótulo de lead específico. |
| **Lead Sources - Get all lead sources** | GET | Retorna todas as fontes de leads. Note que a lista de fontes de leads é fixa e não pode ser modificada. Todos os leads criados pela API Pipedrive terão a fonte de lead `API` atribuída. |
| **Leads - Get all leads** | GET | Retorna múltiplos leads não arquivados, ordenados do mais antigo para o mais recente. |
| **Leads - Add a lead** | POST | Cria um lead vinculado a uma pessoa, organização ou ambos; a origem é definida automaticamente como API. |
| **Leads - Get all archived leads** | GET | Retorna múltiplos leads arquivados, ordenados do mais antigo para o mais recente. |
| **Leads - Get one lead** | GET | Retorna os detalhes de um lead específico. |
| **Leads - Update a lead** | PATCH | Atualiza uma ou mais propriedades de um lead; envie null para desmarcar uma propriedade. |
| **Leads - Delete a lead** | DELETE | Deleta um lead específico. |
| **Leads - List permitted users** | GET | Lista os usuários permitidos para acessar um lead. |
| **Legacy Teams - Get all teams** | GET | Retorna dados sobre os times da empresa. |
| **Legacy Teams - Add a new team** | POST | Adiciona um novo time à empresa e retorna o objeto criado. |
| **Legacy Teams - Get all teams of a user** | GET | Retorna dados sobre todos os times que incluem um usuário específico como membro. |
| **Legacy Teams - Get a single team** | GET | Retorna dados sobre um time específico. |
| **Legacy Teams - Update a team** | PUT | Atualiza um time existente e retorna o objeto atualizado. |
| **Legacy Teams - Get all users in a team** | GET | Retorna uma lista de todos os IDs de usuários de um time. |
| **Legacy Teams - Add users to a team** | POST | Adiciona usuários a um time existente. |
| **Legacy Teams - Delete users from a team** | DELETE | Remove usuários de um time existente. |
| **Mailbox - Get one mail message** | GET | Retorna dados sobre uma mensagem de email específica. |
| **Mailbox - Get mail threads** | GET | Retorna threads de email em uma pasta especificada ordenadas pela mensagem mais recente. |
| **Mailbox - Get one mail thread** | GET | Retorna uma thread de email específica. |
| **Mailbox - Update mail thread details** | PUT | Atualiza as propriedades de uma thread de email. |
| **Mailbox - Delete mail thread** | DELETE | Marca uma thread de email como deletada. |
| **Mailbox - Get all mail messages of mail thread** | GET | Retorna todas as mensagens de email dentro de uma thread de email especificada. |
| **Note Fields - Get all note fields** | GET | Retorna dados sobre todos os campos de nota. |
| **Notes - Get all notes** | GET | Retorna todas as notas. |
| **Notes - Add a note** | POST | Adiciona uma nova nota. |
| **Notes - Get one note** | GET | Retorna os detalhes de uma nota específica. |
| **Notes - Update a note** | PUT | Atualiza uma nota. |
| **Notes - Delete a note** | DELETE | Exclui uma nota específica. |
| **Notes - Get all comments for a note** | GET | Retorna todos os comentários associados a uma nota. |
| **Notes - Add a comment to a note** | POST | Adiciona um novo comentário a uma nota. |
| **Notes - Get one comment** | GET | Retorna os detalhes de um comentário. |
| **Notes - Update a comment related to a note** | PUT | Atualiza um comentário relacionado a uma nota. |
| **Notes - Delete a comment related to a note** | DELETE | Exclui um comentário. |
| **Organization Fields - Delete multiple organization fields in bulk** | DELETE | Marca vários campos como excluídos. |
| **Organization Relationships - Get all relationships for organization** | GET | Obtém todos os relacionamentos de uma ID de organização fornecida. |
| **Organization Relationships - Create an organization relationship** | POST | Cria e retorna um relacionamento de organização. |
| **Organization Relationships - Get one organization relationship** | GET | Encontra e retorna um relacionamento de organização pela sua ID. |
| **Organization Relationships - Update an organization relationship** | PUT | Atualiza e retorna um relacionamento de organização. |
| **Organization Relationships - Delete an organization relationship** | DELETE | Remove um relacionamento de organização e retorna a ID excluída. |
| **Organizations - List updates about organization field values** | GET | Lista atualizações sobre valores de campos de uma organização. |
| **Organizations - List files attached to an organization** | GET | Lista arquivos associados a uma organização. |
| **Organizations - List updates about an organization** | GET | Lista atualizações sobre uma organização. |
| **Organizations - List mail messages associated with an organization** | GET | Lista mensagens de email associadas a uma organização. |
| **Organizations - Merge two organizations** | PUT | Mescla uma organização com outra organização. Para mais informações, veja o tutorial para <a href="https://pipedrive.readme.io/docs/merging-two-organizations" target="_blank" rel="noopener noreferrer">mesclagem de duas organizações</a>. |
| **Organizations - List permitted users** | GET | Lista usuários permitidos para acessar uma organização. |
| **Permission Sets - Get all permission sets** | GET | Retorna dados sobre todos os conjuntos de permissões. |
| **Permission Sets - Get one permission set** | GET | Retorna dados sobre um conjunto de permissões específico. |
| **Permission Sets - List permission set assignments** | GET | Retorna a lista de atribuições para um conjunto de permissões. |
| **Person Fields - Delete multiple person fields in bulk** | DELETE | Marca múltiplos campos como deletados. |
| **Persons - List updates about person field values** | GET | Lista atualizações sobre valores de campos de uma pessoa. |
| **Persons - List files attached to a person** | GET | Lista arquivos associados à pessoa. |
| **Persons - List updates about a person** | GET | Lista atualizações sobre uma pessoa. Se a empresa usa Campanhas, a resposta também inclui atualizações do campo `marketing_status`. |
| **Persons - List mail messages associated with a person** | GET | Lista mensagens de email associadas à pessoa. |
| **Persons - Merge two persons** | PUT | Mescla uma pessoa com outra. Consulte o tutorial sobre mescla de pessoas para mais informações. |
| **Persons - List permitted users** | GET | Lista usuários com permissão para acessar a pessoa. |
| **Persons - Add person picture** | POST | Adiciona uma imagem à pessoa. Se já existe uma imagem, será substituída. A imagem deve ter largura e altura iguais e no mínimo 128 pixels. Aceita GIF, JPG e PNG, redimensionados para 128 e 512 pixels. |
| **Persons - Delete person picture** | DELETE | Remove a imagem da pessoa. |
| **Persons - List products associated with a person** | GET | Lista produtos associados à pessoa. |
| **Pipelines - Get deals conversion rates in pipeline** | GET | Retorna todas as taxas de conversão de etapa a etapa e de pipeline para fechamento no período informado. |
| **Pipelines - Get deals in a pipeline** | GET | Lista negócios em um pipeline específico em todas as suas etapas. Se nenhum parâmetro for fornecido, negócios abertos pertencentes ao usuário autorizado serão retornados. Este endpoint foi descontinuado. |
| **Pipelines - Get deals movements in pipeline** | GET | Retorna estatísticas de movimentos de negócios para o período informado. |
| **Product Fields - Delete multiple product fields in bulk** | DELETE | Marca múltiplos campos como excluídos. |
| **Products - Get deals where a product is attached to** | GET | Retorna dados sobre negócios que têm um produto anexado. |
| **Products - List files attached to a product** | GET | Lista arquivos associados a um produto. |
| **Products - List permitted users** | GET | Lista usuários autorizados a acessar um produto. |
| **Projects - Returns project activities** | GET | Retorna atividades vinculadas a um projeto específico. |
| **Projects - Returns project groups** | GET | Retorna todos os grupos ativos em um projeto específico. |
| **Projects - Returns project plan** | GET | Retorna informações sobre itens em um plano de projeto. Os itens consistem em tarefas e atividades vinculadas a uma fase e grupo de projeto específicos. |
| **Projects - Update activity in project plan** | PUT | Atualiza uma fase ou grupo de atividade em um projeto. |
| **Projects - Update task in project plan** | PUT | Atualiza uma fase ou grupo de tarefa em um projeto. |
| **Projects - Returns project tasks** | GET | Retorna tarefas vinculadas a um projeto específico. |
| **Recents - Get recents** | GET | Retorna dados sobre todas as alterações recentes ocorridas após o timestamp fornecido. |
| **Roles - Get all roles** | GET | Retorna todas as funções dentro da empresa. |
| **Roles - Add a role** | POST | Adiciona uma nova função. |
| **Roles - Get one role** | GET | Retorna os detalhes de uma função específica. |
| **Roles - Update role details** | PUT | Atualiza a função pai e/ou o nome de uma função específica. |
| **Roles - Delete a role** | DELETE | Marca uma função como deletada. |
| **Roles - List role assignments** | GET | Retorna todos os usuários atribuídos a uma função. |
| **Roles - Add role assignment** | POST | Atribui um usuário a uma função. |
| **Roles - Delete a role assignment** | DELETE | Remove o usuário atribuído de uma função e o adiciona à função padrão. |
| **Roles - List pipeline visibility for a role** | GET | Retorna a lista de IDs de pipeline visíveis ou ocultos para uma função específica. Para mais informações sobre visibilidade de pipeline, consulte o artigo sobre Grupos de visibilidade. |
| **Roles - Update pipeline visibility for a role** | PUT | Atualiza os pipelines especificados para serem visíveis e/ou ocultos para uma função específica. Para mais informações sobre visibilidade de pipeline, consulte o artigo sobre Grupos de visibilidade. |
| **Roles - List role settings** | GET | Retorna as configurações de visibilidade de uma função específica. |
| **Roles - Add or update role setting** | POST | Adiciona ou atualiza a configuração de visibilidade para uma função. |
| **Stages - Get deals in a stage** | GET | Lista ofertas em um estágio específico. Se nenhum parâmetro for fornecido, as ofertas abertas do usuário autorizado serão retornadas. Este endpoint foi descontinuado. |
| **User Connections - Get all user connections** | GET | Retorna dados sobre todas as conexões do usuário autorizado. |
| **User Settings - List settings of an authorized user** | GET | Lista as configurações de um usuário autorizado. A resposta de exemplo contém uma lista resumida. |
| **Users - Get all users** | GET | Retorna dados sobre todos os usuários na empresa. |
| **Users - Add a new user** | POST | Adiciona um novo usuário à empresa, retorna o ID ao sucesso. |
| **Users - Find users by name** | GET | Encontra usuários pelo nome. |
| **Users - Get current user data** | GET | Retorna dados do usuário autorizado com dados da empresa (ID, nome e domínio). A propriedade `locale` refere-se ao formato de data/número, não ao idioma. |
| **Users - Get one user** | GET | Retorna dados sobre um usuário específico na empresa. |
| **Users - Update user details** | PUT | Atualiza as propriedades de um usuário. Atualmente, apenas `active_flag` pode ser atualizado. |
| **Users - List user permissions** | GET | Lista permissões agregadas em todos os conjuntos de permissões atribuídos para um usuário. |
| **Users - List role assignments** | GET | Lista atribuições de função para um usuário. |
| **Users - List user role settings** | GET | Lista as configurações da função atribuída do usuário. |
| **Webhooks - Get all Webhooks** | GET | Retorna dados sobre todos os Webhooks da empresa. |
| **Webhooks - Create a new Webhook** | POST | Cria um novo Webhook e retorna seus detalhes. Note que especificar um evento que dispara o Webhook combina 2 parâmetros - `event_action` e `event_object`. |
| **Webhooks - Delete existing Webhook** | DELETE | Deleta o Webhook especificado. |
| **OAuth - Requesting authorization** | GET | Monta a URL de autorização do OAuth 2.0. Abra a URL resultante no navegador do usuário para que ele autorize o app; o Pipedrive redireciona para a callback com o parâmetro code. |
| **OAuth - Get or refresh the tokens** | POST | Troca o código de autorização pelo access token, ou renova o access token a partir do refresh token — os dois usam este mesmo endpoint, variando o grant_type. Exige o header Authorization com Basic base64(client_id:client_secret). O campo api_domain  |

---

## Documentação oficial

[Pipedrive API Reference](https://developers.pipedrive.com/docs/api/v1) — referência das duas versões.
