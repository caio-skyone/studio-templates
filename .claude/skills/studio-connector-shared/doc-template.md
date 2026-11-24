<!-- ## Convenções do template — leia antes de preencher

| Notação | Significado |
|---|---|
| `{chave_assim}` | placeholder **deste template**: substitua pelo valor real e **remova as chaves** |
| `{{chave_assim}}` | referência de variável de **conta conectada do Studio**: **mantenha** as chaves duplas no documento final |
| `*não informado*` | célula cujo valor não se sabe. Nunca preencher com ficção plausível |
| `*A preencher: …*` | lacuna de prosa a resolver com o usuário ou com a documentação oficial |

Regras:

- As tabelas de **Configuração da conta conectada** abaixo são **alternativas**:
  escolha **uma** conforme o `authentication_type` do módulo (mapa em
  `auth-config.md`) e apague as outras.
- A linha de exemplo da tabela de **Operações** é um modelo de formato: repita-a
  uma vez por operação e apague o modelo.
- Prosa em português. O `name` da operação fica como está no IAC (normalmente
  `{Domain} - {Action}` em inglês).
- Este bloco de convenções não vai para o documento final — apague-o.
-->

# {Nome_do_Conector}

## Contexto
{insira_o_que_a_api_pode_fazer}
{insira_dominios_e_conceitos_comuns_na_api}
---

## Autenticação

**Tipo:** {Label_do_Tipo_de_Autenticação}

**Configuração da conta conectada:**
(Varia conforme o tipo de autenticação)
| Variável | Valor |
| -------- | ----- |
| password | {{api_token}} |
| username | {{account_email}} |

| Variável | Valor |
| -------- | ----- |
| Host | {{host}} |
| Client ID | {{client_id}} |
| Client Secret | {{client_secret}} |
| Access Token | {{access_token}} |
| Refresh Token | {{refresh_token}} |
| Endpoint de troca de token | {{token_endpoint}} |

| Variável | Valor |
| -------- | ----- |
| host | {{host}} |
| token | {{token}} |

| Variável | Valor |
| -------- | ----- |
| {chave_da_variavel} | {valor_ou_*não informado*} |

---

## Operações

| Nome da Operação | Método | Descrição da Função |
| :--------------- | :----- | :------------------ |
| **{Nome_da_Requisicao}** | **{Metodo_HTTP}** | {Descricao_ou_*sem_descricao*} |

---

## Documentação oficial

*Link da documentação oficial*
