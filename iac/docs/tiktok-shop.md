# tiktok-shop

## Contexto

A TikTok Shop API dá acesso programático à plataforma de e-commerce da TikTok Shop — o "Partner Center" da TikTok para vendedores, apps parceiros e afiliados. Ela cobre catálogo de produtos, pedidos, fulfillment, logística, devoluções, financeiro, afiliados e muito mais, organizados por domínio (Seller, Products, Promotion, Orders, Fulfillment, Logistics, Finance, Analytics, Affiliate, entre outros).

Este conector cobre dois domínios:

- **Products** — catálogo core (criar/editar/buscar/ativar/desativar/excluir/recuperar produto, preço, estoque), taxonomia e pré-requisitos de listagem (categorias, atributos, marcas), mídia e conteúdo (upload de imagem/arquivo, tabelas de medida, tradução de imagem) e SEO/diagnóstico de listagem.
- **Orders** — busca e detalhe de pedidos, referências de pedido de sistemas externos (integração com ERPs/OMS) e detalhamento de preço do pedido.

*Fora de escopo neste conector (não implementado):* dentro de Products — global/cross-border listing, compliance (manufacturer/responsible person/SKPP/GPA, voltado a requisitos da UE) e opportunity marketplace; dentro de Orders — "Update The Blind Box Opening Results" (lives com caixa-surpresa) e "Pod Details" (print-on-demand), por serem nichados. Os demais domínios da API (Promotion, Fulfillment, Fulfilled by TikTok, Logistics, Return and refund, Finance, Analytics, Customer service, Customer engagement, Affiliate creator/partner/seller, Supply chain, Tools) não foram mapeados.

---

## Autenticação

**Tipo:** Autenticação por cabeçalho customizado

A TikTok Shop usa um esquema híbrido que não se encaixa em um único tipo padrão do Studio:

1. **OAuth2** para obter o token de acesso: o seller/partner aprova um link de autorização do app → o app recebe um `auth_code` (expira em 30 min) → troca por `access_token`/`refresh_token` em `POST https://auth.tiktok-shops.com/api/v2/token/get`. Esse fluxo acontece fora do Studio, na configuração da conta conectada.
2. O `access_token` obtido vai no header `x-tts-access-token` de toda chamada — é isso que o Studio modela como `header-auth` via conta conectada.
3. **Toda requisição também exige uma assinatura HMAC-SHA256** (`sign`), calculada a partir de path + query params ordenados + corpo da requisição, assinada com o `app_secret` do app. Como essa assinatura muda a cada chamada (depende do conteúdo da requisição), ela **não é uma credencial estática** injetável pela conta conectada — por isso `app_key`, `timestamp`, `sign` e `shop_cipher` foram modelados como **parâmetros de query em cada operação** do conector, a serem calculados/preenchidos por fora do Studio antes de cada chamada (ex.: por um script de pré-requisição).

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | https://open-api.tiktokglobalshop.com |
| Porta | 443 |
| token | {{token}} |

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Products - Create product** | **POST** | Cria um novo produto no catálogo da loja. |
| **Products - Get product** | **GET** | Obtém os detalhes de um produto pelo id. |
| **Products - Search products** | **POST** | Busca produtos da loja com filtros e paginação. |
| **Products - Edit product** | **PUT** | Substitui integralmente os dados de um produto existente. |
| **Products - Partial edit product** | **POST** | Atualiza parcialmente os campos de um produto existente. |
| **Products - Activate product** | **POST** | Reativa produtos desativados na loja. |
| **Products - Deactivate products** | **POST** | Desativa produtos na loja. |
| **Products - Delete products** | **DELETE** | Remove produtos da loja. |
| **Products - Recover products** | **POST** | Recupera produtos excluídos dentro do prazo de retenção. |
| **Products - Update price** | **POST** | Atualiza o preço de um produto e suas variações. |
| **Products - Update inventory** | **POST** | Atualiza o estoque de um produto e suas variações. |
| **Products - Search inventory** | **POST** | Busca informações de estoque de produtos. |
| **Products - Check listing prerequisites** | **GET** | Verifica os pré-requisitos da loja para listar produtos. |
| **Products - Get categories** | **GET** | Lista as categorias de produto disponíveis para a loja. |
| **Products - Recommend category** | **POST** | Recomenda uma categoria com base no título/descrição do produto. |
| **Products - Get category rules** | **GET** | Obtém as regras de listagem de uma categoria específica. |
| **Products - Get attributes** | **GET** | Lista os atributos exigidos/opcionais de uma categoria. |
| **Products - Get brands** | **GET** | Lista as marcas disponíveis para vincular a produtos. |
| **Products - Create custom brand** | **POST** | Cria uma marca customizada para uso nos produtos da loja. |
| **Products - Check product listing** | **POST** | Valida se um produto está pronto para ser listado. |
| **Products - Upload product image** | **POST** | Faz upload de uma imagem para uso em produtos. |
| **Products - Upload product file** | **POST** | Faz upload de um arquivo para uso em produtos. |
| **Products - Search size charts** | **POST** | Busca tabelas de medidas cadastradas. |
| **Products - Create size chart** | **POST** | Cria uma nova tabela de medidas. |
| **Products - Edit size charts** | **POST** | Edita tabelas de medidas existentes. |
| **Products - Optimize images** | **POST** | Otimiza imagens de produto automaticamente. |
| **Products - Create image translation task** | **POST** | Cria uma tarefa de tradução automática de texto em imagens. |
| **Products - Get image translation tasks** | **GET** | Consulta o status de tarefas de tradução de imagens. |
| **Products - Diagnose and optimize product** | **POST** | Diagnostica e sugere otimizações para um produto listado. |
| **Products - Get product information issue diagnosis** | **GET** | Lista problemas de informação identificados nos produtos. |
| **Products - Get products SEO words** | **GET** | Sugere palavras-chave de SEO para os produtos. |
| **Products - Get recommended product title and description** | **GET** | Sugere título e descrição otimizados para um produto. |
| **Orders - Get order list** | **POST** | Busca a lista de pedidos da loja com filtros e paginação. |
| **Orders - Get price detail** | **GET** | Obtém o detalhamento de preços de um pedido. |
| **Orders - Add external order references** | **POST** | Vincula referências de pedido de sistemas externos a um pedido. |
| **Orders - Get external order references** | **GET** | Consulta as referências de sistemas externos vinculadas a um pedido. |
| **Orders - Search order by external order reference** | **POST** | Busca um pedido a partir de uma referência de sistema externo. |
| **Orders - Get order detail** | **GET** | Obtém os detalhes completos de um ou mais pedidos. |

---

## Documentação oficial

https://partner.tiktokshop.com/docv2/page/tts-developer-guide
