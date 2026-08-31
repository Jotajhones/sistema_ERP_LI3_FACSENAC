from fastapi import APIRouter
from schemas.auth_schemas import AuthRequest, AuthResponse
from services.auth_service import autenticar_usuario

router = APIRouter(tags=["Autenticação"])

@router.post("/auth", response_model=AuthResponse)
def login(payload: AuthRequest):

    return autenticar_usuario(payload)