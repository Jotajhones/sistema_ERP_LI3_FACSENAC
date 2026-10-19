import bcrypt
from datetime import datetime, timezone
from fastapi import HTTPException, status

from schemas.recuperacao_schemas import (
    EsqueciSenhaRequisicao,
    EsqueciSenhaResposta,
    ValidarTokenRequisicao,
    ValidarTokenResposta,
    RedefinirSenhaRequisicao,
    RedefinirSenhaResposta,
)
from services.jwt_recuperacao import (
    gerar_token_recuperacao,
    decodificar_e_validar_jwt,
)
from repositories.recuperacao_repository import (
    get_user_by_email,
    salvar_token_recuperacao,
    obter_token_recuperacao_por_jti,
    marcar_token_como_usado,
    atualizar_senha_usuario,
    revogar_todas_sessoes_usuario,
)

# Hash dummy para equalização de tempo contra timing-attack e enumeração de usuários (OWASP A07)
_DUMMY_HASH = bcrypt.hashpw(b"dummy-auth-timing-protection", bcrypt.gensalt(12))


def mascarar_email(email: str) -> str:
    """Mascara o e-mail para exibição segura no frontend (ex: mig***s@edu.df.senac.br)."""
    if not email or "@" not in email:
        return "u***@dominio.com"

    usuario, dominio = email.split("@", 1)
    if len(usuario) <= 2:
        usuario_mascarado = usuario[0] + "***"
    else:
        usuario_mascarado = f"{usuario[0]}***{usuario[-1]}"

    return f"{usuario_mascarado}@{dominio}"


def solicitar_recuperacao(dados: EsqueciSenhaRequisicao) -> EsqueciSenhaResposta:
    """
    Inicia o fluxo de recuperação de senha gerando um token JWT temporário.
    Protegido contra enumeração de contas (OWASP A07): retorna mensagem neutra idêntica
    seja o e-mail existente ou inexistente.
    """
    email_limpo = str(dados.email).strip().lower()
    usuario = get_user_by_email(email_limpo)

    mensagem_neutra = (
        "Se o e-mail informado estiver cadastrado em nosso sistema, as instruções "
        "com o link para redefinição de senha foram geradas com sucesso."
    )

    if not usuario or not usuario.get("ativo", True):
        # Proteção contra timing attack
        bcrypt.checkpw(email_limpo.encode("utf-8"), _DUMMY_HASH)
        return EsqueciSenhaResposta(
            mensagem=mensagem_neutra,
            expira_em_minutos=15,
            debug_token=None
        )

    user_id = str(usuario["id"])
    token_jwt, token_jti, expira_em = gerar_token_recuperacao(
        user_id=user_id,
        email=email_limpo,
        validade_minutos=15
    )

    # Persiste na tabela / cache de contingência
    salvar_token_recuperacao(
        user_id=user_id,
        token_jti=token_jti,
        token_jwt=token_jwt,
        expira_em=expira_em
    )

    # Requisito explícito do MVP da Sprint 7 no Card 36:
    # "enviados por e-mail ou logados no console para o escopo do MVP"
    print("\n" + "=" * 70)
    print(f"[RECOVERY SERVICE - SPRINT 7] Notificação de Recuperação de Acesso")
    print(f"Usuário / E-mail: {email_limpo}")
    print(f"JTI de Uso Único: {token_jti}")
    print(f"Validade: Até {expira_em.isoformat()} (15 minutos)")
    print(f"Token JWT: {token_jwt}")
    print(f"Link Simulado (Front): https://sistema-erp-li-3-facsenac.vercel.app/redefinir-senha.html?token={token_jwt}")
    print("=" * 70 + "\n")

    return EsqueciSenhaResposta(
        mensagem=mensagem_neutra,
        expira_em_minutos=15,
        debug_token=token_jwt
    )


def validar_token(token: str) -> ValidarTokenResposta:
    """
    Valida a assinatura, expiração e garantia de uso único do token de recuperação.
    """
    payload = decodificar_e_validar_jwt(token)
    token_jti = payload["jti"]

    registro = obter_token_recuperacao_por_jti(token_jti)
    if registro and registro.get("usado", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este link de recuperação já foi utilizado. Por favor, solicite um novo."
        )

    email_cliente = payload.get("email", "")
    return ValidarTokenResposta(
        valido=True,
        mensagem="Token de recuperação válido e pronto para uso",
        email_mascarado=mascarar_email(email_cliente)
    )


def redefinir_senha(dados: RedefinirSenhaRequisicao) -> RedefinirSenhaResposta:
    """
    Efetua a redefinição da senha do usuário após validação estrita do token de uso único.
    """
    if dados.confirmacao_senha and dados.nova_senha != dados.confirmacao_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha e a confirmação de senha não coincidem"
        )

    if len(dados.nova_senha) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve possuir no mínimo 6 caracteres"
        )

    # Valida criptografia e expiração do JWT
    payload = decodificar_e_validar_jwt(dados.token)
    token_jti = payload["jti"]
    user_id = payload["sub"]

    # Valida single-use
    registro = obter_token_recuperacao_por_jti(token_jti)
    if registro and registro.get("usado", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este token de recuperação já foi utilizado. Solicite um novo link de redefinição."
        )

    # Gera novo hash com bcrypt (12 rounds)
    novo_hash = bcrypt.hashpw(
        dados.nova_senha.encode("utf-8"),
        bcrypt.gensalt(12)
    ).decode("utf-8")

    # Atualiza a senha no banco de dados
    atualizar_senha_usuario(user_id, novo_hash)

    # Invalida o token para impedir qualquer reutilização (Single-Use Enforcement)
    marcar_token_como_usado(token_jti)

    # Revoga todas as sessões anteriores para segurança de conta
    revogar_todas_sessoes_usuario(user_id)

    return RedefinirSenhaResposta(
        sucesso=True,
        mensagem="Senha redefinida com sucesso. Você já pode acessar o sistema com sua nova senha."
    )
