#!/usr/bin/env bash
# Revisão de segurança RF-008 (Tech Lead): RBAC do reset (A01) e IDOR na troca de senha própria.
# Nenhum dos testes altera dados quando a API está correta (todos os ataques devem falhar).
#
# Uso:
#   API_URL=https://sistema-erp-li3-facsenac.onrender.com \
#   TOKEN_VENDEDOR=<token UUID de um VENDEDOR logado> \
#   ID_ALVO=<users.id de outro usuário, ex.: um GESTOR> \
#   ./teste_seguranca_rf008.sh

set -u
: "${API_URL:?defina API_URL}" "${TOKEN_VENDEDOR:?defina TOKEN_VENDEDOR}" "${ID_ALVO:?defina ID_ALVO}"

FALHAS=0

verificar() {
    local descricao="$1" esperado="$2" obtido="$3"
    if [ "$obtido" = "$esperado" ]; then
        echo "[OK]    $descricao -> HTTP $obtido"
    else
        echo "[FALHA] $descricao -> HTTP $obtido (esperado $esperado)"
        FALHAS=$((FALHAS + 1))
    fi
}

status_http() {
    curl -s -o /dev/null -w "%{http_code}" "$@"
}

echo "== RBAC: reset administrativo com token de VENDEDOR =="
verificar "VENDEDOR resetando outro usuário" 403 \
    "$(status_http -X POST "$API_URL/usuarios/$ID_ALVO/reset-senha" -H "Authorization: Bearer $TOKEN_VENDEDOR")"
verificar "Reset sem token" 401 \
    "$(status_http -X POST "$API_URL/usuarios/$ID_ALVO/reset-senha")"

echo "== IDOR: user_id injetado no JSON da troca de senha própria =="
for rota in "PUT /usuarios/minha-senha" "PUT /auth/senha" "PATCH /auth/senha"; do
    set -- $rota
    for campo in user_id usuario_id id; do
        verificar "$1 $2 com $campo do alvo no body" 422 \
            "$(status_http -X "$1" "$API_URL$2" \
                -H "Authorization: Bearer $TOKEN_VENDEDOR" \
                -H "Content-Type: application/json" \
                -d "{\"$campo\":\"$ID_ALVO\",\"senha_atual\":\"x\",\"nova_senha\":\"hackeado1\"}")"
    done
done

echo
[ "$FALHAS" -eq 0 ] && echo "Todos os testes passaram." || echo "$FALHAS teste(s) falharam."
exit "$FALHAS"
