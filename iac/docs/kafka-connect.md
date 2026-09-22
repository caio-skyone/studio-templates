# Kafka Connect

## Contexto

O Apache Kafka Connect é o framework de integração do Kafka: ele roda *connectors* que movem dados entre tópicos Kafka e sistemas externos — bancos de dados, object storage, filas, SaaS. Um connector do tipo *source* lê de um sistema externo e escreve em tópicos; um *sink* faz o caminho inverso.

Este módulo cobre a **REST Interface** exposta pelo worker Connect em modo distribuído. É uma API de **administração**: ela não produz nem consome mensagens, ela gerencia o ciclo de vida dos connectors que fazem isso. Para trafegar mensagens via HTTP seria necessário outro produto (Confluent REST Proxy), que não faz parte deste conector.

Principais domínios da API:

- **Connectors:** criar, listar, consultar, atualizar configuração, pausar, retomar, parar, reiniciar e remover instâncias de connector
- **Tasks:** as unidades de trabalho paralelas de cada connector — listar, consultar estado e reiniciar individualmente
- **Topics:** quais tópicos cada connector consome ou produz, e o reset desse conjunto
- **Offsets:** leitura, alteração e zeramento das posições de leitura/escrita do connector
- **Plugins:** quais classes de connector estão instaladas no worker, e validação de uma configuração contra elas

Conceitos que aparecem nas respostas: o **estado** de um connector e de suas tasks (`RUNNING`, `PAUSED`, `STOPPED`, `FAILED`, `UNASSIGNED`), o **`connector.class`** que identifica o plugin, e o **`tasks.max`** que limita o paralelismo.

> **Nota:** o endpoint raiz `GET /` (versão do worker, commit do Git e ID do cluster Kafka) **não** está neste conector. O Studio exige ao menos um segmento de caminho na operação e rejeita caminho vazio, então essa chamada não é representável em IAC com `url_type` `base-url`.

> **Nota:** as operações **Offsets - Alter** e **Offsets - Reset** exigem que o connector esteja parado (`Connectors - Stop`) antes da chamada; o worker rejeita a alteração de offsets de um connector em execução.

---

## Autenticação

**Tipo:** Autenticação básica (HTTP Basic)

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `http://<>host-do-worker-connect</>` |
| Porta | 8083 |
| password | {{api_token}} |
| username | {{account_email}} |

> **Nota:** o Host é o endereço do worker Kafka Connect do seu ambiente, não um domínio público — por isso vem como parâmetro. A porta padrão da REST Interface é **8083**, e não 443: em instalação self-managed o worker normalmente escuta em HTTP na 8083. Se o worker estiver atrás de TLS ou de um gateway, ajuste Host e Porta conforme o seu ambiente.

> **Nota:** o Kafka Connect self-managed sobe **sem autenticação** por padrão. As credenciais `username`/`password` correspondem ao HTTP Basic configurado no worker (`rest.extension.classes` com `BasicAuthSecurityRestExtension`) ou, no Confluent Cloud, ao par **API key / API secret**. Em um worker sem segurança habilitada, preencha com qualquer valor ou troque o tipo de autenticação do módulo para `no-auth`.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Connectors - List** | **GET** | Lista os connectors ativos no cluster Connect. |
| **Connectors - Create** | **POST** | Cria um novo connector com nome e configuração. |
| **Connectors - Get** | **GET** | Retorna as informações e a configuração de um connector. |
| **Connectors - Delete** | **DELETE** | Remove o connector e encerra todas as suas tasks. |
| **Connectors - Get config** | **GET** | Retorna apenas a configuração do connector. |
| **Connectors - Upsert config** | **PUT** | Cria ou atualiza a configuração de um connector. |
| **Connectors - Get status** | **GET** | Retorna o estado do connector e de cada uma de suas tasks. |
| **Connectors - Restart** | **POST** | Reinicia o connector, opcionalmente incluindo as tasks. |
| **Connectors - Pause** | **PUT** | Pausa o connector e suas tasks. |
| **Connectors - Resume** | **PUT** | Retoma um connector pausado. |
| **Connectors - Stop** | **PUT** | Para o connector sem removê-lo, liberando suas tasks. |
| **Tasks - List** | **GET** | Lista as tasks em execução do connector, com suas configurações. |
| **Tasks - Get status** | **GET** | Retorna o estado de uma task específica do connector. |
| **Tasks - Restart** | **POST** | Reinicia uma task específica do connector. |
| **Topics - List** | **GET** | Lista os tópicos que o connector consome ou produz. |
| **Topics - Reset** | **PUT** | Limpa o conjunto de tópicos registrado para o connector. |
| **Offsets - Get** | **GET** | Retorna os offsets atuais do connector. |
| **Offsets - Alter** | **PATCH** | Altera os offsets do connector, que precisa estar parado. |
| **Offsets - Reset** | **DELETE** | Zera os offsets do connector, que precisa estar parado. |
| **Plugins - List** | **GET** | Lista os plugins de connector instalados no worker. |
| **Plugins - Validate config** | **PUT** | Valida uma configuração contra o plugin informado e retorna os erros. |

---

## Documentação oficial

https://docs.confluent.io/platform/current/connect/references/restapi.html
