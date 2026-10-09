#!/usr/bin/env bash
# RF-006 - cenários de teste via cURL para GET /dashboard/conversao-orcamentos
#
# Uso:
#   BASE_URL=http://localhost:8000 \
#   TOKEN_ADMIN=... TOKEN_GESTOR=... TOKEN_VENDEDOR=... \
#   bash testes_curl.sh
#
# Tokens: POST $BASE_URL/auth {"email": "...", "senha": "..."} -> campo "token".
# Cenários 11 e 12 dependem do ambiente e ficam fora do script (ver o doc do RF).

set -u

BASE_URL="${BASE_URL:-http://localhost:8000}"
ROTA="$BASE_URL/dashboard/conversao-orcamentos"

for v in TOKEN_ADMIN TOKEN_GESTOR TOKEN_VENDEDOR; do
  if [ -z "${!v:-}" ]; then
    echo "Defina $v antes de executar." >&2
    exit 2
  fi
done

falhas=0
corpo=$(mktemp)
trap 'rm -f "$corpo"' EXIT

# executar <n> <descrição> <status esperado> [argumentos do curl...]
executar() {
  local n="$1" descricao="$2" esperado="$3"
  shift 3
  local obtido
  obtido=$(curl -s -o "$corpo" -w "%{http_code}" "$@")
  local resultado="OK"
  if [ "$obtido" != "$esperado" ]; then
    resultado="FALHA"
    falhas=$((falhas + 1))
  fi
  printf "%-3s | %-52s | esperado %s | obtido %s | %s\n" "$n" "$descricao" "$esperado" "$obtido" "$resultado"
  printf "      corpo: %s\n" "$(head -c 300 "$corpo")"
}

P="data_inicio=2026-09-01&data_fim=2026-09-30"

executar 1  "Sem token"                                   401 "$ROTA?$P"
executar 2  "Token inválido"                              401 -H "Authorization: Bearer token-invalido" "$ROTA?$P"
executar 3  "VENDEDOR (sem permissão)"                    403 -H "Authorization: Bearer $TOKEN_VENDEDOR" "$ROTA?$P"
executar 4  "GESTOR, período válido"                      200 -H "Authorization: Bearer $TOKEN_GESTOR" "$ROTA?$P"
executar 5  "ADMIN, período válido"                       200 -H "Authorization: Bearer $TOKEN_ADMIN" "$ROTA?$P"
executar 6  "data_inicio posterior a data_fim"            422 -H "Authorization: Bearer $TOKEN_GESTOR" "$ROTA?data_inicio=2026-09-30&data_fim=2026-09-01"
executar 7  "data_inicio igual a data_fim (1 dia)"        200 -H "Authorization: Bearer $TOKEN_GESTOR" "$ROTA?data_inicio=2026-09-15&data_fim=2026-09-15"
executar 8  "data_fim ausente"                            422 -H "Authorization: Bearer $TOKEN_GESTOR" "$ROTA?data_inicio=2026-09-01"
executar 9  "Formato de data inválido"                    422 -H "Authorization: Bearer $TOKEN_GESTOR" "$ROTA?data_inicio=01/09/2026&data_fim=30/09/2026"
executar 10 "Período sem orçamentos (zeros, taxa 0.0)"    200 -H "Authorization: Bearer $TOKEN_GESTOR" "$ROTA?data_inicio=2000-01-01&data_fim=2000-01-31"

echo
if [ "$falhas" -eq 0 ]; then
  echo "Todos os cenários passaram."
else
  echo "$falhas cenário(s) falharam."
fi
exit "$falhas"
