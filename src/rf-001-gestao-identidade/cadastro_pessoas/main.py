import re
from typing import List
from fastapi import FastAPI, APIRouter, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

try:
    from .schemas import PessoaCreate, PessoaResponse
    from .database import (
        get_user_by_id,
        get_pessoa_by_user_id,
        get_pessoa_by_cpf,
        create_pessoa,
        list_pessoas
    )
except ImportError:
    from schemas import PessoaCreate, PessoaResponse
    from database import (
        get_user_by_id,
        get_pessoa_by_user_id,
        get_pessoa_by_cpf,
        create_pessoa,
        list_pessoas
    )

router = APIRouter(prefix="/pessoas", tags=["Pessoas"])

@router.post(
    "",
    response_model=PessoaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastro de Pessoa"
)
def cadastrar_pessoa(payload: PessoaCreate):
    clean_cpf = re.sub(r"\D", "", payload.cpf)
    if len(clean_cpf) != 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF deve conter 11 dígitos numéricos."
        )

    user = get_user_by_id(str(payload.user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com ID {payload.user_id} não encontrado."
        )

    existing_pessoa_user = get_pessoa_by_user_id(str(payload.user_id))
    if existing_pessoa_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma pessoa cadastrada para este user_id (relação 1:1)."
        )

    existing_cpf = get_pessoa_by_cpf(clean_cpf)
    if existing_cpf:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este CPF já está cadastrado no sistema."
        )

    data = {
        "user_id": str(payload.user_id),
        "nome": payload.nome.strip(),
        "cpf": clean_cpf
    }

    try:
        created = create_pessoa(data)
        return created
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar pessoa no banco de dados: {str(err)}"
        )

@router.get(
    "",
    response_model=List[PessoaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listagem de Pessoas"
)
def listar_pessoas():
    return list_pessoas()

@router.get(
    "/user/{user_id}",
    response_model=PessoaResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar Pessoa por User ID"
)
def buscar_pessoa_por_user_id(user_id: str):
    pessoa = get_pessoa_by_user_id(user_id)
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada para o user_id informado."
        )
    return pessoa

app = FastAPI(
    title="Sistema ERP - Cadastro de Pessoas (RF-001)",
    description="API para cadastro de entidades físicas (Pessoas) associadas aos usuários do ERP.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "API Cadastro de Pessoas - RF-001",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
