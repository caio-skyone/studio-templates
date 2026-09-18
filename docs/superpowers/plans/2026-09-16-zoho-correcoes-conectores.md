# Correções nos conectores Zoho — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** corrigir os conectores Zoho Analytics, Desk, CRM e WorkDrive — `CONFIG` na query em vez do corpo, corpos ausentes em operações de escrita e os nomes do domínio Appointments — aplicando as correções no Studio remoto e no IAC versionado.

**Architecture:** cada conector é corrigido pelo mesmo ciclo de seis passos: `pull_connector` traz o conector publicado para um draft cujos ids são os ids reais do Studio; `export_draft` grava esse draft em um arquivo; um script Python determinístico reescreve o arquivo preservando todos os ids; `import_connector_draft` sobrescreve o draft com o arquivo corrigido; `diff_draft` e `validate_draft` provam que a transformação é a esperada; `patch_connector(dry_run=True)` mostra o plano e, só com aprovação, aplica. O IAC de `iac/` é então regerado a partir do draft. Nenhuma edição é feita à mão em JSON de centenas de operações — toda mudança passa por um script versionado em `scratchpad/tools/`, que é o artefato auditável.

**Tech Stack:** Python 3.13 (stdlib apenas — `json`, `re`, `html`, `argparse`), `jq` para verificação, ferramentas MCP do `studio-connector-mcp`, `curl` para baixar a doc HTML do Zoho Desk.

**Spec:** `docs/superpowers/specs/2026-09-16-zoho-correcoes-conectores-design.md`

## Global Constraints

- **`patch_connector` sempre com `dry_run=True` primeiro.** Mostrar o plano ao usuário e só aplicar com um "sim" explícito. Uma aprovação não vale para o conector seguinte.
- **Nunca `delete_missing_operations=True`.** Nenhuma tarefa deste plano remove operações.
- **Nunca `allow_remote_drift=True` sem aprovação explícita.** Se o dry-run reportar `drifted`, mostrar a lista ao usuário antes de decidir.
- **Bug conhecido:** `push_connector` falha com `Invalid request parameters` em qualquer draft com texto acentuado. Não se sabe se `patch_connector` compartilha o defeito. Se o dry-run ou a aplicação falhar com esse erro genérico, **parar o plano inteiro e reportar** — insistir não adianta e `skip_validation` não contorna.
- **Ordem obrigatória:** Task 1 → 2 (Analytics) antes de tudo. A Task 2 é o portão que prova que `patch_connector` funciona.
- **Ids são sagrados.** Todo script deste plano reescreve campos dentro de operações e parâmetros existentes, ou acrescenta parâmetros novos; nunca regenera `id` de operação nem reordena a lista `operations`.
- **`sample: "{}"`** em todo parâmetro criado, salvo quando a doc oficial fornecer um exemplo real — nesse caso o exemplo prevalece.
- **`type` e `required` seguem a convenção de cada conector:** Desk `object`/`false`, CRM `object`/`false`, WorkDrive `string`/`true`, Analytics `string`/`true`.
- **Normalização de `query` do `CLAUDE.md`:** todo arquivo gravado em `iac/` precisa de `request.query` como array irmão de `request.header` (`[]` quando vazio) e **sem** `request.url.query`. O script `scratchpad/tools/migrate_query_to_root.py` já faz isso.
- **Fora de escopo:** o conector Zoho Books não é tocado. As 13 operações de ação do Desk e as 26 do Analytics que estão sem corpo estão corretas e permanecem como estão.

---

### Task 1: Script `zoho_fix.py` com o subcomando `analytics-config`

Cria a ferramenta que converte o `CONFIG` do Zoho Analytics de corpo `form-urlencoded` para parâmetro de query, e prova a conversão contra o IAC versionado antes de qualquer contato com o Studio.

**Files:**
- Create: `scratchpad/tools/zoho_fix.py`
- Test: verificação por `python3`/`jq` sobre `iac/zoho-analytics.json` (este repositório não tem suíte de testes; a verificação é uma asserção executável, descrita em cada passo)

**Interfaces:**
- Produces: `zoho_fix.py analytics-config <entrada.json> -o <saida.json>` — lê um módulo IAC, grava outro com o `CONFIG` convertido, e imprime no stderr um relatório `convertidas=N ignoradas_json=N intactas=N`. Usado nas Tasks 2.
- Produces: a constante `CONFIG_DESC` e `CONFIG_SAMPLE_FALLBACK`, reusadas pelo subcomando `bodies` da Task 4.

**Contexto factual (medido em 2026-09-16, não precisa ser reverificado):**

`iac/zoho-analytics.json` tem 176 operações. Das que têm o parâmetro `body` (78):
- **76** declaram o header `Content-Type: application/x-www-form-urlencoded`. São as que devem virar `CONFIG` na query. O corpo delas hoje é `raw: "<>body</>"` — repare que nem sequer é `CONFIG=<>body</>`, ou seja, está errado até segundo a própria teoria do corpo urlencoded.
- **2** declaram `Content-Type: application/json` (`Views - Auto Analyse View` e `Data - Sort Data by Columns`). Recebem JSON puro de verdade e **não podem ser convertidas**.

Outras 22 operações já estão no formato correto: `request.query` com `{"key": "CONFIG", "value": "<>config</>"}` e um parâmetro `config` do tipo `string`, `required: true`. Esse é o alvo da conversão.

As 26 operações de escrita sem `body` e sem `CONFIG` (`/favorite`, `/default`, `/sync`, `/execute`, `/wlaccess`, `/trigger`, `/autoanalyse` em coluna, e os `DELETE` puros) foram conferidas contra `scratchpad/iacs/zoho-analytics/spec_inlined.json`: nenhuma declara `requestBody` nem parâmetro de query. São ações sem payload e **ficam como estão**.

- [ ] **Step 1: Escrever a verificação que deve falhar**

Crie `/tmp/check_analytics.py` (arquivo descartável, não versionado):

```python
#!/usr/bin/env python3
"""Verifica o estado-alvo de iac/zoho-analytics.json. Sai 1 se algo estiver errado."""
import json, sys

iac = json.load(open(sys.argv[1], encoding="utf-8"))
erros = []
n_config = n_json = 0

for op in iac["operations"]:
    req = op["request"]
    nomes = {p["name"] for p in op["parameters"]}
    headers = {h["key"]: h["value"] for h in req.get("header", [])}
    ctype = headers.get("Content-Type", "")
    chaves_query = {q["key"] for q in req.get("query", [])}

    if ctype == "application/x-www-form-urlencoded":
        erros.append("%s: ainda tem Content-Type urlencoded" % op["name"])
    if "body" in nomes and ctype != "application/json":
        erros.append("%s: ainda tem parametro 'body' sem ser JSON puro" % op["name"])

    if "CONFIG" in chaves_query:
        n_config += 1
        cfg = [p for p in op["parameters"] if p["name"] == "config"]
        if not cfg:
            erros.append("%s: CONFIG na query sem parametro 'config'" % op["name"])
        elif cfg[0]["type"] != "string" or not cfg[0]["required"]:
            erros.append("%s: parametro 'config' deve ser string e required" % op["name"])
        elif not cfg[0]["sample"]:
            erros.append("%s: parametro 'config' sem sample" % op["name"])
        valor = [q["value"] for q in req["query"] if q["key"] == "CONFIG"][0]
        if valor != "<>config</>":
            erros.append("%s: CONFIG deve valer <>config</>, vale %r" % (op["name"], valor))
        if req.get("body", {}).get("raw"):
            erros.append("%s: CONFIG na query mas corpo nao vazio" % op["name"])
    if ctype == "application/json":
        n_json += 1

if len(iac["operations"]) != 176:
    erros.append("total de operacoes mudou: %d" % len(iac["operations"]))
if n_config != 98:
    erros.append("esperava 98 operacoes com CONFIG na query, achei %d" % n_config)
if n_json != 2:
    erros.append("esperava 2 operacoes JSON puro, achei %d" % n_json)

for e in erros[:20]:
    print("FALHA:", e)
print("total=%d  com CONFIG=%d  json puro=%d  erros=%d"
      % (len(iac["operations"]), n_config, n_json, len(erros)))
sys.exit(1 if erros else 0)
```

`98 = 22 já corretas + 76 convertidas`.

- [ ] **Step 2: Rodar a verificação e confirmar que falha**

```bash
cd /home/caiomtho/projects/studio-templates
python3 /tmp/check_analytics.py iac/zoho-analytics.json; echo "exit=$?"
```

Esperado: `exit=1`, com falhas do tipo `ainda tem Content-Type urlencoded` e `total=176  com CONFIG=22  json puro=2`.

- [ ] **Step 3: Escrever o `zoho_fix.py`**

Crie `scratchpad/tools/zoho_fix.py`:

