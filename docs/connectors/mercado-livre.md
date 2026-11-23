# Mercado Livre

## Contexto

O Mercado Livre Ã© o maior marketplace da AmÃ©rica Latina. A API do Mercado Livre
permite que vendedores e integradores gerenciem publicaÃ§Ãµes, acompanhem vendas
e envios e atendam compradores sem usar o painel web. Este conector cobre o
ciclo principal de um vendedor: consultar o catÃ¡logo de referÃªncia, publicar e
manter itens, acompanhar pedidos e envios e responder perguntas.

DomÃ­nios cobertos:

- **Sites**: paÃ­ses onde o Mercado Livre opera (`MLB` Brasil, `MLA` Argentina,
  `MLM` MÃ©xicoâ€¦), tipos de publicaÃ§Ã£o, nÃ­veis de exposiÃ§Ã£o e tarifas de venda.
- **Categories / Domains**: Ã¡rvore de categorias, atributos e termos de venda
  por categoria, preditor de categoria a partir do tÃ­tulo e ficha tÃ©cnica dos
  domÃ­nios (famÃ­lias de produto como `MLB-CELLPHONES`).
- **Users**: dados do usuÃ¡rio autenticado, cujo `id` Ã© o identificador do
  vendedor exigido por vÃ¡rias buscas.
- **Items**: criaÃ§Ã£o, consulta, atualizaÃ§Ã£o e republicaÃ§Ã£o de publicaÃ§Ãµes, busca
  dos itens do vendedor e gestÃ£o da descriÃ§Ã£o em texto plano.
- **Orders / Order Notes / Packs / Feedback**: busca e detalhe de pedidos,
  descontos aplicados, notas internas do vendedor, pacotes (carrinhos com vÃ¡rios
  pedidos) e qualificaÃ§Ãµes entre comprador e vendedor.
- **Shipments**: detalhe do envio, itens, custos, histÃ³rico, transportadora,
  pagamentos, prazos (SLA, atrasos, lead time), catÃ¡logo de status e marcaÃ§Ã£o de
  envio pronto para despacho.
- **Questions**: busca, consulta, resposta e exclusÃ£o de perguntas feitas nas
  publicaÃ§Ãµes, alÃ©m do tempo mÃ©dio de resposta do vendedor.

**ObservaÃ§Ãµes tÃ©cnicas:**

- **Pausar, fechar ou reativar uma publicaÃ§Ã£o, e alterar preÃ§o ou estoque**, sÃ£o
  feitos pela operaÃ§Ã£o **Items - Update item**, enviando no corpo apenas os
  campos a mudar (`status`, `price`, `available_quantity`â€¦). NÃ£o hÃ¡ operaÃ§Ã£o
  separada para cada aÃ§Ã£o.
- **Id do vendedor:** os parÃ¢metros `user_id`, `seller` e `seller_id` recebem o
  `id` retornado por **Users - Get authenticated user**.
- **`site_id`:** use `MLB` para o Brasil. As operaÃ§Ãµes de catÃ¡logo aceitam
  qualquer site do Mercado Livre.
- **Valores fixos no conector:** as operaÃ§Ãµes GET de **Shipments** enviam o
  header `x-format-new: true`, exigido pela API para o formato atual do JSON de
  envios. **Items - Update item description** envia `api_version=2` na query, e
  as operaÃ§Ãµes de busca e consulta de **Questions** enviam `api_version=4`.
- **Corpos JSON:** as operaÃ§Ãµes de escrita recebem o corpo inteiro em um Ãºnico
  parÃ¢metro `body` do tipo objeto. O formato de cada corpo estÃ¡ descrito no
  parÃ¢metro e na documentaÃ§Ã£o oficial.
- **RecategorizaÃ§Ã£o automÃ¡tica:** desde 29/10/2025 o Mercado Livre pode mudar a
  categoria de itens publicados via API. Fluxos que dependem da categoria (preÃ§o,
  tarifas, frete) devem reconsultar o item.

