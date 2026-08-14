# Service Now

## Contexto

O **ServiceNow** é uma plataforma de gestão de serviços (ITSM) construída sobre um banco de dados relacional cujas tabelas — `incident`, `sc_request`, `sys_user`, `change_request` — são expostas por APIs REST nativas. Este template cobre **48 operações** das APIs da própria plataforma, no namespace `now` e nos escopos `sn_sc` e `sn_km_api`.

Não estão contempladas as **Scripted REST APIs** que cada organização cria dentro da sua instância: são específicas de cada tenant e não têm contrato estável. Se você precisar de uma delas, o caminho é gerar um conector próprio a partir do OpenAPI exportado pelo REST API Explorer da instância.

As operações se agrupam em oito APIs:

**[Table API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/c_TableAPI.html)** — CRUD sobre qualquer tabela da instância. É a API mais versátil do conjunto: como praticamente tudo no ServiceNow é uma tabela, ela cobre incidentes, requisições, usuários, ativos e tabelas customizadas com as mesmas seis operações.

**[Attachment API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/c_AttachmentAPI.html)** — upload, download, consulta de metadados e exclusão de arquivos vinculados a registros.

**[Aggregate API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/c_AggregateAPI.html)** — contagens, somas, médias, mínimos e máximos sobre os registros de uma tabela, com agrupamento. Evita trazer milhares de registros só para contá-los.

**[Import Set API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/c_ImportSetAPI.html)** — carga de dados em tabelas de staging, com transformação pelos transform maps configurados.

**[Batch API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/batch-api.html)** — várias requisições REST da instância em uma única chamada HTTP.

**[Email API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/email-api.html)** — envio e consulta de e-mails pela instância, com vínculo opcional a um registro.

**[Knowledge Management API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/knowledge-api.html)** — busca e leitura de artigos da base de conhecimento, incluindo destaques, mais vistos e anexos.

**[Service Catalog API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/c_ServiceCatalogAPI.html)** — catálogo de autoatendimento: catálogos, categorias, itens, carrinho, checkout, lista de desejos e order guides. Ao contrário da Table API, respeita as regras de negócio do catálogo e dispara os workflows de aprovação configurados.

## Conceitos Fundamentais

### sys_id identifica tudo

Todo registro do ServiceNow tem um `sys_id`: uma string hexadecimal de 32 caracteres. É por ele que se referencia qualquer coisa — um incidente, um usuário, um item de catálogo, um anexo. Os `sample` deste template usam sys_ids reais da instância de demonstração, úteis como referência de formato.

Uma exceção prática: em **Knowledge - Get article details**, o parâmetro `article_id` aceita tanto o sys_id quanto o **número KB** do artigo (`KB0000020`). O parâmetro `language` só tem efeito quando você usa o número KB.

### Query codificada (encoded query)

O filtro do ServiceNow não é um conjunto de campos separados, e sim uma **string codificada** no parâmetro `sysparm_query`:

```
active=true^priority=1^ORpriority=2^ORDERBYDESCsys_created_on
```

Os operadores são `=`, `!=`, `LIKE`, `STARTSWITH`, `>`, `<`; `^` encadeia condições com E, `^OR` com OU, e `ORDERBY`/`ORDERBYDESC` ordenam. A forma mais confiável de montar uma query complexa é aplicar o filtro na interface da instância, clicar com o botão direito na barra de filtro e copiar a query codificada.

### Valor de banco x valor de exibição

`sysparm_display_value` controla o que volta em campos de escolha e de referência. Com `false` (padrão) você recebe o valor do banco — `state` vem como `7`. Com `true`, recebe o rótulo — `Closed`. Com `all`, os dois. No sentido inverso, `sysparm_input_display_value=true` faz a API aceitar rótulos na escrita e convertê-los para o valor de banco.

### Paginação

Table, Attachment e Service Catalog paginam com `sysparm_limit` e `sysparm_offset`. A API de Knowledge usa nomes diferentes: `limit` e `offset`, sem prefixo. Em ambos os casos a técnica é a mesma: incrementar o offset pelo limit até a resposta vir vazia.

### Permissões vêm do usuário, não da API