```python
#!/usr/bin/env python3
"""zoho_fix.py — correcoes deterministicas nos modulos IAC dos conectores Zoho.

Le um modulo IAC, reescreve campos dentro das operacoes existentes e grava outro
arquivo. NUNCA gera id novo de operacao, nunca reordena a lista de operacoes e
nunca remove operacao: os ids sao o que faz o patch_connector ser atualizacao e
nao duplicacao.

Subcomandos:
  analytics-config  CONFIG do Zoho Analytics: de corpo urlencoded para query.
  bodies            adiciona o parametro 'body' nas operacoes listadas.
  crm-appointments  renomeia o dominio Appointments e conserta o delete em massa.
"""
import argparse
import json
import sys
import uuid

CONFIG_DESC = (
    "JSON de configuração da chamada, enviado no parâmetro CONFIG da query "
    "string. Os campos aceitos variam conforme a operação; use o sample como "
    "referência."
)
CONFIG_SAMPLE_FALLBACK = "{}"
URLENCODED = "application/x-www-form-urlencoded"


def carregar(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def gravar(iac, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(iac, fh, ensure_ascii=False, indent=1)


def corpo_vazio():
    return {"mode": "raw", "raw": "", "options": {"raw": {"language": "json"}}}


def analytics_config(iac, samples):
    """Converte CONFIG de corpo urlencoded para parametro de query.

    Alvo: operacao com Content-Type urlencoded e parametro 'body'. As de
    Content-Type application/json recebem JSON puro de verdade e ficam intactas.
    """
    convertidas = ignoradas_json = intactas = 0

    for op in iac["operations"]:
        req = op["request"]
        headers = req.get("header", [])
        ctype = next((h["value"] for h in headers if h["key"] == "Content-Type"), "")
        body_param = next((p for p in op["parameters"] if p["name"] == "body"), None)

        if body_param is None or ctype != URLENCODED:
            if body_param is not None and ctype == "application/json":
                ignoradas_json += 1
            else:
                intactas += 1
            continue

        # o sample real do parametro 'body' vira o sample do 'config'
        sample = samples.get(op["name"]) or body_param.get("sample") or CONFIG_SAMPLE_FALLBACK

        # 'body' vira 'config': mantem o id do parametro, muda nome/tipo/descricao
        body_param["name"] = "config"
        body_param["type"] = "string"
        body_param["required"] = True
        body_param["sensitive"] = False
        body_param["description"] = CONFIG_DESC
        body_param["sample"] = sample

        # corpo esvazia e o Content-Type urlencoded sai junto: sem corpo, sem tipo
        req["body"] = corpo_vazio()
        req["header"] = [h for h in headers if h["key"] != "Content-Type"]

        query = req.setdefault("query", [])
        if not any(q["key"] == "CONFIG" for q in query):
            query.append({"key": "CONFIG", "value": "<>config</>", "enabled": True})

        convertidas += 1

    return {"convertidas": convertidas, "ignoradas_json": ignoradas_json,
            "intactas": intactas}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("analytics-config")
    p.add_argument("entrada")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--samples", help="JSON {nome_da_operacao: sample}", default=None)

    args = ap.parse_args()
    iac = carregar(args.entrada)

    if args.cmd == "analytics-config":
        samples = carregar(args.samples) if args.samples else {}
        rel = analytics_config(iac, samples)
    else:
        ap.error("subcomando nao implementado: %s" % args.cmd)

    gravar(iac, args.out)
    print(" ".join("%s=%s" % kv for kv in sorted(rel.items())), file=sys.stderr)


if __name__ == "__main__":
    main()
```

Note que `uuid` está importado mas ainda não é usado — a Task 4 usa para gerar ids de parâmetros novos. Deixe o import.

- [ ] **Step 4: Rodar o script sobre o IAC versionado e verificar**

```bash
cd /home/caiomtho/projects/studio-templates
python3 scratchpad/tools/zoho_fix.py analytics-config \
  iac/zoho-analytics.json -o /tmp/analytics-fixed.json
python3 /tmp/check_analytics.py /tmp/analytics-fixed.json; echo "exit=$?"
```

Esperado no stderr: `convertidas=76 ignoradas_json=2 intactas=98`.
Esperado da verificação: `exit=0` e `total=176  com CONFIG=98  json puro=2  erros=0`.

Se `convertidas` vier diferente de 76, **pare**: a premissa medida mudou e o plano precisa ser revisto, não o número ajustado.

- [ ] **Step 5: Conferir que só o esperado mudou**

```bash
cd /home/caiomtho/projects/studio-templates
python3 - <<'EOF'
import json
a = json.load(open("iac/zoho-analytics.json", encoding="utf-8"))
b = json.load(open("/tmp/analytics-fixed.json", encoding="utf-8"))
assert [o["id"] for o in a["operations"]] == [o["id"] for o in b["operations"]], "ids de operacao mudaram"
assert a["id"] == b["id"] and a["name"] == b["name"]
for x, y in zip(a["operations"], b["operations"]):
    assert x["name"] == y["name"], (x["name"], y["name"])
    assert x["description"] == y["description"], x["name"]
    assert x["request"]["method"] == y["request"]["method"], x["name"]
    assert x["request"]["url"] == y["request"]["url"], x["name"]
    assert [p["id"] for p in x["parameters"]] == [p["id"] for p in y["parameters"]], x["name"]
print("OK: ids, nomes, descricoes, metodos e rotas preservados")
EOF
```

Esperado: `OK: ids, nomes, descricoes, metodos e rotas preservados`.

- [ ] **Step 6: Commit**

```bash
cd /home/caiomtho/projects/studio-templates
git add scratchpad/tools/zoho_fix.py
git commit -m "feat(tools): zoho_fix.py converte CONFIG do Analytics para query

O conector modelava CONFIG como corpo form-urlencoded em 76 operacoes, com
raw '<>body</>' — nem no formato CONFIG=... que a propria teoria exigiria.
A API v2 recebe CONFIG na query string, como as outras 22 operacoes do
conector ja faziam. As 2 operacoes de JSON puro ficam intactas.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Aplicar a correção do Analytics no Studio e no IAC

Primeiro conector do ciclo completo. **É o portão do plano:** se o `patch_connector` falhar aqui com o erro genérico de encoding, as Tasks 4, 5 e 6 não devem ser tentadas.

**Files:**
- Modify: `iac/zoho-analytics.json`
- Modify: `docs/connectors/zoho-analytics.md:12,118,119,130`
- Remoto: conector `Zoho Analytics`, `module_id` `McnWvZq9EZ`

**Interfaces:**
- Consumes: `zoho_fix.py analytics-config` da Task 1.
- Produces: a resposta à pergunta "o `patch_connector` funciona com texto acentuado?" — de que dependem as Tasks 4, 5 e 6.

- [ ] **Step 1: Trazer o conector publicado para um draft**

Chame a ferramenta MCP:

```
pull_connector(module_id="McnWvZq9EZ")
```

Anote `inherited_issues` do retorno. O `draft_id` é o próprio `McnWvZq9EZ`.

- [ ] **Step 2: Exportar o draft para arquivo**

```
export_draft(id="McnWvZq9EZ", file_path="/tmp/zoho-analytics-pulled.json")
```

- [ ] **Step 3: Confirmar que o remoto bate com o IAC versionado**

```bash
cd /home/caiomtho/projects/studio-templates
python3 - <<'EOF'
import json
r = json.load(open("/tmp/zoho-analytics-pulled.json", encoding="utf-8"))
l = json.load(open("iac/zoho-analytics.json", encoding="utf-8"))
nr = {o["name"] for o in r["operations"]}
nl = {o["name"] for o in l["operations"]}
print("remoto=%d local=%d" % (len(r["operations"]), len(l["operations"])))
print("so no remoto:", sorted(nr - nl)[:10])
print("so no local: ", sorted(nl - nr)[:10])
EOF
```

Esperado: `remoto=176 local=176`, as duas listas de diferença vazias. Se houver divergência, alguém editou o conector pela UI do Studio — **pare e mostre a diferença ao usuário** antes de continuar.

- [ ] **Step 4: Aplicar a transformação sobre o draft exportado**

```bash
cd /home/caiomtho/projects/studio-templates
python3 scratchpad/tools/zoho_fix.py analytics-config \
  /tmp/zoho-analytics-pulled.json -o /tmp/zoho-analytics-fixed.json
