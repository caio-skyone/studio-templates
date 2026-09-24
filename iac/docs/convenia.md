# Convenia

## Contexto

A Convenia é uma plataforma brasileira de gestão de pessoas (RH e departamento pessoal) voltada a pequenas e médias empresas. A API pública v3 cobre o ciclo de vida do colaborador — da admissão ao desligamento — além da estrutura organizacional da empresa e da folha de pagamento.

Principais domínios da API:

- **Colaboradores:** cadastro, atualização, admissão, desligamento, campos customizados, anexos de documentos pessoais, histórico de alterações
- **Férias:** solicitações e períodos aquisitivos por colaborador, férias coletivas da empresa
- **Faltas e afastamentos:** motivos, tipos e o CRUD completo por colaborador
- **Dados do colaborador:** dependentes, contatos de emergência, dados bancários, formação acadêmica, registro de vínculo e salário
- **Estrutura organizacional:** times, departamentos, centros de custo e cargos
- **Benefícios:** catálogo da empresa e vínculo/desvínculo de colaboradores e dependentes
- **Folha:** folhas de pagamento da empresa e seus arquivos
- **Tabelas de domínio (Lookups):** 26 listagens de apoio — etnias, nacionalidades, vínculos empregatícios, estados civis, escolaridade, bancos, estados, cidades, tipos de desligamento e de aviso prévio, identidade de gênero, deficiências, países e demais tabelas usadas para preencher os identificadores exigidos nas operações de escrita

A API aceita até **50 requisições por minuto**. Datas seguem ISO 8601 (`AAAA-MM-DD` ou `AAAA-MM-DDTHH:ii:ss`).

---

## Autenticação

**Tipo:** Autenticação por cabeçalho customizado

**Configuração da conta conectada:**

| Variável | Valor |
| -------- | ----- |
| Host | `https://public-api.convenia.com.br` |
| Porta | 443 |
| token | {{token}} |

> **Nota:** o token vai no cabeçalho `token` (minúsculo), com o valor cru — **sem** o prefixo `Bearer`. Ele é gerado dentro da própria plataforma Convenia.

> **Nota:** o Host é apenas a origem. O prefixo `/api/v3` faz parte do caminho de cada operação, não da conta conectada.

---

## Notas de uso

### Filtros e paginação nas listagens

Nove operações de listagem aceitam os filtros `match`, `different` e `like`, além de `paginate` (máximo de 1000 registros por página) e `page`.

Os três filtros usam **chave variável**: na API real a chave carrega o campo alvo, como `match[hiring_date]=2020-09-09`. No conector eles entraram com as chaves `match[campo]`, `different[campo]` e `like[campo]` — quem monta o fluxo deve **editar a chave na própria operação**, trocando `campo` pelo campo desejado. O valor é o parâmetro; vários valores vão separados por vírgula.

### Corpo das requisições

A documentação da Convenia descreve os corpos em notação de colchetes (`documents[cpf]`, `employee[name]`, `address[zip_code]`). No conector, cada operação de escrita recebe **um único parâmetro `body` do tipo objeto**: informe o JSON completo, com os colchetes virando objetos aninhados.

Exemplo — `documents[cpf]` e `address[zip_code]` viram:

    {"documents": {"cpf": "12345678901"}, "address": {"zip_code": "01310100"}}

### DELETE com corpo obrigatório

Três operações de exclusão exigem corpo, ao contrário do padrão usual:

- **Departments - Delete department** e **Jobs - Delete job** exigem `transfer_to` com o UUID do departamento ou cargo que receberá os vínculos.
- **Cost Centers - Delete cost center** exige `name` — que, apesar do nome, recebe o **UUID** do centro de custo de destino, conforme a documentação oficial.

### Upload de anexos de documentos

**Employees - Upload document file** envia corpo `multipart/form-data` com `file`, `mime_type` e `file_name` parametrizados. O segmento `document_type` do caminho aceita `cpf`, `ctps`, `rg`, `driver-license`, `reservist` e `electoral-card`. Formatos aceitos: pdf, doc, docx, xls, xlsx, ppt, pptx, txt, gif, jpeg, jpg, png, zip, rar e gz.

### Divergências da documentação oficial

- **Absences - Get absence types** — a documentação oficial publica a **mesma URL** (`/api/v3/employees/absences/motives`) nas seções "Obter motivos" e "Obter tipos". O conector mapeou os tipos para `/api/v3/employees/absences/types`, que é a intenção evidente. **Confirme em runtime antes de usar essa operação em produção.**
- **Cost Centers - Create cost center** — usa `POST /api/v3/companies/cost-center`, no **singular**, enquanto as outras três operações do domínio usam `cost-centers`. É como a documentação oficial publica.
- As operações de motivos e tipos de faltas são **globais**, não por colaborador, apesar do título das seções na documentação sugerir o contrário.

### Fora de escopo