Toda operação roda sob as ACLs do usuário da conta conectada. Uma chamada que retorna lista vazia raramente significa "não existe" — quase sempre significa "esse usuário não enxerga". Ao criar o usuário de integração, dê a ele os papéis das tabelas que o fluxo vai tocar (`itil` para incidentes, por exemplo), e não mais que isso.

---

## Autenticação

**Tipo:** OAuth 2.0

O ServiceNow autentica via OAuth 2.0 com **client credentials**. A credencial fica na conta conectada — nenhuma operação deste template carrega parâmetro de token.

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://{{sua_instancia}}.service-now.com` |
| Porta | 443 |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Endpoint de troca de token | `https://{{sua_instancia}}.service-now.com/oauth_token.do` |

Na configuração da conta:

- marque **Content Type** como **URL Encoded**;
- em **configurações do payload de token**, troque `grant_type` para **client_credentials**.

### Host

É a URL da sua instância, visível no painel de desenvolvedor:

```
https://{subdominio}.service-now.com/
```

### Client ID e Client Secret

1. Na instância, clique em **All** e pesquise por OAuth; acesse **System OAuth → Application Registry**.
2. Clique em **New**, escolha **New Inbound Integration Experience** e **New Integration**; a opção recomendada é **OAuth - Client credentials grant**.
3. Preencha as informações. Crie um usuário OAuth específico para a integração e restrinja os *auth scopes* ao uso pretendido.

---

## Convenções do template

### Versão da API é obrigatória em 41 operações

O ServiceNow expõe cada endpoint em duas formas: a **default** (`/api/now/table/incident`), que aponta sempre para a versão mais recente, e a **versionada** (`/api/now/v2/table/incident`). Este template usa a forma versionada, com `api_version` como parâmetro obrigatório.

A escolha é deliberada: na forma default, o comportamento de um fluxo pode mudar sozinho quando a instância é atualizada. Fixar a versão protege contra isso. As diferenças são reais — `GET /table` com query inválida devolve **404** na v1 e **200 com array vazio** na v2.

As versões disponíveis de cada API constam no **REST API Explorer** da sua instância. Os `sample` deste template usam `v2` na Table API e `v1` nas demais.

**Sete operações não têm variante versionada** e por isso não têm o parâmetro: as seis da Attachment API e **Service Catalog - Get wishlist item details**.

### O parâmetro `body` — um objeto, não campos soltos

Operações com corpo JSON expõem um único parâmetro `body` do tipo objeto, com o payload inteiro. Não há um parâmetro por campo. O motivo é que os corpos do ServiceNow são abertos: o corpo de **Table - Create a record** depende de quais colunas a tabela tem, e isso varia por instância e por tabela.

Cada operação traz no `sample` do `body` um exemplo real do formato esperado — use-o como ponto de partida e substitua os campos pelos da sua tabela.

A exceção é **Attachment - Upload a multipart file**, que usa `multipart/form-data` e por isso tem parâmetros granulares (`table_name`, `table_sys_id`, `upload_file`, `content_type`, `file_name`).

### Os dois uploads de anexo

| Operação | Content-Type | Quando usar |
| :--- | :--- | :--- |
| **Attachment - Upload a file** | definido por você em `content_type` | conteúdo textual: CSV, JSON, XML, log |
| **Attachment - Upload a multipart file** | `multipart/form-data` | qualquer arquivo, inclusive binário |

Em **Upload a file** o conteúdo vai no corpo como texto, no parâmetro `file_content`. Para arquivos binários de verdade — imagem, PDF, zip — prefira a operação multipart.

### Agregações: a função fica na chave

Na operação **Aggregate - Get record statistics**, a API do ServiceNow embute o nome da função de agregação na própria chave do parâmetro: `sysparm_avg_fields`, `sysparm_min_fields`, `sysparm_max_fields`, `sysparm_sum_fields`.

O template traz a chave `sysparm_avg_fields`. Para usar outra função, **edite a chave do parâmetro na operação**, não o valor. O parâmetro `sysparm_count=true` funciona à parte e não segue essa regra.

### Filtro direto por coluna não está mapeado