python3 /tmp/check_analytics.py /tmp/zoho-analytics-fixed.json; echo "exit=$?"
```

Esperado: `convertidas=76 ignoradas_json=2 intactas=98` e `exit=0`.

- [ ] **Step 5: Sobrescrever o draft com o arquivo corrigido**

```
import_connector_draft(file_path="/tmp/zoho-analytics-fixed.json")
```

O draft tem o mesmo `id` (`McnWvZq9EZ`), então a importação sobrescreve o draft trazido pelo `pull_connector`, preservando os ids reais do Studio. Confira no retorno: `op_count` deve ser 176.

- [ ] **Step 6: Provar que o draft bate com o arquivo e validar**

```
diff_draft(id="McnWvZq9EZ", file_path="/tmp/zoho-analytics-fixed.json")
validate_draft(id="McnWvZq9EZ")
```

Esperado: `diff_draft` com zero diferenças; `validate_draft` com `ok: true`. O validador checa a regra bidirecional — todo `<>ref</>` tem parâmetro declarado e todo parâmetro é referenciado —, que é exatamente o que pega um `body` órfão se a conversão tiver escapado alguma operação.

- [ ] **Step 7: Dry-run do patch e portão de aprovação**

```
patch_connector(draft_id="McnWvZq9EZ", dry_run=True)
```

Mostre ao usuário: quantas operações seriam atualizadas (esperado: 76), quantas criadas (esperado: 0), quantas removidas (esperado: 0), o aviso `flows_using` se houver, e a lista `drifted` se houver.

**PARE AQUI.** Só siga com um "sim" explícito do usuário.

Se a chamada falhar com `Invalid request parameters` sem detalhe e sem prefixo `local:`/`studio:`, é o bug de encoding UTF-8 do `studio-connector-mcp`. Nesse caso: **pare o plano inteiro**, não tente de novo, não use `skip_validation`, e reporte ao usuário que o remoto está bloqueado por bug de infraestrutura. As Tasks 4, 5 e 6 ficam suspensas; as correções locais de IAC ainda podem ser feitas.

- [ ] **Step 8: Aplicar o patch**

```
patch_connector(draft_id="McnWvZq9EZ", dry_run=False)
```

Sem `delete_missing_operations` e sem `allow_remote_drift`.

- [ ] **Step 9: Confirmar o remoto**

```
get_connector_summary(module_id="McnWvZq9EZ")
```

Esperado: `op_count` 176 — nenhuma criação nem remoção acidental.

- [ ] **Step 10: Regravar o IAC versionado**

```bash
cd /home/caiomtho/projects/studio-templates
cp /tmp/zoho-analytics-fixed.json iac/zoho-analytics.json
python3 scratchpad/tools/migrate_query_to_root.py iac/zoho-analytics.json
python3 /tmp/check_analytics.py iac/zoho-analytics.json; echo "exit=$?"
jq -e '[.operations[] | select(.request.url.query != null)] | length == 0' iac/zoho-analytics.json
```

Esperado: `exit=0` e o `jq -e` saindo 0 (nenhuma operação com `request.url.query`).

- [ ] **Step 11: Atualizar a documentação do conector**

Em `docs/connectors/zoho-analytics.md`, quatro trechos descrevem o modelo antigo como se fosse intencional e ficaram falsos:

- **linha 12** — hoje: "Nos `GET` ele vai na query string; nos `POST`/`PUT`/`DELETE`, no corpo `form-urlencoded`." Troque por: "Ele vai sempre na query string, sob a chave `CONFIG`, em qualquer método."
- **linha 118** — o bloco inteiro "**`CONFIG` na query (`config`) e `CONFIG` no corpo (`body`)**" descreve dois parâmetros que não existem mais. Substitua por um bloco "**`CONFIG` na query (`config`)**" explicando que toda operação que precisa de configuração declara o parâmetro `config`, um JSON que o Studio envia na query string sob a chave `CONFIG`, e que cada operação traz um exemplo real.
- **linha 119** — "**Duas operações usam JSON puro**" continua verdadeiro (`Data - Sort Data by Columns` e `Views - Auto Analyse View`). Mantenha, mas troque "sem envelope `CONFIG`" por "recebem o corpo em `application/json`, sem `CONFIG`" para não sugerir que existe um envelope nas outras.
- **linha 130** — "**Um único parâmetro de corpo por operação**" deve virar "**Um único parâmetro de configuração por operação**", trocando "o corpo é um texto único" por "o `config` é um texto único".

Confira que nenhuma outra menção a corpo urlencoded sobrou:

```bash
cd /home/caiomtho/projects/studio-templates
grep -n "urlencoded\|no corpo\|corpo \`form" docs/connectors/zoho-analytics.md
```

Esperado: nenhuma linha que descreva `CONFIG` indo no corpo.

- [ ] **Step 12: Commit**

```bash
cd /home/caiomtho/projects/studio-templates
git add iac/zoho-analytics.json docs/connectors/zoho-analytics.md
git commit -m "fix(zoho-analytics): CONFIG vai na query, nao no corpo

76 operacoes modelavam CONFIG como corpo form-urlencoded e nao funcionavam.
Agora usam o mesmo formato das outras 22 do conector: parametro config na
query string sob a chave CONFIG. As 2 operacoes de JSON puro ficam intactas.
Aplicado tambem no Studio via patch_connector.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Raspar a doc do Zoho Desk e decidir as 39 operações

Produz a evidência que decide quais das 39 operações do Desk sem corpo são defeito e quais são ações legítimas. Não altera nenhum conector.

**Files:**
- Create: `scratchpad/tools/desk_doc_bodies.py`
- Create: `scratchpad/iacs/zoho-desk/doc_bodies.json` (saída da raspagem)
- Create: `scratchpad/iacs/zoho-desk/decisao-bodies.json` (as 39 classificadas)

**Interfaces:**
- Consumes: nada das tarefas anteriores.
- Produces: `scratchpad/iacs/zoho-desk/decisao-bodies.json`, no formato `{"<nome da operação>": {"has_body": bool, "sample": str, "fonte": "doc"|"ausente"}}`, consumido pela Task 4.

**Contexto factual (verificado em 2026-09-16):**

`https://desk.zoho.com/DeskAPIDocument` é uma página HTML única de ~11,5 MB contendo toda a referência da API. A estrutura: 974 blocos `<div class="totalmain" id="Secao_Operacao">`, e dentro de cada um um snippet `$ curl -X MÉTODO https://desk.zoho.com/api/v1/...` seguido dos headers e, quando a operação recebe corpo, de `-d '{...}'`.

Dois blocos conferidos à mão:
- `Tickets_MarkTicketasRead` — `curl -X POST .../tickets/1892000000988091/markAsRead` com dois `-H` e **nenhum `-d`**. Ação sem corpo.
- `Contacts_CreateContact` — `curl -X POST .../contacts` com dois `-H` e um `-d '{ "zip": "123902", "lastName": "Jack", ... }'`. Corpo com exemplo real.

Os ids nos exemplos são numéricos e longos (`1892000000988091`), o que permite normalizar a rota para placeholder. As rotas do IAC usam `<>nome_do_parametro</>` nos mesmos lugares.

- [ ] **Step 1: Baixar a doc**

```bash
cd /home/caiomtho/projects/studio-templates
mkdir -p scratchpad/iacs/zoho-desk/src
curl -sL -A "Mozilla/5.0" -o scratchpad/iacs/zoho-desk/src/DeskAPIDocument.html \
  https://desk.zoho.com/DeskAPIDocument
wc -c scratchpad/iacs/zoho-desk/src/DeskAPIDocument.html
grep -c 'class="totalmain"' scratchpad/iacs/zoho-desk/src/DeskAPIDocument.html
```

Esperado: cerca de 11.500.000 bytes e 974 blocos. Se vier muito menor, a página mudou ou o download foi bloqueado — **pare e reporte**.

- [ ] **Step 2: Escrever a verificação que deve falhar**

Crie `/tmp/check_desk_decisao.py`:

```python
#!/usr/bin/env python3
"""Verifica que a decisao das 39 operacoes do Desk esta completa e coerente."""
import json, sys

decisao = json.load(open("scratchpad/iacs/zoho-desk/decisao-bodies.json", encoding="utf-8"))
iac = json.load(open("iac/zoho-desk.json", encoding="utf-8"))

vazias = [o["name"] for o in iac["operations"]
          if o["request"]["method"] in ("POST", "PUT", "PATCH")
          and not o["request"].get("body", {}).get("raw")]

erros = []
if len(vazias) != 39:
    erros.append("esperava 39 operacoes vazias, achei %d" % len(vazias))
faltando = [n for n in vazias if n not in decisao]
if faltando:
    erros.append("sem decisao (%d): %s" % (len(faltando), faltando[:5]))
sobrando = [n for n in decisao if n not in vazias]
if sobrando:
    erros.append("decisao para operacao que nao esta vazia: %s" % sobrando[:5])

# as 15 de CRUD de recurso tem de sair com has_body=True
crud = [
    "Accounts - Create Account", "Accounts - Update Account",
    "Calls - Create call", "Calls - Update call",
    "Contacts - Create Contact", "Contacts - Update Contact",
    "Departments - Add department",
    "Events - Create event", "Events - Update an event",
    "Products - Create product", "Products - Update product",
    "Tasks - Create task", "Tasks - Update a task",
    "Tickets - Create a ticket", "Tickets - Update a ticket",
]
for nome in crud:
    if not decisao.get(nome, {}).get("has_body"):
        erros.append("%s: deveria ter has_body=True" % nome)

# as 13 acoes tem de sair com has_body=False
acoes = [
    "Agents - Deactivate agent", "Calls - Clear live call mapping from an activity",
    "Contacts - Dissociate account from contact", "Departments - Enable department",
    "Starredviews - Remove Starred View", "Views - Add Starred View",
    "Tickets - Mark as read", "Tickets - Mark as unread",
    "Tickets - Recalculate Skills for a ticket",
    "Tickets - Revoke Blueprint at Entity Level",
    "Tickets - Delete the during actions transition draft",
    "Follow - Follow the Entity", "Unfollow - UnFollow the entity",
]
for nome in acoes:
    if decisao.get(nome, {}).get("has_body"):
        erros.append("%s: deveria ter has_body=False" % nome)

com = sum(1 for n in vazias if decisao.get(n, {}).get("has_body"))
sem_fonte = [n for n in vazias if decisao.get(n, {}).get("fonte") == "ausente"]
for e in erros[:20]:
    print("FALHA:", e)
print("decididas=%d  com corpo=%d  sem corpo=%d  sem evidencia na doc=%d"
      % (len(vazias), com, len(vazias) - com, len(sem_fonte)))
sys.exit(1 if erros else 0)
```