**Fora do escopo:** troca e renovaÃ§Ã£o de token OAuth (feitas pela conta
conectada), etiquetas de envio (resposta binÃ¡ria em PDF/ZPL), divisÃ£o de envios,
bloqueio de compradores, criaÃ§Ã£o de perguntas (aÃ§Ã£o do comprador), busca
pÃºblica de itens por site, catÃ¡logo, central de promoÃ§Ãµes, faturamento e notas
fiscais, mensagens pÃ³s-venda, reclamaÃ§Ãµes e devoluÃ§Ãµes e Mercado Ads.

---

## AutenticaÃ§Ã£o

**Tipo:** OAuth 2.0

**ConfiguraÃ§Ã£o da conta conectada:**

| VariÃ¡vel | Valor |
| -------- | ----- |
| Host | https://api.mercadolibre.com |
| Porta | 443 |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Access Token | {{access_token}} |
| Refresh Token | {{refresh_token}} |
| Endpoint de troca de token | https://api.mercadolibre.com/oauth/token |

O Mercado Livre usa o fluxo **Authorization Code** (server side). O `Client ID`
e o `Client Secret` sÃ£o o **App ID** e a **Secret Key** da aplicaÃ§Ã£o criada no
DevCenter do Mercado Livre. O vendedor autoriza a aplicaÃ§Ã£o em
`https://auth.mercadolivre.com.br/authorization`, e a `redirect_uri` precisa ser
idÃªntica Ã  cadastrada na aplicaÃ§Ã£o.

O access token expira em **6 horas**. O refresh token Ã© de **uso Ãºnico**: cada
renovaÃ§Ã£o devolve um novo refresh token, que substitui o anterior. Para receber
refresh token, a aplicaÃ§Ã£o precisa ter o escopo `offline_access`.

---

## OperaÃ§Ãµes

