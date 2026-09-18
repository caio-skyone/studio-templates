# Fluxo de callback de OAuth2 com Webhook

Esse tutorial detalha como obter tokens de acesso com OAuth 2 por meio de um fluxo que exija callback (Authorization Code) usando uma automação do Skyone Studio.

## Pré-requisitos

- Um conector que possua a operação para trocar authorization code por tokens de acesso, o que torna necessário **criar uma credencial vazia** apenas para
usar o conector sem tokens de acesso, incluindo remover o chave valor padrão do **Parâmetros no cabeçalho da requisição após autenticação**, visto que
em algumas APIs enviar o header com token vazio/inválido irá provocar erros mesmo nos endpoints de autenticação.

- Variáveis específicas da plataforma, como a URL de autenticação, Client ID, Client Secret, entre outros.

- Um espaço utilizável do Skyone Studio

## Passo a passo

1. Crie uma automação com um gatilho de webhook;

2. Abra o gatilho e marque **Utilizar dados da requisição**;

3. Acesse a aba de **Query** abaixo e insira a chave ***code*** (não insira um valor para a chave);

4. Copie o link do webhook que foi gerado e salve as alterações;

5. Use (ou crie) a operação que troca o authorization code pelos tokens de acesso na API que está autenticando passando como parâmetro a variável code do webhook;

6. Ative a automação;

7. Na plataforma onde está se autenticando, registre a URL do Webhook como **Redirect URI** (URI de redirecionamento) ou equivalente;

8. Acesse a URL de autenticação da plataforma respectiva (lembre-se de apontar a URL do webhook como Redirect URI);

9. Após fazer login e confirmar a autenticação, a automação será executada a partir do webhook. Acesse os Logs da sua automação, veja os logs do componente usado para trocar authorization code pelos tokens;

10. Se a autenticação foi bem sucedida, você verá access token, refresh_token e/ou outras variáveis da API respectiva, use estas variáveis para preencher sua credencial. Lembre-se de reinserir **Parâmetros no cabeçalho da requisição após autenticação** caso tenham sido removidos anteriormente.

