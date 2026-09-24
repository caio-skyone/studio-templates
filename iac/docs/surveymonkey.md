# SurveyMonkey

## Contexto

O SurveyMonkey é uma plataforma de pesquisas online: criação de questionários, distribuição por link, e-mail, SMS ou popup, coleta de respostas e análise dos resultados. A API REST v3 dá acesso programático a todo esse ciclo e à administração de equipes.

Principais domínios da API:

- **Pesquisas (Surveys):** CRUD de pesquisas, busca, detalhes expandidos, links da página de resultados, categorias, templates e idiomas disponíveis
- **Páginas e perguntas (Survey Pages, Survey Questions):** estrutura interna da pesquisa; o formato de cada pergunta depende da `family` e do `subtype`
- **Banco de perguntas e pastas (Question Bank, Survey Folders):** perguntas prontas e organização das pesquisas
- **Traduções (Translations):** versões multilíngues de uma pesquisa, por código de idioma
- **Coletores, mensagens e destinatários (Collectors, Messages, Recipients):** canais de coleta — weblink, e-mail, SMS, popup — e o envio de convites, lembretes e agradecimentos
- **Respostas (Responses):** leitura, criação, alteração e exclusão de respostas, por pesquisa ou por coletor, inclusive em lote (`bulk`) com as respostas de todas as perguntas
- **Resumos e tendências (Rollups and Trends):** contagens consolidadas e séries temporais por pesquisa, página ou pergunta
- **Contatos (Contacts, Contact Lists, Contact Fields):** base de contatos e listas usadas como destinatários de convites
- **Webhooks:** notificações de eventos como `response_completed` para uma URL externa
- **Equipes e organização (Users, Groups, Workgroups, Workgroup Members, Organizations):** conta autenticada, grupos, workgroups, compartilhamento de recursos e papéis — boa parte exige plano de equipe ou usuário administrador
- **Benchmarks e erros:** comparação de resultados de perguntas do Question Bank com dados do mercado, e o catálogo de erros da API

Apps privados e em rascunho começam com limite de **120 chamadas por minuto** e a partir de **500 por dia**; limites maiores são contratados com o SurveyMonkey. O acesso direto à API exige plano pago. Datas nos filtros usam o formato `YYYY-MM-DDTHH:MM:SS`, sem fuso.

---

## Autenticação

**Tipo:** Bearer Token

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://api.surveymonkey.com` |
| Porta | 443 |
| token | {{token}} |

> **Nota:** o token é o access token do app, enviado como `Authorization: Bearer {token}`. Num app privado que acessa só a própria conta, ele aparece nas configurações do app, na aba *My Apps* do portal de desenvolvedores. Para acessar contas de terceiros é preciso o fluxo OAuth 2.0 do SurveyMonkey, que gera um token de longa duração por conta. Os tokens não expiram hoje, mas o usuário pode revogá-los.

> **Nota:** o token só acessa os escopos marcados no app. Em *My Apps* > *Settings* > *Scopes*, marque os escopos das operações que você vai usar (`users_read`, `surveys_read`, `surveys_write`, `collectors_read`, `collectors_write`, `contacts_read`, `contacts_write`, `responses_read`, `responses_read_detail`, `webhooks_read`, `webhooks_write`, `library_read`) e clique em *Update Scopes*. Os escopos ficam gravados no token quando ele é emitido, então depois de alterá-los é preciso copiar o access token de novo (ou refazer a autorização OAuth). Com um escopo faltando, a API responde `403` com o erro `1014 Permission Error`. O header `x-oauth-scopes-granted` da resposta mostra os escopos que o token tem.

> **Nota:** o Host depende do datacenter da conta. Contas da UE usam `https://api.eu.surveymonkey.com` e contas do Canadá `https://api.surveymonkey.ca`. O valor correto vem no campo `access_url` da troca de token OAuth.

> **Nota:** o Host é apenas a origem. O prefixo `/v3` faz parte do caminho de cada operação, não da conta conectada.

---

## Notas de uso

### Paginação e filtros

As listagens aceitam `page` (padrão 1) e `per_page` (padrão 50) como query. Os filtros de cada listagem entraram todos como parâmetros opcionais: query vazia não é enviada, então basta preencher os que interessam. Parâmetros como `include`, `collector_ids`, `page_ids` e `question_ids` recebem valores separados por vírgula.

Dois parâmetros têm nome diferente da chave enviada, porque o mesmo nome tem sentidos diferentes em outros recursos:

