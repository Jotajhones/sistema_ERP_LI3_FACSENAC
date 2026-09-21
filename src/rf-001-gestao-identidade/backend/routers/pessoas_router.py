from typing import List
from fastapi import APIRouter, status, Depends
from schemas.pessoas_schemas import PessoaCreate, PessoaResponse, PessoaUpdate
import services.pessoas_service as service
from dependencies import get_current_user

router = APIRouter(prefix="/pessoas", tags=["Pessoas"])

@router.post("", response_model=PessoaResponse, status_code=status.HTTP_201_CREATED)
async def criar_pessoa(
    payload: PessoaCreate, 
    usuario_id: str = Depends(get_current_user)
):
    return await service.cadastrar_pessoa(payload)

@router.get("", response_model=List[PessoaResponse])
async def listar_pessoas(usuario_id: str = Depends(get_current_user)):
    return await service.listar_todas_pessoas()

@router.get("/{pessoa_id}", response_model=PessoaResponse)
async def obter_pessoa_por_id(pessoa_id: str, usuario_id: str = Depends(get_current_user)):
    return await service.buscar_pessoa_por_id(pessoa_id)

@router.get("/cpf/{cpf}", response_model=PessoaResponse)
async def buscar_pessoa_por_cpf(cpf: str, usuario_id: str = Depends(get_current_user)):
    """Busca os dados de uma pessoa utilizando o CPF para pré-preenchimento no orçamento."""
    return await service.buscar_pessoa_por_cpf_service(cpf)

@router.put("/{pessoa_id}", response_model=PessoaResponse)
async def atualizar_pessoa(
    pessoa_id: str,
    payload: PessoaUpdate,
    usuario_logado: dict = Depends(get_current_user)
):
    """Atualiza os dados comerciais e de endereço de um cliente de balcão."""
    return await service.atualizar_pessoa_segura(pessoa_id, payload, usuario_logado)