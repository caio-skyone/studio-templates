# Mercado Pago

## Introdução

Este artigo detalha como configurar, autenticar e integrar a **API do Mercado Pago** no **Skyone Studio**. O conector é um **template único** com **142 operações** sobre `https://api.mercadopago.com`, cobrindo desde a cobrança online até a operação presencial com maquininha.

| Bloco | Operações | O que cobre |
| :---- | --------: | :---------- |
| **Pagamentos e Checkout** | 21 | Pagamentos da API clássica (`/v1/payments`), reembolsos, cancelamentos, Checkout Pro (preferências), merchant orders, meios de pagamento, parcelamento, tokens de cartão e tipos de documento |
| **Orders API** | 12 | API de Ordens (`/v1/orders`), o modelo novo: criar, processar, capturar, cancelar, reembolsar e manipular transações; intenções de transferência (Pix e TED) |
| **Assinaturas** | 11 | Planos (`preapproval_plan`), assinaturas (`preapproval`) e faturas geradas por elas (`authorized_payments`) |
| **Clientes e cartões salvos** | 15 | CRUD de clientes, cartões tokenizados e endereços |
| **Contestações** | 15 | Reclamações do pós-venda (mensagens, evidências, anexos, histórico, abertura de disputa) e chargebacks |
| **Relatórios financeiros** | 22 | Relatórios de liberações (*releases*) e de liquidação (*settlement*): configuração, agendamento, geração sob demanda, consulta de status e download |
| **Presencial — QR, Point e POS** | 33 | QR Code dinâmico e estático, maquininhas Point, caixas (POS), lojas, terminais e configuração de integrador |
| **Marketplace, split e OAuth** | 7 | Pagamentos avançados com split, transferências para vendedores (*payouts*) e troca de tokens OAuth |
| **Wallet Connect** | 6 | Acordos de pagamento recorrente por carteira, tokens de pagador, cupons e descontos |

## O que é a API do Mercado Pago?

O Mercado Pago é a plataforma de pagamentos do Mercado Livre, disponível na Argentina, no Brasil, no Chile, na Colômbia, no México, no Peru e no Uruguai. A API é **RESTful** sobre HTTPS, com corpos e respostas em JSON, e expõe tanto o fluxo de cobrança online (cartão, Pix, boleto, saldo em conta, carteira) quanto a operação presencial (maquininhas Point, QR Code no caixa), a gestão de assinaturas, a conciliação financeira e o pós-venda.

**Principais capacidades:**

**Cobrança online:** criação de pagamentos com cartão tokenizado, Pix, boleto e dinheiro em conta; reembolso total ou parcial; captura em dois passos; consulta e busca com filtros.
**Checkout hospedado:** criação de preferências do Checkout Pro, que devolvem uma URL (`init_point`) para o comprador concluir o pagamento na interface do Mercado Pago.
**Ordens:** o modelo unificado mais recente, em que uma *ordem* agrupa transações de pagamento e permite processar, capturar, cancelar e reembolsar em etapas explícitas.
**Assinaturas:** planos com periodicidade e valor, assinaturas vinculadas a um pagador e as faturas que elas geram a cada ciclo.
**Clientes:** cofre de clientes com cartões salvos e endereços, para cobranças recorrentes sem re-tokenizar.
**Presencial:** vinculação de maquininhas Point, criação de intenções de pagamento e de reembolso no terminal, QR Code por caixa e por loja.
**Conciliação:** relatórios de liberações e de liquidação, com agendamento, geração sob demanda e download em CSV.
**Pós-venda:** reclamações abertas pelo comprador, troca de mensagens, envio de evidências e anexos, e acompanhamento de chargebacks.
**Marketplace:** pagamentos com divisão de valores entre marketplace e vendedor, e transferências programadas aos vendedores.

## Conceitos fundamentais

### `site_id` — o país é parte do modelo

Quase toda busca e várias criações aceitam ou exigem o país da conta: `MLB` (Brasil), `MLA` (Argentina), `MLM` (México), `MLC` (Chile), `MCO` (Colômbia), `MLU` (Uruguai), `MPE` (Peru). Meios de pagamento, formatos de documento, moeda e disponibilidade de recursos variam por país — uma integração de Brasil não é portável para o México sem revisão.

### Access token e public key não são intercambiáveis

