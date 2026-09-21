# Bling

## Contexto

O Bling é um sistema de gestão (ERP) brasileiro voltado para pequenas e
médias empresas, cobrindo vendas, estoque, financeiro, produção e emissão de
documentos fiscais eletrônicos. A API Bling 3.0 expõe esses módulos via REST,
com endpoints organizados por domínio de negócio.

Principais domínios e conceitos:

- **Vendas e pedidos**: pedidos de compra e de venda, propostas comerciais,
  canais de venda, anúncios de marketplace.
- **Produtos e estoque**: cadastro de produtos (com estruturas/composição,
  variações, fornecedores, vínculos com lojas), grupos e categorias de
  produtos, depósitos, controle de lotes e saldos de estoque.
- **Financeiro**: contas a pagar e a receber, caixas e bancos, contas
  contábeis, formas de pagamento, naturezas de operação, borderôs.
- **Fiscal**: emissão e gestão de NF-e (nota fiscal eletrônica), NFC-e (nota
  fiscal de consumidor eletrônica) e NFS-e (nota fiscal de serviço
  eletrônica), incluindo lançamento/estorno de contas e estoque vinculados às
  notas.
- **Logística**: objetos, remessas e serviços de logística/frete, etiquetas
  de postagem.
- **Cadastros auxiliares**: contatos (clientes/fornecedores), vendedores,
  contratos, campos customizados, situações e transições de status,
  notificações, usuários, dados da empresa.

---

## Autenticação

**Tipo:** OAuth 2.0

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | {{host}} |
| Porta | 443 |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Access Token | {{access_token}} |
| Refresh Token | {{refresh_token}} |
| Endpoint de troca de token | {{token_endpoint}} |

- **Host**: `https://api.bling.com.br/Api/v3` (ambiente de produção; o spec
  também lista um ambiente de teste da documentação em
  `https://developer.bling.com.br/api/bling`, não usado nesta configuração).
- **Endpoint de troca de token** (`token_endpoint`): `https://bling.com.br/Api/v3/oauth/token`.
- **URL de autorização** (não é uma variável de conta, mas fica registrada
  aqui para referência do fluxo OAuth): `https://bling.com.br/Api/v3/oauth/authorize`.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Anuncios - Obtém anúncios** | **GET** | Obtém anúncios paginados. |
