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


def obter_token_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    if not credenciais or not credenciais.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticacao ausente ou invalido"
        )

    token = credenciais.credentials
    sessao = get_session_by_token(token)

    if not sessao:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou sessao expirada"
        )

    return token

get_current_token = obter_token_atual


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


obter_usuario_atual = get_current_user
obter_papel_usuario = get_user_role
exigir_papeis = require_role


import time
import threading
from fastapi import Request


class RateLimiterMemoria:
    """
    Controlador de limitação de taxa (Rate Limiter) em memória com janela deslizante (Sliding Window),
    thread-safe e em conformidade com OWASP A07 (Anti-Brute Force e Anti-Enumeração).
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._historico: dict[str, list[float]] = {}

    def verificar_e_registrar(
        self,
        chave: str,
        limite_requisicoes: int,
        janela_segundos: int
    ) -> tuple[bool, int, int]:
        agora = time.time()
        corte_janela = agora - janela_segundos

        with self._lock:
            timestamps = self._historico.get(chave, [])
            timestamps = [ts for ts in timestamps if ts > corte_janela]

            if len(timestamps) >= limite_requisicoes:
                ts_mais_antiga = timestamps[0]
                segundos_restantes = max(1, int(janela_segundos - (agora - ts_mais_antiga)) + 1)
                self._historico[chave] = timestamps
                return False, segundos_restantes, 0

            timestamps.append(agora)
            self._historico[chave] = timestamps
            restantes = max(0, limite_requisicoes - len(timestamps))
            return True, 0, restantes

    def limpar(self, chave: str = None):
        with self._lock:
            if chave:
                self._historico.pop(chave, None)
            else:
                self._historico.clear()


rate_limiter_global = RateLimiterMemoria()


def extrair_ip_cliente(request: Request) -> str:
    """Extrai o IP real do cliente considerando proxies reversos (Render, Vercel, Cloudflare)."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


def limitar_taxa_requisicao(
    escopo: str,
    limite: int = 5,
    janela_segundos: int = 60
) -> Callable:
    """
    Cria uma dependência FastAPI para aplicar rate limiting (OWASP A07).
    """
    def dependency(request: Request):
        ip = extrair_ip_cliente(request)
        chave = f"{escopo}:{ip}"

        permitido, segundos_espera, restantes = rate_limiter_global.verificar_e_registrar(
            chave=chave,
            limite_requisicoes=limite,
            janela_segundos=janela_segundos
        )

        if not permitido:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Muitas requisições para a rota de {escopo}. "
                    f"Por favor, aguarde {segundos_espera} segundo(s) antes de tentar novamente (OWASP A07)."
                ),
                headers={
                    "Retry-After": str(segundos_espera),
                    "X-RateLimit-Limit": str(limite),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(segundos_espera)
                }
            )

    return dependency

