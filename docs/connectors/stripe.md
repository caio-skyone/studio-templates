# Stripe

## Contexto

A API da **Stripe** é uma API **RESTful** para pagamentos, cobrança recorrente e movimentação de dinheiro. A comunicação é via **HTTPS**, as respostas são **JSON**, mas os **corpos de requisição usam `application/x-www-form-urlencoded`** — não JSON. Esse detalhe muda como o template é preenchido e está explicado em [Convenções do template](#convencoes-do-template).

Este template cobre **276 operações** em 64 domínios, agrupadas em cinco blocos:

**Pagamentos (core):** Customers, PaymentIntents, Charges, Refunds, PaymentMethods, SetupIntents, Balance, Balance Transactions, Payouts, Disputes e os subrecursos do cliente (saldo, contas bancárias, sources, identificações fiscais).
**Faturamento (billing):** Products, Prices, Subscriptions, Subscription Items e Schedules, Invoices, Invoice Items, Coupons, Promotion Codes, Credit Notes, Checkout Sessions, Payment Links, Billing Portal, Tax IDs, Tax Rates, Shipping Rates.
**Connect:** Accounts, Account Links e Sessions, contas bancárias e externas, capacidades, pessoas (representantes), Transfers, Transfer Reversals, Application Fees, Topups.
**Consumo (usage-based):** Billing Meters, Meter Events, Meter Event Adjustments e Summaries.
**Operação e antifraude:** Events, Webhook Endpoints, Radar (Value Lists, Value List Items, Early Fraud Warnings), Reviews, Files, File Links.

## Conceitos Fundamentais

### Objetos e IDs com prefixo

Todo objeto da Stripe tem um ID com prefixo que identifica o tipo — `cus_` (cliente), `pi_` (PaymentIntent), `ch_` (cobrança), `in_` (fatura), `sub_` (assinatura), `price_`, `prod_`, `acct_` (conta Connect). Os `sample` de cada parâmetro deste template já usam o prefixo correto, o que ajuda a conferir se você está passando o ID certo no lugar certo.

### Valores monetários em centavos

Valores são **inteiros na menor unidade da moeda**. `amount=2000` com `currency=brl` significa R$ 20,00. Não envie decimais.

### PaymentIntent é o fluxo recomendado

Para cobrar, o caminho moderno é **PaymentIntent** (criar → confirmar → capturar), não `Charges`. As operações de `Charges` seguem no template por compatibilidade e para consulta de cobranças históricas.

### Modo de teste

A chave define o ambiente: `sk_test_...` opera em modo de teste, `sk_live_...` em produção. Não há mudança de host nem de path — só da credencial na conta conectada.

---

## Autenticação

**Tipo:** Bearer Token

A Stripe autentica com a **secret key** da conta enviada como Bearer Token. A credencial fica na conta conectada — **nenhuma operação deste template carrega parâmetro de token**.

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | https://api.stripe.com |
| Porta | 443 |
| token | {{token}} |

O valor de `token` é a secret key da sua conta Stripe (`sk_live_...` ou `sk_test_...`), obtida em **Developers → API keys** no dashboard.

> A operação **Files - Create a file** aponta para `https://files.stripe.com`, não para o host da conta. Ela já está configurada como `full-url` no template, com o host embutido no path — a mesma credencial da conta conectada se aplica. Não altere esse path.

---

## Convenções do template

### O parâmetro `body` — form-urlencoded, não JSON

Toda operação `POST` tem **um único parâmetro `body`**, do tipo texto, cujo valor é a string form-urlencoded completa. O `sample` de cada operação já traz um exemplo realista e pronto para editar.

```
amount=2000&currency=brl&customer=cus_NffrFeUfNV2Hib&description=Pedido 12345
```

**Campos aninhados usam sintaxe de bracket:**

```
metadata[pedido]=12345
automatic_payment_methods[enabled]=true
line_items[0][price]=price_1MoBy5LkdIwHu7ixZhnattbh
line_items[0][quantity]=1
shipping[address][line1]=Av. Paulista 1000
```

Arrays são indexados por número (`line_items[0]`, `line_items[1]`, …) e objetos por chave (`metadata[pedido]`).

### Como incluir campos opcionais

O `body` de cada operação traz **os campos obrigatórios mais um conjunto representativo de opcionais** — não a lista completa. Vários endpoints da Stripe aceitam 40 ou mais campos de primeiro nível, e alguns chegam a centenas de folhas quando se expande o aninhamento; enumerar tudo tornaria o módulo inutilizável.

**Para usar um campo que não está no exemplo:**

1. Abra a operação no Studio e localize o parâmetro `body`.
2. Consulte o endpoint na [documentação oficial](#documentacao-oficial) e identifique o nome exato do campo.
3. Acrescente `&campo=valor` ao final do valor, usando bracket se for aninhado.
4. Se o valor for dinâmico no seu fluxo, substitua por uma referência de parâmetro do Studio.

O mesmo vale ao contrário: campos do exemplo que você não usa podem ser removidos, desde que os obrigatórios permaneçam. A descrição de cada `body` lista quais são os obrigatórios daquela operação.

### Versionamento da API

Todas as 276 operações têm o header **`Stripe-Version`** parametrizado como `stripe_version`, **obrigatório neste conector**. O template foi gerado a partir do spec `2026-07-29.dahlia`.

### Headers opcionais da API

`Stripe-Account` e `Idempotency-Key` **não fazem parte do conector**. Quando você precisar de um deles, adicione o header manualmente na operação dentro do Studio.

| Header | Para que serve | Valor |
| ------ | -------------- | ----- |
| `Stripe-Account` | Executar a chamada em nome de uma conta conectada (Connect) | um `acct_...` |
| `Idempotency-Key` | Evitar cobrança duplicada quando o fluxo é reexecutado após falha de rede — **recomendado em qualquer operação que movimente dinheiro** | chave única por tentativa lógica, ex. um UUID |

### Expansão de objetos

Onde a API permite, existe o parâmetro `expand` (chave de query `expand[]`). Ele substitui um ID na resposta pelo objeto completo — `expand=customer` numa cobrança devolve o objeto do cliente inline, evitando uma segunda chamada. Para expandir mais de um campo, edite a operação e acrescente chaves `expand[]` adicionais.

### Paginação

Listagens usam paginação por cursor: `limit` (1 a 100, padrão 10), `starting_after` (ID do último item da página atual, avança) e `ending_before` (retrocede). Não há paginação por número de página, exceto nas operações de busca (`Search`), que usam `page`.

### Filtros de data

Filtros como `created` aceitam um timestamp Unix exato. Para **faixas**, edite a chave da query para a forma com bracket:

```
created[gte]=1749513600
created[lte]=1752192000
```

### Busca

Operações `Search` usam a linguagem de consulta da Stripe no parâmetro `query`:

```
status:'succeeded' AND metadata['pedido']:'123'
```

Os dados de busca têm latência de até um minuto em relação às operações de escrita.

---

## Operações

Listadas na ordem do módulo, agrupadas por domínio.

| Nome da Operação | Método | Descrição da Função |
| ---------------- | ------ | ------------------- |
| Balance - Retrieve balance | GET | Recupera o saldo atual da conta Stripe. |
| Balance Transactions - List all balance transactions | GET | Lista as transações que compõem o saldo da conta. |
| Balance Transactions - Retrieve a balance transaction | GET | Recupera os detalhes de uma transação de saldo. |
| Charges - List all charges | GET | Lista todas as cobranças realizadas. |
| Charges - Create a charge | POST | Cria uma cobrança direta em um cartão ou fonte. |
| Charges - Search charges | GET | Busca cobranças usando uma consulta de pesquisa. |
| Charges - Retrieve a charge | GET | Recupera os detalhes de uma cobrança. |
| Charges - Update a charge | POST | Atualiza os metadados de uma cobrança existente. |
| Charges - Capture a charge | POST | Captura os fundos de uma cobrança previamente autorizada. |
| Customer Sessions - Create a Customer Session | POST | Cria uma sessão para embutir componentes voltados ao cliente. |
| Customers - List all customers | GET | Lista todos os clientes cadastrados. |
| Customers - Create a customer | POST | Cria um novo cliente. |
| Customers - Search customers | GET | Busca clientes usando uma consulta de pesquisa. |
| Customers - Delete a customer | DELETE | Remove um cliente permanentemente. |
| Customers - Retrieve a customer | GET | Recupera os detalhes de um cliente. |
| Customers - Update a customer | POST | Atualiza os dados de um cliente. |
| Customers - Create or retrieve funding instructions for a customer cash balance | POST | Gera ou recupera instruções de depósito para o saldo em dinheiro do cliente. |
| Customer Balance Transactions - List customer balance transactions | GET | Lista as transações do saldo de crédito do cliente. |
| Customer Balance Transactions - Create a customer balance transaction | POST | Cria uma transação no saldo de crédito do cliente. |
| Customer Balance Transactions - Retrieve a customer balance transaction | GET | Recupera uma transação do saldo de crédito do cliente. |
| Customer Balance Transactions - Update a customer credit balance transaction | POST | Atualiza os metadados de uma transação do saldo do cliente. |
| Customer Bank Accounts - List all bank accounts | GET | Lista as contas bancárias cadastradas do cliente. |
| Customer Bank Accounts - Create a card | POST | Adiciona um cartão como forma de pagamento do cliente. |
| Customer Bank Accounts - Delete a customer source | DELETE | Remove uma conta bancária do cliente. |
| Customer Bank Accounts - Retrieve a bank account | GET | Recupera uma conta bancária cadastrada do cliente. |
| Customer Bank Accounts - Update a card | POST | Atualiza os dados de um cartão do cliente. |
| Customer Bank Accounts - Verify a bank account | POST | Confirma os microdepósitos para validar a conta bancária do cliente. |
| Customer Cash Balance - Retrieve a cash balance | GET | Recupera o saldo em dinheiro disponível do cliente. |
| Customer Cash Balance - Update a cash balance's settings | POST | Atualiza as configurações do saldo em dinheiro do cliente. |
| Customer Cash Balance Transactions - List cash balance transactions | GET | Lista as transações do saldo em dinheiro do cliente. |
| Customer Cash Balance Transactions - Retrieve a cash balance transaction | GET | Recupera uma transação do saldo em dinheiro do cliente. |
| Customer Discount - Delete a customer discount | DELETE | Remove o desconto aplicado ao cliente. |
| Customer Discount - Retrieve a customer discount | GET | Recupera o desconto ativo aplicado ao cliente. |
| Customer Payment Methods - List a Customer's PaymentMethods | GET | Lista os PaymentMethods vinculados a um cliente. |
| Customer Payment Methods - Retrieve a Customer's PaymentMethod | GET | Recupera um PaymentMethod vinculado a um cliente. |
| Customer Sources - List all sources for a customer | GET | Lista as formas de pagamento legadas (sources) do cliente. |
| Customer Sources - Create a card | POST | Adiciona um cartão como forma de pagamento legada do cliente. |
| Customer Sources - Delete a customer source | DELETE | Remove uma forma de pagamento legada (source) do cliente. |
| Customer Sources - Retrieve a customer source | GET | Recupera uma forma de pagamento legada (source) do cliente. |
| Customer Sources - Update a card | POST | Atualiza os dados de um cartão legado do cliente. |
| Customer Sources - Verify a bank account | POST | Confirma os microdepósitos para validar a conta bancária legada. |
| Customer Tax IDs - List all Customer tax IDs | GET | Lista as identificações fiscais cadastradas do cliente. |
| Customer Tax IDs - Create a Customer tax ID | POST | Cadastra uma identificação fiscal para o cliente. |
| Customer Tax IDs - Delete a Customer tax ID | DELETE | Remove uma identificação fiscal do cliente. |
| Customer Tax IDs - Retrieve a Customer tax ID | GET | Recupera uma identificação fiscal do cliente. |
| Disputes - List all disputes | GET | Lista todas as disputas (chargebacks) registradas. |
| Disputes - Retrieve a dispute | GET | Recupera os detalhes de uma disputa. |
| Disputes - Update a dispute | POST | Envia evidências para contestar uma disputa. |
| Disputes - Close a dispute | POST | Encerra uma disputa aceitando a perda da cobrança. |
| Payment Intents - List all PaymentIntents | GET | Lista todos os PaymentIntents criados. |
| Payment Intents - Create a PaymentIntent | POST | Cria um PaymentIntent para processar um pagamento. |
| Payment Intents - Search PaymentIntents | GET | Busca PaymentIntents usando uma consulta de pesquisa. |
| Payment Intents - Retrieve a PaymentIntent | GET | Recupera os detalhes de um PaymentIntent. |
| Payment Intents - Update a PaymentIntent | POST | Atualiza os dados de um PaymentIntent. |
| Payment Intents - List all PaymentIntent LineItems | GET | Lista os itens de linha de um PaymentIntent. |
| Payment Intents - Reconcile a customer_balance PaymentIntent | POST | Reconcilia um PaymentIntent pago com saldo do cliente. |
| Payment Intents - Cancel a PaymentIntent | POST | Cancela um PaymentIntent antes da conclusão do pagamento. |
| Payment Intents - Capture a PaymentIntent | POST | Captura os fundos de um PaymentIntent previamente autorizado. |
| Payment Intents - Confirm a PaymentIntent | POST | Confirma um PaymentIntent para processar o pagamento. |
| Payment Intents - Increment an authorization | POST | Aumenta o valor autorizado de um PaymentIntent capturado parcialmente. |
| Payment Intents - Verify microdeposits on a PaymentIntent | POST | Confirma os microdepósitos para validar a conta bancária. |
| Payment Methods - List PaymentMethods | GET | Lista os PaymentMethods cadastrados. |
| Payment Methods - Create a PaymentMethod | POST | Cria um PaymentMethod para uso em pagamentos. |
| Payment Methods - Retrieve a PaymentMethod | GET | Recupera os detalhes de um PaymentMethod. |
| Payment Methods - Update a PaymentMethod | POST | Atualiza os dados de um PaymentMethod. |
| Payment Methods - Attach a PaymentMethod to a Customer | POST | Vincula um PaymentMethod a um cliente. |
| Payment Methods - Detach a PaymentMethod from a Customer | POST | Desvincula um PaymentMethod de um cliente. |
| Payouts - List all payouts | GET | Lista todos os repasses realizados. |
| Payouts - Create a payout | POST | Cria um repasse do saldo para a conta bancária. |
| Payouts - Retrieve a payout | GET | Recupera os detalhes de um repasse. |
| Payouts - Update a payout | POST | Atualiza os metadados de um repasse. |
| Payouts - Cancel a payout | POST | Cancela um repasse ainda não processado. |
| Payouts - Reverse a payout | POST | Reverte um repasse já enviado. |
| Refunds - List all refunds | GET | Lista todos os reembolsos realizados. |
| Refunds - Create a refund | POST | Cria um reembolso para uma cobrança. |
| Refunds - Retrieve a refund | GET | Recupera os detalhes de um reembolso. |
| Refunds - Update a refund | POST | Atualiza os metadados de um reembolso. |
| Refunds - Cancel a refund | POST | Cancela um reembolso ainda pendente. |
| Setup Attempts - List all SetupAttempts | GET | Lista as tentativas de configuração de um SetupIntent. |
| Setup Intents - List all SetupIntents | GET | Lista todos os SetupIntents criados. |
| Setup Intents - Create a SetupIntent | POST | Cria um SetupIntent para configurar um pagamento futuro. |
| Setup Intents - Retrieve a SetupIntent | GET | Recupera os detalhes de um SetupIntent. |
| Setup Intents - Update a SetupIntent | POST | Atualiza os dados de um SetupIntent. |
| Setup Intents - Cancel a SetupIntent | POST | Cancela um SetupIntent antes da confirmação. |
| Setup Intents - Confirm a SetupIntent | POST | Confirma um SetupIntent para salvar a forma de pagamento. |
| Setup Intents - Verify microdeposits on a SetupIntent | POST | Confirma os microdepósitos para validar a conta bancária de um SetupIntent. |
| Billing Portal Configurations - List portal configurations | GET | Lista as configurações do portal de cobrança. |
| Billing Portal Configurations - Create a portal configuration | POST | Cria uma configuração para o portal de cobrança do cliente. |
| Billing Portal Configurations - Retrieve a portal configuration | GET | Recupera uma configuração do portal de cobrança. |
| Billing Portal Configurations - Update a portal configuration | POST | Atualiza uma configuração do portal de cobrança. |
| Billing Portal Sessions - Create a portal session | POST | Cria uma sessão de acesso ao portal de cobrança do cliente. |
| Checkout Sessions - List all Checkout Sessions | GET | Lista todas as sessões de Checkout criadas. |
| Checkout Sessions - Create a Checkout Session | POST | Cria uma sessão de Checkout para iniciar um pagamento. |
| Checkout Sessions - Retrieve a Checkout Session | GET | Recupera os detalhes de uma sessão de Checkout. |
| Checkout Sessions - Update a Checkout Session | POST | Atualiza uma sessão de Checkout existente. |
| Checkout Sessions - Expire a Checkout Session | POST | Expira uma sessão de Checkout ainda aberta. |
| Checkout Sessions - Retrieve a Checkout Session's line items | GET | Recupera os itens de linha de uma sessão de Checkout. |
| Coupons - List all coupons | GET | Lista todos os cupons de desconto. |
| Coupons - Create a coupon | POST | Cria um cupom de desconto. |
| Coupons - Delete a coupon | DELETE | Remove um cupom de desconto. |
| Coupons - Retrieve a coupon | GET | Recupera os detalhes de um cupom de desconto. |
| Coupons - Update a coupon | POST | Atualiza os metadados de um cupom de desconto. |
| Credit Notes - List all credit notes | GET | Lista todas as notas de crédito emitidas. |
| Credit Notes - Create a credit note | POST | Cria uma nota de crédito para uma fatura. |
| Credit Notes - Preview a credit note | GET | Pré-visualiza uma nota de crédito antes de criá-la. |
| Credit Notes - Retrieve a credit note preview's line items | GET | Recupera os itens de linha de uma pré-visualização de nota de crédito. |
| Credit Notes - Retrieve a credit note's line items | GET | Recupera os itens de linha de uma nota de crédito. |
| Credit Notes - Retrieve a credit note | GET | Recupera os detalhes de uma nota de crédito. |
| Credit Notes - Update a credit note | POST | Atualiza os metadados de uma nota de crédito. |
| Credit Notes - Void a credit note | POST | Anula uma nota de crédito emitida. |
| Invoice Payments - List all payments for an invoice | GET | Lista os pagamentos vinculados a uma fatura. |
| Invoice Payments - Retrieve an InvoicePayment | GET | Recupera os detalhes de um pagamento de fatura. |
| Invoice Items - List all invoice items | GET | Lista os itens pendentes de fatura. |
| Invoice Items - Create an invoice item | POST | Cria um item para incluir na próxima fatura do cliente. |
| Invoice Items - Delete an invoice item | DELETE | Remove um item pendente de fatura. |
| Invoice Items - Retrieve an invoice item | GET | Recupera os detalhes de um item de fatura. |
| Invoice Items - Update an invoice item | POST | Atualiza um item pendente de fatura. |
| Invoices - List all invoices | GET | Lista todas as faturas emitidas. |
| Invoices - Create an invoice | POST | Cria uma nova fatura para o cliente. |
| Invoices - Create a preview invoice | POST | Gera uma pré-visualização de fatura sem criá-la. |
| Invoices - Search invoices | GET | Busca faturas usando uma consulta de pesquisa. |
| Invoices - Delete a draft invoice | DELETE | Remove uma fatura ainda em rascunho. |
| Invoices - Retrieve an invoice | GET | Recupera os detalhes de uma fatura. |
| Invoices - Update an invoice | POST | Atualiza os dados de uma fatura. |
| Invoices - Bulk add invoice line items | POST | Adiciona vários itens de linha de uma vez a uma fatura. |
| Invoices - Attach a payment to an Invoice | POST | Vincula um pagamento existente a uma fatura. |
| Invoices - Finalize an invoice | POST | Finaliza uma fatura em rascunho para cobrança. |
| Invoices - Retrieve an invoice's line items | GET | Recupera os itens de linha de uma fatura. |
| Invoices - Update an invoice's line item | POST | Atualiza um item de linha específico de uma fatura. |
| Invoices - Mark an invoice as uncollectible | POST | Marca a fatura como incobrável. |
| Invoices - Pay an invoice | POST | Efetua o pagamento de uma fatura pendente. |
| Invoices - Bulk remove invoice line items | POST | Remove vários itens de linha de uma vez de uma fatura. |
| Invoices - Send an invoice for manual payment | POST | Envia a fatura por e-mail para pagamento manual. |
| Invoices - Bulk update invoice line items | POST | Atualiza vários itens de linha de uma vez em uma fatura. |
| Invoices - Void an invoice | POST | Anula uma fatura já finalizada. |
| Payment Links - List all payment links | GET | Lista todos os links de pagamento criados. |
| Payment Links - Create a payment link | POST | Cria um link de pagamento reutilizável. |
| Payment Links - Retrieve payment link | GET | Recupera os detalhes de um link de pagamento. |
| Payment Links - Update a payment link | POST | Atualiza os dados de um link de pagamento. |
| Payment Links - Retrieve a payment link's line items | GET | Recupera os itens de linha de um link de pagamento. |
| Prices - List all prices | GET | Lista todos os preços cadastrados. |
| Prices - Create a price | POST | Cria um preço para um produto. |
| Prices - Search prices | GET | Busca preços usando uma consulta de pesquisa. |
| Prices - Retrieve a price | GET | Recupera os detalhes de um preço. |
| Prices - Update a price | POST | Atualiza os metadados de um preço. |
| Products - List all products | GET | Lista todos os produtos cadastrados. |
| Products - Create a product | POST | Cria um novo produto. |
| Products - Search products | GET | Busca produtos usando uma consulta de pesquisa. |
| Products - Delete a product | DELETE | Remove um produto cadastrado. |
| Products - Retrieve a product | GET | Recupera os detalhes de um produto. |
| Products - Update a product | POST | Atualiza os dados de um produto. |
| Product Features - List all features attached to a product | GET | Lista os recursos vinculados a um produto. |
| Product Features - Attach a feature to a product | POST | Vincula um recurso (feature) a um produto. |
| Product Features - Remove a feature from a product | DELETE | Remove um recurso vinculado de um produto. |
| Product Features - Retrieve a product_feature | GET | Recupera um recurso vinculado a um produto. |
| Promotion Codes - List all promotion codes | GET | Lista todos os códigos promocionais cadastrados. |
| Promotion Codes - Create a promotion code | POST | Cria um código promocional vinculado a um cupom. |
| Promotion Codes - Retrieve a promotion code | GET | Recupera os detalhes de um código promocional. |
| Promotion Codes - Update a promotion code | POST | Atualiza os dados de um código promocional. |
| Shipping Rates - List all shipping rates | GET | Lista todas as taxas de frete cadastradas. |
| Shipping Rates - Create a shipping rate | POST | Cria uma taxa de frete para uso no Checkout. |
| Shipping Rates - Retrieve a shipping rate | GET | Recupera os detalhes de uma taxa de frete. |
| Shipping Rates - Update a shipping rate | POST | Atualiza os dados de uma taxa de frete. |
| Subscription Items - List all subscription items | GET | Lista os itens de uma assinatura. |
| Subscription Items - Create a subscription item | POST | Adiciona um item a uma assinatura existente. |
| Subscription Items - Delete a subscription item | DELETE | Remove um item de uma assinatura. |
| Subscription Items - Retrieve a subscription item | GET | Recupera os detalhes de um item de assinatura. |
| Subscription Items - Update a subscription item | POST | Atualiza um item de uma assinatura. |
| Subscription Schedules - List all schedules | GET | Lista todos os cronogramas de assinatura. |
| Subscription Schedules - Create a schedule | POST | Cria um cronograma para gerenciar fases de uma assinatura. |
| Subscription Schedules - Retrieve a schedule | GET | Recupera os detalhes de um cronograma de assinatura. |
| Subscription Schedules - Update a schedule | POST | Atualiza as fases de um cronograma de assinatura. |
| Subscription Schedules - Cancel a schedule | POST | Cancela um cronograma de assinatura. |
| Subscription Schedules - Release a schedule | POST | Libera a assinatura do controle de um cronograma. |
| Subscriptions - List subscriptions | GET | Lista todas as assinaturas cadastradas. |
| Subscriptions - Create a subscription | POST | Cria uma nova assinatura para o cliente. |
| Subscriptions - Search subscriptions | GET | Busca assinaturas usando uma consulta de pesquisa. |
| Subscriptions - Cancel a subscription | DELETE | Cancela uma assinatura ativa. |
| Subscriptions - Retrieve a subscription | GET | Recupera os detalhes de uma assinatura. |
| Subscriptions - Update a subscription | POST | Atualiza os dados de uma assinatura. |
| Subscriptions - Delete a subscription discount | DELETE | Remove o desconto aplicado a uma assinatura. |
| Subscriptions - Migrate a subscription | POST | Migra uma assinatura para uma nova versão de faturamento. |
| Subscriptions - Resume a subscription | POST | Retoma uma assinatura pausada. |
| Tax IDs - List all tax IDs | GET | Lista as identificações fiscais cadastradas na conta. |
| Tax IDs - Create a tax ID | POST | Cadastra uma identificação fiscal para a conta. |
| Tax IDs - Delete a tax ID | DELETE | Remove uma identificação fiscal da conta. |
| Tax IDs - Retrieve a tax ID | GET | Recupera uma identificação fiscal da conta. |
| Tax Rates - List all tax rates | GET | Lista todas as alíquotas de imposto cadastradas. |
| Tax Rates - Create a tax rate | POST | Cria uma alíquota de imposto. |
| Tax Rates - Retrieve a tax rate | GET | Recupera os detalhes de uma alíquota de imposto. |
| Tax Rates - Update a tax rate | POST | Atualiza os dados de uma alíquota de imposto. |
| Account - Retrieve account | GET | Recupera os detalhes da conta conectada atual. |
| Connect Account Links - Create an account link | POST | Cria um link para onboarding de uma conta conectada. |
| Connect Account Sessions - Create an Account Session | POST | Cria uma sessão para embutir componentes de uma conta conectada. |
| Connect Accounts - List all connected accounts | GET | Lista todas as contas conectadas à plataforma. |
| Connect Accounts - Create an account | POST | Cria uma nova conta conectada na plataforma. |
| Connect Accounts - Delete an account | DELETE | Remove uma conta conectada. |
| Connect Accounts - Retrieve account | GET | Recupera os detalhes de uma conta conectada. |
| Connect Accounts - Update an account | POST | Atualiza os dados de uma conta conectada. |
| Connect Accounts - Create a login link | POST | Cria um link de login para o painel da conta conectada. |
| Connect Accounts - Reject an account | POST | Rejeita uma conta conectada por suspeita de fraude. |
| Connect Accounts - Unreject an account | POST | Remove a rejeição aplicada a uma conta conectada. |
| Connect Account Bank Accounts - Create an external account | POST | Adiciona uma conta bancária externa a uma conta conectada. |
| Connect Account Bank Accounts - Delete an external account | DELETE | Remove uma conta bancária externa de uma conta conectada. |
| Connect Account Bank Accounts - Retrieve an external account | GET | Recupera uma conta bancária externa de uma conta conectada. |
| Connect Account Bank Accounts - Update a bank account | POST | Atualiza uma conta bancária de uma conta conectada. |
| Connect Account Capabilities - List all account capabilities | GET | Lista as capacidades habilitadas em uma conta conectada. |
| Connect Account Capabilities - Retrieve an Account Capability | GET | Recupera uma capacidade específica de uma conta conectada. |
| Connect Account Capabilities - Update an Account Capability | POST | Solicita ou atualiza uma capacidade de uma conta conectada. |
| Connect Account External Accounts - List all external accounts | GET | Lista as contas externas de uma conta conectada. |
| Connect Account External Accounts - Create an external account | POST | Adiciona uma conta externa (bancária ou cartão) a uma conta conectada. |
| Connect Account External Accounts - Delete an external account | DELETE | Remove uma conta externa de uma conta conectada. |
| Connect Account External Accounts - Retrieve an external account | GET | Recupera uma conta externa de uma conta conectada. |
| Connect Account External Accounts - Update a bank account | POST | Atualiza uma conta bancária externa de uma conta conectada. |
| Connect Account People - List all persons | GET | Lista os representantes cadastrados em uma conta conectada. |
| Connect Account People - Create a person | POST | Cadastra um representante (pessoa) em uma conta conectada. |
| Connect Account People - Delete a person | DELETE | Remove um representante de uma conta conectada. |
| Connect Account People - Retrieve a person | GET | Recupera os dados de um representante da conta conectada. |
| Connect Account People - Update a person | POST | Atualiza os dados de um representante da conta conectada. |
| Application Fees - List all application fees | GET | Lista todas as taxas de aplicação cobradas pela plataforma. |
| Application Fees - Retrieve an application fee | GET | Recupera os detalhes de uma taxa de aplicação. |
| Application Fee Refunds - Retrieve an application fee refund | GET | Recupera um reembolso específico de taxa de aplicação. |
| Application Fee Refunds - Update an application fee refund | POST | Atualiza os metadados de um reembolso de taxa de aplicação. |
| Application Fee Refunds - Refund an application fee | POST | Reembolsa uma taxa de aplicação cobrada pela plataforma. |
| Application Fee Refunds - List all application fee refunds | GET | Lista os reembolsos de uma taxa de aplicação. |
| Application Fee Refunds - Create an application fee refund | POST | Cria um reembolso para uma taxa de aplicação cobrada. |
| Topups - List all top-ups | GET | Lista todas as recargas de saldo realizadas. |
| Topups - Create a top-up | POST | Cria uma recarga de saldo da conta. |
| Topups - Retrieve a top-up | GET | Recupera os detalhes de uma recarga de saldo. |
| Topups - Update a top-up | POST | Atualiza os metadados de uma recarga de saldo. |
| Topups - Cancel a top-up | POST | Cancela uma recarga de saldo pendente. |
| Transfers - List all transfers | GET | Lista todas as transferências realizadas. |
| Transfers - Create a transfer | POST | Cria uma transferência de fundos para uma conta conectada. |
| Transfers - Retrieve a transfer | GET | Recupera os detalhes de uma transferência. |
| Transfers - Update a transfer | POST | Atualiza os metadados de uma transferência. |
| Transfer Reversals - List all reversals | GET | Lista as reversões de uma transferência. |
| Transfer Reversals - Create a transfer reversal | POST | Cria uma reversão de uma transferência enviada. |
| Transfer Reversals - Retrieve a reversal | GET | Recupera os detalhes de uma reversão de transferência. |
| Transfer Reversals - Update a reversal | POST | Atualiza os metadados de uma reversão de transferência. |
| Events - List all events | GET | Lista os eventos gerados pela conta Stripe. |
| Events - Retrieve an event | GET | Recupera os detalhes de um evento específico. |
| Webhook Endpoints - List all webhook endpoints | GET | Lista todos os endpoints de webhook cadastrados. |
| Webhook Endpoints - Create a webhook endpoint | POST | Cria um endpoint de webhook para receber eventos. |
| Webhook Endpoints - Delete a webhook endpoint | DELETE | Remove um endpoint de webhook cadastrado. |
| Webhook Endpoints - Retrieve a webhook endpoint | GET | Recupera os detalhes de um endpoint de webhook. |
| Webhook Endpoints - Update a webhook endpoint | POST | Atualiza os dados de um endpoint de webhook. |
| Billing Meter Event Adjustments - Create a billing meter event adjustment | POST | Cria um ajuste para um evento de medidor de cobrança. |
| Billing Meter Events - Create a billing meter event | POST | Registra um novo evento de uso para um medidor de cobrança. |
| Billing Meters - List billing meters | GET | Lista os medidores de cobrança cadastrados. |
| Billing Meters - Create a billing meter | POST | Cria um medidor para rastrear o uso cobrado. |
| Billing Meters - Retrieve a billing meter | GET | Recupera os detalhes de um medidor de cobrança. |
| Billing Meters - Update a billing meter | POST | Atualiza as informações de um medidor de cobrança. |
| Billing Meters - Deactivate a billing meter | POST | Desativa um medidor de cobrança existente. |
| Billing Meters - Reactivate a billing meter | POST | Reativa um medidor de cobrança desativado. |
| Billing Meter Event Summaries - List billing meter event summaries | GET | Lista os resumos de eventos de um medidor de cobrança. |
| File Links - List all file links | GET | Lista os links de arquivo criados. |
| File Links - Create a file link | POST | Cria um link público para acessar um arquivo. |
| File Links - Retrieve a file link | GET | Recupera os detalhes de um link de arquivo. |
| File Links - Update a file link | POST | Atualiza os metadados de um link de arquivo. |
| Files - List all files | GET | Lista os arquivos enviados à Stripe. |
| Files - Create a file | POST | Envia um arquivo para a Stripe. |
| Files - Retrieve a file | GET | Recupera os detalhes de um arquivo. |
| Radar Early Fraud Warnings - List all early fraud warnings | GET | Lista os alertas antecipados de fraude do Radar. |
| Radar Early Fraud Warnings - Retrieve an early fraud warning | GET | Recupera um alerta antecipado de fraude do Radar. |
| Radar Value List Items - List all value list items | GET | Lista os itens de uma lista de valores do Radar. |
| Radar Value List Items - Create a value list item | POST | Adiciona um item a uma lista de valores do Radar. |
| Radar Value List Items - Delete a value list item | DELETE | Remove um item de uma lista de valores do Radar. |
| Radar Value List Items - Retrieve a value list item | GET | Recupera um item de uma lista de valores do Radar. |
| Radar Value Lists - List all value lists | GET | Lista todas as listas de valores do Radar. |
| Radar Value Lists - Create a value list | POST | Cria uma lista de valores do Radar. |
| Radar Value Lists - Delete a value list | DELETE | Remove uma lista de valores do Radar. |
| Radar Value Lists - Retrieve a value list | GET | Recupera os detalhes de uma lista de valores do Radar. |
| Radar Value Lists - Update a value list | POST | Atualiza os dados de uma lista de valores do Radar. |
| Reviews - List all open reviews | GET | Lista as revisões de fraude ainda abertas. |
| Reviews - Retrieve a review | GET | Recupera os detalhes de uma revisão de fraude. |
| Reviews - Approve a review | POST | Aprova uma revisão de fraude do Radar. |
---

## Documentação oficial

* [https://docs.stripe.com/api](https://docs.stripe.com/api) — referência completa da API
* [https://docs.stripe.com/api/versioning](https://docs.stripe.com/api/versioning) — versionamento e o header `Stripe-Version`
* [https://docs.stripe.com/api/idempotent_requests](https://docs.stripe.com/api/idempotent_requests) — idempotência
* [https://docs.stripe.com/api/expanding_objects](https://docs.stripe.com/api/expanding_objects) — expansão de objetos
* [https://docs.stripe.com/search](https://docs.stripe.com/search) — linguagem de consulta das operações de busca
