import os
import sys
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status

_DIRETORIO_MODULO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
if _DIRETORIO_MODULO not in sys.path:
    sys.path.insert(0, _DIRETORIO_MODULO)

_DIRETORIO_RF001 = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "rf-001-gestao-identidade",
        "backend",
    )
)
if _DIRETORIO_RF001 not in sys.path:
    sys.path.append(_DIRETORIO_RF001)

from dependencies import get_current_user
from schemas.contatos_schemas import (
    ContatoConfirmacaoResposta,
    OrcamentoPendenteContatoResposta,
)
from services.contatos_service import (
    obter_pendentes_de_contato,
    registrar_contato,
)

router = APIRouter(
    prefix="/orcamentos",
    tags=["RF-007 - Tracking de Contatos de Orçamentos"]
)


@router.get(
    "/pendentes-contato",
    response_model=List[OrcamentoPendenteContatoResposta],
    status_code=status.HTTP_200_OK,
    summary="Recuperar orçamentos pendentes que ainda não foram contatados",
)
def listar_orcamentos_pendentes(
    usuario_id: str = Depends(get_current_user)
):
    return obter_pendentes_de_contato()


@router.post(
    "/{orcamento_id}/contato",
    response_model=ContatoConfirmacaoResposta,
    status_code=status.HTTP_200_OK,
    summary="Registrar que o orçamento foi contatado via WhatsApp",
)
def registrar_contato_orcamento(
    orcamento_id: UUID,
    usuario_id: str = Depends(get_current_user)
):
    return registrar_contato(
        orcamento_id=str(orcamento_id),
        vendedor_id=usuario_id
    )


@router.post(
    "/{orcamento_id}/contatar",
    response_model=ContatoConfirmacaoResposta,
    status_code=status.HTTP_200_OK,
    summary="Alias de compatibilidade com o frontend para marcar contato",
)
def contatar_orcamento_alias(
    orcamento_id: UUID,
    usuario_id: str = Depends(get_current_user)
):
    return registrar_contato(
        orcamento_id=str(orcamento_id),
        vendedor_id=usuario_id
    )
