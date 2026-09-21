import os
import sys

_BACKEND_RF004 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_RF001 = os.path.abspath(
    os.path.join(_BACKEND_RF004, "..", "..", "rf-001-gestao-identidade", "backend")
)
if _BACKEND_RF001 not in sys.path:
    sys.path.append(_BACKEND_RF001)

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from schemas.orcamentos_schema import OrcamentoCreate, OrcamentoResponse
from services import orcamentos_service
from dependencies import get_current_user, require_role

router = APIRouter(prefix="/orcamentos", tags=["Orçamentos"])

@router.post("", response_model=OrcamentoResponse, status_code=status.HTTP_201_CREATED)
async def gerar_orcamento(
    payload: OrcamentoCreate, 
    vendedor_id: str = Depends(get_current_user)
):
    return await orcamentos_service.criar_orcamento(payload, vendedor_id)

@router.get("", response_model=List[OrcamentoResponse])
async def buscar_orcamentos(vendedor_id: str = Depends(get_current_user)):
    return await orcamentos_service.listar_orcamentos()

@router.get("/{orcamento_id}", response_model=OrcamentoResponse)
async def buscar_orcamento_por_id(
    orcamento_id: UUID, 
    usuario=Depends(require_role(["ADMIN", "GESTOR", "VENDEDOR"]))
):
    orcamento = await orcamentos_service.obter_orcamento(str(orcamento_id))
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    return orcamento