- [ ] **Step 3: Rodar a verificação e confirmar que falha**

```bash
cd /home/caiomtho/projects/studio-templates
python3 /tmp/check_desk_decisao.py; echo "exit=$?"
```

Esperado: erro de arquivo não encontrado (`decisao-bodies.json` ainda não existe).

- [ ] **Step 4: Escrever o `desk_doc_bodies.py`**

Crie `scratchpad/tools/desk_doc_bodies.py`:

```python
#!/usr/bin/env python3
"""desk_doc_bodies.py — decide, pela doc oficial, quais operacoes do Zoho Desk
recebem corpo.

A spec zohodesk-oas tem 1846 $ref externos para Common.json e 51 das 326
operacoes de escrita chegam sem requestBody. Sem isso nao da para distinguir
"corpo faltando na spec" (POST /contacts) de "acao sem corpo"
(POST /tickets/{id}/markAsRead). A doc HTML resolve: cada operacao tem um
snippet `$ curl -X METODO <url>` e, quando ha corpo, um `-d '...'`.

Mesmo metodo ja usado em books_doc_bodies.py, adaptado a estrutura do Desk:
a doc do Desk e uma pagina unica com blocos <div class="totalmain" id="...">.

Uso:
  desk_doc_bodies.py DOC.html --iac iac/zoho-desk.json \\
      -o scratchpad/iacs/zoho-desk/doc_bodies.json \\
      --decisao scratchpad/iacs/zoho-desk/decisao-bodies.json
"""
import argparse
import html
import json
import re

BLOCO_RE = re.compile(
    r'<div class="totalmain" id="([^"]+)">(.*?)(?=<div class="totalmain"|\Z)', re.S
)
TAG_RE = re.compile(r"<[^>]+>")
# `$ curl -X POST https://desk.zoho.com/api/v1/tickets` — a doc as vezes escreve
# `https:// desk.zoho.com`, com espaco depois do //
CURL_RE = re.compile(r"curl\s+-X\s+([A-Z]+)\s+(https?://\s*\S+)")
# -d '...' / --data '...' / -d "..." — o valor pode ter quebras de linha
DATA_RE = re.compile(r"(?:-d|--data(?:-raw|-binary)?)\s+(['\"])(.*?)\1", re.S)
ID_RE = re.compile(r"/\d{6,}")
REF_RE = re.compile(r"<>[a-z0-9_]+</>")


def texto(fragmento):
    """HTML do bloco -> texto puro."""
    return html.unescape(TAG_RE.sub(" ", fragmento))


def normalizar(url):
    """URL de exemplo -> rota com placeholder generico, sem host nem query."""
    rota = url.split("?", 1)[0].strip()
    rota = re.sub(r"^https?://\s*[^/]+", "", rota)
    return ID_RE.sub("/{id}", rota.rstrip("/"))


def rota_do_iac(op):
    """Rota do IAC -> mesma forma normalizada: <>param</> vira {id}."""
    rota = "/" + "/".join(op["request"]["url"]["path"])
    return REF_RE.sub("{id}", rota).rstrip("/")


def raspar(caminho_html):
    """Retorna {"METODO /rota": {"has_body", "sample", "secao"}}."""
    with open(caminho_html, encoding="utf-8", errors="replace") as fh:
        pagina = fh.read()

    resultado = {}
    conflitos = []

    for secao, fragmento in BLOCO_RE.findall(pagina):
        corpo = texto(fragmento)
        curl = CURL_RE.search(corpo)
        if not curl:
            continue
        metodo, url = curl.group(1), curl.group(2)
        # so o que vem depois do curl conta como payload desta operacao;
        # a secao tambem traz o "Response Example", que nao e corpo de request
        trecho = corpo[curl.end():]
        corte = trecho.find("Response Example")
        if corte != -1:
            trecho = trecho[:corte]
        dado = DATA_RE.search(trecho)
        amostra = dado.group(2).strip() if dado else ""

        chave = "%s %s" % (metodo, normalizar(url))
        entrada = {"has_body": bool(amostra), "sample": amostra, "secao": secao}
        anterior = resultado.get(chave)
        if anterior is not None and anterior["has_body"] != entrada["has_body"]:
            conflitos.append((chave, anterior["secao"], secao))
        # mantem a primeira ocorrencia que tenha corpo
        if anterior is None or (entrada["has_body"] and not anterior["has_body"]):
            resultado[chave] = entrada

    return resultado, conflitos


def decidir(doc, iac):
    """Classifica as operacoes de escrita do IAC que estao sem corpo."""
    decisao = {}
    for op in iac["operations"]:
        req = op["request"]
        if req["method"] not in ("POST", "PUT", "PATCH"):
            continue
        if req.get("body", {}).get("raw"):
            continue
        chave = "%s %s" % (req["method"], rota_do_iac(op))
        achado = doc.get(chave)
        if achado is None:
            decisao[op["name"]] = {"has_body": False, "sample": "",
                                   "fonte": "ausente", "rota": chave}
        else:
            decisao[op["name"]] = {"has_body": achado["has_body"],
                                   "sample": achado["sample"],
                                   "fonte": "doc", "rota": chave,
                                   "secao": achado["secao"]}
    return decisao


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc_html")
    ap.add_argument("--iac", required=True)
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--decisao", required=True)
    args = ap.parse_args()

    doc, conflitos = raspar(args.doc_html)
    with open(args.iac, encoding="utf-8") as fh:
        iac = json.load(fh)
    decisao = decidir(doc, iac)

    for caminho, dados in ((args.out, doc), (args.decisao, decisao)):
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(dados, fh, ensure_ascii=False, indent=1)

    com = sum(1 for v in doc.values() if v["has_body"])
    print("rotas na doc:      %d  (com corpo: %d)" % (len(doc), com))
    print("operacoes vazias:  %d" % len(decisao))
    print("  com corpo:       %d" % sum(1 for v in decisao.values() if v["has_body"]))
    print("  sem corpo:       %d" % sum(1 for v in decisao.values() if not v["has_body"]))
    print("  sem evidencia:   %d" % sum(1 for v in decisao.values() if v["fonte"] == "ausente"))
    if conflitos:
        print("conflitos has_body (%d):" % len(conflitos))
        for chave, a, b in conflitos[:10]:
            print("  %s  %s vs %s" % (chave, a, b))
    for nome, v in sorted(decisao.items()):
        if v["fonte"] == "ausente":
            print("  SEM EVIDENCIA  %s  (%s)" % (nome, v["rota"]))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Rodar a raspagem**

```bash
cd /home/caiomtho/projects/studio-templates
python3 scratchpad/tools/desk_doc_bodies.py \
  scratchpad/iacs/zoho-desk/src/DeskAPIDocument.html \
  --iac iac/zoho-desk.json \
  -o scratchpad/iacs/zoho-desk/doc_bodies.json \
  --decisao scratchpad/iacs/zoho-desk/decisao-bodies.json
```

Esperado: algumas centenas de rotas na doc e 39 operações vazias decididas.

- [ ] **Step 6: Rodar a verificação**

```bash
cd /home/caiomtho/projects/studio-templates
python3 /tmp/check_desk_decisao.py; echo "exit=$?"
```

Esperado: `exit=0`.

Se alguma das 15 de CRUD sair com `has_body=False` ou alguma das 13 ações sair com `has_body=True`, a normalização de rota está errando o casamento — ajuste `normalizar()`/`rota_do_iac()` até que as 28 operações de classificação conhecida batam. Elas são o gabarito da raspagem: a doc precisa confirmar o que já se sabe antes de ser confiável nas 11 ambíguas.

- [ ] **Step 7: Mostrar as 11 ambíguas ao usuário**

