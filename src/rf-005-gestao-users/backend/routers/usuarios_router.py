from fastapi import APIRouter, Depends, status

from dependencies import get_current_user
from schemas.usuarios_schemas import UsuarioCreate, UsuarioResponse
from services.usuarios_service import criar_usuario


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED
)
def criar_novo_usuario(
    payload: UsuarioCreate,
    usuario_id: str = Depends(get_current_user)
):
    return criar_usuario(
        payload=payload,
        usuario_logado_id=usuario_id
    )