import os
import sys
from datetime import date

_BACKEND_RF006 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_RF001 = os.path.abspath(
    os.path.join(_BACKEND_RF006, "..", "..", "rf-001-gestao-identidade", "backend")
)
if _BACKEND_RF001 not in sys.path:
    sys.path.append(_BACKEND_RF001)

from fastapi import APIRouter, Depends, Query

from dependencies import require_role
from schemas.dashboard_schemas import ConversaoOrcamentosResponse
from services import dashboard_service


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/conversao-orcamentos",
    response_model=ConversaoOrcamentosResponse,
    summary="Taxa de conversão de orçamentos em OS por período",
    responses={
        401: {"description": "Token ausente, inválido ou sessão expirada"},
        403: {"description": "Perfil sem permissão (apenas ADMIN e GESTOR)"},
        500: {"description": "Erro interno ao calcular o indicador"},
        503: {"description": "Banco de dados indisponível"}
    }
)
def conversao_orcamentos(
    data_inicio: date = Query(..., description="Início do período (YYYY-MM-DD), inclusivo."),
    data_fim: date = Query(..., description="Fim do período (YYYY-MM-DD), inclusivo."),
    _usuario_id: str = Depends(require_role(["ADMIN", "GESTOR"]))
):
    """Total de orçamentos do período, quantos viraram OS, taxa de conversão (%) e valores.
    Acesso restrito a ADMIN e GESTOR. Responde 422 para parâmetros inválidos
    ou quando data_inicio é posterior a data_fim."""
    return dashboard_service.obter_conversao_orcamentos(
        data_inicio=data_inicio,
        data_fim=data_fim
    )
