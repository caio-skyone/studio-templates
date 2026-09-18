# Twilio

## Introdução

Este artigo detalha como configurar, autenticar e integrar as APIs do **Twilio** no **Skyone Studio**. A cobertura do Twilio está dividida em **quatro templates de conector**, um por produto.

| Template | Host da conta conectada | Operações | O que cobre |
| :------- | :---------------------- | --------: | :---------- |
| **Twilio API** | `https://api.twilio.com` | 197 | API principal (`2010-04-01`): mensagens SMS/MMS/WhatsApp, chamadas de voz, conferências, gravações, transcrições, números de telefone, filas, SIP, chaves, uso e saldo |
| **Twilio Messaging** | `https://messaging.twilio.com` | 58 | Messaging Services, remetentes alfanuméricos, short codes, encurtamento de link, registro A2P/brand e verificação toll-free |
| **Twilio Verify** | `https://verify.twilio.com` | 57 | Verificação de identidade e 2FA: verificações por SMS/voz/e-mail, factors, challenges, passkeys, rate limits e templates |
| **Twilio Lookups** | `https://lookups.twilio.com` | 10 | Validação e enriquecimento de números: line type, operadora, risco de fraude, consulta em lote |

Os quatro templates usam a mesma autenticação, porém o Host dos serviços são diferentes, portanto exigem credenciais diferentes.

## O que é a API do Twilio?

O Twilio é uma plataforma de comunicação em nuvem que expõe suas capacidades por meio de APIs **RESTful** sobre HTTPS. Por meio delas é possível enviar e receber mensagens, originar e controlar chamadas de voz, provisionar e gerenciar números de telefone, verificar identidades e consultar dados de telefonia — tudo programaticamente, sem infraestrutura de telecom própria.

**Principais capacidades:**

**Mensagens:** envio e consulta de SMS, MMS e mensagens de WhatsApp, com feedback de entrega, mídia anexada e agrupamento por Messaging Service.
**Voz:** criação e controle de chamadas em tempo real, conferências, filas de espera, gravações, transcrições e streams de áudio.
**Números:** busca de números disponíveis por país e tipo (local, móvel, toll-free, VoIP), compra, configuração de webhooks e liberação.
**Verificação:** fluxos de OTP e 2FA por SMS, voz, e-mail, TOTP e passkeys, com controle de tentativas e rate limits.
**Inteligência de números:** validação de formato, identificação de operadora e tipo de linha, checagem de portabilidade e sinais de risco.
**Administração:** subcontas, chaves de API, chaves de assinatura, registros de uso, gatilhos de cobrança e saldo.

## Conceitos Fundamentais

### SID — o identificador universal

Praticamente todo recurso do Twilio é identificado por um **SID**: uma string de 34 caracteres cujo prefixo indica o tipo (`AC` conta, `SM` mensagem, `CA` chamada, `MG` Messaging Service, `VA` Verify Service, `RE` gravação). Nas operações, os SIDs aparecem como parâmetros de path (`account_sid`, `call_sid`, `service_sid`, `sid`).

### Conta e subcontas

O **Account SID** identifica a conta e é, ao mesmo tempo, o usuário da autenticação e um segmento do caminho da maioria das operações da API principal. Subcontas permitem isolar tráfego, números e cobrança por cliente ou projeto — por isso o `account_sid` é um parâmetro de operação, e não um valor fixo da conta conectada: a mesma credencial pode operar sobre subcontas diferentes.

### Um produto, um subdomínio, uma versão

O Twilio não versiona a plataforma inteira de uma vez. Cada produto tem seu próprio host e sua própria versão, embutidos no caminho: `api.twilio.com/2010-04-01/…`, `messaging.twilio.com/v1/…`, `verify.twilio.com/v2/…`, `lookups.twilio.com/v2/…`. Versões diferentes do mesmo produto quase nunca expõem as mesmas rotas — um "v2" costuma ser um produto novo, não uma casca nova sobre o "v1". Por isso a versão entra **literal no caminho de cada operação**, e não como parâmetro configurável.

### Messaging Service e Verify Service

Tanto o Messaging quanto o Verify organizam a configuração em um **Service**: um agrupador que carrega pool de números, regras de envio, webhooks e políticas. Na prática, a maioria das operações desses dois templates recebe um `service_sid` (ou `messaging_service_sid`) como primeiro parâmetro.

### TwiML

Operações de voz que iniciam ou redirecionam uma chamada esperam uma **URL** que devolva **TwiML** — o XML que instrui o Twilio sobre o que fazer na chamada (falar, tocar áudio, discar, gravar). O conector envia a URL; o conteúdo TwiML fica hospedado no seu lado.

---

## Pré-requisitos e Configuração no Twilio

Para iniciar o desenvolvimento, são necessários:

**Conta ativa** no Twilio.

**Credenciais** (Account SID + Auth Token, ou API Key SID + Secret) obtidas no console.

### Tipos de Autenticação suportados

Os quatro templates usam **Basic Authentication (HTTP Basic)**.

**Tipo:** Autenticação básica (HTTP Basic)

| Variável | Valor                     |
| -------- | ------------------------- |
| password | Auth Token/API Key Secret |
| username | Account SID/API Key SID   |

### Obtendo as credenciais

Existem três tipos diferentes de credenciais do Twilio: credenciais de conta, credenciais de conta de teste e credenciais de API Key. A recomendação é usar API Keys para controle das permissões — observe que certas operações podem não funcionar a depender das permissões escolhidas.

