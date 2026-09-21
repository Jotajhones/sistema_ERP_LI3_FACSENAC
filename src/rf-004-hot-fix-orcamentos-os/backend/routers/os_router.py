import os
import sys

_BACKEND_RF004 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_RF001 = os.path.abspath(os.path.join(_BACKEND_RF004, "..", "..", "rf-001-gestao-identidade", "backend"))
if _BACKEND_RF001 not in sys.path:
    sys.path.append(_BACKEND_RF001)

from fastapi import APIRouter, Depends, status
from schemas.os_schemas import OSConvertPayload, OSResponse
from services import os_service
from dependencies import get_current_user

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Serviço"])

@router.post("/converter/{orcamento_id}", response_model=OSResponse, status_code=status.HTTP_201_CREATED)
async def converter_orcamento_em_os(
    orcamento_id: str,
    payload: OSConvertPayload,
    vendedor_id: str = Depends(get_current_user)
):
    """Transforma um Orçamento existente em uma Ordem de Serviço finalizada e debita o estoque."""
    return await os_service.converter_orcamento(orcamento_id, payload, vendedor_id)