| **Anuncios - Cria um anúncio** | **POST** | Cria um anúncio. |
| **Anuncios - Obtém categorias de anúncios** | **GET** | Obtém categorias de anúncios. |
| **Anuncios - Obtém uma categoria de anúncio** | **GET** | Obtém uma categoria de anúncio pelo ID. |
| **Anuncios - Obtém um anúncio** | **GET** | Obtém os detalhes de um anúncio específico pelo seu ID. |
| **Anuncios - Altera um anúncio** | **PUT** | Altera um anúncio pelo ID. |
| **Anuncios - Remove um anúncio** | **DELETE** | Remove um anúncio pelo ID. |
| **Anuncios - Pausa um anúncio** | **POST** | Altera o status do anúncio para pausado. |
| **Anuncios - Publica um anúncio** | **POST** | Altera o status do anúncio para publicado. |
| **Borderos - Obtém um borderô** | **GET** | Obtém um borderô pelo ID. |
| **Borderos - Remove um borderô** | **DELETE** | Remove um borderô pelo ID. |
| **Caixas - Obtém lista de lançamentos de caixas e bancos.** | **GET** | Obtém lista de lançamentos de caixas e bancos. |
| **Caixas - Cria um novo lançamento de caixa e banco.** | **POST** | Cria um novo lançamento de caixa e banco com os dados fornecidos. |
| **Caixas - Obtém um lançamento de caixa e banco.** | **GET** | Obtém um lançamento de caixa e banco. |
| **Caixas - Atualiza um lançamento de caixa e banco.** | **PUT** | Atualiza um lançamento de caixa e banco existente com os dados fornecidos. |
| **Caixas - Remove um lançamento de caixa e banco** | **DELETE** | Remove um lançamento de caixa e banco pelo ID. O registro não é excluído permanentemente, apenas marcado como excluído (exclusão lógica). |
| **Campos-Customizados - Cria um campo customizado** | **POST** | Cria um campo customizado. |
| **Campos-Customizados - Obtém módulos que possuem campos customizados** | **GET** | Obtém módulos que possuem campos customizados. |
| **Campos-Customizados - Obtém campos customizados por módulo** | **GET** | Obtém campos customizados por módulo paginados. |
| **Campos-Customizados - Obtém tipos de campos customizados** | **GET** | Obtém tipos de campos customizados. |
| **Campos-Customizados - Obtém um campo customizado** | **GET** | Obtém um campo customizado pelo ID. |
| **Campos-Customizados - Altera um campo customizado** | **PUT** | Altera um campo customizado pelo ID. |
| **Campos-Customizados - Remove um campo customizado** | **DELETE** | Remove um campo customizado pelo ID. |
| **Campos-Customizados - Altera a situação de um campo customizado** | **PATCH** | Altera a situação de um campo customizado pelo ID. |
| **Canais-Venda - Obtém canais de venda** | **GET** | Obtém canais de venda paginados. |
| **Canais-Venda - Obtém os tipos de canais de venda** | **GET** | Obtém os tipos de canais de venda paginados. |
| **Canais-Venda - Obtém um canal de venda** | **GET** | Obtém uma canal de venda pelo ID. |
| **Categorias - Obtém categorias de lojas virtuais vinculadas a de produtos** | **GET** | Obtém categorias de lojas virtuais vinculadas a de produtos paginadas. |
| **Categorias - Cria o vínculo de uma categoria da loja com a de produto** | **POST** | Cria o vínculo de uma categoria da loja com a de produto. |
| **Categorias - Obtém uma categoria da loja vinculada a de produto** | **GET** | Obtém uma categoria da loja vinculada a de produto pelo ID. |
| **Categorias - Altera o vínculo de uma categoria da loja com a de produto** | **PUT** | Altera o vínculo de uma categoria da loja com a de produto pelo ID. |
| **Categorias - Remove o vínculo de uma categoria da loja com a de produto** | **DELETE** | Remove o vínculo de uma categoria da loja com a de produto pelo ID. |
| **Categorias - Obtém categorias de produtos** | **GET** | Obtém categorias de produtos paginadas. |
| **Categorias - Cria uma categoria de produto** | **POST** | Cria uma categoria de produto. |
| **Categorias - Obtém uma categoria de produto** | **GET** | Obtém uma categoria de produto pelo ID. |
| **Categorias - Altera uma categoria de produto** | **PUT** | Altera uma categoria de produto pelo ID. |
| **Categorias - Remove uma categoria de produto** | **DELETE** | Remove uma categoria de produto pelo ID. |
| **Categorias - Obtém categorias de receitas e despesas** | **GET** | Obtém categorias de receitas e despesas paginadas. |
| **Categorias - Cria uma categoria de receita e despesa** | **POST** | Cria uma categoria de receita e despesa. |
| **Categorias - Remove múltiplas categorias de receita e despesa** | **DELETE** | Remove múltiplas categorias de receita e despesa a partir de uma lista de IDs. |
| **Categorias - Obtém uma categoria de receita e despesa** | **GET** | Obtém uma categoria de receita e despesa pelo ID. |
| **Categorias - Atualiza uma categoria de receita e despesa** | **PUT** | Atualiza uma categoria de receita e despesa a partir do ID. |
| **Categorias - Remove uma categoria de receita e despesa** | **DELETE** | Remove uma categoria de receita e despesa pelo ID. |
| **Contas-Contabeis - Obtém contas financeiras** | **GET** | Obtém contas financeiras paginadas. |
| **Contas-Contabeis - Obtém uma conta financeira** | **GET** | Obtém uma conta financeira pelo ID. |
| **Contas - Obtém contas a pagar** | **GET** | Obtém contas a pagar paginadas. |
| **Contas - Cria uma conta a pagar** | **POST** | Cria uma conta a pagar. |
| **Contas - Obtém uma conta a pagar** | **GET** | Obtém uma conta a pagar pelo ID. |
| **Contas - Atualiza uma conta a pagar** | **PUT** | Atualiza uma conta a pagar pelo ID. |
| **Contas - Remove uma conta a pagar** | **DELETE** | Remove uma conta a pagar pelo ID. |
| **Contas - Cria o recebimento de uma conta a pagar** | **POST** | Cria o recebimento de uma conta a pagar. |
| **Contas - Obtém contas a receber** | **GET** | Obtém contas a receber paginadas. |
| **Contas - Cria uma conta a receber** | **POST** | Cria uma conta a receber. |
| **Contas - Obtém boletos de contas a receber** | **GET** | Obtém os boletos vinculados a um idOrigem, o qual corresponde ao ID de uma venda ou nota fiscal. |
| **Contas - Cancela boletos de contas a receber** | **POST** | Cancela um ou todos os boletos em aberto vinculados a uma venda ou nota fiscal. |
| **Contas - Obtém uma conta a receber** | **GET** | Obtém uma conta a receber pelo ID. |
| **Contas - Altera uma conta a receber** | **PUT** | Altera uma conta a receber pelo ID. |
| **Contas - Remove uma conta a receber** | **DELETE** | Remove uma conta a receber pelo ID. |
| **Contas - Cria o recebimento de uma conta a receber** | **POST** | Cria o recebimento de uma conta a receber. |
| **Contatos - Obtém contatos** | **GET** | Obtém contatos paginados. |
| **Contatos - Cria um contato** | **POST** | Cria um contato. |
| **Contatos - Remove múltiplos contatos** | **DELETE** | Remove múltiplos contatos pelos IDs. |
| **Contatos - Obtém os dados do contato Consumidor Final** | **GET** | Obtém os dados do contato Consumidor Final. O consumidor final é um contato padrão do sistema que é criado automaticamente e não pode ser alterado. |
| **Contatos - Altera a situação de múltiplos contatos** | **POST** | Altera a situação de múltiplos contatos pelos IDs. |
| **Contatos - Obtém tipos de contato** | **GET** | Obtém tipos de contato pelo ID. |
| **Contatos - Obtém um contato** | **GET** | Obtém um contato pelo ID. |
| **Contatos - Altera um contato** | **PUT** | Altera um contato pelo ID. |
| **Contatos - Remove um contato** | **DELETE** | Remove um contato pelo ID. |
| **Contatos - Altera a situação de um contato** | **PATCH** | Altera a situação de um contato pelo ID. |
| **Contatos - Obtém os tipos de contato de um contato** | **GET** | Obtém os tipos de contato de um contato pelo ID. |
| **Contratos - Obtém contratos** | **GET** | Obtém contratos paginados. |
| **Contratos - Cria um contrato** | **POST** | Cria um contrato. |
| **Contratos - Obtém um contrato** | **GET** | Obtém um contrato pelo ID. |
| **Contratos - Altera um contrato** | **PUT** | Altera um contrato pelo ID. |
| **Contratos - Remove um contrato** | **DELETE** | Remove um contrato pelo ID. |
| **Depositos - Obtém depósitos** | **GET** | Obtém depósitos paginados. |
| **Depositos - Cria um depósito** | **POST** | Cria um depósito. Até 100 depósitos podem ser criados. |
| **Depositos - Obtém um depósito** | **GET** | Obtém um depósito pelo ID. |
| **Depositos - Altera um depósito** | **PUT** | Altera um depósito pelo ID. |
| **Documentos-Compartilhados - Obtém um documento compartilhado.** | **GET** | Obtém um documento compartilhado pelo token. |
| **Empresas - Obtém dados básicos da empresa** | **GET** | Obtém CNPJ, razão social e e-mail da empresa. |
| **Estoques - Cria um registro de estoque** | **POST** | Cria um registro de estoque. |
| **Estoques - Obtém o saldo em estoque de produtos** | **GET** | Obtém o saldo em estoque de produtos, em todos os depósitos. |
| **Estoques - Obtém o saldo em estoque de produtos por depósito** | **GET** | Obtém o saldo em estoque de produtos pelo ID do depósito. |
| **Estoques - Altera um registro de estoque** | **PUT** | Altera um registro de estoque pelo ID. |
| **Formas-Pagamentos - Obtém formas de pagamentos** | **GET** | Obtém formas de pagamentos paginadas. |
| **Formas-Pagamentos - Cria uma forma de pagamento** | **POST** | Cria uma forma de pagamento. |
| **Formas-Pagamentos - Obtém uma forma de pagamento** | **GET** | Obtém uma forma de pagamento pelo ID. |
| **Formas-Pagamentos - Altera uma forma de pagamento** | **PUT** | Altera uma forma de pagamento pelo ID. |
| **Formas-Pagamentos - Remove uma forma de pagamento** | **DELETE** | Remove uma forma de pagamento pelo ID. |
| **Formas-Pagamentos - Altera o padrão de uma forma de pagamento** | **PATCH** | Altera o padrão de uma forma de pagamento pelo ID. |
| **Formas-Pagamentos - Altera a situação de uma forma de pagamento** | **PATCH** | Altera a situação de uma forma de pagamento pelo ID. |
| **Grupos-Produtos - Obtém grupos de produtos** | **GET** | Obtém grupos de produtos paginados. |
| **Grupos-Produtos - Cria um grupo de produtos** | **POST** | Cria um grupo de produtos. |
| **Grupos-Produtos - Remove múltiplos grupos de produtos** | **DELETE** | Remove múltiplos grupos de produtos pelos IDs. |
| **Grupos-Produtos - Obtém um grupo de produtos** | **GET** | Obtém um grupo de produtos pelo ID. |
| **Grupos-Produtos - Altera um grupo de produtos** | **PUT** | Altera um grupo de produtos pelo ID. |
| **Grupos-Produtos - Remove um grupo de produtos** | **DELETE** | Remove um grupo de produtos pelo ID. |
| **Homologacao - Obtém o produto da homologação** | **GET** | Obtém o produto que será utilizado durante os demais passos da homologação, e inicia o processo de validação, o qual deve ser acompanhado via interface do cadastro de aplicativos. |
| **Homologacao - Cria o produto da homologação** | **POST** | Cria o produto da homologação. |
| **Homologacao - Altera o produto da homologação** | **PUT** | Altera o produto da homologação pelo ID. |
| **Homologacao - Remove o produto da homologação** | **DELETE** | Remove o produto da homologação pelo ID. |
| **Homologacao - Altera a situação do produto da homologação** | **PATCH** | Altera a situação do produto da homologação pelo ID. |
| **Logisticas - Obtém logísticas** | **GET** | Obtém logísticas paginados. |
| **Logisticas - Cria logística** | **POST** | Cria uma logística. |
| **Logisticas - Obtém etiquetas das vendas** | **GET** | Obtém as etiquetas dos pedidos de venda a partir dos ID's dos pedidos. No momento, o filtro está limitado para apenas um ID. |
| **Logisticas - Cria um objeto de logística** | **POST** | Cria um objeto de logística personalizada. |
| **Logisticas - Obtém um objeto de logística** | **GET** | Obtém um objeto de logística pelo ID. |
| **Logisticas - Altera um objeto de logística pelo ID** | **PUT** | Altera dados de um objeto de logística personalizada pelo ID. |
| **Logisticas - Remove um objeto de logística personalizada** | **DELETE** | Remove um objeto de logística personalizada que não esteja em uma PLP. |
| **Logisticas - Cria uma remessa de postagem de uma logística** | **POST** | Cria uma remessa de postagem de uma logística. |
| **Logisticas - Obtém uma remessa de postagem** | **GET** | Obtém uma remessa de postagem pelo ID. |
| **Logisticas - Altera uma remessa de postagem** | **PUT** | Altera uma remessa de postagem pelo ID. |
| **Logisticas - Remove uma remessa de postagem** | **DELETE** | Remove uma remessa de postagem pelo ID. |
| **Logisticas - Obtém serviços de logísticas** | **GET** | Obtém serviços de logísticas paginados. |
| **Logisticas - Cria um serviço de logística** | **POST** | Cria um serviço de logística personalizada. |
| **Logisticas - Obtém um servico de logística** | **GET** | Obtém um servico de logística pelo ID. |
| **Logisticas - Altera um serviço de logística pelo ID** | **PUT** | Altera dados de um serviço de logística personalizada pelo ID. |
| **Logisticas - Desativa ou ativa um serviço de uma logística** | **PATCH** | Desativa ou ativa um serviço de uma logística personalizada pelo ID. |
| **Logisticas - Obtém uma logística** | **GET** | Obtém uma logística pelo ID. |
| **Logisticas - Altera uma logística** | **PUT** | Altera uma logística pelo ID. |
| **Logisticas - Remove uma logística** | **DELETE** | Remove uma logística pelo ID. |
| **Logisticas - Obtém as remessas de postagem de uma logística** | **GET** | Obtém as remessas de postagem de uma logística pelo ID. |
| **Naturezas-Operacoes - Obtém naturezas de operações** | **GET** | Obtém naturezas de operação paginadas. |
| **Naturezas-Operacoes - Obtém regras de tributação da natureza de operação** | **POST** | Obtém regras de tributação que incidem sobre o item, dada uma natureza de operação. |
| **Nfce - Obtém notas fiscais de consumidor** | **GET** | Obtém notas fiscais de consumidor paginadas. |
| **Nfce - Cria uma nota fiscal de consumidor** | **POST** | Cria uma nota fiscal de consumidor. |
| **Nfce - Obtém uma nota fiscal de consumidor** | **GET** | Obtém uma nota fiscal de consumidor pelo ID. |
| **Nfce - Altera uma nota fiscal de consumidor** | **PUT** | Altera uma nota fiscal de consumidor. |
| **Nfce - Envia uma nota de consumidor** | **POST** | Envia uma nota de consumidor pelo ID para emissão na Sefaz. |
| **Nfce - Estorna as contas de uma nota fiscal** | **POST** | Estorna as contas de uma nota fiscal pelo ID. |
| **Nfce - Estorna o estoque de uma nota fiscal** | **POST** | Estorna o estoque de uma nota fiscal pelo ID. |
| **Nfce - Lança as contas de uma nota fiscal** | **POST** | Lança as contas de uma nota fiscal pelo ID. |
| **Nfce - Lança o estoque de uma nota fiscal no depósito padrão** | **POST** | Lança o estoque de uma nota fiscal pelo ID, no depósito padrão. |
| **Nfce - Lança o estoque de uma nota fiscal especificando o depósito** | **POST** | Lança o estoque de uma nota fiscal pelo ID, especificando o ID do depósito. |
| **Nfe - Obtém notas fiscais** | **GET** | Obtém notas fiscais paginadas. |
| **Nfe - Cria uma nota fiscal** | **POST** | Cria uma nota fiscal. |
| **Nfe - Remove múltiplas notas fiscais** | **DELETE** | Remove múltiplas notas fiscais por IDs. |
| **Nfe - Obtém o documento de uma nota fiscal** | **GET** | Obtém o PDF ou XML de uma nota fiscal pela chave de acesso. O formato desejado deve ser informado via query param. |
| **Nfe - Obtém uma nota fiscal** | **GET** | Obtém uma nota fiscal pelo ID. |
| **Nfe - Altera uma nota fiscal** | **PUT** | Altera uma nota fiscal pelo ID. Notas com vínculos possuem restrições de atualização. Notas autorizadas não podem ter dados fiscais alterados: valores, impostos, informações do destinatário e qualquer outro dado transmitido no XML da nota. |
| **Nfe - Envia uma nota fiscal** | **POST** | Envia uma nota fiscal pelo ID para emissão na Sefaz. |
| **Nfe - Estorna as contas de uma nota fiscal** | **POST** | Estorna as contas de uma nota fiscal pelo ID. |
| **Nfe - Estorna o estoque de uma nota fiscal** | **POST** | Estorna o estoque de uma nota fiscal pelo ID. |
| **Nfe - Lança as contas de uma nota fiscal** | **POST** | Lança as contas de uma nota fiscal pelo ID. |
| **Nfe - Lança o estoque de uma nota fiscal no depósito padrão** | **POST** | Lança o estoque de uma nota fiscal pelo ID, no depósito padrão. |
| **Nfe - Lança o estoque de uma nota fiscal especificando o depósito** | **POST** | Lança o estoque de uma nota fiscal pelo ID, especificando o ID do depósito. |
| **Nfse - Obtém notas de serviços** | **GET** | Obtém notas de serviços paginadas. |
| **Nfse - Cria uma nota de serviço** | **POST** | Cria uma nota de serviço. |
| **Nfse - Configurações de nota de serviço** | **GET** | Obtém todas as configurações de nota de serviço. |
| **Nfse - Alterar configurações de nota de serviço** | **PUT** | Cria e altera configurações para emissão de notas de serviço. |
| **Nfse - Obtém uma nota de serviço** | **GET** | Obtém uma nota de serviço pelo ID. |
| **Nfse - Exclui uma nota de serviço** | **DELETE** | Exclui uma nota de serviço pelo ID. |
| **Nfse - Cancela uma nota de serviço** | **POST** | Cancela uma nota de serviço pelo ID. |
| **Nfse - Envia uma nota de serviço** | **POST** | Envia uma nota de serviço pelo ID. |
| **Notificacoes - Obtém todas as notificações de uma empresa em um período** | **GET** | Obtém todas as notificações de uma empresa no período informado. Caso período não seja informado, será considerado o ano atual. |
| **Notificacoes - Obtém a quantidade de notificações de uma empresa em um período** | **GET** | Obtém a quantidade de notificações de uma empresa no período informado. Caso período não seja informado, será considerado o ano atual. |
| **Notificacoes - Marca notificação como lida** | **POST** | Marca a notificação relacionada à empresa como lida. |
| **Ordens-Producao - Obtém ordens de produção** | **GET** | Obtém ordens de produção paginadas. |
| **Ordens-Producao - Cria uma ordem de produção** | **POST** | Cria uma ordem de produção. |
| **Ordens-Producao - Gera ordens de produção sob demanda** | **POST** | Gera ordens de produção sob demanda (abaixo do estoque mínimo). |
| **Ordens-Producao - Obtém uma ordem de produção** | **GET** | Obtém uma ordem de produção pelo ID. |
| **Ordens-Producao - Altera uma ordem de produção** | **PUT** | Altera uma ordem de produção pelo ID. |
| **Ordens-Producao - Remove uma ordem de produção** | **DELETE** | Remove uma ordem de produção pelo ID. |
| **Ordens-Producao - Altera a situação de uma ordem de produção** | **PUT** | Altera a situação de uma ordem de produção pelo ID. |
| **Ordens - Obtém ordens de serviço** | **GET** | Obtém ordens de serviço paginadas. |
| **Ordens - Cria uma ordem de serviço** | **POST** | Cria uma ordem de serviço. |
| **Ordens - Obtém uma ordem de serviço** | **GET** | Obtém uma ordem de serviço pelo ID. |
| **Ordens - Altera uma ordem de serviço** | **PUT** | Altera uma ordem de serviço pelo ID; campos não informados recebem valor padrão. |
| **Ordens - Remove uma ordem de serviço** | **DELETE** | Remove uma ordem de serviço pelo ID. |
| **Ordens - Altera a situação de uma ordem de serviço** | **PATCH** | Altera a situação de uma ordem de serviço pelo ID. |
| **Pedidos - Obtém pedidos de compras** | **GET** | Obtém pedidos de compras paginados. |
| **Pedidos - Cria um pedido de compra** | **POST** | Cria um pedido de compra. |
| **Pedidos - Obtém um pedido de compra** | **GET** | Obtém um pedido de compra pelo ID. |
| **Pedidos - Altera um pedido de compra** | **PUT** | Altera um pedido de compra pelo ID. |
| **Pedidos - Remove um pedido de compra** | **DELETE** | Remove um pedido de compra pelo ID. |
| **Pedidos - Estorna as contas de um pedido de compra** | **POST** | Estorna as contas de um pedido de compra pelo ID. |
| **Pedidos - Estorna o estoque de um pedido de compra** | **POST** | Estorna o estoque de um pedido de compra pelo ID. |
| **Pedidos - Lança as contas de um pedido de compra** | **POST** | Lança as contas de um pedido de compra pelo ID. |
| **Pedidos - Lança o estoque de um pedido de compra** | **POST** | Lança o estoque de um pedido de compra pelo ID. |
| **Pedidos - Altera a situação de um pedido de compra** | **PATCH** | Altera a situação de um pedido de compra pelo ID. |
| **Pedidos - Obtém pedidos de vendas** | **GET** | Obtém pedidos de vendas paginados. |
| **Pedidos - Cria um pedido de venda** | **POST** | Cria um pedido de venda. |
| **Pedidos - Remove pedidos de vendas** | **DELETE** | Remove pedidos de vendas pelos IDs. |
| **Pedidos - Obtém um pedido de venda** | **GET** | Obtém um pedido de venda pelo ID. |
| **Pedidos - Altera um pedido de venda** | **PUT** | Altera um pedido de venda pelo ID. |
| **Pedidos - Remove um pedido de venda** | **DELETE** | Remove um pedido de venda pelo ID. |
| **Pedidos - Estorna as contas de um pedido de venda** | **POST** | Estorna as contas de um pedido de venda pelo ID. |
| **Pedidos - Estorna o estoque de um pedido de venda** | **POST** | Estorna o estoque de um pedido de venda pelo ID. |
| **Pedidos - Gera nota fiscal de consumidor eletrônica a partir do pedido de venda** | **POST** | Gera nota fiscal de consumidor eletrônica a partir do pedido de venda. |
| **Pedidos - Gera nota fiscal eletrônica a partir do pedido de venda** | **POST** | Gera nota fiscal eletrônica a partir do pedido de venda. |
| **Pedidos - Lança as contas de um pedido de venda** | **POST** | Lança as contas de um pedido de venda pelo ID. |
| **Pedidos - Lança o estoque de um pedido de venda no depósito padrão** | **POST** | Lança o estoque de um pedido de venda no depósito padrão. |
| **Pedidos - Lança o estoque de um pedido de venda especificando o depósito** | **POST** | Lança o estoque de um pedido de venda especificando o depósito. |
| **Pedidos - Altera a situação de um pedido de venda** | **PATCH** | Altera a situação de um pedido de venda pelo ID. |
| **Produtos - Obtém produtos** | **GET** | Obtém produtos paginados. |
| **Produtos - Cria um produto** | **POST** | Cria um produto. |
| **Produtos - Remove múltiplos produtos** | **DELETE** | Remove múltiplos produtos pelos IDs. |
| **Produtos - Remove a estrutura de múltiplos produtos** | **DELETE** | Remove a estrutura de múltiplos produtos com composição pelos IDs. |
| **Produtos - Obtém a estrutura de um produto com composição** | **GET** | Obtém a estrutura de um produto com composição pelo ID. |
| **Produtos - Altera a estrutura de um produto com composição** | **PUT** | Altera a estrutura de um produto com composição pelo ID. |
| **Produtos - Adiciona componente(s) a uma estrutura** | **POST** | Adiciona múltiplos componentes a uma estrutura pelo ID. |
| **Produtos - Remove componentes específicos de um produto com composição** | **DELETE** | Remove os componentes de um produto com composição pelos IDs dos componentes. |
| **Produtos - Altera um componente de uma estrutura** | **PATCH** | Altera um componente de uma estrutura pelo ID. |
| **Produtos - Obtém produtos fornecedores** | **GET** | Obtém produtos fornecedores paginados. |
| **Produtos - Cria um produto fornecedor** | **POST** | Cria um produto fornecedor. |
| **Produtos - Obtém um produto fornecedor** | **GET** | Obtém um produto fornecedor pelo ID. |
| **Produtos - Altera um produto fornecedor** | **PUT** | Altera um produto fornecedor pelo ID. |
| **Produtos - Remove um produto fornecedor** | **DELETE** | Remove um produto fornecedor pelo ID. |
| **Produtos - Obtém vínculos de produtos com lojas** | **GET** | Obtém vínculos de produtos com lojas paginados. |
| **Produtos - Cria o vínculo de um produto com uma loja** | **POST** | Cria o vínculo de um produto com uma loja. |
| **Produtos - Obtém um vínculo de produto com loja** | **GET** | Obtém um vínculo de produto com loja pelo ID. |
| **Produtos - Altera o vínculo de um produto com uma loja** | **PUT** | Altera o vínculo de um produto com uma loja pelo ID. |
| **Produtos - Remove o vínculo de um produto com uma loja** | **DELETE** | Remove o vínculo de um produto com uma loja pelo ID. |
| **Produtos - Obtém lotes de produtos** | **GET** | Obtém lotes de produtos paginados. |
| **Produtos - Salva lotes de produtos** | **PUT** | Cria/altera lotes de produtos. |
| **Produtos - Remove lotes de produtos** | **DELETE** | Remove lotes de produtos pelos IDs. |
| **Produtos - Obtém a informação se determinados produtos possuem controle de lote** | **GET** | Obtém a informação se determinados produtos possuem controle de lote. |
| **Produtos - Obtém um lançamento de um lote de produto** | **GET** | Obtém um lançamento de um lote de produto pelo ID do lançamento. |
| **Produtos - Altera a observação de um lançamento de um lote de um produto** | **PATCH** | Altera a observação de um lançamento de um lote de um produto pelo ID do lançamento. |
| **Produtos - Obtém um lote de um produto** | **GET** | Obtém um lote de um produto pelo ID. |
| **Produtos - Altera um lote de um produto** | **PUT** | Altera um lote de um produto pelo ID. |
| **Produtos - Obtém os lançamentos de um lote de produto** | **GET** | Obtém os lançamentos de um lote de produto pelo ID. |
| **Produtos - Cria um lançamento de um lote** | **POST** | Inclui lançamento de um lote. |
| **Produtos - Altera o status de um lote do produto** | **PATCH** | Altera o status de um lote do produto pelo ID. |
| **Produtos - Altera a situação de múltiplos produtos** | **POST** | Altera a situação de múltiplos produtos pelos IDs. |
| **Produtos - Retorna o produto pai com combinações de novas variações** | **POST** | Retorna o produto pai com combinação de novas variações a partir dos atributos sem persistir os dados. |
| **Produtos - Obtém o produto e variações** | **GET** | Obtém o produto e variações pelo ID do produto pai. |
| **Produtos - Altera o nome do atributo nas variações** | **PATCH** | Altera o nome do atributo nas variações de um produto pai. |
| **Produtos - Obtém um produto** | **GET** | Obtém um produto pelo ID. |
| **Produtos - Altera um produto** | **PUT** | Altera um produto pelo ID. |
| **Produtos - Altera parcialmente um produto** | **PATCH** | Altera parcialmente um produto pelo ID. Somente os campos informados terão o valor alterado. |
| **Produtos - Remove um produto** | **DELETE** | Remove um produto pelo ID. |
| **Produtos - Desativa controle de lotes para o produto** | **POST** | Desativa controle de lotes para o produto pelo ID do produto. |
| **Produtos - Obtém os saldos dos lotes de um produto por depósito** | **GET** | Obtém os saldos dos lotes de um produto por depósito. |
| **Produtos - Obtém a soma dos saldos dos lotes de um produto em um depósito** | **GET** | Obtém a soma dos saldos dos lotes de um produto em um depósito. |
| **Produtos - Obtém o saldo total dos lotes de um produto** | **GET** | Obtém o saldo total dos lotes de um produto pelo ID do produto. |
| **Produtos - Obtém o saldo de um lote de produto** | **GET** | Obtém o saldo de um lote de produto. |
| **Produtos - Altera a situação de um produto** | **PATCH** | Altera a situação de um produto pelo ID. |
| **Propostas-Comerciais - Obtém propostas comerciais** | **GET** | Obtém propostas comerciais paginadas. |
| **Propostas-Comerciais - Cria uma proposta comercial** | **POST** | Cria uma proposta comercial. |
| **Propostas-Comerciais - Remove múltiplas propostas comerciais** | **DELETE** | Remove múltiplas propostas comerciais pelos IDs. |
| **Propostas-Comerciais - Obtém uma proposta comercial** | **GET** | Obtém uma proposta comercial pelo ID. |
| **Propostas-Comerciais - Altera uma proposta comercial** | **PUT** | Altera uma proposta comercial pelo ID. |
| **Propostas-Comerciais - Remove uma proposta comercial** | **DELETE** | Remove uma proposta comercial pelo ID. |
| **Propostas-Comerciais - Altera a situação de uma proposta comercial** | **PATCH** | Altera a situação de uma proposta comercial pelo ID. |
| **Situacoes - Cria uma situação** | **POST** | Cria uma situação. |
| **Situacoes - Obtém módulos** | **GET** | Obtém módulos. |
| **Situacoes - Obtém situações de um módulo** | **GET** | Obtém situações de um módulo pelo ID. |
| **Situacoes - Obtém as ações de um módulo** | **GET** | Obtém as ações de um módulo pelo ID. |
| **Situacoes - Obtém as transições de um módulo** | **GET** | Obtém as transições de um módulo pelo ID. |
| **Situacoes - Cria uma transição** | **POST** | Cria uma transição. |
| **Situacoes - Obtém uma transição** | **GET** | Obtém uma transição pelo ID. |
| **Situacoes - Altera uma transição** | **PUT** | Altera uma transição pelo ID. |
| **Situacoes - Remove uma transição** | **DELETE** | Remove uma transição pelo ID. |
| **Situacoes - Obtém uma situação** | **GET** | Obtém uma situação pelo ID. |
| **Situacoes - Altera uma situação** | **PUT** | Altera uma situação pelo ID. |
| **Situacoes - Remove uma situação** | **DELETE** | Remove uma situação pelo ID. |
| **Usuarios - Envia solicitação de recuperação de senha** | **POST** | Envia solicitação de recuperação de senha por e-mail. |
| **Usuarios - Redefine senha do usuário** | **PATCH** | Redefine senha do usuário utilizando token enviado por e-mail. |
| **Usuarios - Valida o hash recebido** | **GET** | Valida o hash recebido por e-mail. |
| **Vendedores - Obtém vendedores** | **GET** | Obtém vendedores paginados. |
| **Vendedores - Obtém um vendedor** | **GET** | Obtém um vendedor pelo ID. |
---

## Documentação oficial

https://developer.bling.com.br/referencia
