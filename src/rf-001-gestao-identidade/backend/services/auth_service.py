import bcrypt
from fastapi import HTTPException, status
from repositories.auth_repository import get_user_by_email
from schemas.auth_schemas import AuthRequest, AuthResponse

_DUMMY_HASH = bcrypt.hashpw(b"dummy-password", bcrypt.gensalt())

def autenticar_usuario(payload: AuthRequest) -> AuthResponse:
    usuario = get_user_by_email(payload.email)

    if not usuario:

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

    return AuthResponse(role=usuario["user_role"])