A documentação do ServiceNow permite filtrar passando a coluna diretamente na query string — `&active=true&priority=1` em vez de `sysparm_query=active=true^priority=1`. Esse atalho **não está no template**: como a chave da query é o próprio nome da coluna, ela varia por tabela e não pode virar um parâmetro nomeado.

Não há perda de funcionalidade: `sysparm_query` faz exatamente o mesmo. Se ainda assim quiser o atalho, acrescente a query manualmente na operação.

### Headers não aparecem nas operações

O ServiceNow aceita `Accept` (JSON ou XML) e `X-no-response-body` na maioria dos endpoints, mas todos são opcionais e já têm o default correto — `application/json`. Um header opcional deixado em branco é enviado com valor vazio e pode ser rejeitado pela API, então nenhum entra no template.

A única exceção é `Content-Type` em **Attachment - Upload a file**, obrigatório para o upload funcionar, mapeado no parâmetro `content_type`.

---

## Operações

### Table

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Table - Create a record** | **POST** | Insere um registro na tabela informada. Não suporta inserção múltipla. |
| **Table - Delete a record** | **DELETE** | Exclui da tabela o registro identificado pelo sys_id. |
| **Table - Modify a record** | **PUT** | Substitui o registro informado pelos dados enviados no corpo da requisição. |
| **Table - Retrieve a record** | **GET** | Obtém um registro específico da tabela pelo sys_id. |
| **Table - Retrieve records from a table** | **GET** | Recupera múltiplos registros da tabela informada, com filtro por query codificada e paginação. |
| **Table - Update a record** | **PATCH** | Atualiza parcialmente o registro com os pares campo/valor enviados no corpo. |

### Aggregate

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Aggregate - Get record statistics** | **GET** | Executa funções de agregação (contagem, soma, média, mínimo, máximo) sobre os registros da tabela. |

### Attachment

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Attachment - Delete an attachment** | **DELETE** | Exclui o anexo identificado pelo sys_id. |
| **Attachment - Retrieve attachment content** | **GET** | Baixa o conteúdo binário do arquivo anexado, identificado pelo sys_id. |
| **Attachment - Retrieve attachment metadata** | **GET** | Lista os metadados de múltiplos anexos da tabela sys_attachment. |
| **Attachment - Retrieve attachment metadata by id** | **GET** | Obtém os metadados de um anexo específico pelo sys_id. |
| **Attachment - Upload a file** | **POST** | Anexa um arquivo enviado no corpo da requisição ao registro indicado. |
| **Attachment - Upload a multipart file** | **POST** | Anexa um arquivo a um registro usando requisição multipart/form-data. |

### Import Set

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Import Set - Insert a record** | **POST** | Insere dados na tabela de staging e dispara a transformação síncrona dos transform maps. |
| **Import Set - Insert multiple records** | **POST** | Insere vários registros na tabela de staging numa única requisição, com transformação assíncrona. |
| **Import Set - Retrieve a record** | **GET** | Recupera um registro de staging do import set e o resultado da sua transformação. |

### Batch

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Batch - Send multiple requests** | **POST** | Envia várias requisições REST da instância em uma única chamada. |

### Email

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Email - Retrieve an email** | **GET** | Obtém os detalhes de um registro de e-mail da tabela sys_email. |
| **Email - Send an email** | **POST** | Cria um registro de e-mail na instância para envio pelos destinatários informados. |

### Knowledge

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Knowledge - Get article attachment** | **GET** | Baixa como arquivo um anexo de um artigo da base de conhecimento. |
| **Knowledge - Get article details** | **GET** | Obtém o conteúdo e os campos de um artigo específico da base de conhecimento. |
| **Knowledge - Get featured articles** | **GET** | Lista os artigos em destaque da base de conhecimento. |
| **Knowledge - Get most viewed articles** | **GET** | Lista os artigos da base de conhecimento ordenados pelos mais visualizados. |
| **Knowledge - Search articles** | **GET** | Busca artigos da base de conhecimento com filtro por texto, base, idioma e query codificada. |