```bash
cd /home/caiomtho/projects/studio-templates
python3 - <<'EOF'
import json
d = json.load(open("scratchpad/iacs/zoho-desk/decisao-bodies.json", encoding="utf-8"))
ambiguas = [
    "Agents - Auto Display an Entity",
    "Lastaccessedview - Update Last Accessed View",
    "Recenttickettags - Update recent tags",
    "Tasks - Performs Task Timer actions",
    "Tickets - Performs Ticket Timer actions",
    "Tickets - Draft Email Reply",
    "Tickets - Update Draft",
    "Tickets - Execute Skill Based Assignment",
    "Tickets - Send Email Reply",
    "Tickets - Split tickets",
    "Templates - Cloning a Email Template Attachments",
]
for nome in ambiguas:
    v = d.get(nome, {})
    marca = "COM CORPO" if v.get("has_body") else "sem corpo "
    print("%s  %-52s  fonte=%s" % (marca, nome, v.get("fonte")))
    if v.get("sample"):
        print("     sample: %s" % v["sample"][:160].replace("\n", " "))
EOF
```

**PARE AQUI.** Mostre a tabela ao usuário e peça confirmação das 11 decisões antes de aplicá-las. Operações marcadas `fonte=ausente` não foram encontradas na doc: trate como sem corpo e aponte-as explicitamente ao usuário como dúvida não resolvida.

- [ ] **Step 8: Commit**

```bash
cd /home/caiomtho/projects/studio-templates
git add scratchpad/tools/desk_doc_bodies.py \
        scratchpad/iacs/zoho-desk/doc_bodies.json \
        scratchpad/iacs/zoho-desk/decisao-bodies.json
git commit -m "feat(tools): desk_doc_bodies.py decide corpos pela doc do Zoho Desk

A spec zohodesk-oas deixa 51 de 326 operacoes de escrita sem requestBody, e
corpo vazio nao distingue defeito de acao sem payload. A doc HTML oficial
traz um curl por operacao; a presenca de -d decide, e o valor vira sample.
Mesmo metodo do books_doc_bodies.py.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Subcomando `bodies` e aplicação no Zoho Desk

Acrescenta o parâmetro `body` às operações que a Task 3 confirmou receberem corpo, e aplica no Studio.

**Files:**
- Modify: `scratchpad/tools/zoho_fix.py`
- Modify: `iac/zoho-desk.json`
- Remoto: conector `Zoho Desk`, `module_id` `In23lcm6eQ`

**Interfaces:**
- Consumes: `scratchpad/iacs/zoho-desk/decisao-bodies.json` da Task 3.
- Produces: `zoho_fix.py bodies <entrada.json> -o <saida.json> --decisao <decisao.json> --tipo object|string --required true|false --descricao <texto>` — acrescenta o parâmetro `body` a cada operação com `has_body: true` na decisão, e imprime `adicionados=N ja_tinham=N ignorados=N`. Reusado nas Tasks 5 e 6.

**Pré-requisito:** a Task 2 concluiu com o patch aplicado. Se o `patch_connector` estiver bloqueado pelo bug de encoding, faça só os passos locais (1 a 5 e 13) e pare.

- [ ] **Step 1: Escrever a verificação que deve falhar**

Crie `/tmp/check_bodies.py`:

```python
#!/usr/bin/env python3
"""Verifica que toda operacao decidida com corpo tem o parametro 'body' ligado.

Uso: check_bodies.py <iac.json> <decisao.json> <tipo> <required>
"""
import json, sys

iac = json.load(open(sys.argv[1], encoding="utf-8"))
decisao = json.load(open(sys.argv[2], encoding="utf-8"))
tipo, obrigatorio = sys.argv[3], sys.argv[4] == "true"

erros = []
adicionados = intactas = 0
for op in iac["operations"]:
    d = decisao.get(op["name"])
    if d is None:
        continue
    params = {p["name"]: p for p in op["parameters"]}
    raw = op["request"].get("body", {}).get("raw", "")
    if d["has_body"]:
        if "body" not in params:
            erros.append("%s: falta o parametro 'body'" % op["name"])
            continue
        p = params["body"]
        if p["type"] != tipo:
            erros.append("%s: body deve ser %s, e %s" % (op["name"], tipo, p["type"]))
        if p["required"] != obrigatorio:
            erros.append("%s: body required deve ser %s" % (op["name"], obrigatorio))
        if not p["sample"]:
            erros.append("%s: body sem sample" % op["name"])
        if not p.get("description"):
            erros.append("%s: body sem descricao" % op["name"])
        if raw != "<>body</>":
            erros.append("%s: raw deve ser <>body</>, e %r" % (op["name"], raw))
        adicionados += 1
    else:
        if "body" in params:
            erros.append("%s: acao sem corpo ganhou parametro 'body'" % op["name"])
        if raw:
            erros.append("%s: acao sem corpo ganhou raw %r" % (op["name"], raw))
        intactas += 1

for e in erros[:20]:
    print("FALHA:", e)
print("com corpo=%d  intactas=%d  erros=%d" % (adicionados, intactas, len(erros)))
sys.exit(1 if erros else 0)
```

- [ ] **Step 2: Rodar a verificação e confirmar que falha**

```bash
cd /home/caiomtho/projects/studio-templates
python3 /tmp/check_bodies.py iac/zoho-desk.json \
  scratchpad/iacs/zoho-desk/decisao-bodies.json object false; echo "exit=$?"
```

Esperado: `exit=1`, com `FALHA: Contacts - Create Contact: falta o parametro 'body'` entre as primeiras.

- [ ] **Step 3: Acrescentar o subcomando `bodies` ao `zoho_fix.py`**

Em `scratchpad/tools/zoho_fix.py`, acrescente a função abaixo logo depois de `analytics_config`:

```python
def bodies(iac, decisao, tipo, obrigatorio, descricao):
    """Acrescenta o parametro 'body' as operacoes decididas como tendo corpo.

    Operacoes com has_body False nao sao tocadas: sao acoes sem payload, e
    dar corpo a elas seria regressao.
    """
    adicionados = ja_tinham = ignorados = 0

    for op in iac["operations"]:
        d = decisao.get(op["name"])
        if d is None or not d.get("has_body"):
            ignorados += 1
            continue
        if any(p["name"] == "body" for p in op["parameters"]):
            ja_tinham += 1
            continue

        op["parameters"].append({
            "id": str(uuid.uuid4()),
            "name": "body",
            "type": tipo,
            "description": descricao,
            "required": obrigatorio,
            "sensitive": False,
            "sample": d.get("sample") or "{}",
        })
        op["request"]["body"] = {
            "mode": "raw",
            "raw": "<>body</>",
            "options": {"raw": {"language": "json"}},
        }
        adicionados += 1

    return {"adicionados": adicionados, "ja_tinham": ja_tinham,
            "ignorados": ignorados}
```

E, no `main()`, registre o subcomando logo depois do parser `analytics-config`:

```python
    p = sub.add_parser("bodies")
    p.add_argument("entrada")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--decisao", required=True)
    p.add_argument("--tipo", choices=["object", "string"], required=True)
    p.add_argument("--required", choices=["true", "false"], required=True)
    p.add_argument("--descricao", required=True)
```

e o despacho, substituindo a linha `ap.error("subcomando nao implementado: %s" % args.cmd)` por:

```python
    elif args.cmd == "bodies":
        rel = bodies(iac, carregar(args.decisao), args.tipo,
                     args.required == "true", args.descricao)
    else:
        ap.error("subcomando nao implementado: %s" % args.cmd)
```

- [ ] **Step 4: Rodar o script sobre o IAC versionado e verificar**

```bash
cd /home/caiomtho/projects/studio-templates
python3 scratchpad/tools/zoho_fix.py bodies iac/zoho-desk.json \
  -o /tmp/desk-fixed.json \
  --decisao scratchpad/iacs/zoho-desk/decisao-bodies.json \
  --tipo object --required false \
  --descricao "Corpo da requisição"
python3 /tmp/check_bodies.py /tmp/desk-fixed.json \
  scratchpad/iacs/zoho-desk/decisao-bodies.json object false; echo "exit=$?"
```

Esperado: `exit=0`. O `adicionados` no stderr deve bater com o número de `has_body: true` da decisão — no mínimo as 15 de CRUD.

- [ ] **Step 5: Conferir que só o esperado mudou**

```bash
cd /home/caiomtho/projects/studio-templates
python3 - <<'EOF'
import json
a = json.load(open("iac/zoho-desk.json", encoding="utf-8"))
b = json.load(open("/tmp/desk-fixed.json", encoding="utf-8"))
assert [o["id"] for o in a["operations"]] == [o["id"] for o in b["operations"]]
mudou = 0
for x, y in zip(a["operations"], b["operations"]):
    assert x["name"] == y["name"] and x["description"] == y["description"]
    assert x["request"]["url"] == y["request"]["url"], x["name"]
    assert x["request"]["header"] == y["request"]["header"], x["name"]
    assert x["request"].get("query") == y["request"].get("query"), x["name"]
    antigos = [p["id"] for p in x["parameters"]]
    novos = [p["id"] for p in y["parameters"]]
    assert novos[:len(antigos)] == antigos, x["name"]
    if len(novos) != len(antigos):
        assert [p["name"] for p in y["parameters"][len(antigos):]] == ["body"], x["name"]
        mudou += 1
