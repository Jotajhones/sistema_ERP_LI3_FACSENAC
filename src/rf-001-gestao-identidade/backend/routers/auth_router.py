from fastapi import APIRouter, Depends, status
from schemas.auth_schemas import AuthRequest, AuthResponse, AlterarSenhaRequest, MensagemResposta
from services.auth_service import autenticar_usuario, encerrar_sessao, alterar_senha_usuario
from dependencies import obter_token_atual, obter_usuario_atual

router = APIRouter(tags=["Autenticação"])

@router.post("/auth", response_model=AuthResponse)
def login(requisicao: AuthRequest):
    return autenticar_usuario(requisicao)

@router.post("/auth/logout", status_code=status.HTTP_200_OK)
def encerrar_sessao_usuario(token: str = Depends(obter_token_atual)):
    return encerrar_sessao(token)

@router.patch("/auth/senha", status_code=status.HTTP_200_OK, response_model=MensagemResposta)
@router.put("/auth/senha", status_code=status.HTTP_200_OK, response_model=MensagemResposta)
def alterar_propria_senha(
    requisicao: AlterarSenhaRequest,
    usuario_id: str = Depends(obter_usuario_atual)
):
    return alterar_senha_usuario(usuario_id, requisicao)
