# Backend: Dashboard — Conversão de Orçamentos (RF-006)

API REST em **FastAPI (Python)** que expõe o primeiro indicador do Dashboard gerencial: a **taxa de conversão de orçamentos em Ordens de Serviço (OS)** por período. Segue o mesmo padrão em camadas do RF-005 (`routers` → `services` → `repositories` + `schemas`) e consulta o Supabase via RPC (sem ORM).

---

## Endpoint

`GET /dashboard/conversao-orcamentos?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD`

| Item | Valor |
| --- | --- |
| Autenticação | `Authorization: Bearer <token>` (token de `POST /auth`) |
| Perfis permitidos | `ADMIN` e `GESTOR` (`Depends(require_role(["ADMIN", "GESTOR"]))`) |
| Parâmetros | `data_inicio` e `data_fim`, ambos obrigatórios, formato `YYYY-MM-DD`, **ambos inclusivos** |

### Resposta 200

```json
{
  "periodo": { "data_inicio": "2026-09-01", "data_fim": "2026-09-30" },
  "total_orcamentos": 8,
  "orcamentos_convertidos": 3,
  "orcamentos_pendentes": 5,
  "taxa_conversao": 37.5,
  "valor_total_orcado": 12450.9,
  "valor_total_convertido": 4300.0
}
```

* `taxa_conversao` é percentual (0 a 100, 2 casas) e vale `0.0` quando não há orçamentos no período (sem divisão por zero).
* `periodo` devolve as datas exatamente como o cliente enviou (inclusivas).

### Erros

| Status | Quando |
| --- | --- |
| 401 | Token ausente, inválido ou sessão expirada; usuário inativo |
| 403 | Perfil `VENDEDOR` (ou qualquer perfil fora de `ADMIN`/`GESTOR`) |
| 422 | Parâmetro ausente ou com formato inválido; `data_inicio > data_fim` |
| 503 | Supabase inacessível (timeout, falha de conexão ou resposta 5xx) |
| 500 | Resposta inesperada do banco (função ausente, 4xx do PostgREST, JSON inválido) |

Nos erros 503 e 500 a mensagem ao cliente é genérica. O corpo da resposta do banco (`resp.text`) **nunca** é enviado ao cliente; ele é registrado apenas no log do servidor (`logging`).

---

## Estrutura

```text
rf-006-dashboard/backend/
├── routers/dashboard_router.py          # rota + RBAC
├── services/dashboard_service.py        # validação de período, data_fim exclusiva, taxa, tradução de erros
├── repositories/dashboard_repository.py # POST /rest/v1/rpc/rf006_conversao_orcamentos
├── schemas/dashboard_schemas.py         # PeriodoResponse, ConversaoOrcamentosResponse
└── testes_curl.sh                       # cenários de teste do RF
```

Os módulos são carregados dinamicamente pelo `main.py` do RF-001, e as pastas `routers/`, `services/`, `repositories/` e `schemas/` se repetem entre os RFs. Por isso os arquivos têm nomes únicos com o prefixo `dashboard_`; não crie arquivos genéricos (`router.py`, `service.py`, etc.) aqui.

---

## Regras de negócio

* **Período inclusivo na API, exclusivo no banco:** o service valida `data_inicio <= data_fim` (senão 422) e envia ao banco `data_fim + 1 dia`. A função SQL filtra `created_at >= data_inicio` e `created_at < data_fim_exclusiva`, então um orçamento criado às 23:59 do último dia entra no período.
* **Dia comercial em Brasília:** a função SQL converte as datas usando o fuso `America/Sao_Paulo`, e não o UTC do servidor.
* **Orçamento convertido:** `orcamentos.status = 'CONVERTIDO'`. Pendente: `status = 'PENDENTE'`.
* **Menor privilégio:** `get_current_user` sozinho deixaria qualquer usuário logado (inclusive `VENDEDOR`) acessar a rota; por isso a rota usa `require_role`.

---

## Pré-requisito no banco (obrigatório)

Antes de usar a rota, execute **uma vez** no SQL Editor do Supabase o arquivo
`database/ddl/rf-006-conversao-orcamentos.sql`. Ele cria o índice `idx_orcamentos_created_at` e a função `rf006_conversao_orcamentos(p_data_inicio date, p_data_fim date)`. Sem a função, a rota responde `500`.

---

## Como executar localmente

A execução deve ser feita a partir da pasta do RF-001, que carrega este módulo:

```bash
cd ../../rf-001-gestao-identidade/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Swagger: http://localhost:8000/docs (tag **Dashboard**). Contrato estático: `docs/api/swagger.json`.

Não há novas dependências; o `requirements.txt` do RF-001 continua valendo.

---

## Testes

`testes_curl.sh` executa os cenários da tabela do documento `docs/requisitos/rf-006-dashboard-conversao-orcamentos.md` e imprime esperado × obtido:

```bash
BASE_URL=http://localhost:8000 \
TOKEN_ADMIN=... TOKEN_GESTOR=... TOKEN_VENDEDOR=... \
bash testes_curl.sh
```