print("operacoes com parametro novo:", mudou)
EOF
```

Esperado: nenhuma asserção falha; `operacoes com parametro novo` igual ao `adicionados` do passo anterior.

- [ ] **Step 6: Trazer o conector publicado para um draft**

```
pull_connector(module_id="In23lcm6eQ")
export_draft(id="In23lcm6eQ", file_path="/tmp/zoho-desk-pulled.json")
```

- [ ] **Step 7: Confirmar que o remoto bate com o IAC versionado**

```bash
cd /home/caiomtho/projects/studio-templates
python3 - <<'EOF'
import json
r = json.load(open("/tmp/zoho-desk-pulled.json", encoding="utf-8"))
l = json.load(open("iac/zoho-desk.json", encoding="utf-8"))
nr = {o["name"] for o in r["operations"]}
nl = {o["name"] for o in l["operations"]}
print("remoto=%d local=%d" % (len(r["operations"]), len(l["operations"])))
print("so no remoto:", sorted(nr - nl)[:10])
print("so no local: ", sorted(nl - nr)[:10])
EOF
```

Esperado: `remoto=339 local=339` e nenhuma diferença. Havendo divergência, **pare e mostre ao usuário**.

- [ ] **Step 8: Aplicar a transformação sobre o draft exportado**

```bash
cd /home/caiomtho/projects/studio-templates
python3 scratchpad/tools/zoho_fix.py bodies /tmp/zoho-desk-pulled.json \
  -o /tmp/zoho-desk-fixed.json \
  --decisao scratchpad/iacs/zoho-desk/decisao-bodies.json \
  --tipo object --required false \
  --descricao "Corpo da requisição"
python3 /tmp/check_bodies.py /tmp/zoho-desk-fixed.json \
  scratchpad/iacs/zoho-desk/decisao-bodies.json object false; echo "exit=$?"
```

Esperado: `exit=0`.

- [ ] **Step 9: Sobrescrever o draft, provar e validar**

```
import_connector_draft(file_path="/tmp/zoho-desk-fixed.json")
diff_draft(id="In23lcm6eQ", file_path="/tmp/zoho-desk-fixed.json")
validate_draft(id="In23lcm6eQ")
```

Esperado: `op_count` 339, `diff_draft` com zero diferenças, `validate_draft` com `ok: true`.

- [ ] **Step 10: Dry-run do patch e portão de aprovação**

```
patch_connector(draft_id="In23lcm6eQ", dry_run=True)
```

Mostre ao usuário o número de operações atualizadas, criadas (esperado: 0), removidas (esperado: 0), `flows_using` e `drifted`. **PARE.** Só siga com um "sim" explícito.

- [ ] **Step 11: Aplicar o patch**

```
patch_connector(draft_id="In23lcm6eQ", dry_run=False)
get_connector_summary(module_id="In23lcm6eQ")
```

Esperado: `op_count` 339.

- [ ] **Step 12: Regravar o IAC versionado**

```bash
cd /home/caiomtho/projects/studio-templates
cp /tmp/zoho-desk-fixed.json iac/zoho-desk.json
python3 scratchpad/tools/migrate_query_to_root.py iac/zoho-desk.json
python3 /tmp/check_bodies.py iac/zoho-desk.json \
  scratchpad/iacs/zoho-desk/decisao-bodies.json object false; echo "exit=$?"
jq -e '[.operations[] | select(.request.url.query != null)] | length == 0' iac/zoho-desk.json
```

Esperado: `exit=0` e o `jq -e` saindo 0.

- [ ] **Step 13: Commit**

```bash
cd /home/caiomtho/projects/studio-templates
git add scratchpad/tools/zoho_fix.py iac/zoho-desk.json
git commit -m "fix(zoho-desk): corpo nas operacoes de escrita que a spec omitiu

Operacoes como Contacts - Create Contact e Tickets - Create a ticket nao
tinham como enviar corpo: a spec zohodesk-oas as entrega sem requestBody.
As que a doc oficial confirma receberem payload ganham o parametro body,
com o exemplo real da doc como sample. As acoes sem corpo ficam intactas.
Aplicado tambem no Studio via patch_connector.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Zoho CRM — corpos e o domínio Appointments

Corrige as 3 operações sem corpo e os 7 nomes de fallback do domínio Appointments, incluindo o delete em massa que hoje é inexecutável.

**Files:**
- Modify: `scratchpad/tools/zoho_fix.py`
- Modify: `iac/zoho-crm.json`
- Modify: `docs/connectors/zoho-crm.md:111-117`
- Remoto: conector `Zoho CRM`, `module_id` `PORy1eg57X`

**Interfaces:**
- Consumes: o subcomando `bodies` da Task 4.
- Produces: `zoho_fix.py crm-appointments <entrada.json> -o <saida.json>`, que imprime `renomeadas=N ids_adicionado=N`.

**Contexto factual (medido em 2026-09-16):**

As 3 operações de escrita sem corpo do CRM:

| Operação | Rota | Decisão |
|---|---|---|
| `Actions - Share Emails of a record` | `POST /{version}/{module_api_name}/{id}/actions/share_emails` | recebe a lista de usuários no corpo |
| `Actions - Unshare Emails of a record` | `POST /{version}/{module_api_name}/{id}/actions/unshare_emails` | idem |
| `Settings - Add specific user` | `PUT /{version}/settings/territories/{territory}/users/{user}` | recebe as opções da atribuição; como o parâmetro é opcional, acrescentá-lo não quebra a chamada sem corpo |

Os 7 nomes do domínio Appointments vêm de `summary` cru da própria spec da Zoho (`"GET /Appointments__s"`), e o domínio saiu `Appointments  S` com dois espaços porque deriva de `Appointments__s`. O segmento literal `Appointments__s` da rota está **correto** — é o nome real do módulo na API — e não muda.

O delete em massa (`DELETE /{version}/Appointments__s`) tem `request.query` vazio e nenhum parâmetro `ids`: a API do CRM espera `?ids=...`.

- [ ] **Step 1: Escrever a verificação que deve falhar**

Crie `/tmp/check_crm.py`:

```python
#!/usr/bin/env python3
"""Verifica os nomes do dominio Appointments e o delete em massa do Zoho CRM."""
import json, sys

iac = json.load(open(sys.argv[1], encoding="utf-8"))
ops = {o["name"]: o for o in iac["operations"]}
erros = []

esperados = [
    "Appointments - List appointments",
    "Appointments - Create appointments",
    "Appointments - Update appointments",
    "Appointments - Delete appointments",
    "Appointments - Get appointment",
    "Appointments - Update appointment",
    "Appointments - Delete appointment",
]
for nome in esperados:
    if nome not in ops:
        erros.append("falta a operacao %r" % nome)

antigos = [n for n in ops if n.startswith("Appointments  S")]
if antigos:
    erros.append("nomes antigos ainda presentes: %s" % antigos)

bulk = ops.get("Appointments - Delete appointments")
if bulk:
    q = {x["key"]: x["value"] for x in bulk["request"].get("query", [])}
    if q.get("ids") != "<>ids</>":
        erros.append("delete em massa sem ids na query: %r" % q)
    p = [x for x in bulk["parameters"] if x["name"] == "ids"]
    if not p:
        erros.append("delete em massa sem o parametro 'ids'")
    elif p[0]["type"] != "string" or not p[0]["required"] or not p[0]["sample"]:
        erros.append("parametro 'ids' deve ser string, required e com sample")

# as rotas nao mudam: Appointments__s continua literal
for nome in esperados:
    op = ops.get(nome)
    if op and "Appointments__s" not in op["request"]["url"]["path"]:
        erros.append("%s: perdeu o segmento literal Appointments__s" % nome)

if len(iac["operations"]) != 170:
    erros.append("total de operacoes mudou: %d" % len(iac["operations"]))

for e in erros[:20]:
    print("FALHA:", e)
print("operacoes=%d  erros=%d" % (len(iac["operations"]), len(erros)))
sys.exit(1 if erros else 0)
```

- [ ] **Step 2: Rodar a verificação e confirmar que falha**

```bash
cd /home/caiomtho/projects/studio-templates
python3 /tmp/check_crm.py iac/zoho-crm.json; echo "exit=$?"
```

Esperado: `exit=1`, listando as 7 operações faltando e os nomes antigos presentes.

- [ ] **Step 3: Acrescentar o subcomando `crm-appointments` ao `zoho_fix.py`**

Acrescente a função depois de `bodies`:

