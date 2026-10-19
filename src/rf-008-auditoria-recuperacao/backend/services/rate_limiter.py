import os
import sys
import time
import threading
from typing import Dict, List, Tuple, Callable
from fastapi import Request, HTTPException, status

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

try:
    from dependencies import (
        RateLimiterMemoria,
        rate_limiter_global,
        extrair_ip_cliente,
        limitar_taxa_requisicao
    )
    criar_dependencia_rate_limit = limitar_taxa_requisicao
except ImportError:
    class RateLimiterMemoria:
        def __init__(self):
            self._lock = threading.Lock()
            self._historico: Dict[str, List[float]] = {}

        def verificar_e_registrar(
            self,
            chave: str,
            limite_requisicoes: int,
            janela_segundos: int
        ) -> Tuple[bool, int, int]:
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
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    def criar_dependencia_rate_limit(
        escopo: str,
        limite: int = 5,
        janela_segundos: int = 60
    ) -> Callable:
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
