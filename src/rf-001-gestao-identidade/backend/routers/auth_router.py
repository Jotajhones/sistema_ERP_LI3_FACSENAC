from fastapi import APIRouter, Depends, status
from schemas.auth_schemas import AuthRequest, AuthResponse
from services.auth_service import autenticar_usuario, encerrar_sessao
from dependencies import obter_token_atual

router = APIRouter(tags=["Autenticação"])

@router.post("/auth", response_model=AuthResponse)
def login(requisicao: AuthRequest):
    return autenticar_usuario(requisicao)

@router.post("/auth/logout", status_code=status.HTTP_200_OK)
def encerrar_sessao_usuario(token: str = Depends(obter_token_atual)):
    return encerrar_sessao(token)