```python
# nome antigo -> nome novo. Os antigos vem de summary cru da spec da Zoho.
APPOINTMENTS_RENOMEIO = {
    "Appointments  S - GET /Appointments__s": "Appointments - List appointments",
    "Appointments  S - POST /Appointments__s": "Appointments - Create appointments",
    "Appointments  S - PUT /Appointments__s": "Appointments - Update appointments",
    "Appointments  S - DELETE /Appointments__s/{ids}": "Appointments - Delete appointments",
    "Appointments  S - GET /Appointments__s/{appointmentId}": "Appointments - Get appointment",
    "Appointments  S - PUT /Appointments__s/{id}": "Appointments - Update appointment",
    "Appointments  S - DELETE /Appointments__s/id": "Appointments - Delete appointment",
}
IDS_DESC = ("Identificadores dos compromissos a excluir, separados por vírgula. "
            "Máximo de 100 por chamada.")
IDS_SAMPLE = "1234567890123456789,1234567890123456790"


def crm_appointments(iac):
    """Renomeia o dominio Appointments e conserta o delete em massa.

    A rota nao muda: 'Appointments__s' e o nome real do modulo na API do CRM.
    """
    renomeadas = 0
    ids_adicionado = 0

    for op in iac["operations"]:
        novo = APPOINTMENTS_RENOMEIO.get(op["name"])
        if novo is None:
            continue
        op["name"] = novo
        renomeadas += 1

        if novo != "Appointments - Delete appointments":
            continue
        # delete em massa: a API espera ?ids=...
        if not any(p["name"] == "ids" for p in op["parameters"]):
            op["parameters"].append({
                "id": str(uuid.uuid4()),
                "name": "ids",
                "type": "string",
                "description": IDS_DESC,
                "required": True,
                "sensitive": False,
                "sample": IDS_SAMPLE,
            })
        query = op["request"].setdefault("query", [])
        if not any(q["key"] == "ids" for q in query):
            query.append({"key": "ids", "value": "<>ids</>", "enabled": True})
        ids_adicionado = 1

    return {"renomeadas": renomeadas, "ids_adicionado": ids_adicionado}
```

Registre o subcomando no `main()`:

```python
    p = sub.add_parser("crm-appointments")
    p.add_argument("entrada")
    p.add_argument("-o", "--out", required=True)
```

e o despacho, antes do `else` final:

```python
    elif args.cmd == "crm-appointments":
        rel = crm_appointments(iac)
```

- [ ] **Step 4: Montar a decisão de corpos do CRM**

```bash
cd /home/caiomtho/projects/studio-templates
cat > scratchpad/iacs/zoho-crm/decisao-bodies.json <<'EOF'
{
 "Actions - Share Emails of a record": {"has_body": true, "sample": "{}"},
 "Actions - Unshare Emails of a record": {"has_body": true, "sample": "{}"},
 "Settings - Add specific user": {"has_body": true, "sample": "{}"}
}
EOF
```

- [ ] **Step 5: Rodar as duas transformações e verificar**

```bash
cd /home/caiomtho/projects/studio-templates
python3 scratchpad/tools/zoho_fix.py bodies iac/zoho-crm.json \
  -o /tmp/crm-passo1.json \
  --decisao scratchpad/iacs/zoho-crm/decisao-bodies.json \
  --tipo object --required false \
  --descricao 'Corpo da requisição em formato JSON. Informe o objeto completo na sintaxe da própria API do Zoho CRM; na maioria das operações os registros vão dentro do array "data".'
python3 scratchpad/tools/zoho_fix.py crm-appointments /tmp/crm-passo1.json -o /tmp/crm-fixed.json
python3 /tmp/check_crm.py /tmp/crm-fixed.json; echo "exit=$?"
python3 /tmp/check_bodies.py /tmp/crm-fixed.json \
  scratchpad/iacs/zoho-crm/decisao-bodies.json object false; echo "exit=$?"
```

Esperado: `adicionados=3` e `renomeadas=7 ids_adicionado=1` no stderr, e `exit=0` nas duas verificações.

- [ ] **Step 6: Trazer o conector publicado e conferir**

```
pull_connector(module_id="PORy1eg57X")
export_draft(id="PORy1eg57X", file_path="/tmp/zoho-crm-pulled.json")
```

```bash
cd /home/caiomtho/projects/studio-templates
python3 - <<'EOF'
import json
r = json.load(open("/tmp/zoho-crm-pulled.json", encoding="utf-8"))
l = json.load(open("iac/zoho-crm.json", encoding="utf-8"))
nr = {o["name"] for o in r["operations"]}
nl = {o["name"] for o in l["operations"]}
print("remoto=%d local=%d" % (len(r["operations"]), len(l["operations"])))
print("so no remoto:", sorted(nr - nl)[:10])
print("so no local: ", sorted(nl - nr)[:10])
EOF
```

Esperado: `remoto=170 local=170` e nenhuma diferença. Havendo divergência, **pare e mostre ao usuário**.

- [ ] **Step 7: Aplicar as transformações sobre o draft exportado**

```bash
cd /home/caiomtho/projects/studio-templates
python3 scratchpad/tools/zoho_fix.py bodies /tmp/zoho-crm-pulled.json \
  -o /tmp/zoho-crm-passo1.json \
  --decisao scratchpad/iacs/zoho-crm/decisao-bodies.json \
  --tipo object --required false \
  --descricao 'Corpo da requisição em formato JSON. Informe o objeto completo na sintaxe da própria API do Zoho CRM; na maioria das operações os registros vão dentro do array "data".'
python3 scratchpad/tools/zoho_fix.py crm-appointments /tmp/zoho-crm-passo1.json \
  -o /tmp/zoho-crm-fixed.json
python3 /tmp/check_crm.py /tmp/zoho-crm-fixed.json; echo "exit=$?"
python3 /tmp/check_bodies.py /tmp/zoho-crm-fixed.json \
  scratchpad/iacs/zoho-crm/decisao-bodies.json object false; echo "exit=$?"
```

Esperado: `exit=0` nas duas.

- [ ] **Step 8: Sobrescrever o draft, provar e validar**

```
import_connector_draft(file_path="/tmp/zoho-crm-fixed.json")
diff_draft(id="PORy1eg57X", file_path="/tmp/zoho-crm-fixed.json")
validate_draft(id="PORy1eg57X")
```

Esperado: `op_count` 170, zero diferenças, `ok: true`.

- [ ] **Step 9: Dry-run do patch e portão de aprovação**

```
patch_connector(draft_id="PORy1eg57X", dry_run=True)
```

Esperado: 10 operações atualizadas (3 com corpo novo + 7 renomeadas), 0 criadas, 0 removidas. Renomear operação é atualização, não criação — se o dry-run mostrar 7 criações e 7 remoções, o casamento por id se perdeu: **pare e reporte**, não aplique.

**PARE.** Só siga com um "sim" explícito.

- [ ] **Step 10: Aplicar o patch**

```
patch_connector(draft_id="PORy1eg57X", dry_run=False)
get_connector_summary(module_id="PORy1eg57X")
```

Esperado: `op_count` 170.

`operation_name_already_exists` só é verificado no servidor. Se aparecer, algum dos 7 nomes novos já está em uso no conector — mostre o nome ao usuário e escolha outro com ele.

- [ ] **Step 11: Regravar o IAC versionado**

```bash
cd /home/caiomtho/projects/studio-templates
cp /tmp/zoho-crm-fixed.json iac/zoho-crm.json
python3 scratchpad/tools/migrate_query_to_root.py iac/zoho-crm.json
python3 /tmp/check_crm.py iac/zoho-crm.json; echo "exit=$?"
jq -e '[.operations[] | select(.request.url.query != null)] | length == 0' iac/zoho-crm.json
```

Esperado: `exit=0` e o `jq -e` saindo 0.

- [ ] **Step 12: Atualizar a documentação do conector**

As linhas 111 a 117 de `docs/connectors/zoho-crm.md` listam os nomes antigos na tabela de operações. Troque cada um pelo nome novo, mantendo a coluna de método e a descrição em português, que continuam corretas:

```bash
cd /home/caiomtho/projects/studio-templates
python3 - <<'EOF'
import re
caminho = "docs/connectors/zoho-crm.md"
renomeio = {
    "Appointments  S - GET /Appointments__s": "Appointments - List appointments",
    "Appointments  S - POST /Appointments__s": "Appointments - Create appointments",
    "Appointments  S - PUT /Appointments__s": "Appointments - Update appointments",
    "Appointments  S - DELETE /Appointments__s/{ids}": "Appointments - Delete appointments",
    "Appointments  S - GET /Appointments__s/{appointmentId}": "Appointments - Get appointment",
    "Appointments  S - PUT /Appointments__s/{id}": "Appointments - Update appointment",
    "Appointments  S - DELETE /Appointments__s/id": "Appointments - Delete appointment",
}
texto = open(caminho, encoding="utf-8").read()
# do mais longo para o mais curto: evita que um nome seja prefixo de outro
for antigo in sorted(renomeio, key=len, reverse=True):
    texto = texto.replace(antigo, renomeio[antigo])
open(caminho, "w", encoding="utf-8").write(texto)
EOF
grep -n "Appointments" docs/connectors/zoho-crm.md
```

