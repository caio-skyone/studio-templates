# Como usar OAuth2 com callback no Skyone Studio?

## O que é o fluxo Authorization Code?

O fluxo **Authorization Code** é o tipo de OAuth2 utilizado quando a autenticação exige a interação direta do usuário. O ciclo completo funciona da seguinte forma:

1. A plataforma A redireciona o usuário para a plataforma B, onde ele realiza o login
2. Após autenticar, a plataforma B redireciona o usuário de volta para a plataforma A usando uma **URL pré-cadastrada** (o callback/redirect URI), anexando um `code` temporário como parâmetro de query
3. A plataforma A usa esse `code` para fazer uma requisição à plataforma B, recebendo em troca os tokens de acesso (`access_token` e `refresh_token`)

Esse fluxo é comum em APIs públicas de plataformas consolidadas, quando **não é possível autenticar sem a interação do usuário** — o que o diferencia do fluxo **Client Credentials**, onde a autenticação é feita diretamente entre sistemas.

---

## Por que o Studio não possui um callback nativo?

O Skyone Studio não possui uma rota de callback pré-configurada. Para que uma conta funcione de forma autônoma e contínua, ela necessita **no mínimo do `refresh_token`** acessível para renovar o `access_token` automaticamente.

Por isso, é necessário obter os tokens antecipadamente, fora do fluxo padrão de criação de conta. Existem dois caminhos possíveis:

- **Usando o Skyone Studio** (Webhook como receptor do callback)
- **Usando o Postman** (interceptando o callback localmente)

Opte pelo método que lhe for mais confortável.
