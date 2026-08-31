import re
from fastapi import HTTPException, status
from schemas.pessoas_schemas import PessoaCreate, PessoaResponse
from repositories import pessoas_repository

def cadastrar_pessoa(payload: PessoaCreate) -> PessoaResponse:
    clean_cpf = re.sub(r"\D", "", payload.cpf)
    
    if len(clean_cpf) != 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF deve conter 11 dígitos numéricos."
        )

    user = pessoas_repository.get_user_by_id(str(payload.user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com ID {payload.user_id} não encontrado."
        )

    if pessoas_repository.get_pessoa_by_user_id(str(payload.user_id)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma pessoa cadastrada para este usuário (relação 1:1)."
        )
        
    if pessoas_repository.get_pessoa_by_cpf(clean_cpf):
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
        criado = pessoas_repository.create_pessoa(data)
        return PessoaResponse(**criado)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar pessoa: {str(err)}"
        )

def listar_todas_pessoas() -> list[PessoaResponse]:
    return [PessoaResponse(**p) for p in pessoas_repository.list_pessoas()]

def buscar_pessoa_por_user(user_id: str) -> PessoaResponse:
    pessoa = pessoas_repository.get_pessoa_by_user_id(user_id)
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada para o user_id informado."
        )
    return PessoaResponse(**pessoa)