### Service Catalog

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Service Catalog - Add item to cart** | **POST** | Adiciona o item do catálogo ao carrinho do usuário logado. |
| **Service Catalog - Add item to wishlist** | **POST** | Adiciona o item do catálogo à lista de desejos do usuário logado. |
| **Service Catalog - Checkout cart** | **POST** | Processa o checkout do carrinho atual conforme o fluxo de uma ou duas etapas configurado. |
| **Service Catalog - Checkout order guide** | **POST** | Retorna os itens de um order guide preparados para checkout. |
| **Service Catalog - Empty cart** | **DELETE** | Esvazia e exclui o carrinho indicado, conforme o papel do usuário autenticado. |
| **Service Catalog - Get cart details** | **GET** | Recupera os itens e os detalhes do carrinho do usuário logado. |
| **Service Catalog - Get catalog categories** | **GET** | Lista as categorias disponíveis no catálogo informado. |
| **Service Catalog - Get catalog details** | **GET** | Obtém as informações de um catálogo específico. |
| **Service Catalog - Get catalog item details** | **GET** | Obtém os detalhes de um item do catálogo, incluindo suas variáveis. |
| **Service Catalog - Get catalog items** | **GET** | Lista os itens do catálogo com filtro por catálogo, categoria, texto e tipo. |
| **Service Catalog - Get catalogs** | **GET** | Lista os catálogos de serviço aos quais o usuário tem acesso. |
| **Service Catalog - Get category details** | **GET** | Obtém as informações de uma categoria específica do catálogo. |
| **Service Catalog - Get delivery address** | **GET** | Recupera o endereço de entrega configurado para o usuário informado. |
| **Service Catalog - Get invalid delegated users** | **POST** | Lista os usuários cuja solicitação do item não pode ser delegada a terceiros. |
| **Service Catalog - Get item delegation** | **GET** | Verifica se o usuário delegado tem direito de aquisição sobre o item do catálogo. |
| **Service Catalog - Get variable display value** | **POST** | Retorna o valor de exibição da variável de catálogo informada. |
| **Service Catalog - Get wishlist** | **GET** | Lista os itens da lista de desejos do usuário logado. |
| **Service Catalog - Get wishlist item details** | **GET** | Obtém os detalhes de um item específico da lista de desejos. |
| **Service Catalog - Order item now** | **POST** | Faz o pedido imediato do item do catálogo, sem passar pelo carrinho. |
| **Service Catalog - Remove item from cart** | **DELETE** | Remove o item indicado do carrinho atual. |
| **Service Catalog - Submit order** | **POST** | Finaliza o pedido do carrinho do usuário e devolve o número da requisição gerada. |
| **Service Catalog - Submit order guide** | **PUT** | Retorna a lista de itens de um order guide a partir das necessidades descritas. |
| **Service Catalog - Submit record producer** | **POST** | Cria um registro a partir do record producer e devolve o caminho do registro criado. |
| **Service Catalog - Update cart item** | **PUT** | Atualiza a quantidade e as variáveis de um item do carrinho. |

---

## Fora do escopo

Duas coisas ficaram deliberadamente de fora:

**Service Catalog Open API** (8 endpoints, namespace `sn_tmf_api`) — apesar do nome parecido, não é o catálogo de autoatendimento coberto aqui. É a API padrão TMForum de gestão de catálogo de serviços de telecom, de produto separado e dependente de plugin.

**APIs de produto** — HR Service Delivery, CSM, Security Operations, DevOps, Field Service e demais módulos licenciados. Duas razões: dependem de plugins que a maioria das instâncias não tem, e a Table API já alcança as tabelas por trás delas (`sn_hr_core_case`, `sn_customerservice_case`) para leitura e escrita direta.

---

## Documentação oficial

[Todas as APIs REST do ServiceNow](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/api-rest.html)

[REST API Explorer](https://www.servicenow.com/docs/r/api-reference/rest-api-explorer/use-REST-API-Explorer.html)

[Table API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/c_TableAPI.html) ·
[Attachment API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/c_AttachmentAPI.html) ·
[Service Catalog API](https://www.servicenow.com/docs/r/zurich/api-reference/rest-apis/c_ServiceCatalogAPI.html)