> [Saiba mais sobre credenciais](https://www.twilio.com/docs/iam/credentials/api)

É possível usar os dados da conta (**Account SID** e **Auth Token**) como, respectivamente, usuário e senha na autenticação do Skyone Studio, permitindo utilizar qualquer operação da API que a conta tenha acesso. Em **Go to API Keys**, você terá acesso ao painel de criação de API Keys e às credenciais de teste.

---

## Configuração da conta no Skyone Studio

1. No template do conector, clique em **Credencial** e em **Adicionar credencial**.
2. Preencha conforme o template — o **Host muda de um template para o outro**, o resto é idêntico.

### Twilio API

| Nome da conta | [Escolha um nome identificável]   |
| ------------- | --------------------------------- |
| **Host**      | https://api.twilio.com            |
| **Porta**     | 443                               |
| **Usuário**   | [Account SID ou API Key SID]      |
| **Senha**     | [Auth Token ou API Key Secret]    |

### Twilio Messaging

| Nome da conta | [Escolha um nome identificável]   |
| ------------- | --------------------------------- |
| **Host**      | https://messaging.twilio.com      |
| **Porta**     | 443                               |
| **Usuário**   | [Account SID ou API Key SID]      |
| **Senha**     | [Auth Token ou API Key Secret]    |

### Twilio Verify

| Nome da conta | [Escolha um nome identificável]   |
| ------------- | --------------------------------- |
| **Host**      | https://verify.twilio.com         |
| **Porta**     | 443                               |
| **Usuário**   | [Account SID ou API Key SID]      |
| **Senha**     | [Auth Token ou API Key Secret]    |

### Twilio Lookups

| Nome da conta | [Escolha um nome identificável]   |
| ------------- | --------------------------------- |
| **Host**      | https://lookups.twilio.com        |
| **Porta**     | 443                               |
| **Usuário**   | [Account SID ou API Key SID]      |
| **Senha**     | [Auth Token ou API Key Secret]    |

---

## Como preencher os parâmetros

### Corpo da requisição

O Twilio **não aceita JSON** no corpo das operações da API principal, do Messaging e da maior parte do Verify: o corpo vai em **`application/x-www-form-urlencoded`**, ou seja, pares `chave=valor` separados por `&`, com os valores percent-encoded. Os templates já enviam o cabeçalho `Content-Type` correto; ao configurar a operação, escreva o parâmetro `body` nesse formato.

Exemplo, em **Twilio API → `Messages - Create message`**:

```
To=%2B5511999999999&From=%2B5511888888888&Body=Mensagem+de+teste+do+Studio
```

As únicas exceções são as operações de **Passkeys** do Verify e as de **Overrides**/**batch** do Lookups, que usam JSON — nessas, o parâmetro `body` é um objeto.

Cada operação traz no `sample` do parâmetro `body` um exemplo com os campos obrigatórios daquele endpoint. Campos opcionais não estão no exemplo: consulte a documentação oficial da operação e acrescente-os na mesma sintaxe.

### Paginação

As operações de listagem aceitam `PageSize` (padrão 50, máximo 1000), `Page` e `PageToken`. Para percorrer páginas, use o `PageToken` devolvido na resposta em vez de incrementar `Page`.

### Filtros por data

Alguns filtros de data existem em três variantes: valor exato, "antes de" e "depois de". No Twilio, as duas últimas são as chaves `DateCreated<` e `DateCreated>`; nos templates elas aparecem como os parâmetros `date_created_before` e `date_created_after` (e equivalentes para `start_time`, `end_time`, `date_sent` e `message_date`). A chave enviada continua sendo a original com `<` ou `>`.

### Sufixo `.json`

Todos os caminhos da API principal terminam em `.json` — é assim que o Twilio seleciona a resposta em JSON em vez de XML. Os templates já embutem esse sufixo; não o remova ao editar uma operação.

---

## Operações Disponíveis

Abaixo listamos as operações mapeadas em cada template.

### Twilio API — 197 operações

| Nome da Operação | Método HTTP | Descrição da Função |
| :--------------- | :---------- | :------------------ |
| **Accounts - List account** | GET | Recupera uma coleção de contas pertencentes à conta usada para fazer a solicitação. |
| **Accounts - Create account** | POST | Cria uma nova subconta Twilio a partir da conta fazendo a solicitação. |
| **Addresses - List address** | GET | Lista endereços. |
| **Addresses - Create address** | POST | Cria um endereço. |
| **Addresses - List dependent phone number** | GET | Lista números de telefone dependentes. |
| **Addresses - Fetch address** | GET | Obtém um endereço. |
| **Addresses - Update address** | POST | Atualiza um endereço. |
| **Addresses - Delete address** | DELETE | Exclui um endereço. |
| **Applications - List application** | GET | Recupera uma lista de aplicativos que representam um aplicativo dentro da conta solicitante. |
| **Applications - Create application** | POST | Cria um novo aplicativo em sua conta. |
| **Applications - Fetch application** | GET | Obtém o aplicativo especificado pelo SID fornecido. |
| **Applications - Update application** | POST | Atualiza as propriedades do aplicativo. |
| **Applications - Delete application** | DELETE | Exclui o aplicativo especificado pelo SID fornecido. |
| **Authorized Connect Apps - List authorized connect app** | GET | Recupera uma lista de aplicativos de conexão autorizada pertencentes à conta usada para fazer a solicitação. |
| **Authorized Connect Apps - Fetch authorized connect app** | GET | Obtém uma instância de um aplicativo de conexão autorizada. |
| **Available Phone Numbers - List available phone number country** | GET | Lista país com números de telefone disponíveis. |
| **Available Phone Numbers - Fetch available phone number country** | GET | Obtém país com números de telefone disponíveis. |
| **Available Phone Numbers - List available phone number local** | GET | Lista números de telefone disponíveis locais. |
| **Available Phone Numbers - List available phone number machine to machine** | GET | Lista números de telefone disponíveis máquina a máquina. |
| **Available Phone Numbers - List available phone number mobile** | GET | Lista números de telefone disponíveis móveis. |
| **Available Phone Numbers - List available phone number national** | GET | Lista números de telefone disponíveis nacionais. |
| **Available Phone Numbers - List available phone number shared cost** | GET | Lista números de telefone disponíveis de custo compartilhado. |
| **Available Phone Numbers - List available phone number toll free** | GET | Lista números de telefone disponíveis gratuitos. |
| **Available Phone Numbers - List available phone number voip** | GET | Lista números de telefone disponíveis VoIP. |
| **Balance - Fetch balance** | GET | Obtém o saldo de uma conta com base no SID da conta. Alterações de saldo podem não ser refletidas imediatamente. Contas filhas não contêm informações de saldo. |
| **Calls - List call** | GET | Recupera uma coleção de chamadas feitas para e da sua conta. |
| **Calls - Create call** | POST | Cria uma nova chamada sainte para telefones, pontos de extremidade habilitados para SIP ou conexões Twilio Client. |
| **Calls - List call event** | GET | Recupera uma lista de todos os eventos de uma chamada. |
| **Calls - List call notification** | GET | Lista notificações de chamada. |
| **Calls - Fetch call notification** | GET | Busca uma notificação de chamada. |
| **Calls - Create payments** | POST | Cria uma instância de pagamentos. Inicia uma nova sessão de pagamentos. |
| **Calls - Update payments** | POST | Atualiza uma instância de pagamentos com diferentes fases de fluxos de pagamento. |
| **Calls - List call recording** | GET | Recupera uma lista de gravações pertencentes à chamada usada para fazer a solicitação. |
| **Calls - Create call recording** | POST | Cria uma gravação para a chamada. |
| **Calls - Fetch call recording** | GET | Busca uma instância de gravação de uma chamada. |
| **Calls - Update call recording** | POST | Altera o status da gravação para pausada, interrompida ou em andamento. Use `Twilio.CURRENT` em vez do SID da gravação para referenciar a gravação ativa atual. |
| **Calls - Delete call recording** | DELETE | Exclui uma gravação da sua conta. |
| **Calls - Create siprec** | POST | Cria um Siprec. |
| **Calls - Update siprec** | POST | Para um Siprec usando o SID do recurso Siprec ou o `name` usado ao criar o recurso. |
| **Calls - Create stream** | POST | Cria um Stream. |
| **Calls - Update stream** | POST | Para um Stream usando o SID do recurso Stream ou o `name` usado ao criar o recurso. |
| **Calls - Create realtime transcription** | POST | Cria uma Transcrição. |
| **Calls - Update realtime transcription** | POST | Para uma Transcrição usando o SID do recurso Transcrição ou o `name` usado ao criar o recurso. |
| **Calls - Create user defined message subscription** | POST | Inscreve-se em Mensagens Definidas pelo Usuário para um determinado SID de Chamada. |
| **Calls - Delete user defined message subscription** | DELETE | Exclui uma inscrição específica de Mensagem Definida pelo Usuário. |
| **Calls - Create user defined message** | POST | Cria uma nova Mensagem Definida pelo Usuário para o determinado SID de Chamada. |
| **Calls - Fetch call** | GET | Busca a chamada especificada pelo SID da Chamada fornecido. |
| **Calls - Update call** | POST | Inicia um redirecionamento de chamada ou encerra uma chamada. |
| **Calls - Delete call** | DELETE | Exclui um registro de Chamada da sua conta. Não aparecerá mais nos logs da API e Portal da Conta após exclusão. |
| **Conferences - List conference** | GET | Recupera uma lista de conferências pertencentes à conta usada para fazer a solicitação. |
| **Conferences - List participant** | GET | Lista todos os participantes da conta usada para fazer a requisição. |
| **Conferences - Create participant** | POST | Cria um novo participante. |
| **Conferences - Fetch participant** | GET | Obtém um participante específico. |
| **Conferences - Update participant** | POST | Atualiza as propriedades do participante. |
| **Conferences - Delete participant** | DELETE | Remove um participante de uma conferência. |
| **Conferences - List conference recording** | GET | Lista todas as gravações associadas à chamada usada para fazer a requisição. |
| **Conferences - Fetch conference recording** | GET | Obtém uma gravação específica de uma chamada. |
| **Conferences - Update conference recording** | POST | Altera o status da gravação para pausada, parada ou em progresso. Use `Twilio.CURRENT` como identificador da gravação. |
| **Conferences - Delete conference recording** | DELETE | Remove uma gravação da conta. |
| **Conferences - Fetch conference** | GET | Obtém uma conferência específica. |
| **Conferences - Update conference** | POST | Atualiza uma conferência. |
| **Connect Apps - List connect app** | GET | Lista todos os Connect Apps da conta usada para fazer a requisição. |
| **Connect Apps - Fetch connect app** | GET | Obtém um Connect App específico. |
| **Connect Apps - Update connect app** | POST | Atualiza um Connect App com os parâmetros especificados. |
| **Connect Apps - Delete connect app** | DELETE | Remove um Connect App. |
| **Incoming Phone Numbers - List incoming phone number** | GET | Lista todos os números de telefone recebidos da conta usada para fazer a requisição. |
| **Incoming Phone Numbers - Create incoming phone number** | POST | Compra um número de telefone para a conta. |
| **Incoming Phone Numbers - List incoming phone number local** | GET | Lista números de telefone locais para recebimento. |
| **Incoming Phone Numbers - Create incoming phone number local** | POST | Cria um número de telefone local para recebimento. |
| **Incoming Phone Numbers - List incoming phone number mobile** | GET | Lista números de telefone móvel para recebimento. |
| **Incoming Phone Numbers - Create incoming phone number mobile** | POST | Cria um número de telefone móvel para recebimento. |
| **Incoming Phone Numbers - List incoming phone number toll free** | GET | Lista números de telefone gratuito para recebimento. |
| **Incoming Phone Numbers - Create incoming phone number toll free** | POST | Cria um número de telefone gratuito para recebimento. |
| **Incoming Phone Numbers - List incoming phone number assigned add on** | GET | Lista os complementos atualmente atribuídos a este número. |
| **Incoming Phone Numbers - Create incoming phone number assigned add on** | POST | Atribui um complemento ao número especificado. |
| **Incoming Phone Numbers - List incoming phone number assigned add on extension** | GET | Recuperar uma lista de extensões para o complemento atribuído. |
| **Incoming Phone Numbers - Fetch incoming phone number assigned add on extension** | GET | Obter uma instância de uma extensão para o complemento atribuído. |
| **Incoming Phone Numbers - Fetch incoming phone number assigned add on** | GET | Obter uma instância de uma instalação de complemento atualmente atribuída a este número. |
| **Incoming Phone Numbers - Delete incoming phone number assigned add on** | DELETE | Remover a atribuição de uma instalação de complemento do número especificado. |
| **Incoming Phone Numbers - Fetch incoming phone number** | GET | Obter um número de telefone de entrada pertencente à conta usada para fazer a solicitação. |
| **Incoming Phone Numbers - Update incoming phone number** | POST | Atualizar uma instância de número de telefone de entrada. |
| **Incoming Phone Numbers - Delete incoming phone number** | DELETE | Excluir um número de telefone pertencente à conta usada para fazer a solicitação. |
| **Keys - List key** | GET | Listar chaves. |
| **Keys - Create new key** | POST | Criar nova chave. |
| **Keys - Fetch key** | GET | Obter chave. |
| **Keys - Update key** | POST | Atualizar chave. |
| **Keys - Delete key** | DELETE | Excluir chave. |
| **Messages - List message** | GET | Recuperar uma lista de recursos de mensagem associados a uma conta Twilio. |
| **Messages - Create message** | POST | Enviar uma mensagem. |
| **Messages - Create message feedback** | POST | Criar feedback de mensagem para confirmar que uma ação de usuário rastreada foi executada pelo destinatário da mensagem associada. |
| **Messages - List media** | GET | Ler uma lista de recursos de mídia associados a um recurso de mensagem específico. |
| **Messages - Fetch media** | GET | Obter um único recurso de mídia associado a um recurso de mensagem específico. |
| **Messages - Delete media** | DELETE | Excluir o recurso de mídia. |
| **Messages - Fetch message** | GET | Obter uma mensagem específica. |
| **Messages - Update message** | POST | Atualizar um recurso de mensagem (usado para remover o texto `body` da mensagem e cancelar mensagens não enviadas). |
| **Messages - Delete message** | DELETE | Excluir um recurso de mensagem da sua conta. |
| **Notifications - List notification** | GET | Recuperar uma lista de notificações pertencentes à conta usada para fazer a solicitação. |
| **Notifications - Fetch notification** | GET | Obter uma notificação pertencente à conta usada para fazer a solicitação. |
| **Outgoing Caller IDs - List outgoing caller id** | GET | Recuperar uma lista de IDs de chamador de saída pertencentes à conta usada para fazer a solicitação. |
| **Outgoing Caller IDs - Create validation request** | POST | Criar solicitação de validação. |
| **Outgoing Caller IDs - Fetch outgoing caller id** | GET | Busca um ID de chamador de saída pertencente à conta usada para fazer a requisição. |
| **Outgoing Caller IDs - Update outgoing caller id** | POST | Atualiza o ID do chamador. |
| **Outgoing Caller IDs - Delete outgoing caller id** | DELETE | Exclui o ID do chamador especificado da conta. |
| **Queues - List queue** | GET | Recupera uma lista de filas pertencentes à conta usada para fazer a requisição. |
| **Queues - Create queue** | POST | Cria uma fila. |
| **Queues - List member** | GET | Recupera os membros da fila. |
| **Queues - Fetch member** | GET | Busca um membro específico da fila. |
| **Queues - Update member** | POST | Remove um membro de uma fila e inicia a execução do documento TwiML nessa URL para a chamada do membro. |
| **Queues - Fetch queue** | GET | Busca uma instância de fila identificada pelo QueueSid. |
| **Queues - Update queue** | POST | Atualiza a fila com os novos parâmetros. |
| **Queues - Delete queue** | DELETE | Remove uma fila vazia. |
| **Recordings - List recording** | GET | Recupera uma lista de gravações pertencentes à conta usada para fazer a requisição. |
| **Recordings - List recording transcription** | GET | Lista as transcrições de gravação. |
| **Recordings - Fetch recording transcription** | GET | Busca a transcrição de gravação. |
| **Recordings - Delete recording transcription** | DELETE | Exclui a transcrição de gravação. |
| **Recordings - List recording add on result** | GET | Recupera uma lista de resultados pertencentes à gravação. |
| **Recordings - List recording add on result payload** | GET | Recupera uma lista de cargas pertencentes ao AddOnResult. |
| **Recordings - Fetch recording add on result payload data** | GET | Busca uma instância de carga de resultado. |
| **Recordings - Fetch recording add on result payload** | GET | Busca uma instância de carga de resultado. |
| **Recordings - Delete recording add on result payload** | DELETE | Exclui uma carga do resultado junto com todos os Dados associados. |
| **Recordings - Fetch recording add on result** | GET | Busca uma instância de AddOnResult. |
| **Recordings - Delete recording add on result** | DELETE | Exclui um resultado e remove todas as Cargas associadas. |
| **Recordings - Fetch recording** | GET | Busca uma instância de uma gravação. |
| **Recordings - Delete recording** | DELETE | Exclui uma gravação da sua conta. |
| **SIP - List sip credential list** | GET | Obtém todas as listas de credenciais. |
| **SIP - Create sip credential list** | POST | Criar uma lista de credenciais. |
| **SIP - List sip credential** | GET | Recuperar uma lista de credenciais. |
| **SIP - Create sip credential** | POST | Criar um novo recurso de credencial. |
| **SIP - Fetch sip credential** | GET | Obter uma credencial única. |
| **SIP - Update sip credential** | POST | Atualizar um recurso de credencial. |
| **SIP - Delete sip credential** | DELETE | Excluir um recurso de credencial. |
| **SIP - Fetch sip credential list** | GET | Obter uma lista de credenciais. |
| **SIP - Update sip credential list** | POST | Atualizar uma lista de credenciais. |
| **SIP - Delete sip credential list** | DELETE | Excluir uma lista de credenciais. |
| **SIP - List sip domain** | GET | Recuperar uma lista de domínios pertencentes à conta usada para fazer a requisição. |
| **SIP - Create sip domain** | POST | Criar um novo domínio. |
| **SIP - List sip auth calls credential list mapping** | GET | Recuperar uma lista de mapeamentos de lista de credenciais pertencentes ao domínio usado na requisição. |
| **SIP - Create sip auth calls credential list mapping** | POST | Criar um novo recurso de mapeamento de lista de credenciais. |
| **SIP - Fetch sip auth calls credential list mapping** | GET | Obter uma instância específica de um mapeamento de lista de credenciais. |
| **SIP - Delete sip auth calls credential list mapping** | DELETE | Excluir um mapeamento de lista de credenciais do domínio solicitado. |
| **SIP - List sip auth calls ip access control list mapping** | GET | Recuperar uma lista de mapeamentos de Lista de Controle de Acesso por IP pertencentes ao domínio usado na requisição. |
| **SIP - Create sip auth calls ip access control list mapping** | POST | Criar um novo mapeamento de Lista de Controle de Acesso por IP. |
| **SIP - Fetch sip auth calls ip access control list mapping** | GET | Obter uma instância específica de um mapeamento de Lista de Controle de Acesso por IP. |
| **SIP - Delete sip auth calls ip access control list mapping** | DELETE | Excluir um mapeamento de Lista de Controle de Acesso por IP do domínio solicitado. |
| **SIP - List sip auth registrations credential list mapping** | GET | Recuperar uma lista de mapeamentos de lista de credenciais pertencentes ao domínio usado na requisição. |
| **SIP - Create sip auth registrations credential list mapping** | POST | Criar um novo recurso de mapeamento de lista de credenciais. |
| **SIP - Fetch sip auth registrations credential list mapping** | GET | Obter uma instância específica de um mapeamento de lista de credenciais. |
| **SIP - Delete sip auth registrations credential list mapping** | DELETE | Excluir um mapeamento de lista de credenciais do domínio solicitado. |
| **SIP - List sip credential list mapping** | GET | Ler múltiplos recursos de mapeamento de lista de credenciais de uma conta. |
| **SIP - Create sip credential list mapping** | POST | Criar um recurso de mapeamento de lista de credenciais para uma conta. |
| **SIP - Fetch sip credential list mapping** | GET | Buscar um único recurso CredentialListMapping de uma conta. |
| **SIP - Delete sip credential list mapping** | DELETE | Deletar um recurso CredentialListMapping de uma conta. |
| **SIP - List sip ip access control list mapping** | GET | Recuperar uma lista de recursos IpAccessControlListMapping. |
| **SIP - Create sip ip access control list mapping** | POST | Criar um novo recurso IpAccessControlListMapping. |
| **SIP - Fetch sip ip access control list mapping** | GET | Buscar um recurso IpAccessControlListMapping. |
| **SIP - Delete sip ip access control list mapping** | DELETE | Deletar um recurso IpAccessControlListMapping. |
| **SIP - Fetch sip domain** | GET | Buscar uma instância de um Domain |
| **SIP - Update sip domain** | POST | Atualizar os atributos de um domain |
| **SIP - Delete sip domain** | DELETE | Deletar uma instância de um Domain |
| **SIP - List sip ip access control list** | GET | Recuperar uma lista de IpAccessControlLists que pertencem à conta usada para fazer a solicitação |
| **SIP - Create sip ip access control list** | POST | Criar um novo recurso IpAccessControlList |
| **SIP - List sip ip address** | GET | Ler múltiplos recursos IpAddress. |
| **SIP - Create sip ip address** | POST | Criar um novo recurso IpAddress. |
| **SIP - Fetch sip ip address** | GET | Ler um recurso IpAddress. |
| **SIP - Update sip ip address** | POST | Atualizar um recurso IpAddress. |
| **SIP - Delete sip ip address** | DELETE | Deletar um recurso IpAddress. |
| **SIP - Fetch sip ip access control list** | GET | Buscar uma instância específica de um IpAccessControlList |
| **SIP - Update sip ip access control list** | POST | Renomear um IpAccessControlList |
| **SIP - Delete sip ip access control list** | DELETE | Deletar um IpAccessControlList da conta solicitada |
| **SMS - List short code** | GET | Recuperar uma lista de short-codes que pertencem à conta usada para fazer a solicitação |
| **SMS - Fetch short code** | GET | Buscar uma instância de um short code |
| **SMS - Update short code** | POST | Atualizar um short code com os seguintes parâmetros |
| **Signing Keys - List signing key** | GET | Listar signing key |
| **Signing Keys - Create new signing key** | POST | Criar uma nova Signing Key para a conta que faz a solicitação. |
| **Signing Keys - Fetch signing key** | GET | Buscar signing key |
| **Signing Keys - Update signing key** | POST | Atualizar chave de assinatura |
| **Signing Keys - Delete signing key** | DELETE | Excluir chave de assinatura |
| **Tokens - Create token** | POST | Criar um novo token para servidores ICE |
| **Transcriptions - List transcription** | GET | Listar transcrições da conta utilizada para fazer a solicitação |
| **Transcriptions - Fetch transcription** | GET | Buscar uma transcrição específica |
| **Transcriptions - Delete transcription** | DELETE | Excluir uma transcrição da conta |
| **Usage - List usage record** | GET | Listar registros de uso da conta |
| **Usage - List usage record all time** | GET | Listar todos os registros de uso |
| **Usage - List usage record daily** | GET | Listar registros de uso diários |
| **Usage - List usage record last month** | GET | Listar registros de uso do mês anterior |
| **Usage - List usage record monthly** | GET | Listar registros de uso mensais |
| **Usage - List usage record this month** | GET | Listar registros de uso deste mês |
| **Usage - List usage record today** | GET | Listar registros de uso de hoje |
| **Usage - List usage record yearly** | GET | Listar registros de uso anuais |
| **Usage - List usage record yesterday** | GET | Listar registros de uso de ontem |
| **Usage - List usage trigger** | GET | Listar gatilhos de uso da conta |
| **Usage - Create usage trigger** | POST | Criar um novo gatilho de uso |
| **Usage - Fetch usage trigger** | GET | Buscar uma instância de um gatilho de uso |
| **Usage - Update usage trigger** | POST | Atualizar uma instância de um gatilho de uso |
| **Usage - Delete usage trigger** | DELETE | Excluir gatilho de uso |
| **Accounts - Fetch account** | GET | Buscar a conta pelo Account Sid fornecido |
| **Accounts - Update account** | POST | Modificar as propriedades de uma conta |

### Twilio Messaging — 58 operações

| Nome da Operação | Método HTTP | Descrição da Função |
| :--------------- | :---------- | :------------------ |
| **Deactivations - Fetch deactivation** | GET | Recupera uma lista de todos os números dos EUA que foram desativados em uma data específica. |
| **Link Shortening - Fetch domain cert v4** | GET | Recuperar certificado de domínio v4. |
| **Link Shortening - Update domain cert v4** | POST | Atualizar certificado de domínio v4. |
| **Link Shortening - Delete domain cert v4** | DELETE | Excluir certificado de domínio v4. |
| **Link Shortening - Fetch domain config** | GET | Recuperar configuração de domínio. |
| **Link Shortening - Update domain config** | POST | Atualizar configuração de domínio. |
| **Link Shortening - Create linkshortening messaging service** | POST | Criar serviço de mensagens de encurtamento de link. |
| **Link Shortening - Delete linkshortening messaging service** | DELETE | Excluir serviço de mensagens de encurtamento de link. |
| **Link Shortening - Update request managed cert** | POST | Atualizar solicitação de certificado gerenciado. |
| **Link Shortening - Fetch domain dns validation** | GET | Recuperar validação de DNS do domínio. |
| **Link Shortening - Fetch domain config messaging service** | GET | Recuperar configuração de domínio do serviço de mensagens. |
| **Link Shortening - Fetch linkshortening messaging service domain association** | GET | Recuperar associação de domínio do serviço de mensagens de encurtamento de link. |
| **Services - List service** | GET | Listar serviço. |
| **Services - Create service** | POST | Criar serviço. |
| **Preregistered USA2P - Create external campaign** | POST | Criar campanha externa. |
| **Usecases - Fetch usecase** | GET | Recuperar caso de uso. |
| **Channel Senders - List channel sender** | GET | Listar remetente de canal. |
| **Channel Senders - Create channel sender** | POST | Criar remetente de canal. |
| **Channel Senders - Fetch channel sender** | GET | Recuperar remetente de canal. |
| **Channel Senders - Delete channel sender** | DELETE | Excluir remetente de canal. |
| **Compliance - List us app to person** | GET | Listar app-to-person americano. |
| **Compliance - Create us app to person** | POST | Criar app-to-person americano. |
| **Compliance - Fetch us app to person usecase** | GET | Obter caso de uso de app-to-person americano. |
| **Compliance - Fetch us app to person** | GET | Obter app-to-person americano. |
| **Compliance - Update us app to person** | POST | Atualizar app-to-person americano. |
| **Compliance - Delete us app to person** | DELETE | Excluir app-to-person americano. |
| **Alpha Senders - List alpha sender** | GET | Listar remetente alfanumérico. |
| **Alpha Senders - Create alpha sender** | POST | Criar remetente alfanumérico. |
| **Alpha Senders - Fetch alpha sender** | GET | Obter remetente alfanumérico. |
| **Alpha Senders - Delete alpha sender** | DELETE | Excluir remetente alfanumérico. |
| **Destination Alpha Senders - List destination alpha sender** | GET | Listar remetente alfanumérico de destino. |
| **Destination Alpha Senders - Create destination alpha sender** | POST | Criar remetente alfanumérico de destino. |
| **Destination Alpha Senders - Fetch destination alpha sender** | GET | Obter remetente alfanumérico de destino. |
| **Destination Alpha Senders - Delete destination alpha sender** | DELETE | Excluir remetente alfanumérico de destino. |
| **Phone Numbers - List phone number** | GET | Listar número de telefone. |
| **Phone Numbers - Create phone number** | POST | Criar número de telefone. |
| **Phone Numbers - Fetch phone number** | GET | Obter número de telefone. |
| **Phone Numbers - Delete phone number** | DELETE | Excluir número de telefone. |
| **Short Codes - List short code** | GET | Listar código curto. |
| **Short Codes - Create short code** | POST | Criar código curto. |
| **Short Codes - Fetch short code** | GET | Recupera um código curto. |
| **Short Codes - Delete short code** | DELETE | Exclui um código curto. |
| **Services - Fetch service** | GET | Recupera um serviço de mensageria. |
| **Services - Update service** | POST | Atualiza um serviço de mensageria. |
| **Services - Delete service** | DELETE | Exclui um serviço de mensageria. |
| **Tollfree - List tollfree verification** | GET | Lista verificações de números Tollfree. |
| **Tollfree - Create tollfree verification** | POST | Cria uma verificação de número Tollfree. |
| **Tollfree - Fetch tollfree verification** | GET | Recupera uma verificação de número Tollfree. |
| **Tollfree - Update tollfree verification** | POST | Edita uma verificação de número Tollfree. |
| **Tollfree - Delete tollfree verification** | DELETE | Exclui uma verificação de número Tollfree. |
| **A2P - List brand registrations** | GET | Lista registros de marcas. |
| **A2P - Create brand registrations** | POST | Cria registros de marcas. |
| **A2P - Create brand registration otp** | POST | Cria OTP de registro de marca. |
| **A2P - List brand vetting** | GET | Lista verificações de marca. |
| **A2P - Create brand vetting** | POST | Cria uma verificação de marca. |
| **A2P - Fetch brand vetting** | GET | Recupera uma verificação de marca. |
| **A2P - Fetch brand registrations** | GET | Recupera registros de marcas. |
| **A2P - Update brand registrations** | POST | Atualiza registros de marcas. |

### Twilio Verify — 57 operações

| Nome da Operação | Método HTTP | Descrição da Função |
| :--------------- | :---------- | :------------------ |
| **Attempts - List verification attempt** | GET | Lista todas as tentativas de verificação de uma conta específica. |
| **Attempts - Fetch verification attempts summary** | GET | Obtém um resumo de quantas tentativas foram feitas e quantas foram convertidas. |
| **Attempts - Fetch verification attempt** | GET | Obtém uma tentativa de verificação específica. |
| **Forms - Fetch form** | GET | Obtém os formulários de um tipo de formulário específico. |
| **Safe List - Create safelist** | POST | Adiciona um novo número de telefone à lista de segurança. |
| **Safe List - Fetch safelist** | GET | Verifica se um número de telefone existe na lista de segurança. |
| **Safe List - Delete safelist** | DELETE | Remove um número de telefone da lista de segurança. |
| **Services - List service** | GET | Recupera uma lista de todos os serviços de verificação de uma conta. |
| **Services - Create service** | POST | Cria um novo serviço de verificação. |
| **Access Tokens - Create access token** | POST | Cria um novo token de acesso de inscrição para a entidade. |
| **Access Tokens - Fetch access token** | GET | Obtém um token de acesso para a entidade. |
| **Entities - List entity** | GET | Recupera uma lista de todas as entidades de um serviço. |
| **Entities - Create entity** | POST | Cria uma nova entidade para o serviço. |
| **Entities - Fetch entity** | GET | Obtém uma entidade específica. |
| **Entities - Delete entity** | DELETE | Deleta uma entidade específica. |
| **Challenges - List challenge** | GET | Recupera uma lista de todos os desafios de um fator. |
| **Challenges - Create challenge** | POST | Cria um novo desafio para o fator. |
| **Challenges - Create notification** | POST | Cria uma nova notificação para o desafio correspondente. |
| **Challenges - Fetch challenge** | GET | Obtém um desafio específico. |
| **Challenges - Update challenge** | POST | Verifica um Desafio específico. |
| **Factors - List factor** | GET | Recupera uma lista de todos os Fatores para uma Entidade. |
| **Factors - Create new factor** | POST | Cria um novo Fator para a Entidade. |
| **Factors - Fetch factor** | GET | Busca um Fator específico. |
| **Factors - Update factor** | POST | Atualiza um Fator específico. Este endpoint pode ser usado para Verificar um Fator se passado um parâmetro `AuthPayload`. |
| **Factors - Delete factor** | DELETE | Exclui um Fator específico. |
| **Messaging Configurations - List messaging configuration** | GET | Recupera uma lista de todas as Configurações de Mensagens para um Serviço. |
| **Messaging Configurations - Create messaging configuration** | POST | Cria uma nova Configuração de Mensagens para um serviço. |
| **Messaging Configurations - Fetch messaging configuration** | GET | Busca uma Configuração de Mensagens específica. |
| **Messaging Configurations - Update messaging configuration** | POST | Atualiza uma Configuração de Mensagens específica. |
| **Messaging Configurations - Delete messaging configuration** | DELETE | Exclui uma Configuração de Mensagens específica. |
| **Passkeys - Update challenge passkeys** | POST | Aprova um desafio de Chaves de Acesso. |
| **Passkeys - Create challenge passkeys** | POST | Cria um Desafio de Chaves de Acesso. |
| **Passkeys - Create new factor passkey** | POST | Cria um novo Fator de Chaves de Acesso para a Entidade. |
| **Passkeys - Update passkeys factor** | POST | Verifica um Fator de Chaves de Acesso. |
| **Rate Limits - List rate limit** | GET | Recupera uma lista de todos os Limites de Taxa para um serviço. |
| **Rate Limits - Create rate limit** | POST | Cria um novo Limite de Taxa para um Serviço. |
| **Rate Limits - List bucket** | GET | Recupera uma lista de todos os Buckets para um Limite de Taxa. |
| **Rate Limits - Create bucket** | POST | Cria um novo Bucket para um Limite de Taxa. |
| **Rate Limits - Fetch bucket** | GET | Obter um Bucket específico. |
| **Rate Limits - Update bucket** | POST | Atualizar um Bucket específico. |
| **Rate Limits - Delete bucket** | DELETE | Excluir um Bucket específico. |
| **Rate Limits - Fetch rate limit** | GET | Obter um Limite de Taxa específico. |
| **Rate Limits - Update rate limit** | POST | Atualizar um Limite de Taxa específico. |
| **Rate Limits - Delete rate limit** | DELETE | Excluir um Limite de Taxa específico. |
| **Verification Check - Create verification check** | POST | Desafiar uma Verificação de Verificação específica. |
| **Verifications - Create verification** | POST | Criar uma nova Verificação usando um Serviço. |
| **Verifications - Fetch verification** | GET | Obter uma Verificação específica. |
| **Verifications - Update verification** | POST | Atualizar o status de uma Verificação. |
| **Webhooks - List webhook** | GET | Recuperar uma lista de todos os Webhooks para um Serviço. |
| **Webhooks - Create webhook** | POST | Criar um novo Webhook para o Serviço. |
| **Webhooks - Fetch webhook** | GET | Obter um Webhook específico. |
| **Webhooks - Update webhook** | POST | Atualizar webhook. |
| **Webhooks - Delete webhook** | DELETE | Excluir um Webhook específico. |
| **Services - Fetch service** | GET | Obter uma Instância de Serviço de Verificação específica. |
| **Services - Update service** | POST | Atualizar um Serviço de Verificação específico. |
| **Services - Delete service** | DELETE | Excluir uma Instância de Serviço de Verificação específica. |
| **Templates - List verification template** | GET | Listar todos os templates disponíveis para uma Conta fornecida. |

### Twilio Lookups — 10 operações

| Nome da Operação | Método HTTP | Descrição da Função |
| :--------------- | :---------- | :------------------ |
| **Phone Numbers - Fetch phone number** | GET | A API de Lookup permite consultar informações de um número de telefone para fazer uma interação confiável com seu usuário. |
| **Phone Numbers - Fetch lookup phone number overrides** | GET | Recupera um Override para um pacote e número de telefone específicos. |
| **Phone Numbers - Create lookup phone number overrides** | POST | Cria um Override para um pacote e número de telefone específicos. |
| **Phone Numbers - Update lookup phone number overrides** | PUT | Atualiza um Override para um pacote e número de telefone específicos. |
| **Phone Numbers - Delete lookup phone number overrides** | DELETE | Exclui um Override para um pacote e número de telefone específicos. |
| **Rate Limits - Fetch lookup account rate limits** | GET | Recupera a lista de limites de taxa para todos os campos e os limites de taxa do Twilio. |
| **Rate Limits - Fetch lookup rate limit** | GET | Recupera o limite de taxa de lookup. |
| **Rate Limits - Update lookup rate limit** | PUT | Atualiza o limite de taxa de lookup. |
| **Rate Limits - Delete lookup rate limit** | DELETE | Exclui o limite de taxa de lookup. |
| **Batch - Create bulk lookup** | POST | Envia um lote de números de telefone em uma única solicitação e recebe resultados de lookup para todos. |

---

## Documentação oficial

**Documentação Oficial da API:** [Twilio Docs](https://www.twilio.com/docs)

- [API principal (2010-04-01)](https://www.twilio.com/docs/usage/api)
- [Messaging](https://www.twilio.com/docs/messaging/api)
- [Verify](https://www.twilio.com/docs/verify/api)
- [Lookup](https://www.twilio.com/docs/lookup/v2-api)
- [Especificações OpenAPI oficiais](https://github.com/twilio/twilio-oai/tree/main/spec/json)
