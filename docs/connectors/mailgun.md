# Mailgun

## Introdução

Este artigo detalha como configurar, autenticar e integrar a API do **Mailgun** no **Skyone Studio** usando o template de módulo.

## O que é a API do Mailgun?

A API do Mailgun utiliza uma arquitetura **RESTful** para permitir a interação programática com a plataforma de **automação e envio de e-mails (Email Service Provider)**. A comunicação é realizada via protocolo **HTTPS**, com troca de dados padronizada no formato **JSON**.

Se sua intenção é apenas enviar emails usando Mailgun, pode ser vantajoso usar o template **Mailgun (SMTP)**, combinar os dois templates é provavelmente o formato ideal, mas observe que eles possuem credenciais separadas que serão abordadas posteriormente.

**Principais capacidades:**

**Envio de E-mails:** Envio de mensagens transacionais e de marketing com suporte a templates e formato MIME.
**Gerenciamento de Listas:** Controle completo sobre listas de mailing, membros e uploads em lote via CSV ou JSON.
**Monitoramento de Entregabilidade:** Gestão de bounces, reclamações (complaints), desinscrições (unsubscribes) e tabelas de permissão (allowlists).
**Analytics e Logs:** Acesso a estatísticas detalhadas por dispositivo, país e provedor, além de logs de eventos em tempo real.

## Conceitos Fundamentais

A estrutura do Mailgun baseia-se nos seguintes pilares:

### Estrutura de Dados e Hierarquia

Para manipular dados com sucesso, é fundamental compreender a hierarquia:

**Domain (Domínio)**: É a entidade central. Todas as credenciais, estatísticas, webhooks e configurações de rastreamento estão vinculadas a um domínio específico.
**Mailing List**: Um grupo de membros associado a um endereço de e-mail próprio que funciona como um identificador para comunicações em massa.
**Subaccounts**: Contas vinculadas à conta principal que permitem isolar o tráfego e os limites de envio para diferentes clientes ou projetos.

---

## Pré-requisitos e Configuração no Mailgun

Para iniciar o desenvolvimento, são necessários:

**Conta ativa** no Mailgun.

**API Key / Credentials**: Obtida no dashboard da plataforma.

### Tipos de Autenticação suportados

A API suporta: **Basic Authentication** (utilizando a API Key) ou o login de SMTP (para Mailgun SMTP).

### Obtendo as credenciais

Para integrar a plataforma ao Mailgun, siga os passos abaixo para obter os diferentes tipos de identificadores e chaves:

1. Crie uma conta no Mailgun e siga o **Get Started Guide** na tela inicial.
2. Resgate um dos tipos de tokens
#### Tipos de Chaves e Tokens