- **`contact_status`** vai como a chave `status` nas listagens de contatos (`active`, `optout`, `bounced`)
- **`custom_question_bank`** vai como a chave `custom` em **Question Bank - Get questions**

### Corpo das requisições

Cada operação de escrita recebe **um único parâmetro `body` do tipo objeto** com o JSON completo, na estrutura da API. O `sample` de cada operação traz um exemplo baseado na documentação oficial. Estruturas aninhadas — `headings` e `answers` de perguntas, `pages` de respostas, `thank_you_page` de coletores — vão como objetos e listas dentro do próprio `body`.

**Organizations - Initialize organization** e **Contact Lists - Copy contact list** são POST sem corpo.

### Fluxo de envio de convites

Enviar um convite por e-mail é uma sequência de operações: **Collectors - Create collector** (tipo `email`) → **Messages - Create message** → **Recipients - Add message recipient** ou **Recipients - Add message recipients in bulk** → **Messages - Send message**. A mensagem só pode ser enviada com status `not_sent`.

### Respostas por pesquisa ou por coletor

As operações de **Responses** existem em duas variantes: por pesquisa (`/surveys/{survey_id}/responses…`) e por coletor (`/collectors/{collector_id}/responses…`). Criar resposta e excluir todas as respostas só existem na variante por coletor.

### Pontos a confirmar em runtime

A documentação oficial deixa algumas lacunas; o conector segue a interpretação abaixo:

- **Surveys - Update results link** usa o mesmo caminho do POST (`/surveys/{survey_id}/share`); a documentação não mostra o caminho do PUT
- **Responses - Delete survey response** aparece nos títulos da documentação, mas não na lista de métodos da rota
- **Rollups and Trends - Get survey trends** usa a chave `last_respondent`; a documentação escreve `last_respondnet`, que parece erro de digitação

### Fora do escopo

