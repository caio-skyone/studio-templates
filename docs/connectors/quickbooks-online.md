# QuickBooks Online

## Contexto

O QuickBooks Online (QBO) é uma plataforma de contabilidade em nuvem da Intuit voltada a pequenas e médias empresas. Sua API v3 (Accounting API) permite gerenciar todo o ciclo financeiro da empresa: contas contábeis, clientes, fornecedores, faturas, pagamentos, compras, lançamentos contábeis e relatórios gerenciais.

Principais domínios da API:

- **Transações de venda:** Invoice, SalesReceipt, Estimate, CreditMemo, RefundReceipt
- **Transações de compra:** Bill, BillPayment, Purchase, PurchaseOrder, VendorCredit
- **Cadastros:** Customer, Vendor, Employee, Item, Account, Department, Class
- **Financeiro:** Payment, Deposit, Transfer, JournalEntry, ExchangeRate
- **Fiscal:** TaxAgency, TaxCode, TaxRate, TaxService
- **Configurações:** Preferences, CompanyInfo, Term, PaymentMethod, TimeActivity
- **Utilitários:** Batch, Query, CDC (Change Data Capture), Attachable, Upload
- **Relatórios:** AccountList, BalanceSheet, CashFlow, ProfitAndLoss, GeneralLedger, TrialBalance, AgedPayables, AgedReceivables, CustomerBalance, VendorBalance, entre outros

---

## Autenticação

**Tipo:** OAuth 2.0

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://quickbooks.api.intuit.com` |
| Porta | 443 |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Access Token | {{access_token}} |
| Refresh Token | {{refresh_token}} |
| Endpoint de troca de token | `https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer` |

