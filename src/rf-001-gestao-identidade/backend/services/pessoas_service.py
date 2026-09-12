import re
from fastapi import HTTPException, status
from schemas.pessoas_schemas import PessoaCreate, PessoaResponse
from repositories import pessoas_repository

def cadastrar_pessoa(payload: PessoaCreate) -> PessoaResponse:
    clean_cpf = re.sub(r"\D", "", payload.cpf) if payload.cpf else None
    
    if clean_cpf and len(clean_cpf) != 11:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CPF inválido. Deve conter 11 dígitos numéricos."
        )

    if clean_cpf and pessoas_repository.get_pessoa_by_cpf(clean_cpf):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este CPF já está cadastrado no sistema."
        )

    data = {
        "nome": payload.nome.strip(),
    }
    
    if clean_cpf:
        data["cpf"] = clean_cpf
        
    if payload.user_id:

        user = pessoas_repository.get_user_by_id(str(payload.user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário vinculado com ID {payload.user_id} não encontrado."
            )
        if pessoas_repository.get_pessoa_by_user_id(str(payload.user_id)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma pessoa vinculada a este usuário."
            )
        data["user_id"] = str(payload.user_id)

    try:
        criado = pessoas_repository.create_pessoa(data)
        return PessoaResponse(**criado)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar cliente/pessoa."
        )

def listar_todas_pessoas() -> list[PessoaResponse]:
    return [PessoaResponse(**p) for p in pessoas_repository.list_pessoas()]

def buscar_pessoa_por_user(user_id: str) -> PessoaResponse:
    pessoa = pessoas_repository.get_pessoa_by_user_id(user_id)
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada."
        )
    return PessoaResponse(**pessoa)

def buscar_pessoa_por_cpf_service(cpf: str) -> PessoaResponse:
    clean_cpf = re.sub(r"\D", "", cpf)
    if len(clean_cpf) != 11:
         raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CPF inválido."
        )
         
    pessoa = pessoas_repository.get_pessoa_by_cpf(clean_cpf)
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    return PessoaResponse(**pessoa)