from fastapi import APIRouter, Depends, status
from schemas.auth_schemas import AuthRequest, AuthResponse
from services.auth_service import autenticar_usuario, encerrar_sessao
from dependencies import get_current_token

router = APIRouter(tags=["Autenticação"])

@router.post("/auth", response_model=AuthResponse)
def login(payload: AuthRequest):
    return autenticar_usuario(payload)

@router.post("/auth/logout", status_code=status.HTTP_200_OK)
def logout(token: str = Depends(get_current_token)):
    return encerrar_sessao(token)