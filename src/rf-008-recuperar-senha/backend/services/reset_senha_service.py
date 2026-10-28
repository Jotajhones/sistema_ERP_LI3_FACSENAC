import bcrypt

from fastapi import HTTPException, status

from repositories.auth_repository import obter_usuario_por_id
from repositories.reset_senha_repository import resetar_senha_usuario


# RN-01: a senha padrão vive apenas no backend, nunca chega pelo payload
NOVA_SENHA = "senha123"


def resetar_senha(
    user_id_alvo: str,
    usuario_logado_id: str
):

    usuario_alvo = obter_usuario_por_id(user_id_alvo)

    if not usuario_alvo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    usuario_logado = obter_usuario_por_id(usuario_logado_id)

    role_logado = str(
        usuario_logado.get("user_role", "")
    ).upper()

    role_alvo = str(
        usuario_alvo.get("user_role", "")
    ).upper()

    if role_logado == "GESTOR" and role_alvo == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="GESTOR não pode resetar a senha de um ADMIN."
        )

    hash_padrao = bcrypt.hashpw(
        NOVA_SENHA.encode("utf-8"),
        bcrypt.gensalt(12)
    ).decode("utf-8")

    if not resetar_senha_usuario(user_id_alvo, hash_padrao):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    # RNF-01: a resposta nunca expõe a senha gerada
    return {
        "mensagem": "Senha resetada com sucesso. Todas as sessões do usuário foram encerradas."
    }