| Nome da OperaÃ§Ã£o | MÃ©todo | DescriÃ§Ã£o da FunÃ§Ã£o |
| :--------------- | :----- | :------------------ |
| **Sites - Get all sites** | **GET** | Lista os sites (países) onde o Mercado Livre opera, com a moeda padrão de cada um. |
| **Sites - Get listing types** | **GET** | Lista os tipos de publicação disponíveis no site. |
| **Sites - Get listing exposures** | **GET** | Lista os níveis de exposição associados aos tipos de publicação do site. |
| **Sites - Get listing prices** | **GET** | Consulta as tarifas de venda e publicação para um preço, tipo de publicação e categoria. |
| **Categories - Get site categories** | **GET** | Lista as categorias de primeiro nível do site. |
| **Categories - Get category by id** | **GET** | Obtém os detalhes de uma categoria, incluindo caminho na árvore, subcategorias e configurações. |
| **Categories - Get category attributes** | **GET** | Lista os atributos e regras usados para descrever os itens da categoria. |
| **Categories - Get category sale terms** | **GET** | Lista os termos de venda aceitos pela categoria, como garantia e prazo de fabricação. |
| **Categories - Get promotion packs** | **GET** | Lista os pacotes promocionais de classificados disponíveis para a categoria. |
| **Categories - Predict category** | **GET** | Sugere domínio, categoria e atributos para um item a partir do título informado. |
| **Domains - Get technical specs** | **GET** | Obtém a ficha técnica do domínio, com grupos e atributos de entrada e saída. |
| **Users - Get authenticated user** | **GET** | Obtém os dados do usuário dono do token de acesso, incluindo o id usado como seller. |
| **Items - Create item** | **POST** | Cria uma publicação (item) com título, categoria, preço, estoque, imagens e atributos. |
| **Items - Get item by id** | **GET** | Obtém os dados completos de uma publicação. |
| **Items - Get multiple items** | **GET** | Obtém várias publicações de uma vez, com até 20 ids, opcionalmente limitando os campos retornados. |
| **Items - Update item** | **PUT** | Atualiza uma publicação: preço, estoque, título, imagens, atributos ou status (paused, active, closed). |
| **Items - Relist item** | **POST** | Republica um item finalizado, criando uma nova publicação com preço, quantidade e tipo informados. |
| **Items - Search seller items** | **GET** | Busca os ids das publicações de um vendedor, com filtros por status, SKU e tipo de publicação. |
| **Items - Get item description** | **GET** | Obtém a descrição em texto plano de uma publicação. |
| **Items - Create item description** | **POST** | Adiciona a descrição em texto plano a uma publicação que ainda não tem descrição. |
| **Items - Update item description** | **PUT** | Substitui a descrição em texto plano de uma publicação. |
| **Orders - Search orders** | **GET** | Busca os pedidos de um vendedor, com filtros por status, período de criação e texto livre. |
| **Orders - Get order by id** | **GET** | Obtém os dados completos de um pedido: itens, pagamentos, comprador, envio e status. |
| **Orders - Get order discounts** | **GET** | Obtém os descontos aplicados a um pedido, como cupons e campanhas. |
| **Order Notes - Get order notes** | **GET** | Lista as notas internas do vendedor registradas em um pedido. |
| **Order Notes - Create order note** | **POST** | Registra uma nota interna do vendedor em um pedido. |
| **Order Notes - Update order note** | **PUT** | Altera o texto de uma nota interna de um pedido. |
| **Order Notes - Delete order note** | **DELETE** | Exclui uma nota interna de um pedido. |
| **Packs - Get pack by id** | **GET** | Obtém um pacote (pack) que agrupa pedidos de um mesmo carrinho, com seus pedidos e envio. |
| **Feedback - Get order feedback** | **GET** | Obtém as qualificações de comprador e vendedor de um pedido. |
| **Feedback - Create order feedback** | **POST** | Qualifica a contraparte de um pedido, informando se a venda foi concluída e a avaliação. |
| **Feedback - Get feedback by id** | **GET** | Obtém os detalhes de uma qualificação. |
| **Feedback - Update feedback** | **PUT** | Altera uma qualificação já enviada, dentro do prazo permitido. |
| **Feedback - Reply to feedback** | **POST** | Responde a uma qualificação recebida. |
| **Shipments - Get shipment by id** | **GET** | Obtém os dados de um envio: status, endereço, modalidade, rastreio e prazos. |
| **Shipments - Get shipment items** | **GET** | Lista os itens contidos em um envio. |
| **Shipments - Get shipment costs** | **GET** | Obtém os custos de um envio para comprador e vendedor, com descontos aplicados. |
| **Shipments - Get shipment history** | **GET** | Obtém o histórico de status e substátus de um envio. |
| **Shipments - Get shipment carrier** | **GET** | Obtém a transportadora responsável e a URL de rastreio de um envio. |
| **Shipments - Get shipment payments** | **GET** | Lista os pagamentos associados ao custo de um envio. |
| **Shipments - Get shipment SLA** | **GET** | Obtém o prazo de despacho prometido ao vendedor para um envio. |
| **Shipments - Get shipment delays** | **GET** | Lista os atrasos registrados em um envio. |
| **Shipments - Get shipment lead time** | **GET** | Obtém as estimativas de prazo de entrega e custo de um envio. |
| **Shipments - Mark ready to ship** | **POST** | Marca um envio como pronto para despacho (ready_to_ship). |
| **Shipments - Get shipment statuses** | **GET** | Lista todos os status e substátus possíveis de um envio. |
| **Questions - Search questions** | **GET** | Busca perguntas recebidas por item ou vendedor, com filtros de status e ordenação. |
| **Questions - Get question by id** | **GET** | Obtém uma pergunta com texto, status, autor e resposta. |
| **Questions - Answer question** | **POST** | Responde a uma pergunta feita em uma publicação do vendedor. |
| **Questions - Delete question** | **DELETE** | Exclui uma pergunta feita em uma publicação do vendedor. |
| **Questions - Get response time** | **GET** | Obtém o tempo médio de resposta do vendedor às perguntas, total e por faixa de horário. |

---

## DocumentaÃ§Ã£o oficial

https://developers.mercadolivre.com.br/pt_br/api-docs-pt-br
