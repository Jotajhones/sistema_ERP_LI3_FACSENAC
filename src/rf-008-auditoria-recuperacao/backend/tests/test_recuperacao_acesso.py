import os
import sys
import time
from pathlib import Path
from fastapi.testclient import TestClient

# Configuração de paths para importação de dependências
_TEST_DIR = Path(__file__).resolve().parent
_BACKEND_RF008 = _TEST_DIR.parent
_BACKEND_RF001 = _BACKEND_RF008.parent.parent / "rf-001-gestao-identidade" / "backend"

for p in [str(_BACKEND_RF001), str(_BACKEND_RF008)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from main import app
from dependencies import rate_limiter_global

client = TestClient(app)

def testar_fluxo_completo_recuperacao():
    print("=" * 70)
    print("INICIANDO HOMOLOGAÇÃO: SPRINT 7 - RECUPERAÇÃO DE ACESSO E APPSEC OWASP")
    print("=" * 70)

    # Limpa contadores de rate limit para ambiente de teste isolado
    rate_limiter_global.limpar()

    # 1. Anti-enumeração de contas (OWASP A07) com e-mail inexistente
    print("\n[CENÁRIO 1] Solicitação com e-mail inexistente (Anti-Enumeração OWASP A07)...")
    resp_inexistente = client.post(
        "/recuperar-senha/solicitar",
        json={"email": "usuario_fantasma_9999@senac.edu.br"}
    )
    assert resp_inexistente.status_code == 200, f"Esperado 200, recebido {resp_inexistente.status_code}"
    dados_inexistente = resp_inexistente.json()
    assert "Se o e-mail informado estiver cadastrado" in dados_inexistente["mensagem"]
    assert dados_inexistente.get("debug_token") is None
    print("  -> Sucesso: Resposta neutra sem vazar ausência de cadastro.")

    # 2. Solicitação com e-mail válido existente
    print("\n[CENÁRIO 2] Solicitação com e-mail cadastrado (Geração de Token JWT)...")
    email_teste = "admin@erp.com"
    resp_solicitacao = client.post(
        "/recuperar-senha/solicitar",
        json={"email": email_teste}
    )
    assert resp_solicitacao.status_code == 200, f"Esperado 200, recebido {resp_solicitacao.status_code}"
    dados_solicitacao = resp_solicitacao.json()
    token_jwt = dados_solicitacao.get("debug_token")
    assert token_jwt is not None, "Token JWT deveria ser gerado para usuário existente"
    print(f"  -> Sucesso: Token JWT gerado ({token_jwt[:35]}...).")

    # 3. Teste do alias /auth/esqueci-senha
    rate_limiter_global.limpar()
    print("\n[CENÁRIO 3] Teste de compatibilidade do alias /auth/esqueci-senha...")
    resp_alias = client.post(
        "/auth/esqueci-senha",
        json={"email": email_teste}
    )
    assert resp_alias.status_code == 200
    print("  -> Sucesso: Alias /auth/esqueci-senha responde perfeitamente.")

    # 4. Validação de token via GET query param (Ideal para página web)
    print("\n[CENÁRIO 4] Validação de token via GET /recuperar-senha/validar?token=...")
    resp_validar = client.get(f"/recuperar-senha/validar?token={token_jwt}")
    assert resp_validar.status_code == 200, f"Esperado 200, recebido {resp_validar.status_code}"
    dados_validar = resp_validar.json()
    assert dados_validar["valido"] is True
    assert "a***n@erp.com" in dados_validar["email_mascarado"]
    print(f"  -> Sucesso: Token validado. E-mail mascarado: {dados_validar['email_mascarado']}")

    # 5. Tentativa de redefinição com senhas divergentes
    print("\n[CENÁRIO 5] Tentativa de redefinição com senhas divergentes...")
    resp_divergente = client.post(
        "/recuperar-senha/confirmar",
        json={
            "token": token_jwt,
            "nova_senha": "NovaSenhaSegura123",
            "confirmacao_senha": "OutraSenhaDiferente999"
        }
    )
    assert resp_divergente.status_code == 400
    print("  -> Sucesso: Rejeitado com HTTP 400 (senhas divergentes).")

    # 6. Redefinição bem-sucedida de senha
    print("\n[CENÁRIO 6] Confirmação e redefinição com nova senha válida...")
    nova_senha_teste = "NovaSenhaForte2026!"
    resp_redefinir = client.post(
        "/recuperar-senha/confirmar",
        json={
            "token": token_jwt,
            "nova_senha": nova_senha_teste,
            "confirmacao_senha": nova_senha_teste
        }
    )
    assert resp_redefinir.status_code == 200, f"Esperado 200, recebido {resp_redefinir.status_code}"
    assert resp_redefinir.json()["sucesso"] is True
    print("  -> Sucesso: Senha redefinida, sessões antigas revogadas e token marcado como usado.")

    # 7. Garantia de Uso Único (Single-Use Enforcement): reutilização rejeitada
    print("\n[CENÁRIO 7] Tentativa de reutilizar o mesmo token (Single-Use Enforcement)...")
    resp_reutilizar = client.post(
        "/recuperar-senha/confirmar",
        json={
            "token": token_jwt,
            "nova_senha": "TentativaFraudeTokenUsado123",
            "confirmacao_senha": "TentativaFraudeTokenUsado123"
        }
    )
    assert resp_reutilizar.status_code == 400
    assert "já foi utilizado" in resp_reutilizar.json()["detail"]
    print("  -> Sucesso: Reutilização do token bloqueada com HTTP 400.")

    # 8. Rate Limiting OWASP A07 (Bloqueio anti-força bruta após 3 tentativas no endpoint)
    print("\n[CENÁRIO 8] Rate Limiting OWASP A07 (Anti-Brute Force)...")
    rate_limiter_global.limpar()
    
    # Faz 3 requisições válidas (limite da rota de solicitar)
    for i in range(3):
        r = client.post("/recuperar-senha/solicitar", json={"email": "teste@senac.br"})
        assert r.status_code == 200

    # A 4ª requisição no mesmo minuto deve ser barrada com 429 Too Many Requests
    resp_bloqueio = client.post("/recuperar-senha/solicitar", json={"email": "teste@senac.br"})
    assert resp_bloqueio.status_code == 429, f"Esperado 429, recebido {resp_bloqueio.status_code}"
    assert "Retry-After" in resp_bloqueio.headers
    print(f"  -> Sucesso: Requisição bloqueada com HTTP 429. Retry-After: {resp_bloqueio.headers['Retry-After']}s.")

    print("\n" + "=" * 70)
    print("TODOS OS 8 CENÁRIOS HOMOLOGADOS COM 100% DE SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    testar_fluxo_completo_recuperacao()
