# RabbitMQ

## Contexto

O RabbitMQ é um broker de mensageria que implementa AMQP 0-9-1 e, via plugins,
os protocolos MQTT, STOMP e Stream. Este conector cobre a **Management HTTP
API**, exposta pelo plugin `rabbitmq_management`, que permite administrar e
monitorar o broker sem acesso ao shell dos nós.

Domínios e conceitos cobertos:

- **Cluster e nós** — visão geral (`overview`), nome do cluster, métricas por nó
  e detalhamento de memória.
- **Virtual hosts** — isolamento lógico de recursos; criação, remoção, proteção
  contra exclusão e inicialização em um nó específico.
- **Exchanges, filas e bindings** — declaração e remoção de recursos de
  mensageria, consulta de bindings, publicação de mensagens e leitura de
  mensagens de uma fila pela API.
- **Conexões, canais e consumidores** — inspeção e encerramento de conexões
  AMQP, inclusive por usuário autenticado.
- **Usuários, permissões e limites** — banco interno de usuários, permissões de
  `configure`/`write`/`read`, permissões de tópico e limites por usuário e por
  virtual host.
- **Policies, operator policies e parâmetros de runtime** — configuração
  declarativa de comportamento de filas e exchanges, parâmetros por componente
  e parâmetros globais.
- **Definitions** — exportação e importação em massa da configuração do cluster
  ou de um virtual host, usada em backup e provisionamento.
- **Streams** — conexões, publishers e consumidores do protocolo stream.
- **Health checks** — verificações prontas para monitoramento e readiness
  probes (alarmes, listeners, quorum, expiração de certificados).
- **Federação e extensões** — status dos links de federação e extensões
  registradas no plugin de gerenciamento.

Todas as operações usam o prefixo de path `api`, apendado ao Host da conta
conectada.

> **Atenção ao parâmetro `vhost`:** ele deve ser informado **URL-encoded**. O
> virtual host padrão `/` corresponde a `%2F`.

---

## Autenticação

**Tipo:** Autenticação básica (HTTP Basic)

A Management API autentica contra o banco interno de usuários do RabbitMQ. O
usuário precisa da tag `management`, `monitoring`, `policymaker` ou
`administrator`, conforme as operações que for executar — operações de escrita
em usuários, permissões e vhosts exigem `administrator`.

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://<>seu-host-rabbitmq</>` |
| Porta | 15672 |
| password | {{api_token}} |
| username | {{account_email}} |