- A **API SCIM v2** (`/scim/v2`), de provisionamento de usuários em planos Enterprise, que usa outro caminho base
- Os métodos **HEAD** e **OPTIONS**, que só verificam disponibilidade
- O formato dos **callbacks de webhook**, que é o que o SurveyMonkey envia à URL cadastrada, não uma operação

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Users - Get current user** | **GET** | Retorna os dados da conta do usuário autenticado, incluindo o plano contratado. |
| **Users - Get user workgroups** | **GET** | Lista os workgroups dos quais um usuário faz parte. |
| **Users - Get user shared resources** | **GET** | Lista os recursos compartilhados com o usuário em todos os workgroups. |
| **Groups - Get all groups** | **GET** | Lista os grupos (equipes) aos quais o usuário tem acesso. |
| **Groups - Get group by id** | **GET** | Retorna as informações de um grupo (equipe). |
| **Groups - Get group activities** | **GET** | Lista as atividades registradas no grupo. Exige usuário administrador. |
| **Groups - Get group activity count** | **GET** | Retorna a contagem de um tipo de atividade do grupo agrupada por intervalo de tempo. Exige usuário administrador. |
| **Groups - Get group members** | **GET** | Lista os usuários que são membros do grupo. |
| **Groups - Get group member by id** | **GET** | Retorna os dados de um membro do grupo, incluindo papel e status. |
| **Groups - Update group member** | **PATCH** | Atualiza o e-mail de um membro do grupo. |
| **Workgroups - Get all workgroups** | **GET** | Lista todos os workgroups disponíveis. |
| **Workgroups - Create workgroup** | **POST** | Cria um novo workgroup. |
| **Workgroups - Get workgroup by id** | **GET** | Retorna as informações de um workgroup. |
| **Workgroups - Update workgroup** | **PATCH** | Altera as informações de um workgroup. |
| **Workgroups - Get workgroup shares** | **GET** | Lista os recursos compartilhados no workgroup. |
| **Workgroups - Create workgroup share** | **POST** | Compartilha um recurso, como uma pesquisa, com o workgroup. |
| **Workgroups - Get workgroup share by id** | **GET** | Retorna um recurso compartilhado no workgroup. |
| **Workgroups - Delete workgroup share** | **DELETE** | Remove o compartilhamento de um recurso no workgroup. |
| **Workgroups - Create workgroup shares in bulk** | **POST** | Compartilha vários recursos com o workgroup em uma única chamada. |
| **Workgroup Members - Get all members** | **GET** | Lista os membros de um workgroup. |
| **Workgroup Members - Create member** | **POST** | Adiciona um usuário como membro do workgroup. |
| **Workgroup Members - Create members in bulk** | **POST** | Adiciona vários usuários como membros do workgroup em uma única chamada. |
| **Workgroup Members - Get member by id** | **GET** | Retorna um membro do workgroup. |
| **Workgroup Members - Update member** | **PATCH** | Altera um membro do workgroup, como a marcação de proprietário. |
| **Workgroup Members - Delete member** | **DELETE** | Remove um membro do workgroup. |
| **Organizations - Get all organizations** | **GET** | Retorna as propriedades das organizações (grupo, equipe) relativas à funcionalidade de workgroups. |
| **Organizations - Initialize organization** | **POST** | Ativa a funcionalidade de workgroups na organização. Só precisa ser feito uma vez. |
| **Organizations - Get organization by id** | **GET** | Retorna as propriedades de workgroups de uma organização específica. |
| **Organizations - Update organization** | **PATCH** | Altera as configurações de workgroups da organização. |
| **Organizations - Get roles** | **GET** | Lista os papéis de usuário disponíveis na organização. |
| **Surveys - Get all surveys** | **GET** | Lista as pesquisas do usuário autenticado ou compartilhadas com ele. |
| **Surveys - Create survey** | **POST** | Cria uma pesquisa vazia ou, a partir de um template ou pesquisa existente, uma pesquisa já com páginas e perguntas. |
| **Surveys - Search surveys** | **GET** | Busca pesquisas por texto e filtros, com resultados paginados. |
| **Surveys - Get survey by id** | **GET** | Retorna os dados de uma pesquisa. Para páginas e perguntas completas, use a operação de detalhes. |
| **Surveys - Update survey** | **PATCH** | Altera título, apelido, idioma e outras propriedades de uma pesquisa. |
| **Surveys - Replace survey** | **PUT** | Substitui uma pesquisa. Aceita os mesmos campos da criação. |
| **Surveys - Delete survey** | **DELETE** | Exclui uma pesquisa. |
| **Surveys - Get survey details** | **GET** | Retorna a pesquisa expandida, com todas as páginas e perguntas. |
| **Surveys - Create results link** | **POST** | Cria um link para a página de resultados da pesquisa. |
| **Surveys - Update results link** | **PUT** | Atualiza um link existente da página de resultados da pesquisa. |
| **Surveys - Get results links** | **GET** | Lista os links de página de resultados gerados para a pesquisa. |
| **Surveys - Get survey categories** | **GET** | Lista as categorias usadas para filtrar templates de pesquisa. |
| **Surveys - Get survey templates** | **GET** | Lista os templates de pesquisa. O id do template pode ser usado na criação de uma pesquisa. |
| **Surveys - Get team survey templates** | **GET** | Lista os templates de pesquisa da equipe do usuário autenticado. |
| **Surveys - Get survey languages** | **GET** | Lista os idiomas disponíveis para traduções de pesquisas multilíngues. |
| **Survey Pages - Get all pages** | **GET** | Lista as páginas de uma pesquisa. |
| **Survey Pages - Create page** | **POST** | Cria uma página vazia na pesquisa. |
| **Survey Pages - Get page by id** | **GET** | Retorna os dados de uma página da pesquisa. |
| **Survey Pages - Update page** | **PATCH** | Altera título, descrição ou posição de uma página. |
| **Survey Pages - Replace page** | **PUT** | Substitui uma página. Aceita os mesmos campos da criação. |
| **Survey Pages - Delete page** | **DELETE** | Exclui uma página da pesquisa. |
| **Survey Questions - Get all questions** | **GET** | Lista as perguntas de uma página da pesquisa. |
| **Survey Questions - Create question** | **POST** | Cria uma pergunta na página. A estrutura depende do tipo (family e subtype) da pergunta. |
| **Survey Questions - Get question by id** | **GET** | Retorna uma pergunta da pesquisa. |
| **Survey Questions - Update question** | **PATCH** | Altera os campos informados de uma pergunta. |
| **Survey Questions - Replace question** | **PUT** | Substitui uma pergunta. Aceita os mesmos campos da criação. |
| **Survey Questions - Delete question** | **DELETE** | Exclui uma pergunta da pesquisa. |
| **Question Bank - Get questions** | **GET** | Lista as perguntas do banco de perguntas disponíveis para o usuário. |
| **Survey Folders - Get all folders** | **GET** | Lista as pastas de pesquisas disponíveis. |
| **Survey Folders - Create folder** | **POST** | Cria uma pasta para organizar pesquisas. |
| **Translations - Get all translations** | **GET** | Lista as traduções existentes de uma pesquisa. |
| **Translations - Get translation** | **GET** | Retorna a tradução de uma pesquisa em um idioma, ou a estrutura a traduzir se ainda não existir. |
| **Translations - Create translation** | **POST** | Cria a tradução de uma pesquisa em um idioma. |
| **Translations - Update translation** | **PATCH** | Atualiza a tradução de uma pesquisa em um idioma. |
| **Translations - Delete translation** | **DELETE** | Exclui a tradução de uma pesquisa em um idioma. |
| **Contact Lists - Get all contact lists** | **GET** | Lista todas as listas de contatos. |
| **Contact Lists - Create contact list** | **POST** | Cria uma lista de contatos para envio de convites por e-mail ou SMS. |
| **Contact Lists - Get contact list by id** | **GET** | Retorna uma lista de contatos. |
| **Contact Lists - Update contact list** | **PATCH** | Altera o nome de uma lista de contatos. |
| **Contact Lists - Replace contact list** | **PUT** | Substitui uma lista de contatos. Aceita os mesmos campos da criação. |
| **Contact Lists - Delete contact list** | **DELETE** | Exclui uma lista de contatos. |
| **Contact Lists - Copy contact list** | **POST** | Cria uma cópia de uma lista de contatos existente. |
| **Contact Lists - Merge contact lists** | **POST** | Copia os contatos da lista informada no corpo para a lista indicada no caminho. |
| **Contact Lists - Get list contacts** | **GET** | Lista os contatos de uma lista de contatos. |
| **Contact Lists - Add contact to list** | **POST** | Cria um contato e o adiciona à lista de contatos. |
| **Contact Lists - Get list contacts in bulk** | **GET** | Lista os contatos de uma lista com todos os campos disponíveis. |
| **Contact Lists - Add contacts to list in bulk** | **POST** | Cria vários contatos e os adiciona à lista em uma única chamada. |
| **Contacts - Get all contacts** | **GET** | Lista todos os contatos. |
| **Contacts - Create contact** | **POST** | Cria um contato para envio de convites por e-mail ou SMS. |
| **Contacts - Get contacts in bulk** | **GET** | Lista todos os contatos com todos os campos disponíveis. |
| **Contacts - Create contacts in bulk** | **POST** | Cria vários contatos em uma única chamada. |
| **Contacts - Get contact by id** | **GET** | Retorna um contato. |
| **Contacts - Update contact** | **PATCH** | Altera os campos informados de um contato. |
| **Contacts - Replace contact** | **PUT** | Substitui um contato. Aceita os mesmos campos da criação. |
| **Contacts - Delete contact** | **DELETE** | Exclui um contato. |
| **Contact Fields - Get all contact fields** | **GET** | Lista os campos personalizados de contato. |
| **Contact Fields - Get contact field by id** | **GET** | Retorna um campo personalizado de contato. |
| **Contact Fields - Update contact field** | **PATCH** | Altera o rótulo de um campo personalizado de contato. |
| **Collectors - Get all collectors** | **GET** | Lista os coletores de uma pesquisa. |
| **Collectors - Create collector** | **POST** | Cria um coletor de SMS, weblink, e-mail ou popup para a pesquisa. |
| **Collectors - Get collector by id** | **GET** | Retorna um coletor. |
| **Collectors - Update collector** | **PATCH** | Altera os campos informados de um coletor, incluindo o status. O tipo não pode ser alterado. |
| **Collectors - Replace collector** | **PUT** | Substitui um coletor. Aceita os campos da criação, com status e sem tipo. |
| **Collectors - Delete collector** | **DELETE** | Exclui um coletor. |
| **Collectors - Get collector stats** | **GET** | Retorna as estatísticas de um coletor. |
| **Messages - Get all messages** | **GET** | Lista as mensagens de convite de um coletor. |
| **Messages - Create message** | **POST** | Cria uma mensagem de convite, lembrete ou agradecimento no coletor. Depois adicione destinatários e envie. |
| **Messages - Get message by id** | **GET** | Retorna uma mensagem do coletor. |
| **Messages - Update message** | **PATCH** | Altera assunto, corpo, identidade visual e status dos destinatários de uma mensagem. |
| **Messages - Replace message** | **PUT** | Substitui uma mensagem. Só assunto, corpo, identidade visual e status dos destinatários podem mudar. |
| **Messages - Delete message** | **DELETE** | Exclui uma mensagem do coletor. |
| **Messages - Send message** | **POST** | Envia ou agenda o envio da mensagem para todos os destinatários. A mensagem precisa estar com status not_sent. |
| **Messages - Get message stats** | **GET** | Retorna as estatísticas de uma mensagem do coletor. |
| **Recipients - Get message recipients** | **GET** | Lista os destinatários de uma mensagem. |
| **Recipients - Add message recipient** | **POST** | Adiciona um destinatário à mensagem. Só vale para SMS ou convites ainda não enviados. |
| **Recipients - Add message recipients in bulk** | **POST** | Adiciona vários destinatários à mensagem, por contatos, listas ou dados avulsos. |
| **Recipients - Get collector recipients** | **GET** | Lista os destinatários de um coletor. |
| **Recipients - Get recipient by id** | **GET** | Retorna um destinatário do coletor. |
| **Recipients - Delete recipient** | **DELETE** | Exclui um destinatário do coletor. |
| **Responses - Get survey responses** | **GET** | Lista as respostas de uma pesquisa. |
| **Responses - Get survey responses in bulk** | **GET** | Lista as respostas completas de uma pesquisa, com as respostas de todas as perguntas. |
| **Responses - Get survey response by id** | **GET** | Retorna uma resposta da pesquisa. |
| **Responses - Update survey response** | **PATCH** | Altera os campos informados de uma resposta da pesquisa. |
| **Responses - Replace survey response** | **PUT** | Substitui uma resposta da pesquisa. |
| **Responses - Delete survey response** | **DELETE** | Exclui uma resposta da pesquisa. |
| **Responses - Get survey response details** | **GET** | Retorna uma resposta completa da pesquisa, com as respostas de todas as perguntas. |
| **Responses - Get collector responses** | **GET** | Lista as respostas recebidas por um coletor. |
| **Responses - Create collector response** | **POST** | Cria uma resposta no coletor. |
| **Responses - Delete collector responses** | **DELETE** | Exclui todas as respostas do coletor. |
| **Responses - Get collector responses in bulk** | **GET** | Lista as respostas completas de um coletor, com as respostas de todas as perguntas. |
| **Responses - Get collector response by id** | **GET** | Retorna uma resposta do coletor. |
| **Responses - Update collector response** | **PATCH** | Altera os campos informados de uma resposta do coletor. |
| **Responses - Replace collector response** | **PUT** | Substitui uma resposta do coletor. |
| **Responses - Delete collector response** | **DELETE** | Exclui uma resposta do coletor. |
| **Responses - Get collector response details** | **GET** | Retorna uma resposta completa do coletor, com as respostas de todas as perguntas. |
| **Rollups and Trends - Get survey rollups** | **GET** | Retorna o resumo consolidado das respostas de todas as perguntas da pesquisa. |
| **Rollups and Trends - Get page rollups** | **GET** | Retorna o resumo consolidado das respostas das perguntas de uma página. |
| **Rollups and Trends - Get question rollups** | **GET** | Retorna o resumo consolidado das respostas de uma pergunta. |
| **Rollups and Trends - Get survey trends** | **GET** | Retorna a contagem de respostas das perguntas da pesquisa por período. |
| **Rollups and Trends - Get page trends** | **GET** | Retorna a contagem de respostas das perguntas de uma página por período. |
| **Rollups and Trends - Get question trends** | **GET** | Retorna a contagem de respostas de uma pergunta por período. |
| **Webhooks - Get all webhooks** | **GET** | Lista os webhooks cadastrados. |
| **Webhooks - Create webhook** | **POST** | Cria um webhook para receber eventos de pesquisas ou coletores. |
| **Webhooks - Get webhook by id** | **GET** | Retorna um webhook. |
| **Webhooks - Update webhook** | **PATCH** | Altera os campos informados de um webhook, exceto eventos app_installed e app_uninstalled. |
| **Webhooks - Replace webhook** | **PUT** | Substitui um webhook. Aceita os mesmos campos da criação. |
| **Webhooks - Delete webhook** | **DELETE** | Exclui um webhook. |
| **Benchmarks - Get benchmark bundles** | **GET** | Lista os pacotes de benchmark aos quais o usuário tem acesso. |
| **Benchmarks - Get benchmark bundle by id** | **GET** | Retorna as perguntas e os detalhes de um pacote de benchmark. |
| **Benchmarks - Analyze benchmark bundle** | **GET** | Retorna o benchmark do pacote informado. |
| **Benchmarks - Get question benchmark** | **GET** | Retorna o benchmark de uma pergunta da pesquisa. |
| **Errors - Get all errors** | **GET** | Lista os erros conhecidos da API. |
| **Errors - Get error by id** | **GET** | Retorna os detalhes de um erro conhecido da API. |

---

## Documentação oficial

https://api.surveymonkey.com/v3/docs
