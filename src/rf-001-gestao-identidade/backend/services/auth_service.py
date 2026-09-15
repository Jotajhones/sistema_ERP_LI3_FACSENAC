import uuid
import bcrypt
from fastapi import HTTPException, status
from repositories.auth_repository import (
    get_user_by_email,
    create_session,
    excluir_sessao,
    obter_usuario_por_id,
    atualizar_senha_usuario
)
from schemas.auth_schemas import AuthRequest, AuthResponse, AlterarSenhaRequest

# Hash de custo 12 para uniformizar com o padrão de segurança
_DUMMY_HASH = bcrypt.hashpw(b"dummy-password", bcrypt.gensalt(12))

def autenticar_usuario(payload: AuthRequest) -> AuthResponse:
    usuario = get_user_by_email(payload.email)

    if not usuario or not usuario.get("ativo", True):
        # Queima o mesmo ciclo de CPU mesmo se o usuário não existir ou estiver inativo
        bcrypt.checkpw(payload.senha.encode("utf-8"), _DUMMY_HASH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos"
        )

    senha_valida = bcrypt.checkpw(
        payload.senha.encode("utf-8"),
        usuario["password_hash"].encode("utf-8")
    )

    if not senha_valida:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos"
        )

    token = str(uuid.uuid4())
    create_session(str(usuario["id"]), token)

    return AuthResponse(
        role=usuario["user_role"],
        token=token
    )

def encerrar_sessao(token: str) -> dict:
    excluir_sessao(token)
    return {"detail": "Sessão encerrada com sucesso"}

def alterar_senha_usuario(usuario_id: str, dados: AlterarSenhaRequest) -> dict:
    usuario = obter_usuario_por_id(usuario_id)

    if not usuario or not usuario.get("ativo", True):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado ou inativo"
        )

    senha_valida = bcrypt.checkpw(
        dados.senha_atual.encode("utf-8"),
        usuario["password_hash"].encode("utf-8")
    )

    if not senha_valida:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )

    if dados.senha_atual == dados.nova_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve ser diferente da senha atual"
        )

    novo_hash = bcrypt.hashpw(
        dados.nova_senha.encode("utf-8"),
        bcrypt.gensalt(12)
    ).decode("utf-8")

    atualizar_senha_usuario(usuario_id, novo_hash)

    return {"mensagem": "Senha atualizada com sucesso"}