import logging
from datetime import date
from typing import Any, Dict

import httpx

from database import get_supabase_client


logger = logging.getLogger(__name__)

RPC_CONVERSAO_ORCAMENTOS = "/rest/v1/rpc/rf006_conversao_orcamentos"


class DashboardRepositoryError(Exception):
    """Falha ao consultar o banco. Nunca carrega o corpo da resposta do banco."""


class DashboardIndisponivelError(DashboardRepositoryError):
    """Banco inacessível (timeout, conexão ou 5xx do Supabase)."""


class DashboardErroInternoError(DashboardRepositoryError):
    """Resposta inesperada do banco (4xx, JSON inválido, função ausente)."""


def obter_conversao_orcamentos(
    data_inicio: date,
    data_fim_exclusiva: date
) -> Dict[str, Any]:

    payload = {
        "p_data_inicio": data_inicio.isoformat(),
        "p_data_fim": data_fim_exclusiva.isoformat()
    }

    try:
        with get_supabase_client() as client:
            response = client.post(RPC_CONVERSAO_ORCAMENTOS, json=payload)
    except httpx.RequestError as erro:
        logger.error("RF-006: falha de rede ao chamar o Supabase: %r", erro)
        raise DashboardIndisponivelError() from erro

    if response.status_code in (200, 201):
        try:
            data = response.json()
        except ValueError as erro:
            logger.error("RF-006: resposta do Supabase não é JSON válido.")
            raise DashboardErroInternoError() from erro

        if isinstance(data, list):
            data = data[0] if data else {}

        if not isinstance(data, dict):
            logger.error("RF-006: formato inesperado na resposta do Supabase.")
            raise DashboardErroInternoError()

        return data

    # O corpo do erro vai apenas para o log do servidor, nunca para o cliente.
    logger.error(
        "RF-006: Supabase respondeu %s: %s",
        response.status_code,
        response.text[:500]
    )

    if response.status_code >= 500:
        raise DashboardIndisponivelError()

    raise DashboardErroInternoError()