A Convenia publica 13 eventos de **webhook** (admissão iniciada e finalizada, desligamento, criação/aprovação/atualização de férias, alteração de perfil e de dados salariais, criação/atualização/deleção de faltas e aniversariantes do dia). Webhooks são entregas feitas pela Convenia para uma URL configurada na plataforma — não são operações REST chamáveis e, por isso, não fazem parte deste conector.

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **Lookups - Get ethnicities** | **GET** | Retorna todas as etnias disponíveis na Convenia. |
| **Lookups - Get nationalities** | **GET** | Retorna todas as nacionalidades disponíveis na Convenia. |
| **Lookups - Get employment relationships** | **GET** | Retorna todos os tipos de vínculo empregatício disponíveis na Convenia. |
| **Lookups - Get marital statuses** | **GET** | Retorna todos os estados civis disponíveis na Convenia. |
| **Lookups - Get education types** | **GET** | Retorna todos os tipos de escolaridade disponíveis na Convenia. |
| **Lookups - Get bank account types** | **GET** | Retorna todos os tipos de conta bancária disponíveis na Convenia. |
| **Lookups - Get banks** | **GET** | Retorna a listagem de bancos disponíveis na Convenia. |
| **Lookups - Get states** | **GET** | Retorna todos os estados disponíveis na Convenia. |
| **Lookups - Get cities** | **GET** | Retorna as cidades disponíveis na Convenia, opcionalmente filtradas por estado. |
| **Lookups - Get dismissal types** | **GET** | Retorna todos os tipos de desligamento disponíveis na Convenia. |
| **Lookups - Get termination notice types** | **GET** | Retorna todos os tipos de aviso prévio disponíveis na Convenia. |
| **Lookups - Get gender identities** | **GET** | Retorna todas as identidades de gênero disponíveis na Convenia. |
| **Lookups - Get emergency contact relations** | **GET** | Retorna os tipos de relacionamento de contatos de emergência disponíveis na Convenia. |
| **Lookups - Get admission types** | **GET** | Retorna todos os tipos de admissão disponíveis na Convenia. |
| **Lookups - Get disability types** | **GET** | Retorna todos os tipos de deficiência disponíveis na Convenia. |
| **Lookups - Get payment methods** | **GET** | Retorna todos os tipos de pagamento disponíveis na Convenia. |
| **Lookups - Get salary types** | **GET** | Retorna todos os tipos de salário disponíveis na Convenia. |
| **Lookups - Get stability types** | **GET** | Retorna todos os tipos de estabilidade disponíveis na Convenia. |
| **Lookups - Get dependent relations** | **GET** | Retorna os tipos de relacionamento de dependentes disponíveis na Convenia. |
| **Lookups - Get document genders** | **GET** | Retorna as opções de gênero no documento disponíveis na Convenia. |
| **Lookups - Get visa types** | **GET** | Retorna os tipos de visto para estrangeiros disponíveis na Convenia. |
| **Lookups - Get entry conditions** | **GET** | Retorna as condições de ingresso de estrangeiros disponíveis na Convenia. |
| **Lookups - Get residence times** | **GET** | Retorna as opções de tempo de residência no Brasil para estrangeiros. |
| **Lookups - Get address descriptions** | **GET** | Retorna as opções de descrição do logradouro para endereços no exterior. |
| **Lookups - Get countries** | **GET** | Retorna a listagem de países disponíveis na Convenia. |
| **Lookups - Get worker categories** | **GET** | Retorna as categorias de trabalhadores disponíveis na Convenia. |
| **Tokens - Get token permissions** | **GET** | Retorna o detalhe do token de integração e as permissões associadas a ele. |
| **Employees - Get all employees** | **GET** | Retorna todos os colaboradores da empresa, com filtros e paginação opcionais. |
| **Employees - Get dismissed employees** | **GET** | Retorna os colaboradores desligados, opcionalmente limitados a um intervalo de datas. |
| **Employees - Get employee** | **GET** | Retorna os dados de um colaborador específico. |
| **Employees - Get salary history** | **GET** | Retorna o histórico salarial de um colaborador. |
| **Employees - Get dependents** | **GET** | Retorna os dependentes vinculados a um colaborador. |
| **Employees - Get benefits** | **GET** | Retorna os benefícios vinculados a um colaborador específico. |
| **Employees - Get change histories** | **GET** | Retorna as alterações registradas para um colaborador, com filtros e paginação opcionais. |
| **Employees - Get change history** | **GET** | Retorna uma alteração específica registrada para um colaborador. |
| **Employees - Get vacation solicitations** | **GET** | Retorna as solicitações de férias de um colaborador, com filtros e paginação opcionais. |
| **Employees - Get vacation solicitation** | **GET** | Retorna uma solicitação de férias específica de um colaborador. |
| **Employees - Get vacation solicitation file** | **GET** | Retorna um arquivo anexado a uma solicitação de férias de um colaborador. |
| **Employees - Get vacation periods** | **GET** | Retorna os períodos aquisitivos de férias de um colaborador, com filtros e paginação opcionais. |
| **Employees - Get vacation period** | **GET** | Retorna um período aquisitivo de férias específico de um colaborador. |
| **Employees - Start admission** | **POST** | Inicia o processo de admissão de um colaborador na Convenia. |
| **Employees - Start dismissal** | **POST** | Inicia o processo de desligamento de um colaborador. |
| **Employees - Set custom field values** | **POST** | Atribui valores aos campos customizados de um colaborador. |
| **Employees - Upload document file** | **POST** | Envia um anexo para um documento pessoal do colaborador. |
| **Employees - Update employee** | **PUT** | Atualiza os dados cadastrais de um colaborador. |
| **Dependents - Update dependent** | **PUT** | Atualiza os dados de um dependente de um colaborador. |
| **Emergency Contacts - Update contact** | **PUT** | Atualiza os dados de um contato de emergência de um colaborador. |
| **Bank Accounts - Update bank account** | **PUT** | Atualiza os dados bancários de um colaborador. |
| **Educations - Create education** | **POST** | Cria um registro de formação acadêmica para um colaborador. |
| **Educations - Update education** | **PUT** | Atualiza um registro de formação acadêmica de um colaborador. |
| **Educations - Delete education** | **DELETE** | Exclui um registro de formação acadêmica de um colaborador. |
| **Salaries History - Create salary record** | **POST** | Cria um registro de vínculo e salário para um colaborador. |
| **Salaries History - Update salary record** | **PUT** | Atualiza um registro de vínculo e salário de um colaborador. |
| **Absences - Get absence motives** | **GET** | Retorna os motivos de faltas e afastamentos disponíveis na Convenia. |
| **Absences - Get absence types** | **GET** | Retorna os tipos de faltas e afastamentos disponíveis na Convenia. |
| **Absences - Get all absences** | **GET** | Retorna todas as faltas e afastamentos de um colaborador. |
| **Absences - Get absence** | **GET** | Retorna uma falta ou afastamento específico de um colaborador. |
| **Absences - Create absence** | **POST** | Cria uma falta ou afastamento para um colaborador. |
| **Absences - Update absence** | **PUT** | Atualiza uma falta ou afastamento de um colaborador. |
| **Absences - Delete absence** | **DELETE** | Exclui uma falta ou afastamento de um colaborador. |
| **Company - Get custom fields** | **GET** | Retorna todos os campos customizados configurados na empresa. |
| **Company - Get collective vacations** | **GET** | Retorna as solicitações de férias coletivas da empresa, com filtros e paginação opcionais. |
| **Company - Get collective vacation** | **GET** | Retorna uma solicitação de férias coletivas específica da empresa. |
| **Benefits - Get all benefits** | **GET** | Retorna todos os benefícios cadastrados na empresa. |
| **Benefits - Get benefit** | **GET** | Retorna um benefício específico da empresa. |
| **Benefits - Get benefit employees** | **GET** | Retorna os colaboradores vinculados a um benefício da empresa. |
| **Benefits - Upsert benefit employees** | **PUT** | Vincula ou desvincula colaboradores de um benefício, conforme o campo is_active de cada item. |
| **Benefits - Upsert benefit dependents** | **PUT** | Vincula ou desvincula dependentes de um benefício, conforme o campo is_active de cada item. |
| **Teams - Get all teams** | **GET** | Retorna todos os times cadastrados na empresa. |
| **Departments - Get all departments** | **GET** | Retorna todos os departamentos cadastrados na empresa. |
| **Departments - Create department** | **POST** | Cria um departamento na empresa. |
| **Departments - Update department** | **PUT** | Atualiza o nome de um departamento da empresa. |
| **Departments - Delete department** | **DELETE** | Exclui um departamento e transfere seus colaboradores para o departamento indicado em transfer_to. |
| **Cost Centers - Get all cost centers** | **GET** | Retorna todos os centros de custo cadastrados na empresa. |
| **Cost Centers - Create cost center** | **POST** | Cria um centro de custo na empresa. A documentação usa o caminho no singular nesta operação. |
| **Cost Centers - Update cost center** | **PUT** | Atualiza o nome de um centro de custo da empresa. |
| **Cost Centers - Delete cost center** | **DELETE** | Exclui um centro de custo e transfere seus vínculos para o centro de custo informado no corpo. |
| **Jobs - Get all jobs** | **GET** | Retorna todos os cargos cadastrados na empresa. |
| **Jobs - Create job** | **POST** | Cria um cargo na empresa. |
| **Jobs - Update job** | **PUT** | Atualiza os dados de um cargo da empresa. |
| **Jobs - Delete job** | **DELETE** | Exclui um cargo e transfere seus colaboradores para o cargo indicado em transfer_to. |
| **Payrolls - Get all payrolls** | **GET** | Retorna todas as folhas de pagamento da empresa, com filtros e paginação opcionais. |
| **Payrolls - Get payroll** | **GET** | Retorna uma folha de pagamento específica da empresa. |
| **Payrolls - Get payroll file** | **GET** | Retorna um arquivo de uma folha de pagamento específica da empresa. |

---

## Documentação oficial

https://docs-api.convenia.com.br/
