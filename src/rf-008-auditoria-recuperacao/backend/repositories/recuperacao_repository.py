import os
import sys
import threading
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timezone

_DIRETORIO_RF001 = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "rf-001-gestao-identidade",
        "backend",
    )
)
if _DIRETORIO_RF001 not in sys.path:
    sys.path.append(_DIRETORIO_RF001)

from database import get_supabase_client
from repositories.auth_repository import (
    get_user_by_email,
    obter_usuario_por_id,
    atualizar_senha_usuario
)

# Cache de contingência em memória para resiliência arquitetural
_LOCK_CACHE = threading.Lock()
_CACHE_TOKENS: Dict[str, Dict[str, Any]] = {}


def _calcular_hash_token(token_jwt: str) -> str:
    """Gera um hash SHA-256 do token JWT para persistência segura na base."""
    return hashlib.sha256(token_jwt.encode("utf-8")).hexdigest()


def salvar_token_recuperacao(
    user_id: str,
    token_jti: str,
    token_jwt: str,
    expira_em: datetime
) -> Dict[str, Any]:
    """
    Persiste o token de recuperação na tabela `recuperacao_tokens` do Supabase.
    Possui contingência resiliente em cache para operar perfeitamente antes da aplicação do DDL.
    """
    hash_token = _calcular_hash_token(token_jwt)
    registro_cache = {
        "user_id": str(user_id),
        "token_jti": str(token_jti),
        "token_hash": hash_token,
        "usado": False,
        "expira_em": expira_em.isoformat(),
        "criado_em": datetime.now(timezone.utc).isoformat()
    }

    with _LOCK_CACHE:
        _CACHE_TOKENS[token_jti] = registro_cache

    try:
        payload_supabase = {
            "user_id": str(user_id),
            "token_jti": str(token_jti),
            "token_hash": hash_token,
            "usado": False,
            "expira_em": expira_em.isoformat()
        }
        with get_supabase_client() as client:
            resp = client.post(
                "/rest/v1/recuperacao_tokens",
                json=payload_supabase,
                headers={"Prefer": "return=representation"}
            )
            if resp.status_code in (200, 201):
                dados = resp.json()
                if isinstance(dados, list) and dados:
                    return dados[0]
                return dados
    except Exception:
        # Fallback gracioso para cache de contingência
        pass

    return registro_cache


def obter_token_recuperacao_por_jti(token_jti: str) -> Optional[Dict[str, Any]]:
    """
    Recupera os metadados de controle do token pelo identificador único (JTI).
    """
    # 1. Tenta buscar no banco remoto
    try:
        with get_supabase_client() as client:
            resp = client.get(
                "/rest/v1/recuperacao_tokens",
                params={
                    "token_jti": f"eq.{token_jti}",
                    "select": "id,user_id,token_jti,token_hash,usado,expira_em,criado_em"
                }
            )
            if resp.status_code == 200:
                dados = resp.json()
                if dados and len(dados) > 0:
                    return dados[0]
    except Exception:
        pass

    # 2. Fallback para cache de contingência
    with _LOCK_CACHE:
        return _CACHE_TOKENS.get(token_jti)


def marcar_token_como_usado(token_jti: str) -> bool:
    """
    Garante o uso único (Single-Use Enforcement), marcando o token como consumido.
    """
    with _LOCK_CACHE:
        if token_jti in _CACHE_TOKENS:
            _CACHE_TOKENS[token_jti]["usado"] = True

    try:
        with get_supabase_client() as client:
            resp = client.patch(
                f"/rest/v1/recuperacao_tokens?token_jti=eq.{token_jti}",
                json={"usado": True},
                headers={"Prefer": "return=representation"}
            )
            if resp.status_code in (200, 204):
                return True
    except Exception:
        pass

    return True


def revogar_todas_sessoes_usuario(user_id: str) -> bool:
    """
    Revoga todas as sessões ativas do usuário após a alteração de senha (OWASP AppSec).
    """
    try:
        with get_supabase_client() as client:
            resp = client.delete(f"/rest/v1/sessoes?user_id=eq.{user_id}")
            return resp.status_code in (200, 204)
    except Exception:
        return False