Para integrar a plataforma ao Mailgun, utilize a chave de API adequada ao escopo da sua operação, veja mais informações na [documentação oficial](https://documentation.mailgun.com/docs/mailgun/user-manual/api-key-mgmt/rbac-mgmt).

#### SMTP

1. No dashboard do Mailgun, acesse **Domain Settings** na aba lateral e depois **SMTP Credentials** nesta seção.
2. Clique em **Add new user** e escolha entre criar uma senha ou gerar ela automaticamente (o segundo é o método recomendado)
3. Guarde o login e senha que irão aparecer

---

## Configuração da conta no Skyone Studio

1. No template do conector, clique em **Conta conectada** e em **Adicionar conta conectada**
2. Preencha da seguinte forma:

### Conectividade REST

| Nome da conta | [Escolha um nome identificável] |
| ------------- | ------------------------------- |
| **Host**      | https://api.mailgun.net         |
| **Porta**     | 443                             |
| **Usuário**   | api                             |
| **Senha**     | [Insira seu token]              |

### Conectividade SMTP

| Nome da conta | [Escolha um nome identificável]                                                                               |
| ------------- | ------------------------------------------------------------------------------------------------------------- |
| **Host**      | smtp.mailgun.org                                                                                              |
| **Porta**     | [Entenda qual porta usar](https://www.mailgun.com/blog/email/which-smtp-port-understanding-ports-25-465-587/) |
| **Login**     | [Seu login do SMTP User]                                                                                      |
| **Password**  | [Sua password do SMTP User]                                                                                   |

---
## Operações Disponíveis

Abaixo listamos as operações mapeadas neste conector.

| Nome da Operação                                | Método HTTP | Descrição da Função                                                 |
| :---------------------------------------------- | :---------- | :------------------------------------------------------------------ |
| **Mailing Lists-Delete a member**               | DELETE      | Exclui um assinante de uma lista de e‑mail.                         |
| **Routes-Update a route**                       | PUT         | Atualiza rota, alterando apenas os campos informados.               |
| **Routes-Delete a route**                       | DELETE      | Remove uma rota da conta.                                           |
| **Routes-Match address to route**               | GET         | Verifica se um endereço corresponde a pelo menos uma rota.          |
| **Mailing Lists-Create a mailing list**         | POST        | Adiciona uma lista de emails à conta.                               |
| **Mailing Lists-Get mailing lists**             | GET         | Lista os grupos de membros com endereços próprios.                  |
| **Mailing Lists-Get mailing lists members**     | GET         | Exibe os membros de uma lista de correio específica.                |
| **Mailing Lists-Create a mailing list member**  | POST        | Inclui um novo membro na lista de emails.                           |
| **Mailing Lists-Bulk upload members (JSON)**    | POST        | Adiciona até 1000 membros em lote via JSON.                         |
| **Mailing Lists-Bulk upload members (CSV)**     | POST        | Adiciona até 1000 membros em lote via arquivo CSV.                  |
| **Mailing Lists-Get a member**                  | GET         | Obtém detalhes de um membro específico da lista.                    |
| **Mailing Lists-Update a mailing list member**  | PUT         | Atualiza um membro de mailing list com as propriedades indicadas.   |
| **Routes-Get a route**                          | GET         | Retorna visualização detalhada da rota.                             |
| **Mailing Lists-Update a mailing list**         | PUT         | Atualiza os campos de uma lista de e-mails (endereço, nome, etc).   |
| **Mailing Lists-Delete a mailing list**         | DELETE      | Exclui uma lista de distribuição.                                   |
| **Mailing Lists-Get a mailing list by address** | GET         | Retorna a lista de correio que corresponde ao endereço informado.   |
| **Mailing Lists-Get mailing lists by page**     | GET         | Paginador de listas de mailing.                                     |
| **Mailing Lists-Get members by page**           | GET         | Listar membros de uma lista com paginação ascendente.               |
| **Templates-Get templates**                     | GET         | Retorna a lista de templates disponíveis para o domínio.            |
| **Templates-Create a template**                 | POST        | Armazena um novo template com nome e descrição.                     |
| **Templates-Delete all templates**              | DELETE      | Remove todos os templates e suas versões no domínio.                |
| **Templates-Get all template versions**         | GET         | Lista paginada de todas as versões de template.                     |
| **Templates-Create a template version**         | POST        | Adiciona nova versão a um template existente.                       |
| **Templates-Get template**                      | GET         | Retorna metadados do template especificado.                         |
| **Bounces-Clear a single bounce**               | DELETE      | Remove um registro de bounce para retomar entregas.                 |
| **Unsubscribe-View all unsubscribes**           | GET         | Pagina a lista de cancelamentos de inscrição de um domínio.         |
| **Unsubscribe-Insert records**                  | POST        | Envia registros de cancelamento via JSON ou form-data.              |
| **Unsubscribe-Delete entire list**              | DELETE      | Limpa a lista completa de e-mails cancelados do domínio.            |
| **Complaints-Import list**                      | POST        | Importa arquivo CSV para a lista de reclamações.                    |
| **Complaints-View a single record**             | GET         | Verifica se um endereço está na lista de queixas.                   |
| **Complaints-Clear a single event**             | DELETE      | Reinicia entregas para um endereço que reclamou anteriormente.      |
| **Complaints-View all**                         | GET         | Listagem paginada de reclamações do domínio.                        |
| **Complaints-Insert records**                   | POST        | Envia registros de reclamações em lote.                             |
| **Complaints-Delete entire list**               | DELETE      | Remove todas as reclamações do domínio.                             |
| **Bounces-Import list**                         | POST        | Importar lista de bounces via arquivo CSV.                          |
| **Bounces-View single event**                   | GET         | Obtém o evento de bounce para um e-mail específico.                 |
| **Templates-Update template**                   | PUT         | Atualizar a descrição de um template.                               |
| **Bounces-View all bounces**                    | GET         | Exibe e pagina a lista de retornos de e-mails.                      |
| **Bounces-Insert records**                      | POST        | Envia registros de rejeição em lote.                                |
| **Bounces-Delete entire list**                  | DELETE      | Limpa a lista de bounce permitindo futuras entregas.                |
| **Allowlist-Import list**                       | POST        | Importa CSV de endereços ou domínios autorizados.                   |
| **Allowlist-View a single record**              | GET         | Recupera um registro para validar permissão.                        |
| **Allowlist-Remove a record**                   | DELETE      | Remove um registro da lista de permissões.                          |
| **Allowlist-View all records**                  | GET         | Exibe registros de allowlist do domínio divididos em páginas.       |
| **Allowlist-Add a single record**               | POST        | Adiciona um endereço ou domínio à tabela de permissões.             |
| **Allowlist-Clear domains allowlist**           | DELETE      | Exclui a lista de permissões completa de um domínio.                |
| **Routes-Create a route**                       | POST        | Adiciona uma nova rota à conta.                                     |
| **Routes-Get all routes**                       | GET         | Lista todas as rotas definidas globalmente na conta.                |
| **Credentials-Delete all SMTP credentials**     | DELETE      | Apaga todas as credenciais SMTP de um domínio.                      |
| **Subaccounts-Enable a subaccount**             | POST        | Habilita uma subconta.                                              |
| **Subaccounts-Get current sending limit**       | GET         | Obtém detalhes do limite de envio personalizado da subconta.        |
| **Subaccounts-Set custom sending limit**        | PUT         | Define um limite personalizado de envio para mensagens.             |
| **Subaccounts-Delete custom sending limit**     | DELETE      | Exclui o limite personalizado de envio.                             |
| **Subaccounts-Update subaccount feature**       | PUT         | Atualiza recursos específicos de uma subconta.                      |
| **Keys-List Mailgun API keys**                  | GET         | Listar chaves da API Mailgun.                                       |
| **Keys-Create Mailgun API key**                 | POST        | Cria uma nova chave de API (domain, user ou web).                   |
| **Keys-Delete Mailgun API key**                 | DELETE      | Remove uma chave da API Mailgun.                                    |
| **Keys-Regenerate Public API key**              | POST        | Regenera a chave pública da API.                                    |
| **Credentials-List SMTP metadata**              | GET         | Lista metadados das credenciais SMTP de um domínio.                 |
| **Credentials-Create SMTP credentials**         | POST        | Cria credenciais SMTP para o domínio especificado.                  |
| **Subaccounts-Disable a subaccount**            | POST        | Desabilita uma subconta informando o motivo.                        |
| **Credentials-Update SMTP credentials**         | PUT         | Atualiza a senha de uma credencial SMTP específica.                 |
| **Credentials-Delete SMTP credentials**         | DELETE      | Exclui uma credencial SMTP específica de um usuário.                |
| **IP Allowlist-List entries**                   | GET         | Exibir entradas da lista de IPs autorizados da conta.               |
| **IP Allowlist-Update description**             | PUT         | Atualiza a descrição de uma entrada na allowlist de IP.             |
| **IP Allowlist-Add entry**                      | POST        | Adiciona um IP à lista de permissões da conta.                      |
| **IP Allowlist-Delete entry**                   | DELETE      | Exclui uma entrada da lista de IPs autorizados.                     |
| **Users-Get users**                             | GET         | Retorna os usuários de uma conta filtrados por cargo.               |
| **Users-Get details**                           | GET         | Recupera os dados completos de um usuário.                          |
| **Users-Get own details**                       | GET         | Obtém detalhes do usuário autenticado (exige chave 'user').         |
| **Users-Add to organization**                   | PUT         | Adiciona um usuário a uma organização.                              |
| **Users-Remove from organization**              | DELETE      | Remove um usuário de uma organização.                               |
| **Account Management-Resend activation**        | POST        | Reenvia o e-mail de ativação ao proprietário da conta.              |
| **Templates-Delete a template**                 | DELETE      | Exclui um template e todas as suas versões.                         |
| **Templates-Get a version**                     | GET         | Recupera conteúdo de uma versão específica de um template.          |
| **Templates-Update a version**                  | PUT         | Atualiza informações ou conteúdo de uma versão específica.          |
| **Templates-Delete a version**                  | DELETE      | Exclui uma versão específica de um template.                        |
| **Templates-Copy a version**                    | PUT         | Cria uma nova versão copiando uma existente.                        |
| **Account Management-Update settings**          | PUT         | Atualiza configurações variáveis (timeouts, URLs de logout).        |
| **Account Management-Get webhook key**          | GET         | Recupera a chave de assinatura de webhook da conta.                 |
| **Account Management-Regenerate webhook key**   | POST        | Cria ou regenera a chave de assinatura de webhook.                  |
| **Account Management-Get sandbox recipients**   | GET         | Lista destinatários autorizados de um domínio sandbox.              |
| **Account Management-Add sandbox recipient**    | POST        | Adiciona destinatário autorizado a um domínio sandbox.              |
| **Account Management-Remove sandbox recipient** | DELETE      | Remove destinatário autorizado de um domínio sandbox.               |
| **Unsubscribe-Clear event**                     | DELETE      | Remove evento de desinscrição para retomar envios.                  |
| **Account Management-Get SAML Org ID**          | GET         | Retorna o ID da organização SAML da conta.                          |
| **Account Management-Add SAML Org**             | POST        | Adiciona uma organização SAML à conta.                              |
| **Custom Message Limit-Get current**            | GET         | Obtém detalhes do limite de envio personalizado da conta.           |
| **Custom Message Limit-Set**                    | PUT         | Define limite de envio personalizado para a conta.                  |
| **Custom Message Limit-Delete**                 | DELETE      | Exclui limite de envio personalizado da conta.                      |
| **Custom Message Limit-Re-enable account**      | PUT         | Reativa conta bloqueada por atingir limite de envio.                |
| **Subaccounts-Get single**                      | GET         | Recuperar detalhes de uma subconta específica.                      |
| **Subaccounts-List all**                        | GET         | Recupera todas as subcontas da conta principal.                     |
| **Subaccounts-Create**                          | POST        | Cria uma nova subconta.                                             |
| **Subaccounts-Delete**                          | DELETE      | Exclui uma subconta.                                                |
| **IPs-Get domains by IP**                       | GET         | Lista domínios onde um IP específico está atribuído.                |
| **Domain Keys-Update DKIM selector**            | PUT         | Atualiza o seletor DKIM de um domínio.                              |
| **DKIM Security-Update rotation**               | PUT         | Atualiza a rotação automática da chave DKIM.                        |
| **DKIM Security-Rotate now**                    | POST        | Roda a chave DKIM imediatamente.                                    |
| **Webhooks-Get domain webhooks**                | GET         | Retorna todos os webhooks configurados no domínio.                  |
| **Webhooks-Create**                             | POST        | Cria URLs de webhook para receber dados de eventos.                 |
| **Webhooks-Get by type**                        | GET         | Recupera as URLs de um webhook específico pelo nome.                |
| **Webhooks-Update**                             | PUT         | Atualiza a URL de um webhook existente.                             |
| **Webhooks-Delete by type**                     | DELETE      | Remove todas as URLs de um tipo específico de webhook.              |
| **IPs-Remove from domain pool**                 | DELETE      | Remove um IP ou desvincula DIPP de um domínio.                      |
| **IPs-List account IPs**                        | GET         | Lista IPs atribuíveis e totais segundo filtros.                     |
| **IPs-Get details**                             | GET         | Retorna informações detalhadas sobre um IP da conta.                |
| **Domain Keys-Update authority**                | PUT         | Delega a autoridade do domínio para outro domínio.                  |
| **IPs-Assign to all domains**                   | POST        | Atribui um IP da conta a todos os seus domínios.                    |
| **IPs-Remove from all domains**                 | DELETE      | Remove um IP de todos os domínios da conta.                         |
| **IPs-Place into IP band**                      | POST        | Aloca um IP dedicado em uma faixa específica.                       |
| **IPs-Get available by plan**                   | GET         | Retorna IPs disponíveis conforme o plano de faturamento.            |
| **IPs-Add new dedicated**                       | POST        | Adiciona um novo IP dedicado à conta.                               |
| **IP Pools-List pools**                         | GET         | Lista todos os pools de IP dedicados da conta.                      |
| **IP Pools-Add DIPP**                           | POST        | Cria um novo pool de IP dedicado (DIPP).                            |
| **IP Pools-Get details**                        | GET         | Verifica vínculos de domínios em um DIPP.                           |
| **IP Pools-Delete DIPP**                        | DELETE      | Apaga um DIPP e gerencia a substituição de IPs.                     |
| **IP Pools-Edit DIPP**                          | PATCH       | Adiciona/remove IPs ou vincula/desvincula domínios.                 |
| **Domain Tracking-Update click**                | PUT         | Habilita ou desabilita o rastreamento de cliques.                   |
| **Messages-Send MIME**                          | POST        | Envia um e-mail a partir de uma string no formato MIME.             |
| **Messages-Retrieve stored**                    | GET         | Recupera um e-mail guardado via storage key.                        |
| **Messages-Queue status**                       | GET         | Fornece informações das filas padrão e agendadas.                   |
| **Messages-Delete scheduled**                   | DELETE      | Remove e-mails agendados que ainda não foram entregues.             |
| **Domains-Get domains**                         | GET         | Recupera e filtra a lista de domínios da conta.                     |
| **Domains-Create**                              | POST        | Cria um novo domínio para envio de e-mails.                         |
| **Domains-Get details**                         | GET         | Recupera o estado e configurações detalhadas de um domínio.         |
| **Domains-Update**                              | PUT         | Atualiza parâmetros de segurança, rastreamento e spam.              |
| **Domains-Verify**                              | PUT         | Verifica os registros DNS para validar o domínio.                   |
| **Domains-Delete**                              | DELETE      | Apaga um domínio da conta.                                          |
| **Domain Tracking-Get settings**                | GET         | Verifica status de abertura, clique e cancelamento.                 |
| **IP Pools-Get linked domains**                 | GET         | Exibe domínios vinculados a um pool específico.                     |
| **Domain Tracking-Update open**                 | PUT         | Ativa ou desativa o rastreamento de abertura.                       |
| **Domain Tracking-Update unsubscribe**          | PUT         | Gerencia o rastreamento de desinscrição e rodapés.                  |
| **Tracking Certificate-Get status**             | GET         | Obtém o certificado x509 e seu estado atual.                        |
| **Tracking Certificate-Regenerate**             | PUT         | Inicia a regeneração de certificado expirado.                       |
| **Tracking Certificate-Generate**               | POST        | Inicia a geração de novo certificado TLS.                           |
| **Domain Keys-List all**                        | GET         | Lista chaves de todos os domínios com filtros.                      |
| **Domain Keys-Create**                          | POST        | Cria uma chave de domínio importando ou gerando PEM.                |
| **Domain Keys-Delete**                          | DELETE      | Remove uma chave de domínio permanentemente.                        |
| **Domain Keys-Activate**                        | PUT         | Ativa uma chave DKIM específica para assinatura.                    |
| **Domain Keys-List domain keys**                | GET         | Exibe todas as chaves (ativas/inativas) de um domínio.              |
| **Domain Keys-Deactivate**                      | PUT         | Desativa uma chave de domínio para assinaturas.                     |
| **Tags-Delete tag**                             | DELETE      | Excluir tag associada a um domínio.                                 |
| **Logs-List logs**                              | POST        | Exibe logs de eventos da conta.                                     |
| **Stats-Total account**                         | GET         | Obtém totais estatísticos de toda a conta.                          |
| **Stats-Total domain**                          | GET         | Obtém totais estatísticos para um domínio específico.               |
| **Stats-Resolution totals**                     | GET         | Totais de domínios para uma única resolução de tempo.               |
| **Stats-Filtered account**                      | GET         | Totais filtrados e agrupados para a conta inteira.                  |
| **Stats-Aggregate by ESP**                      | GET         | Contagem agregada por provedor de serviço (ESP).                    |
| **Stats-Aggregate by device**                   | GET         | Contagem agregada por tipo de dispositivo.                          |
| **Stats-Aggregate by country**                  | GET         | Contagem agregada por país.                                         |
| **Tags-List all**                               | GET         | Listar todas as tags associadas a um domínio.                       |
| **Tags-Get a tag**                              | GET         | Recuperar metadados de uma tag específica.                          |
| **Tags-Update tag**                             | PUT         | Atualiza a descrição de uma tag.                                    |
| **Events-Retrieve list**                        | GET         | Recupera lista paginada de eventos de mensagens.                    |
| **Tags-Get aggregate types**                    | GET         | Tipos estatísticos agregados por tag (país, disp, etc).             |
| **Tags-Get stats**                              | GET         | Recupera estatísticas detalhadas agrupadas por tag.                 |
| **Tags-Get limits**                             | GET         | Obtém limites de tags por domínio.                                  |
| **Tags V2-Update account tag**                  | PUT         | Atualiza a descrição da tag no nível da conta.                      |
| **Tags V2-Search/List**                         | POST        | Lista ou busca tags da conta via query.                             |
| **Tags V2-Delete**                              | DELETE      | Deleta uma tag do nível da conta.                                   |
| **Tags V2-Get limit info**                      | GET         | Obtém limites e contagem de tags únicas da conta.                   |
| **Metrics-Account metrics**                     | POST        | Recupera métricas filtradas de uma conta.                           |
| **Metrics-Usage metrics**                       | POST        | Obtém métricas de uso (billing) para a conta.                       |
| **Unsubscribe-Import list**                     | POST        | Importa arquivo CSV para a lista de desinscrição.                   |
| **Unsubscribe-View single**                     | GET         | Verifica se um endereço está desinscrito.                           |
| **Dynamic IP Pools-Update IPs**                 | PATCH       | Adiciona ou remove IPs de um pool dinâmico.                         |
| **IP Pools-Add IP to DIPP**                     | PUT         | Vincula IP dedicado a um pool específico.                           |
| **IP Pools-Remove IP from DIPP**                | DELETE      | Desvincula IP de um pool específico.                                |
| **IP Pools-Add multiple IPs**                   | POST        | Adiciona múltiplos IPs a um DIPP de forma assíncrona.               |
| **Dynamic IP Pools-Enroll domain**              | POST        | Registra domínio no pool dinâmico conforme reputação.               |
| **Dynamic IP Pools-Remove domain**              | DELETE      | Remove domínio do pool e define IP de substituição.                 |
| **Dynamic IP Pools-List assignable**            | GET         | Lista domínios aptos a entrar em pools dinâmicos.                   |
| **Dynamic IP Pools-Enroll all**                 | POST        | Vincula todos os domínios da conta aos pools dinâmicos.             |
| **Dynamic IP Pools-List all**                   | GET         | Exibe a lista de IPs de cada pool dinâmico.                         |
| **Dynamic IP Pools-Initialize/Set**             | POST        | Substitui IPs em todos os pools dinâmicos.                          |
| **Dynamic IP Pools-Remove all**                 | DELETE      | Remove todos os pools dinâmicos da conta.                           |
| **Dynamic IP Pools-Add IP**                     | POST        | Adiciona um IP a um pool dinâmico nomeado.                          |
| **Messages-Send**                               | POST        | Envia e-mail via parâmetros estruturados (to, from, subject, body). |
| **Dynamic IP Pools-List assigned**              | GET         | Lista domínios atribuídos a pools dinâmicos (pai e subs).           |
| **Dynamic IP Pools-Preview**                    | GET         | Verifica saúde e antecipa qual pool seria atribuído.                |
| **Dynamic IP Pools-List history**               | GET         | Obtém registros históricos de um domínio nos pools.                 |
| **Dynamic IP Pools-Override**                   | PUT         | Sobrepõe alocação manual de pool IP.                                |
| **Dynamic IP Pools-Remove override**            | DELETE      | Devolve a atribuição do pool aos health checks.                     |
| **Dynamic IP Pools-Account history**            | GET         | Histórico completo de domínios em pools (pai e subs).               |
| **IP Warmup-List statuses**                     | GET         | Lista status de aquecimento de IPs em processamento.                |
| **IP Warmup-Get status**                        | GET         | Verifica status de aquecimento de um IP específico.                 |
| **IP Warmup-Create plan**                       | POST        | Cria um plano de aquecimento para um IP dedicado.                   |
| **IP Warmup-Cancel plan**                       | DELETE      | Cancela o plano de aquecimento de um IP dedicado.                   |

> Mailgun (SMTP) tem uma única operação que serve de uso flexível, você pode criar seus próprios templates de emails. Lembre-se de usar **HTML** no body.

---

## Exemplo de Fluxo utilizando o Mailgun

Este exemplo demonstra como construir um fluxo básico usando o conector do Mailgun, recebendo dados de cadastro em um webhook e enviando um email de boas vindas.

![fluxo.png](../img/mailgun/fluxo.png)

**Documentação Oficial da API:** [Mailgun API Reference](https://documentation.mailgun.com/docs/mailgun/api-reference/)