from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from dependencies import get_current_user
from schemas.pessoas_schemas import PessoaResponse
from services.usuarios_service import listar_pessoas


router = APIRouter(
    prefix="/pessoas",
    tags=["Pessoas - RF005"]
)


@router.get(
    "",
    response_model=List[PessoaResponse]
)
def listar_pessoas_rf005(
    ativo: Optional[bool] = Query(
        None,
        description="Filtra pessoas por situação ativa/inativa."
    ),
    usuario_id: str = Depends(get_current_user)
):
    return listar_pessoas(
        usuario_logado_id=usuario_id,
        ativo=ativo
    )