> **Nota:** O `realmId` (ID da empresa QBO) é um parâmetro de caminho presente em todas as requisições. Ele identifica a empresa à qual a operação se refere e deve ser informado em cada chamada.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Account - Account-Create** | **POST** | Cria uma nova conta contábil no QuickBooks. |
| **Account - Account-ReadById** | **GET** | Retorna os dados da conta contábil com o ID informado. |
| **Attachable - Attachable-Create** | **POST** | Cria um objeto anexável associado a uma transação ou entidade do QuickBooks. |
| **Attachable - Attachable-ReadById** | **GET** | Retorna um objeto anexável pelo ID informado. |
| **Batch - Batch** | **POST** | Executa múltiplas operações em lote em uma única requisição. |
| **Bill - Bill-Create** | **POST** | Cria uma nova fatura de fornecedor no QuickBooks. |
| **Bill - Bill-GetById** | **GET** | Retorna os dados de uma fatura de fornecedor pelo ID informado. |
| **Billpayment - BillPayment-Update** | **POST** | Atualiza os dados de um pagamento de fatura existente no QuickBooks. |
| **Billpayment - BillPayment-ReadById** | **GET** | Retorna os dados de um pagamento de fatura pelo ID informado. |
| **Cdc - CDC-Read** | **GET** | Retorna objetos alterados desde a data especificada, para as entidades informadas no parâmetro entities. |
| **Class - Class-Create** | **POST** | Cria um novo objeto de classe para segmentação de transações no QuickBooks. |
| **Class - Class-ReadById** | **GET** | Retorna os dados de uma classe pelo ID informado. |
| **Companyinfo - CompanyInfo-ReadById** | **GET** | Retorna as informações da empresa cadastrada no QuickBooks pelo ID informado. |
| **Creditmemo - CreditMemo-Update** | **POST** | Atualiza os dados de um memorando de crédito existente no QuickBooks. |
| **Creditmemo - CreditMemo-ReadById** | **GET** | Retorna os dados de um memorando de crédito pelo ID informado. |
| **Customer - Customer-Create** | **POST** | Cria um novo cliente no QuickBooks. |
| **Customer - Customer-ReadById** | **GET** | Retorna os dados de um cliente pelo ID informado. |
| **Department - Department-Create** | **POST** | Cria um novo departamento para organização de transações no QuickBooks. |
| **Department - Department-ReadById** | **GET** | Retorna os dados de um departamento pelo ID informado. |
| **Deposit - Deposit-Update** | **POST** | Atualiza os dados de um depósito existente no QuickBooks. |
| **Deposit - Deposit-ReadById** | **GET** | Retorna os dados de um depósito pelo ID informado. |
| **Employee - Employee-Delete** | **POST** | Desativa um funcionário no QuickBooks definindo o campo Active como false. |
| **Employee - Employee-ReadById** | **GET** | Retorna os dados de um funcionário pelo ID informado. |
| **Estimate - Estimate-Update** | **POST** | Atualiza os dados de um orçamento existente no QuickBooks. |
| **Estimate - Estimate-ReadById** | **GET** | Retorna os dados de um orçamento pelo ID informado. |
| **Exchangerate - ExchangeRate - GetDetails** | **GET** | Retorna a taxa de câmbio para a moeda de origem e data de referência informadas. |
| **Invoice - Invoice-Create** | **POST** | Cria uma nova fatura de venda no QuickBooks. |
| **Invoice - Invoice-ReadById** | **GET** | Retorna os dados de uma fatura de venda pelo ID informado. |
| **Item - Item-Create** | **POST** | Cria um objeto de item no QuickBooks Online. |
| **Item - Item-ReadById** | **GET** | Lê um item pelo seu identificador único. |
| **Journalentry - JournalEntry-Create** | **POST** | Cria um objeto de lançamento contábil no QuickBooks Online. |
| **Journalentry - JournalEntry-ReadById** | **GET** | Lê um objeto de lançamento contábil pelo seu identificador único. |
| **Payment - Payment-Create** | **POST** | Cria um objeto de pagamento no QuickBooks Online. |
| **Payment - Payment-ReadByID** | **GET** | Lê um objeto de pagamento pelo seu identificador único. |
| **Paymentmethod - PaymentMethod-Update** | **POST** | Atualiza um método de pagamento no QuickBooks Online. |
| **Paymentmethod - PaymentMethod-ReadById** | **GET** | Lê um método de pagamento pelo seu identificador único. |
| **Preferences - Preference-Read** | **GET** | Lê o objeto de preferências da empresa no QuickBooks Online. |
| **Preferences - Preference-Update** | **POST** | Atualiza o objeto de preferências da empresa no QuickBooks Online. |
| **Purchase - Purchase-Update** | **POST** | Cria um objeto de compra no QuickBooks Online. |
| **Purchase - Purchase-ReadById** | **GET** | Lê um objeto de compra pelo seu identificador único. |
| **Purchaseorder - PurchaseOrder-Create** | **POST** | Cria um objeto de ordem de compra no QuickBooks Online. |
| **Purchaseorder - PurchaseOrder-ReadById** | **GET** | Lê um objeto de ordem de compra pelo seu identificador único. |
| **Query - Transfer-ReadAll** | **POST** | Lê todos os objetos de transferência utilizando o endpoint de consulta (Query). |
| **Refundreceipt - RefundReceipt-Update** | **POST** | Atualiza um objeto de recibo de reembolso no QuickBooks Online. |
| **Refundreceipt - RefundReceipt-ReadById** | **GET** | Lê um objeto de recibo de reembolso pelo seu identificador único. |
| **Reports - Report-AccountList** | **GET** | Retorna o relatório de lista de contas detalhada do serviço de relatórios do QuickBooks Online. |
| **Reports - Report-AgedPayableDetail** | **GET** | Retorna o relatório detalhado de envelhecimento de contas a pagar (AP Aging Detail) do QuickBooks Online. |
| **Reports - Report-AgedPayables** | **GET** | Retorna o relatório resumido de envelhecimento de contas a pagar (AP Aging Summary) do QuickBooks Online. |
| **Reports - Report-AgedReceivableDetail** | **GET** | Retorna o relatório detalhado de envelhecimento de contas a receber (AR Aging Detail) do QuickBooks Online. |
| **Reports - Report-AgedReceivables** | **GET** | Retorna o relatório resumido de envelhecimento de contas a receber (AR Aging Summary) do QuickBooks Online. |
| **Reports - Report-BalanceSheet** | **GET** | Retorna o relatório de balanço patrimonial (Balance Sheet) do serviço de relatórios do QuickBooks Online. |
| **Reports - Report-CashFlow** | **GET** | Retorna o relatório de fluxo de caixa (Cash Flow) do serviço de relatórios do QuickBooks Online. |
| **Reports - Report-CashSales** | **GET** | Retorna o relatório de vendas à vista (CashSales) do serviço de relatórios do QuickBooks Online. |
| **Reports - Report-CustomerBalance** | **GET** | Retorna o relatório de saldo de clientes (CustomerBalance) do serviço de relatórios do QuickBooks Online. |
| **Reports - Report-CustomerBalanceDetail** | **GET** | Retorna o relatório detalhado de saldo de clientes (Customer Balance Detail) do QuickBooks Online. |
| **Reports - Report-CustomerIncome** | **GET** | Retorna o relatório de receita por cliente (Customer Income) do serviço de relatórios do QuickBooks Online. |
| **Reports - Report-CustomerSales** | **GET** | Retorna o relatório de Vendas por Cliente via GET. |
| **Reports - Report-DepartmentSales** | **GET** | Retorna o relatório de Vendas por Departamento via GET. |
| **Reports - Report-GeneralLedger** | **GET** | Retorna o relatório de Razão Geral (General Ledger) via GET. |
| **Reports - Report-InventoryValuationSummary** | **GET** | Retorna o relatório de Resumo de Avaliação de Estoque via GET. |
| **Reports - Report-ItemSales** | **GET** | Retorna o relatório de Vendas por Item via GET. |
| **Reports - Report-ProfitAndLoss** | **GET** | Retorna o relatório de Lucros e Perdas via GET. |
| **Reports - Report-ProfitAndLossDetail** | **GET** | Retorna o relatório detalhado de Lucros e Perdas via GET. |
| **Reports - Report-TransactionList** | **GET** | Retorna o relatório de Lista de Transações via GET. |
| **Reports - Report-TrialBalance** | **GET** | Retorna o relatório de Balancete de Verificação (Trial Balance) via GET. |
| **Reports - Report-VendorBalance** | **GET** | Retorna o relatório de Saldo por Fornecedor via GET. |
| **Reports - Report-VendorBalanceDetail** | **GET** | Retorna o relatório detalhado de Saldo por Fornecedor via GET. |
| **Reports - Report-VendorExpense** | **GET** | Retorna o relatório de Despesas por Fornecedor via GET. |
| **Salesreceipt - SalesReceipt-Create** | **POST** | Cria um objeto de recibo de venda (salesreceipt) via POST. |
| **Salesreceipt - SalesReceipt-ReadByID** | **GET** | Retorna um objeto de recibo de venda (salesreceipt) pelo ID via GET. |
| **Taxagency - TaxAgency-Create** | **POST** | Cria um objeto de agência fiscal (tax-agency) via POST. |
| **Taxagency - TaxAgency-ReadByID** | **GET** | Retorna um objeto de agência fiscal (tax-agency) pelo ID via GET. |
| **Taxcode - TaxCode-ReadById** | **GET** | Retorna um objeto de código fiscal (taxcode) pelo ID. |
| **Taxrate - TaxRate-ReadById** | **GET** | Retorna um objeto de alíquota fiscal (taxRate) pelo ID. |
| **Taxservice - TaxService-Create** | **POST** | Cria um código fiscal (taxcode) e suas alíquotas correspondentes usando o TaxService via POST. |
| **Term - Term-Delete** | **POST** | Atualiza um objeto de prazo (term); exclusão permanente não é suportada — para desativar, defina o atributo 'Active' como false. |
| **Term - Term-ReadById** | **GET** | Retorna um objeto de prazo (term) pelo ID via GET. |
| **Timeactivity - TimeActivity-Create** | **POST** | Cria um objeto de registro de atividade de tempo (timeactivity) via POST. |
| **Transfer - Transfer-Create** | **POST** | Cria um objeto de transferência (transfer) via POST. |
| **Transfer - Transfer-ReadById** | **GET** | Retorna um objeto de transferência (transfer) pelo ID via GET. |
| **Upload - Upload-Attachments** | **POST** | Envia e vincula novos anexos a um objeto do QuickBooks Online via POST multipart/form-data. |
| **Vendor - Vendor-Update** | **POST** | Atualiza um objeto de fornecedor (vendor) via POST. |
| **Vendor - Vendor-ReadById** | **GET** | Retorna um objeto de fornecedor (vendor) pelo ID via GET. |
| **Vendorcredit - VendorCredit-Delete** | **POST** | Exclui um objeto de crédito de fornecedor (vendorcredit) pelo ID via POST. |
| **Vendorcredit - VendorCredit-ReadById** | **GET** | Retorna um objeto de crédito de fornecedor (vendorcredit) pelo ID via GET. |

---

## Documentação oficial

https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account
