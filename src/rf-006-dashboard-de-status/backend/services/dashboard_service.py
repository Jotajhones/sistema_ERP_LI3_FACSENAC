import logging
from datetime import date, timedelta

from fastapi import HTTPException, status
from pydantic import ValidationError

from repositories import dashboard_repository
from schemas.dashboard_schemas import (
    ConversaoOrcamentosResponse,
    PeriodoResponse
)


logger = logging.getLogger(__name__)


def obter_conversao_orcamentos(
    data_inicio: date,
    data_fim: date
) -> ConversaoOrcamentosResponse:

    if data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="data_inicio não pode ser posterior a data_fim."
        )

    # data_fim chega inclusiva; o banco filtra com limite superior exclusivo.
    try:
        data_fim_exclusiva = data_fim + timedelta(days=1)
    except OverflowError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="data_fim fora do intervalo suportado."
        )

    try:
        bruto = dashboard_repository.obter_conversao_orcamentos(
            data_inicio=data_inicio,
            data_fim_exclusiva=data_fim_exclusiva
        )
    except dashboard_repository.DashboardIndisponivelError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de dados indisponível. Tente novamente em instantes."
        )
    except dashboard_repository.DashboardRepositoryError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao calcular a conversão de orçamentos."
        )

    try:
        total = int(bruto.get("total_orcamentos") or 0)
        convertidos = int(bruto.get("orcamentos_convertidos") or 0)
        pendentes = int(bruto.get("orcamentos_pendentes") or 0)

        taxa = round(convertidos / total * 100, 2) if total else 0.0

        return ConversaoOrcamentosResponse(
            periodo=PeriodoResponse(
                data_inicio=data_inicio,
                data_fim=data_fim
            ),
            total_orcamentos=total,
            orcamentos_convertidos=convertidos,
            orcamentos_pendentes=pendentes,
            taxa_conversao=taxa,
            valor_total_orcado=round(float(bruto.get("valor_total_orcado") or 0), 2),
            valor_total_convertido=round(float(bruto.get("valor_total_convertido") or 0), 2)
        )
    except (TypeError, ValueError, ValidationError) as erro:
        logger.error("RF-006: payload inesperado vindo do banco: %r", erro)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao calcular a conversão de orçamentos."
        )