O **access token** é credencial de servidor e autoriza tudo que este conector faz. A **public key** serve exclusivamente para tokenizar cartão no navegador ou no app, via MercadoPago.js. Enviar dados brutos de cartão (PAN, CVV) para a API a partir do backend joga a integração inteira para dentro do escopo PCI DSS completo — por isso a tokenização é client-side e não foi contemplada no template (requisições de conectores são feitas em server-side).

### Payments e Orders convivem

`/v1/payments` é a API clássica: um pagamento é a unidade. `/v1/orders` é o modelo novo: uma **ordem** agrupa transações e tem ciclo de vida explícito (criar → processar → capturar → reembolsar/cancelar). Os dois estão no conector porque integrações existentes seguem no modelo antigo, e ambos permanecem suportados. Para uma integração nova, a Orders API é o caminho indicado pelo Mercado Pago.

### `merchant_order` amarra o checkout ao pagamento

Um checkout pode gerar mais de uma tentativa de pagamento. A *merchant order* é o agrupador: ela referencia a preferência, os itens e todos os pagamentos associados, e é o objeto que informa se a compra foi de fato paga por inteiro.

### `preapproval` é a assinatura

Um **`preapproval_plan`** é o modelo (valor, frequência, moeda). Um **`preapproval`** é a assinatura de um pagador àquele plano. Cada ciclo cobrado gera um **`authorized_payment`** — a fatura, consultável no domínio *Authorized Payments*.

### Reclamação e chargeback são coisas diferentes

A **reclamação** (*claim*) nasce no pós-venda do Mercado Livre/Mercado Pago: o comprador abre, há troca de mensagens e envio de evidências, e ela pode escalar para disputa. O **chargeback** nasce no emissor do cartão: o titular contesta a cobrança no banco. Os dois têm endpoints e prazos próprios.

## Pré-requisitos e configuração no Mercado Pago

