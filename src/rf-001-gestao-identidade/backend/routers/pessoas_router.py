from typing import List
from fastapi import APIRouter, status
from schemas.pessoas_schemas import PessoaCreate, PessoaResponse
import services.pessoas_service as service

router = APIRouter(prefix="/pessoas", tags=["Pessoas"])

@router.post("", response_model=PessoaResponse, status_code=status.HTTP_201_CREATED)
def criar_pessoa(payload: PessoaCreate):
    return service.cadastrar_pessoa(payload)

@router.get("", response_model=List[PessoaResponse])
def listar_pessoas():
    return service.listar_todas_pessoas()

@router.get("/user/{user_id}", response_model=PessoaResponse)
def obter_pessoa(user_id: str):
    return service.buscar_pessoa_por_user(user_id)