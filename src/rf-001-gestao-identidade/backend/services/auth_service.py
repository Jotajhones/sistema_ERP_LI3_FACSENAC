import uuid
import bcrypt
from fastapi import HTTPException, status
from repositories.auth_repository import get_user_by_email, create_session
from schemas.auth_schemas import AuthRequest, AuthResponse

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