1. Acesse o **[painel de desenvolvedores](https://www.mercadopago.com.br/developers/panel)** com a conta que vai receber os pagamentos.
2. Crie uma **aplicação** e escolha o produto (Checkout Pro, Checkout Transparente, assinaturas, etc.).
3. Em **Credenciais**, você encontra dois tokens: de teste e de produção, escolha um conforme o seu uso do conector.

> Homologue a aplicação antes de ir a produção, o Mercado Pago exige checklist de qualidade para liberar recursos como Pix e split.

## Autenticação

**Tipo:** Bearer token

Este template usa o fluxo de bearer token do Mercado Pago.

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://api.mercadopago.com` |
| Porta | 443 |
| Token | {{token}} |

## Convenções deste conector

- **A versão fica no caminho, não em um parâmetro.** O Mercado Pago versiona por recurso, não por API: há `/v1/payments`, `/v2/wallet_connect`, versão no meio do caminho (`/post-purchase/v1/claims`, `/terminals/v1/...`) e recursos sem versão nenhuma (`/checkout/preferences`, `/preapproval`, `/pos`, `/merchant_orders`, `/instore/...`). Como nenhum recurso tem duas versões concorrentes, um parâmetro de versão só criaria erro — cada operação aponta para a versão em que aquele recurso existe.
- **Upload de anexo é multipart e exige base64.** Uma operação envia arquivo: **Claims - Attach a file to a claim message**. Informe o conteúdo em **base64** no parâmetro `file`, ajuste `file_mime_type` (JPEG, PNG ou PDF) e `attachment_file_name`, e marque **"Forçar bufferização da requisição"** na operação — sem isso o corpo é truncado. O limite do Mercado Pago é de 10 MB por arquivo.
- **Operações que devolvem arquivo têm `(Binary)` no nome.** São quatro: **Preapproval - Export subscriptions (Binary)**, **Claims - Download an attached file (Binary)**, **Reports - Download a releases report file (Binary)** e **Reports - Download a settlements report file (Binary)**. As três primeiras e a última devolvem CSV ou octet-stream, não JSON — trate a resposta como arquivo Base64 no fluxo, não como objeto.
- **Idempotência** `X-Idempotency-Key` é parâmetro obrigatório nas 10 operações de criação em que uma repetição cobraria o cliente duas vezes: as 7 da Orders API, **Advanced Payments - Create an advanced payment**, **Payments - Create a payment** e **Payments - Create a refund**. Use um UUID novo por tentativa lógica e o **mesmo** UUID ao repetir por timeout ou erro de rede. Você pode adicionar esse parâmetro em outras operações se necessário conforme a documentação do Mercado Pago.
- **Datas usam ISO 8601 com fuso.** Filtros como `begin_date`, `end_date`, `date_created_from` e `last_updated_from` esperam `2026-01-01T00:00:00.000-03:00`. Alguns endpoints de busca aceitam também as palavras relativas do Mercado Pago (`NOW`, `NOW-1DAYS`).
- **Paginação por `offset` + `limit`.** As buscas usam `offset`/`limit` (padrão 30, teto que varia por endpoint) e devolvem o total em `paging.total`.

## Limitações conhecidas

- **Tokenização de cartão não deve rodar aqui.** **Card Tokens - Create a card token (client-side only)** e **Card Tokens - Get a card token** não devem trafegar em server-side portanto não foram incluídas no template.
- **Headers opcionais ficaram fora.** `x-platform-id` (4 operações de Wallet Connect) e `X-Meli-Session-Id` (1 de Advanced Payments) não entraram. Se a sua integração precisar de um deles, acrescente na operação.
- **Operações marcadas como *deprecated* pelo Mercado Pago.** O bloco presencial ainda expõe rotas de QR dinâmico antigas (`Instore - Create a QR trama`, `Instore - Create dynamic QR order`) e o par `MP Mobile`. Estão aqui para integrações legadas; para projetos novos, use as rotas de `POS`/`Point`.
- **Escopo por país e por homologação.** Pix (`MLB`), split de pagamento, Wallet Connect e a Orders API exigem habilitação da aplicação junto ao Mercado Pago. Uma operação existir no conector não garante que a sua conta possa chamá-la.
- **Webhooks não são operações.** A configuração de notificações (`payment`, `merchant_order`, `subscription_preapproval`, `point_integration_wh`) é feita no painel de desenvolvedores ou no campo `notification_url` da própria requisição, não por endpoint — logo, não há operação para isso no conector.

---

## Operações Disponíveis

As 142 operações estão agrupadas nos nove blocos da tabela da Introdução.

### Pagamentos e Checkout — 21 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Card Tokens - Get a card token** | GET | Escopo PCI DSS: Tratar este endpoint traz sua integração para o escopo PCI DSS completo. |
| **Checkout - Create a preference** | POST | Cria uma preferência de Checkout Pro. A resposta contém `init_point` (produção). Eventos de webhook acionados: payment, merchant_order. |
| **Checkout - Get preference by ID** | GET | Obter preferência por ID. |
| **Checkout - Search preferences** | GET | Pesquisar preferências. |
| **Checkout - Update a preference** | PUT | Atualizar uma preferência. |
| **Identification Types - List identification types** | GET | Retorna tipos válidos de documento de identificação para site_id da credencial. Exemplos: CPF/CNPJ (Brasil), DNI/CUIL/CUIT (Argentina), RFC/CURP (México). Use para preencher seletores de tipo e validar entradas. |
| **Merchant Orders - Create a merchant order** | POST | Eventos de webhook acionados: merchant_order. |
| **Merchant Orders - Get merchant order** | GET | Obter pedido de comerciante. |
| **Merchant Orders - Search merchant orders** | GET | Pesquisar pedidos de comerciante. |
| **Merchant Orders - Update merchant order** | PUT | Atualizar pedido de comerciante. |
| **Payment Methods - Get installment options** | GET | Retorna planos de parcelamento disponíveis para um BIN, valor e site. Use para popular seletores de parcelamento no checkout. |
| **Payment Methods - List available payment methods** | GET | Retorna todos os métodos de pagamento disponíveis para o site_id. Use para construir seletores e validar disponibilidade antes de um pagamento. |
| **Payments - Cancel a payment** | PUT | Cancela um pagamento com status pending ou authorized. Apenas pagamentos não capturados ou processados podem ser cancelados. |
| **Payments - Create a payment** | POST | Cria um pagamento. Para cartões, gere token no cliente via MercadoPago.js. Para métodos offline (Boleto, OXXO, Pix), resposta inclui URL em transaction_details.external_resource_url. Suporta X-Idempotency-Key para retry seguro. |
| **Payments - Create a refund** | POST | Cria reembolso total ou parcial de pagamento aprovado. Omita amount para reembolso total. Suporta X-Idempotency-Key para retry seguro. |
| **Payments - Get a specific refund** | GET | Obtém um reembolso específico. |
| **Payments - Get payment by ID** | GET | Obtém um pagamento por ID. |
| **Payments - List refunds for a payment** | GET | Lista reembolsos de um pagamento. |
| **Payments - Search payments** | GET | Pesquisa pagamentos. |
| **Payments - Update or capture a payment** | PUT | Atualiza campos de pagamento ou captura um pagamento autorizado. Para capturar: `{"capture": true}`. Para cancelar: `{"status": "cancelled"}`. |

### Orders API — 12 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Orders - Add a transaction to an order** | POST | Adiciona uma transação de pagamento a um pedido em modo manual. O pedido deve estar com status=created. |
| **Orders - Cancel an order** | POST | Cancela pedido e todas as suas transações. Apenas pedidos com status=action_required ou status=created podem ser cancelados. |
| **Orders - Capture an authorized order** | POST | Captura totalmente pedido autorizado anteriormente (capture_mode=manual). Todas as transações autorizadas associadas são capturadas na íntegra. |
| **Orders - Create an order** | POST | Cria uma ordem para processar pagamentos. Em `processing_mode` automático, envie o array `transactions.payments`; em manual, omita-o e adicione as transações depois, disparando o processamento à parte. |
| **Orders - Delete a transaction from an order** | DELETE | Remove uma transação de um pedido em modo manual. Disponível apenas antes do processamento. |
| **Orders - Get order by ID** | GET | Retorna todas as informações do pedido para o ID de pedido fornecido. |
| **Orders - Process an order** | POST | Dispara o processamento de um pedido e todas as suas transações. Disponível apenas para pedidos em modo manual. O pedido passa a processado ou action_required. |
| **Orders - Refund an order** | POST | Executa reembolso total ou parcial das transações de um pedido. Para reembolso total, envie corpo vazio. Para parcial, inclua o array de transações com IDs e valores. |
| **Orders - Search orders** | GET | Pesquisar pedidos usando intervalo de datas e filtros opcionais. begin_date e end_date são obrigatórios. |
| **Orders - Update a transaction on an order** | PUT | Atualiza o método de pagamento de uma transação pendente em um pedido no modo manual. |
| **Transaction Intents - Create a disbursement (Pix or bank transfer)** | POST | Cria desembolso via Pix ou transferência bancária para Brasil. payment_method_id define: pix (instantâneo, 24/7) ou bank_transfer (TED/DOC). |
| **Transaction Intents - Get disbursement status** | GET | Disponível no Brasil (MLB) |

### Assinaturas — 11 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Authorized Payments - Get subscription invoice** | GET | Obter fatura de assinatura. |
| **Authorized Payments - Search subscription invoices** | GET | Pesquisa faturas de cobrança geradas por assinaturas. |
| **Preapproval - Create a subscription** | POST | Cria uma assinatura |
| **Preapproval - Export subscriptions (Binary)** | GET | Exporta uma lista de assinaturas para um cobrador como um arquivo baixável. Filtre por ID do plano, status e ordem de classificação. |
| **Preapproval - Get subscription** | GET | Obtém assinatura |
| **Preapproval - Search subscriptions** | GET | Pesquisa assinaturas |
| **Preapproval - Update subscription** | PUT | Atualiza status da assinatura ou detalhes de cobrança. Uso comum: `{"status": "paused"}` para pausar, `{"status": "authorized"}` para retomar, `{"status": "cancelled"}` para cancelar. |
| **Preapproval Plan - Create a subscription plan** | POST | Cria um plano de cobrança recorrente. Assinaturas individuais referenciam este plano. A resposta inclui `init_point` para enviar assinantes para autorizar a cobrança. |
| **Preapproval Plan - Get subscription plan** | GET | Obtém plano de assinatura |
| **Preapproval Plan - Search subscription plans** | GET | Pesquisa planos de assinatura |
| **Preapproval Plan - Update a subscription plan** | PUT | Atualiza um plano de assinatura |

### Clientes e cartões salvos — 15 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Customers - Create a customer** | POST | Cria perfil de cliente para armazenar métodos de pagamento. E-mail do cliente é único por conta. |
| **Customers - Create a customer address** | POST | Adiciona endereço de entrega ou cobrança ao perfil de cliente. |
| **Customers - Delete a customer** | DELETE | Exclui permanentemente perfil de cliente. Ação não pode ser desfeita. Cartões salvos associados também serão removidos. |
| **Customers - Delete a customer address** | DELETE | Excluir um endereço do cliente. |
| **Customers - Delete a saved card** | DELETE | Excluir um cartão salvo. |
| **Customers - Get a customer address** | GET | Obter um endereço do cliente. |
| **Customers - Get a saved card** | GET | Obter um cartão salvo. |
| **Customers - Get customer by ID** | GET | Obter cliente por ID. |
| **Customers - List customer addresses** | GET | Listar endereços do cliente. |
| **Customers - List customer cards** | GET | Listar cartões do cliente. |
| **Customers - Save a card to a customer** | POST | Salva cartão tokenizado ao perfil do cliente para pagamentos futuros. Token deve ser criado no lado cliente via MercadoPago.js. Dados brutos nunca devem passar pelo servidor. Escopo PCI DSS completo. |
| **Customers - Search customers** | GET | Pesquisar clientes. |
| **Customers - Update a customer** | PUT | Atualizar um cliente. |
| **Customers - Update a customer address** | PUT | Atualizar um endereço do cliente. |
| **Customers - Update a saved card** | PUT | Atualizar um cartão salvo. |

### Contestações — 15 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Chargebacks - Get chargeback by ID** | GET | Obter contestação por ID. |
| **Chargebacks - Upload chargeback documentation** | PUT | Enviar documentação de contestação. |
| **Claims - Attach a file to a claim message** | POST | Carrega e anexa um arquivo (imagem, PDF) a uma reclamação. Formatos suportados: JPEG, PNG, PDF. Tamanho máximo: 10 MB. |
| **Claims - Download an attached file (Binary)** | GET | Baixa um arquivo anexado |
| **Claims - Get attached file metadata** | GET | Obtém metadados do arquivo anexado |
| **Claims - Get claim details** | GET | Retorna todos os detalhes de uma reclamação pós-venda, incluindo status, etapa e partes envolvidas. |
| **Claims - Get claim evidence** | GET | Obtém comprovante de reclamação |
| **Claims - Get claim messages** | GET | Obtém mensagens de reclamação |
| **Claims - Get claim reason** | GET | Retorna a descrição e metadados para um código de motivo de reclamação específico. |
| **Claims - Get claim status history** | GET | Obtém histórico de status de reclamação |
| **Claims - Get expected mediation resolutions** | GET | Retorna as opções de resolução possíveis para uma reclamação na etapa de mediação. |
| **Claims - Request claim mediation** | POST | Escalaciona uma reclamação para mediação, solicitando que o MP intervenha na disputa. |
| **Claims - Search claims** | GET | Pesquisa reclamações |
| **Claims - Send a message in a claim** | POST | Envia uma mensagem de texto (com anexos opcionais) no encadeamento da reclamação. |
| **Claims - Upload shipping evidence** | POST | Envia comprovante de envio (código de rastreamento, comprovante de entrega) para apoiar o caso do vendedor em uma reclamação. Aceito como parte do processo de resolução. |

### Relatórios financeiros — 22 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Reports - Create a releases report** | POST | Gera um relatório único de lançamentos para o intervalo de datas especificado. Retorna um ID de tarefa para sondagem de conclusão. |
| **Reports - Create a settlements report** | POST | Gera um relatório único de todas as transações para o intervalo de datas especificado. Retorna um ID de tarefa para sondagem. |
| **Reports - Create releases report configuration** | POST | Cria a configuração para geração automática de relatórios de lançamentos. Define colunas, frequência de agendamento, formato de arquivo e entrega SFTP opcional. |
| **Reports - Create settlements report configuration** | POST | Cria a configuração para geração automática de relatórios de todas as transações (liquidação). Define colunas, frequência, formato e entrega SFTP. |
| **Reports - Disable automatic releases report generation** | DELETE | Desativa a geração automática de relatórios de lançamentos. |
| **Reports - Disable automatic settlements report generation** | DELETE | Desativa a geração automática de relatórios de liquidação. |
| **Reports - Download a releases report file (Binary)** | GET | Baixa o arquivo CSV do relatório gerado pelo nome do arquivo. |
| **Reports - Download a settlements report file (Binary)** | GET | Baixa um arquivo de relatório de liquidações. |
| **Reports - Enable automatic releases report generation** | POST | Ativa a geração de relatório agendado com base na frequência configurada. |
| **Reports - Enable automatic settlements report generation** | POST | Ativa a geração automática de relatórios de liquidação. |
| **Reports - Get releases report configuration** | GET | Obtém a configuração do relatório de lançamentos. |
| **Reports - Get releases report list** | GET | Obtém a lista de relatórios de lançamentos. |
| **Reports - Get releases report task status** | GET | Sonda o status de uma tarefa de geração de relatório. Verifique até que `status=done`. |
| **Reports - Get settlements report configuration** | GET | Obtém a configuração do relatório de liquidação. |
| **Reports - Get settlements report list** | GET | Obtém a lista de relatórios de liquidação. |
| **Reports - Get settlements report task status** | GET | Obtém o status da tarefa do relatório de liquidação. |
| **Reports - List scheduled releases reports** | GET | Lista os relatórios de lançamentos agendados. |
| **Reports - List scheduled settlements reports** | GET | Lista os relatórios de liquidação agendados. |
| **Reports - Search releases reports** | GET | Pesquisa relatórios de lançamentos. |
| **Reports - Search settlements reports** | GET | Pesquisa relatórios de liquidação. |
| **Reports - Update releases report configuration** | PUT | Atualiza a configuração do relatório de lançamentos. |
| **Reports - Update settlements report configuration** | PUT | Atualiza a configuração do relatório de liquidação. |

### Presencial — QR, Point e POS — 33 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Instore - Confirm QR cashout status** | POST | Confirma o status de saque para um pedido de retirada de dinheiro baseado em QR. Disponível em: Argentina, Brasil (MLA, MLB). |
| **Instore - Create a QR trama (deprecated Dynamic QR)** | POST | Disponível em: Argentina, Brasil, México (MLA, MLB, MLM). Guia de migração: https://www.mercadopago.com/developers/en/docs/qr-code/orders/create-order. |
| **Instore - Create dynamic QR order (deprecated)** | PUT | Disponível em: Argentina, Brasil, México (MLA, MLB, MLM). Guia de migração: https://www.mercadopago.com/developers/en/docs/qr-code/orders/create-order. |
| **Instore - Create in-store order (deprecated V2)** | PUT | Guia de migração: https://www.mercadopago.com/developers/en/docs/qr-code/orders/create-order. |
| **Instore - Create or update QR integrator configuration** | PATCH | Configura as definições do integrador para pagamentos QR no ponto de venda. |
| **Instore - Delete in-store order (deprecated V2)** | DELETE | Guia de migração: https://www.mercadopago.com/developers/en/docs/qr-code/orders/create-order. |
| **Instore - Get QR integrator configuration** | GET | Obter configuração do integrador QR. |
| **Instore - Get in-store order (deprecated V2)** | GET | Guia de migração: https://www.mercadopago.com/developers/en/docs/qr-code/orders/create-order. |
| **MP Mobile - Create in-store order (deprecated V1)** | PUT | Guia de migração: https://www.mercadopago.com/developers/en/docs/qr-code/orders/create-order. |
| **MP Mobile - Delete in-store order (deprecated V1)** | DELETE | Guia de migração: https://www.mercadopago.com/developers/en/docs/qr-code/orders/create-order. |
| **POS - Create a point of sale** | POST | Cria um ponto de venda em uma loja para receber pagamentos de produtos ou serviços. Cada POS terá um código QR único vinculado a ele. |
| **POS - Delete a point of sale** | DELETE | Exclui um ponto de venda |
| **POS - Get a point of sale** | GET | Obtém um ponto de venda |
| **POS - Search points of sale** | GET | Pesquisar pontos de venda. |
| **POS - Update a point of sale** | PUT | Atualiza um ponto de venda |
| **Point - Cancel a payment intent** | DELETE | Disponível em: Argentina, Brasil, México (MLA, MLB, MLM). |
| **Point - Cancel a refund intent on a terminal** | DELETE | Cancelar uma intenção de reembolso em um terminal. |
| **Point - Create a payment intent on a Point device** | POST | Cria uma intenção de pagamento enviada a um dispositivo Point POS para o cliente tocar/inserir seu cartão. Disponível em: Argentina, Brasil, México (MLA, MLB, MLM). Idempotente com header `X-Idempotency-Key`. Webhook: point_integration_wh. |
| **Point - Create a refund intent on a terminal** | POST | Inicia uma intenção de reembolso em um dispositivo terminal Point. |
| **Point - Get a refund intent status** | GET | Obter status de uma intenção de reembolso. |
| **Point - Get payment intent details** | GET | Disponível em: Argentina, Brasil, México (MLA, MLB, MLM). |
| **Point - List Point devices** | GET | Disponível em: Argentina, Brasil, México (MLA, MLB, MLM). |
| **Stores - Get store by ID** | GET | Obtém loja por ID |
| **Terminals - Cancel a terminal action** | POST | Cancela uma ação de terminal. |
| **Terminals - Create a terminal print action** | POST | Envia uma ação de impressão para um terminal Point: imagem de recibo (`type` = `PRINT_INFO`) ou DTE, documento fiscal eletrônico disponível apenas no Chile (`PRINT_DTE`). Disponível em MLA, MLB, MLC e MLM. |
| **Terminals - Get list of terminals** | GET | Retorna todos os terminais Point (hardware) registrados na conta. |
| **Terminals - Get terminal action status** | GET | Disponível em: Argentina, Brasil, Chile, México (MLA, MLB, MLC, MLM) |
| **Terminals - Update terminal operation mode** | PATCH | Altera o modo de operação de um ou mais terminais. PDV — modo integrado (conectado ao seu sistema); STANDALONE — modo independente (sem integração). |
| **Users - Create a store** | POST | Cria uma loja. |
| **Users - Delete a store** | DELETE | Deleta uma loja. |
| **Users - List POS devices for a user** | GET | Lista os dispositivos POS de um usuário. |
| **Users - Search stores** | GET | Pesquisa lojas. |
| **Users - Update a store** | PUT | Atualiza uma loja. |

### Marketplace, split e OAuth — 7 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Advanced Payments - Capture or cancel an advanced payment** | PUT | Captura ou cancela um pagamento avançado. Disponível em: Argentina, Brasil, México (MLA, MLB, MLM). |
| **Advanced Payments - Create an advanced payment** | POST | Cria um pagamento avançado Wallet Connect (pagamento dividido marketplace). Disponível em: Argentina, Brasil, México (MLA, MLB, MLM). |
| **Advanced Payments - Get an advanced payment** | GET | Disponível em: Argentina, Brasil, México (MLA, MLB, MLM). |
| **OAuth - Create OAuth token** | POST | Troca códigos de autorização por tokens de acesso, atualiza tokens expirados ou solicita tokens de credenciais de cliente para fluxos máquina-a-máquina. O parâmetro `state` é obrigatório em fluxos authorization_code para prevenir CSRF. |
| **Payouts - Cancel a payout transaction** | PUT | Disponível em: Argentina, México (MLA, MLM) |
| **Payouts - Create a batch of payout transactions** | POST | Disponível em: Argentina, México (MLA, MLM) |
| **Payouts - List payout transactions** | GET | Disponível em: Argentina, México (MLA, MLM) |

### Wallet Connect — 6 operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Wallet Connect - Create a Wallet Connect agreement** | POST | Cria acordo de autorização para Wallet Connect. Retorna token para redirecionar pagador para autorização de carteira. |
| **Wallet Connect - Create a discount promise** | POST | Valida um cupom e retorna valor de desconto e termos legais. |
| **Wallet Connect - Create a payer token from agreement** | POST | Disponível em: Argentina, Brasil, México (MLA, MLB, MLM) |
| **Wallet Connect - Get a Wallet Connect agreement** | GET | Disponível em: Argentina, Brasil, México (MLA, MLB, MLM) |
| **Wallet Connect - Revoke a Wallet Connect agreement** | DELETE | Disponível em: Argentina, Brasil, México (MLA, MLB, MLM) |
| **Wallet Connect - Validate a coupon** | POST | Verifica status do cupom e retorna descrição e termos legais. |
---

## Documentação oficial

- **Portal de desenvolvedores:** https://www.mercadopago.com.br/developers/pt/docs
- **Referência da API:** https://www.mercadopago.com.br/developers/pt/reference
- **Especificação OpenAPI (fonte deste conector):** https://github.com/mercadopago/openapi/blob/main/spec3.json
