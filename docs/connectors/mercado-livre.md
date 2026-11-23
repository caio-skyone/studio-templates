# Mercado Livre

## Contexto

O Mercado Livre é o maior marketplace da América Latina. A API do Mercado Livre
permite que vendedores e integradores gerenciem publicações, acompanhem vendas
e envios e atendam compradores sem usar o painel web. Este conector cobre o
ciclo principal de um vendedor: consultar o catálogo de referência, publicar e
manter itens, acompanhar pedidos e envios e responder perguntas.

Domínios cobertos:

- **Sites**: países onde o Mercado Livre opera (`MLB` Brasil, `MLA` Argentina,
  `MLM` México…), tipos de publicação, níveis de exposição e tarifas de venda.
- **Categories / Domains**: árvore de categorias, atributos e termos de venda
  por categoria, preditor de categoria a partir do título e ficha técnica dos
  domínios (famílias de produto como `MLB-CELLPHONES`).
- **Users**: dados do usuário autenticado, cujo `id` é o identificador do
  vendedor exigido por várias buscas.
- **Items**: criação, consulta, atualização e republicação de publicações, busca
  dos itens do vendedor e gestão da descrição em texto plano.
- **Orders / Order Notes / Packs / Feedback**: busca e detalhe de pedidos,
  descontos aplicados, notas internas do vendedor, pacotes (carrinhos com vários
  pedidos) e qualificações entre comprador e vendedor.
- **Shipments**: detalhe do envio, itens, custos, histórico, transportadora,
  pagamentos, prazos (SLA, atrasos, lead time), catálogo de status e marcação de
  envio pronto para despacho.
- **Questions**: busca, consulta, resposta e exclusão de perguntas feitas nas
  publicações, além do tempo médio de resposta do vendedor.

**Observações técnicas:**

- **Pausar, fechar ou reativar uma publicação, e alterar preço ou estoque**, são
  feitos pela operação **Items - Update item**, enviando no corpo apenas os
  campos a mudar (`status`, `price`, `available_quantity`…). Não há operação
  separada para cada ação.
- **Id do vendedor:** os parâmetros `user_id`, `seller` e `seller_id` recebem o
  `id` retornado por **Users - Get authenticated user**.
- **`site_id`:** use `MLB` para o Brasil. As operações de catálogo aceitam
  qualquer site do Mercado Livre.
- **Valores fixos no conector:** as operações GET de **Shipments** enviam o
  header `x-format-new: true`, exigido pela API para o formato atual do JSON de
  envios. **Items - Update item description** envia `api_version=2` na query, e
  as operações de busca e consulta de **Questions** enviam `api_version=4`.
- **Corpos JSON:** as operações de escrita recebem o corpo inteiro em um único
  parâmetro `body` do tipo objeto. O formato de cada corpo está descrito no
  parâmetro e na documentação oficial.
- **Recategorização automática:** desde 29/10/2025 o Mercado Livre pode mudar a
  categoria de itens publicados via API. Fluxos que dependem da categoria (preço,
  tarifas, frete) devem reconsultar o item.

**Fora do escopo:** troca e renovação de token OAuth (feitas pela conta
conectada), etiquetas de envio (resposta binária em PDF/ZPL), divisão de envios,
bloqueio de compradores, criação de perguntas (ação do comprador), busca
pública de itens por site, catálogo, central de promoções, faturamento e notas
fiscais, mensagens pós-venda, reclamações e devoluções e Mercado Ads.

---

## Autenticação

**Tipo:** OAuth 2.0

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | https://api.mercadolibre.com |
| Porta | 443 |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Access Token | {{access_token}} |
| Refresh Token | {{refresh_token}} |
| Endpoint de troca de token | https://api.mercadolibre.com/oauth/token |

O Mercado Livre usa o fluxo **Authorization Code** (server side). O `Client ID`
e o `Client Secret` são o **App ID** e a **Secret Key** da aplicação criada no
DevCenter do Mercado Livre. O vendedor autoriza a aplicação em
`https://auth.mercadolivre.com.br/authorization`, e a `redirect_uri` precisa ser
idêntica à cadastrada na aplicação.

O access token expira em **6 horas**. O refresh token é de **uso único**: cada
renovação devolve um novo refresh token, que substitui o anterior. Para receber
refresh token, a aplicação precisa ter o escopo `offline_access`.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
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

## Documentação oficial

https://developers.mercadolivre.com.br/pt_br/api-docs-pt-br