Esperado: nenhuma ocorrência de `Appointments  S`.

Se a doc tiver uma seção descrevendo o delete em massa, acrescente que ele agora exige o parâmetro `ids`. Confira:

```bash
cd /home/caiomtho/projects/studio-templates
grep -n "Delete appointments" docs/connectors/zoho-crm.md
```

- [ ] **Step 13: Commit**

```bash
cd /home/caiomtho/projects/studio-templates
git add scratchpad/tools/zoho_fix.py scratchpad/iacs/zoho-crm/decisao-bodies.json \
        iac/zoho-crm.json docs/connectors/zoho-crm.md
git commit -m "fix(zoho-crm): nomes do dominio Appointments e corpos ausentes

O dominio saia como 'Appointments  S' e as 7 operacoes carregavam o summary
cru da spec da Zoho ('GET /Appointments__s'). O delete em massa estava sem o
parametro ids e era inexecutavel. Tres operacoes de escrita ganharam corpo.
Aplicado tambem no Studio via patch_connector.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Zoho WorkDrive — corpos das sessões de upload

Última correção. As quatro operações de sessão de upload em partes não têm como enviar os metadados do arquivo.

**Files:**
- Modify: `iac/zoho-workdrive.json`
- Remoto: conector `Zoho WorkDrive`, `module_id` `ioneV7_cQY`

**Interfaces:**
- Consumes: o subcomando `bodies` da Task 4.

**Contexto factual (medido em 2026-09-16):**

As 4 operações de escrita sem corpo são `Uploadsession - Create Session (Normal Upload)`, `Uploadsession - Commit Session (Normal Upload)`, `Uploadsession - Create Session for Revision Upload` e `Uploadsession - Commit Session for Revision Upload`. Todas recebem metadados no corpo — arquivo, pasta de destino, id da sessão. Nenhuma é endpoint de ação.

No WorkDrive a convenção do conector é `body` do tipo `string` e `required: true` (assim estão as 30 operações já corretas), porque o corpo é JSON:API.

- [ ] **Step 1: Montar a decisão de corpos e verificar que a checagem falha**

```bash
cd /home/caiomtho/projects/studio-templates
mkdir -p scratchpad/iacs/zoho-workdrive
cat > scratchpad/iacs/zoho-workdrive/decisao-bodies.json <<'EOF'
{
 "Uploadsession - Create Session (Normal Upload)": {"has_body": true, "sample": "{}"},
 "Uploadsession - Commit Session (Normal Upload)": {"has_body": true, "sample": "{}"},
 "Uploadsession - Create Session for Revision Upload": {"has_body": true, "sample": "{}"},
 "Uploadsession - Commit Session for Revision Upload": {"has_body": true, "sample": "{}"}
}
EOF
python3 /tmp/check_bodies.py iac/zoho-workdrive.json \
  scratchpad/iacs/zoho-workdrive/decisao-bodies.json string true; echo "exit=$?"
```

Esperado: `exit=1`, com quatro `FALHA: ... falta o parametro 'body'`.

- [ ] **Step 2: Rodar o script sobre o IAC versionado e verificar**

```bash
cd /home/caiomtho/projects/studio-templates
python3 scratchpad/tools/zoho_fix.py bodies iac/zoho-workdrive.json \
  -o /tmp/workdrive-fixed.json \
  --decisao scratchpad/iacs/zoho-workdrive/decisao-bodies.json \
  --tipo string --required true \
  --descricao 'Corpo da requisição em JSON, no formato JSON:API do WorkDrive: {"data":{"type":"<recurso>","attributes":{...}}}. Informe o objeto completo da ação desejada; o exemplo do campo mostra o formato esperado.'
python3 /tmp/check_bodies.py /tmp/workdrive-fixed.json \
  scratchpad/iacs/zoho-workdrive/decisao-bodies.json string true; echo "exit=$?"
```

Esperado: `adicionados=4` no stderr e `exit=0`.

- [ ] **Step 3: Trazer o conector publicado e conferir**

```
pull_connector(module_id="ioneV7_cQY")
export_draft(id="ioneV7_cQY", file_path="/tmp/zoho-workdrive-pulled.json")
```

```bash
cd /home/caiomtho/projects/studio-templates
python3 - <<'EOF'
import json
r = json.load(open("/tmp/zoho-workdrive-pulled.json", encoding="utf-8"))
l = json.load(open("iac/zoho-workdrive.json", encoding="utf-8"))
nr = {o["name"] for o in r["operations"]}
nl = {o["name"] for o in l["operations"]}
print("remoto=%d local=%d" % (len(r["operations"]), len(l["operations"])))
print("so no remoto:", sorted(nr - nl)[:10])
print("so no local: ", sorted(nl - nr)[:10])
EOF
```

Esperado: `remoto=163 local=163` e nenhuma diferença.

- [ ] **Step 4: Aplicar a transformação sobre o draft exportado**

```bash
cd /home/caiomtho/projects/studio-templates
python3 scratchpad/tools/zoho_fix.py bodies /tmp/zoho-workdrive-pulled.json \
  -o /tmp/zoho-workdrive-fixed.json \
  --decisao scratchpad/iacs/zoho-workdrive/decisao-bodies.json \
  --tipo string --required true \
  --descricao 'Corpo da requisição em JSON, no formato JSON:API do WorkDrive: {"data":{"type":"<recurso>","attributes":{...}}}. Informe o objeto completo da ação desejada; o exemplo do campo mostra o formato esperado.'
python3 /tmp/check_bodies.py /tmp/zoho-workdrive-fixed.json \
  scratchpad/iacs/zoho-workdrive/decisao-bodies.json string true; echo "exit=$?"
```

Esperado: `exit=0`.

- [ ] **Step 5: Sobrescrever o draft, provar e validar**

```
import_connector_draft(file_path="/tmp/zoho-workdrive-fixed.json")
diff_draft(id="ioneV7_cQY", file_path="/tmp/zoho-workdrive-fixed.json")
validate_draft(id="ioneV7_cQY")
```

Esperado: `op_count` 163, zero diferenças, `ok: true`.

- [ ] **Step 6: Dry-run do patch e portão de aprovação**

```
patch_connector(draft_id="ioneV7_cQY", dry_run=True)
```

Esperado: 4 operações atualizadas, 0 criadas, 0 removidas. **PARE.** Só siga com um "sim" explícito.

- [ ] **Step 7: Aplicar o patch**

```
patch_connector(draft_id="ioneV7_cQY", dry_run=False)
get_connector_summary(module_id="ioneV7_cQY")
```

Esperado: `op_count` 163.

- [ ] **Step 8: Regravar o IAC versionado**

```bash
cd /home/caiomtho/projects/studio-templates
cp /tmp/zoho-workdrive-fixed.json iac/zoho-workdrive.json
python3 scratchpad/tools/migrate_query_to_root.py iac/zoho-workdrive.json
python3 /tmp/check_bodies.py iac/zoho-workdrive.json \
  scratchpad/iacs/zoho-workdrive/decisao-bodies.json string true; echo "exit=$?"
jq -e '[.operations[] | select(.request.url.query != null)] | length == 0' iac/zoho-workdrive.json
```

Esperado: `exit=0` e o `jq -e` saindo 0.

- [ ] **Step 9: Verificação final dos quatro conectores**

```bash
cd /home/caiomtho/projects/studio-templates
python3 - <<'EOF'
import json
for arquivo, esperado in (("zoho-analytics", 176), ("zoho-desk", 339),
                          ("zoho-crm", 170), ("zoho-workdrive", 163)):
    iac = json.load(open("iac/%s.json" % arquivo, encoding="utf-8"))
    ops = iac["operations"]
    orfaos = []
    for op in ops:
        declarados = {p["name"] for p in op["parameters"]}
        alvo = json.dumps(op["request"], ensure_ascii=False)
        import re
        usados = set(re.findall(r"<>([a-z0-9_]+)</>", alvo))
        if usados - declarados:
            orfaos.append((op["name"], sorted(usados - declarados)))
        if declarados - usados:
            orfaos.append((op["name"], sorted(declarados - usados)))
    marca = "OK " if len(ops) == esperado and not orfaos else "ERRO"
    print("%s %-16s ops=%d (esperado %d)  refs inconsistentes=%d"
          % (marca, arquivo, len(ops), esperado, len(orfaos)))
    for nome, quais in orfaos[:5]:
        print("      %s: %s" % (nome, quais))
EOF
```

Esperado: quatro linhas `OK`, com as contagens batendo e zero referências inconsistentes.

- [ ] **Step 10: Commit**

```bash
cd /home/caiomtho/projects/studio-templates
git add scratchpad/iacs/zoho-workdrive/decisao-bodies.json iac/zoho-workdrive.json
git commit -m "fix(zoho-workdrive): corpo nas operacoes de sessao de upload

As quatro operacoes de uploadsession (create e commit, normal e revisao) nao
tinham como enviar os metadados do arquivo. Aplicado tambem no Studio via
patch_connector.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```