> A porta padrão do plugin de gerenciamento é **15672** (HTTP). Em clusters com
> TLS habilitado no plugin, use **15671**.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Overview - Get overview** | **GET** | Retorna informações e estatísticas gerais do cluster. |
| **Overview - Get cluster name** | **GET** | Retorna o identificador atual do cluster. |
| **Overview - Update cluster name** | **PUT** | Atualiza o nome do cluster. |
| **Overview - Get current user** | **GET** | Retorna os dados do usuário autenticado na requisição. |
| **Nodes - Get all nodes** | **GET** | Lista todos os nós do cluster com suas métricas. |
| **Nodes - Get node** | **GET** | Retorna as métricas de um nó específico do cluster. |
| **Nodes - Get node memory** | **GET** | Retorna o detalhamento do uso de memória de um nó. |
| **Definitions - Export definitions** | **GET** | Exporta todas as definições do cluster. |
| **Definitions - Import definitions** | **POST** | Importa definições para o cluster. |
| **Definitions - Export vhost definitions** | **GET** | Exporta as definições de um virtual host. |
| **Definitions - Import vhost definitions** | **POST** | Importa definições para um virtual host. |
| **Connections - Get all connections** | **GET** | Lista todas as conexões abertas no cluster. |
| **Connections - Get connections by vhost** | **GET** | Lista as conexões abertas em um virtual host. |
| **Connections - Get connection** | **GET** | Retorna as métricas de uma conexão específica. |
| **Connections - Close connection** | **DELETE** | Encerra uma conexão específica. |
| **Connections - Get connections by username** | **GET** | Lista as conexões abertas por um usuário autenticado. |
| **Connections - Close connections by username** | **DELETE** | Encerra todas as conexões abertas por um usuário. |
| **Connections - Get connection channels** | **GET** | Lista os canais abertos em uma conexão. |
| **Channels - Get all channels** | **GET** | Lista todos os canais abertos no cluster. |
| **Channels - Get channels by vhost** | **GET** | Lista os canais abertos em um virtual host. |
| **Channels - Get channel** | **GET** | Retorna os detalhes de um canal específico. |
| **Consumers - Get all consumers** | **GET** | Lista todos os consumidores do cluster. |
| **Consumers - Get consumers by vhost** | **GET** | Lista os consumidores de um virtual host. |
| **Exchanges - Get all exchanges** | **GET** | Lista todos os exchanges do cluster. |
| **Exchanges - Get exchanges by vhost** | **GET** | Lista os exchanges de um virtual host. |
| **Exchanges - Get exchange** | **GET** | Retorna as métricas de um exchange específico. |
| **Exchanges - Declare exchange** | **PUT** | Cria ou atualiza um exchange em um virtual host. |
| **Exchanges - Delete exchange** | **DELETE** | Remove um exchange de um virtual host. |
| **Exchanges - Get source bindings** | **GET** | Lista as bindings em que o exchange é a origem. |
| **Exchanges - Get destination bindings** | **GET** | Lista as bindings em que o exchange é o destino. |
| **Exchanges - Publish message** | **POST** | Publica uma mensagem em um exchange. |
| **Queues - Get all queues** | **GET** | Lista todas as filas do cluster. |
| **Queues - Get all queues detailed** | **GET** | Lista todas as filas com métricas detalhadas. |
| **Queues - Get queues by vhost** | **GET** | Lista as filas de um virtual host. |
| **Queues - Get queue** | **GET** | Retorna as métricas de uma fila específica. |
| **Queues - Declare queue** | **PUT** | Cria ou atualiza uma fila em um virtual host. |
| **Queues - Delete queue** | **DELETE** | Remove uma fila de um virtual host. |
| **Queues - Get queue bindings** | **GET** | Lista todas as bindings associadas a uma fila. |
| **Queues - Purge queue** | **DELETE** | Remove todas as mensagens de uma fila. |
| **Queues - Get messages** | **POST** | Lê mensagens de uma fila sem consumi-las por um cliente AMQP. |
| **Bindings - Get all bindings** | **GET** | Lista todas as bindings do cluster. |
| **Bindings - Get bindings by vhost** | **GET** | Lista as bindings de um virtual host. |
| **Bindings - Get exchange to queue bindings** | **GET** | Lista as bindings entre um exchange e uma fila. |
| **Bindings - Bind queue to exchange** | **POST** | Cria uma binding entre um exchange e uma fila. |
| **Bindings - Get exchange to queue binding** | **GET** | Retorna uma binding específica entre exchange e fila. |
| **Bindings - Delete exchange to queue binding** | **DELETE** | Remove uma binding específica entre exchange e fila. |
| **Bindings - Get exchange to exchange bindings** | **GET** | Lista as bindings entre dois exchanges. |
| **Bindings - Bind exchange to exchange** | **POST** | Cria uma binding entre dois exchanges. |
| **Bindings - Get exchange to exchange binding** | **GET** | Retorna uma binding específica entre dois exchanges. |
| **Bindings - Delete exchange to exchange binding** | **DELETE** | Remove uma binding específica entre dois exchanges. |
| **Vhosts - Get all vhosts** | **GET** | Lista todos os virtual hosts do cluster. |
| **Vhosts - Get vhost** | **GET** | Retorna as métricas de um virtual host específico. |
| **Vhosts - Create vhost** | **PUT** | Cria ou atualiza um virtual host. |
| **Vhosts - Delete vhost** | **DELETE** | Remove um virtual host e todo o seu conteúdo. |
| **Vhosts - Get vhost permissions** | **GET** | Lista as permissões concedidas em um virtual host. |
| **Vhosts - Get vhost topic permissions** | **GET** | Lista as permissões de tópico em um virtual host. |
| **Vhosts - Enable deletion protection** | **POST** | Ativa a proteção contra exclusão de um virtual host. |
| **Vhosts - Disable deletion protection** | **DELETE** | Desativa a proteção contra exclusão de um virtual host. |
| **Vhosts - Start vhost on node** | **POST** | Inicia um virtual host em um nó específico do cluster. |
| **Users - Get all users** | **GET** | Lista todos os usuários do banco interno do RabbitMQ. |
| **Users - Get users without permissions** | **GET** | Lista os usuários que não possuem nenhuma permissão. |
| **Users - Bulk delete users** | **POST** | Remove vários usuários em uma única requisição. |
| **Users - Get user** | **GET** | Retorna os dados de um usuário específico. |
| **Users - Create or update user** | **PUT** | Cria ou atualiza um usuário do banco interno. |
| **Users - Delete user** | **DELETE** | Remove um usuário do banco interno. |
| **Users - Get user permissions** | **GET** | Lista as permissões de um usuário em todos os vhosts. |
| **Users - Get user topic permissions** | **GET** | Lista as permissões de tópico de um usuário. |
| **Users - Get user queues** | **GET** | Lista as filas declaradas por um usuário. |
| **User Limits - Get all user limits** | **GET** | Lista os limites por usuário de todos os usuários. |
| **User Limits - Get user limits** | **GET** | Lista os limites configurados para um usuário. |
| **User Limits - Set user limit** | **PUT** | Define um limite para um usuário. |
| **User Limits - Clear user limit** | **DELETE** | Remove um limite configurado para um usuário. |
| **Permissions - Get all permissions** | **GET** | Lista todas as permissões de usuários do cluster. |
| **Permissions - Get user permissions in vhost** | **GET** | Retorna as permissões de um usuário em um virtual host. |
| **Permissions - Set user permissions** | **PUT** | Concede ou atualiza as permissões de um usuário em um vhost. |
| **Permissions - Delete user permissions** | **DELETE** | Revoga as permissões de um usuário em um virtual host. |
| **Topic Permissions - Get all topic permissions** | **GET** | Lista todas as permissões de tópico do cluster. |
| **Topic Permissions - Get user topic permissions** | **GET** | Retorna as permissões de tópico de um usuário em um vhost. |
| **Topic Permissions - Set user topic permissions** | **PUT** | Concede ou atualiza permissões de tópico de um usuário. |
| **Topic Permissions - Delete user topic permissions** | **DELETE** | Revoga as permissões de tópico de um usuário em um vhost. |
| **Parameters - Get all parameters** | **GET** | Lista todos os parâmetros de runtime do cluster. |
| **Parameters - Get parameters by component** | **GET** | Lista os parâmetros de runtime de um componente. |
| **Parameters - Get parameters by component and vhost** | **GET** | Lista os parâmetros de um componente em um virtual host. |
| **Parameters - Get parameter** | **GET** | Retorna um parâmetro de runtime específico. |
| **Parameters - Set parameter** | **PUT** | Cria ou atualiza um parâmetro de runtime. |
| **Parameters - Delete parameter** | **DELETE** | Remove um parâmetro de runtime. |
| **Global Parameters - Get all global parameters** | **GET** | Lista todos os parâmetros globais de runtime. |
| **Global Parameters - Get global parameter** | **GET** | Retorna um parâmetro global específico. |
| **Global Parameters - Set global parameter** | **PUT** | Cria ou atualiza um parâmetro global de runtime. |
| **Global Parameters - Delete global parameter** | **DELETE** | Remove um parâmetro global de runtime. |
| **Policies - Get all policies** | **GET** | Lista todas as policies do cluster. |
| **Policies - Get policies by vhost** | **GET** | Lista as policies de um virtual host. |
| **Policies - Get policy** | **GET** | Retorna uma policy específica. |
| **Policies - Create or update policy** | **PUT** | Cria ou atualiza uma policy em um virtual host. |
| **Policies - Delete policy** | **DELETE** | Remove uma policy de um virtual host. |
| **Operator Policies - Get all operator policies** | **GET** | Lista todas as operator policies do cluster. |
| **Operator Policies - Get operator policies by vhost** | **GET** | Lista as operator policies de um virtual host. |
| **Operator Policies - Get operator policy** | **GET** | Retorna uma operator policy específica. |
| **Operator Policies - Create or update operator policy** | **PUT** | Cria ou atualiza uma operator policy em um virtual host. |
| **Operator Policies - Delete operator policy** | **DELETE** | Remove uma operator policy de um virtual host. |
| **Vhost Limits - Get all vhost limits** | **GET** | Lista os limites de todos os virtual hosts. |
| **Vhost Limits - Get vhost limits** | **GET** | Lista os limites configurados para um virtual host. |
| **Vhost Limits - Set vhost limit** | **PUT** | Define um limite para um virtual host. |
| **Vhost Limits - Clear vhost limit** | **DELETE** | Remove um limite configurado para um virtual host. |
| **Federation - Get all federation links** | **GET** | Lista o status de todos os links de federação. |
| **Federation - Get federation links by vhost** | **GET** | Lista os links de federação de um virtual host. |
| **Health - Check alarms** | **GET** | Verifica se há alarmes de recurso ativos no cluster. |
| **Health - Check local alarms** | **GET** | Verifica se há alarmes de recurso ativos no nó local. |
| **Health - Check certificate expiration** | **GET** | Verifica se algum certificado expira dentro da janela informada. |
| **Health - Check port listener** | **GET** | Verifica se há um listener ativo na porta informada. |
| **Health - Check protocol listener** | **GET** | Verifica se há listeners ativos para os protocolos informados. |
| **Health - Check virtual hosts** | **GET** | Verifica se todos os virtual hosts do nó estão operacionais. |
| **Health - Check node quorum criticality** | **GET** | Verifica se há filas quorum sem redundância no nó. |
| **Health - Check node is in service** | **GET** | Verifica se o nó está em serviço e pronto para uso. |
| **Health - Check node connection limit** | **GET** | Verifica se o nó está abaixo do limite de conexões. |
| **Health - Check ready to serve clients** | **GET** | Verifica se o nó está pronto para atender clientes. |
| **Streams - Get all stream connections** | **GET** | Lista todas as conexões do protocolo stream. |
| **Streams - Get stream connections by vhost** | **GET** | Lista as conexões stream de um virtual host. |
| **Streams - Get stream connection** | **GET** | Retorna os detalhes de uma conexão stream específica. |
| **Streams - Close stream connection** | **DELETE** | Encerra uma conexão do protocolo stream. |
| **Streams - Get connection publishers** | **GET** | Lista os publishers ativos em uma conexão stream. |
| **Streams - Get connection consumers** | **GET** | Lista os consumidores ativos em uma conexão stream. |
| **Streams - Get all stream publishers** | **GET** | Lista todos os publishers de stream do cluster. |
| **Streams - Get stream publishers by vhost** | **GET** | Lista os publishers de stream de um virtual host. |
| **Streams - Get publishers by stream** | **GET** | Lista os publishers que escrevem em um stream específico. |
| **Streams - Get all stream consumers** | **GET** | Lista todos os consumidores de stream do cluster. |
| **Streams - Get stream consumers by vhost** | **GET** | Lista os consumidores de stream de um virtual host. |
| **Auth - Get auth attempts by node** | **GET** | Lista as tentativas de autenticação registradas em um nó. |
| **Auth - Get auth attempts by source** | **GET** | Lista as tentativas de autenticação agrupadas por origem. |
| **Auth - Hash password** | **GET** | Gera o hash de uma senha com o algoritmo configurado no cluster. |
| **Auth - Get OAuth configuration** | **GET** | Retorna a configuração de OAuth 2 do plugin de gerenciamento. |
| **Extensions - Get all extensions** | **GET** | Lista as extensões registradas no plugin de gerenciamento. |
| **Cluster - Rebalance queues** | **POST** | Redistribui as líderes das filas entre os nós do cluster. |

---

## Documentação oficial

- Referência da HTTP API: <https://www.rabbitmq.com/docs/http-api-reference>
- Plugin de gerenciamento: <https://www.rabbitmq.com/docs/management>
