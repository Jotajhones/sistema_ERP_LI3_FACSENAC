from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import get_supabase_client
from repositories.auth_repository import get_session_by_token


security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticacao ausente ou invalido"
        )

    token = credentials.credentials
    sessao = get_session_by_token(token)

    if not sessao:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou sessao expirada"
        )

    return str(sessao["user_id"])


def get_user_role(user_id: str) -> str:
    with get_supabase_client() as client:
        response = client.get(
            "/rest/v1/users",
            params={
                "id": f"eq.{user_id}",
                "select": "id,user_role,ativo"
            }
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível validar as permissões do usuário."
        )

    usuarios = response.json()

    if not usuarios:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário da sessão não encontrado."
        )

    usuario = usuarios[0]

    if not usuario.get("ativo", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo."
        )

    user_role = usuario.get("user_role")

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: permissões insuficientes para esta ação"
        )

    return str(user_role).upper()


def require_role(allowed_roles: list[str]) -> Callable:
    roles_permitidas = {
        role.strip().upper()
        for role in allowed_roles
        if role and role.strip()
    }

    def role_checker(
        user_id: str = Depends(get_current_user)
    ) -> str:
        user_role = get_user_role(user_id)

        if user_role not in roles_permitidas:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Acesso negado: permissões insuficientes "
                    "para esta ação"
                )
            )

        return user_id

    return role_checker
