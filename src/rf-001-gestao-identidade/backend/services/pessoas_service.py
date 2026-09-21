import re
from fastapi import HTTPException, status
from schemas.pessoas_schemas import PessoaCreate, PessoaResponse, PessoaUpdate
from repositories import pessoas_repository

async def cadastrar_pessoa(payload: PessoaCreate):
    clean_cpf = re.sub(r"\D", "", payload.cpf) if payload.cpf else None
    
    if clean_cpf:
        if len(clean_cpf) != 11:
            raise HTTPException(status_code=422, detail="CPF inválido. Deve conter 11 dígitos numéricos.")
        if pessoas_repository.get_pessoa_by_cpf(clean_cpf):
            raise HTTPException(status_code=409, detail="Este CPF já está cadastrado no sistema.")

    if payload.user_id:
        if not pessoas_repository.get_user_by_id(str(payload.user_id)):
            raise HTTPException(status_code=404, detail=f"Usuário {payload.user_id} não encontrado.")
        if pessoas_repository.get_pessoa_by_user_id(str(payload.user_id)):
            raise HTTPException(status_code=409, detail="Já existe uma pessoa vinculada a este usuário.")


    pessoa_data = {"nome": payload.nome.strip()}
    if clean_cpf: pessoa_data["cpf"] = clean_cpf
    if payload.user_id: pessoa_data["user_id"] = str(payload.user_id)

    try:
        pessoa_criada = pessoas_repository.create_pessoa(pessoa_data)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


    if payload.endereco:
        endereco_data = payload.endereco.model_dump(exclude_unset=True)
        endereco_data["pessoa_id"] = pessoa_criada["id"]
        
        try:
            enderecos_criados = pessoas_repository.create_endereco(endereco_data)
            pessoa_criada["enderecos"] = enderecos_criados
        except Exception as err:
            pass 

    return pessoa_criada

async def listar_todas_pessoas():
    return pessoas_repository.list_pessoas()

async def buscar_pessoa_por_id(pessoa_id: str):
    pessoa = pessoas_repository.get_pessoa_by_id(pessoa_id)
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada.")
    return pessoa

async def buscar_pessoa_por_cpf_service(cpf: str):
    clean_cpf = re.sub(r"\D", "", cpf)
    if len(clean_cpf) != 11:
         raise HTTPException(status_code=422, detail="CPF inválido.")
         
    pessoa = pessoas_repository.get_pessoa_by_cpf(clean_cpf)
    if not pessoa:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return pessoa

async def atualizar_pessoa_segura(pessoa_id: str, payload: PessoaUpdate, usuario_logado: dict):

    alvo = pessoas_repository.get_pessoa_by_id(pessoa_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    alvo_user_id = alvo.get("user_id")
    if alvo_user_id:
        is_owner = str(alvo_user_id) == str(usuario_logado["id"])
        is_admin_or_gestor = usuario_logado.get("role") in ["ADMIN", "GESTOR"]
        if not is_owner and not is_admin_or_gestor:
            raise HTTPException(
                status_code=403, 
                detail="Acesso Negado: Vendedores só podem alterar dados de Clientes."
            )

    pessoa_data = {}
    if payload.nome: 
        pessoa_data["nome"] = payload.nome.strip()
    if payload.telefone: 
        pessoa_data["telefone"] = re.sub(r"\D", "", payload.telefone) #

    try:
        
        if pessoa_data:
            pessoas_repository.update_pessoa(pessoa_id, pessoa_data)
        
       
        if payload.endereco:
            endereco_data = payload.endereco.model_dump(exclude_unset=True)
            if endereco_data:
                endereco_data["pessoa_id"] = pessoa_id
                
                pessoas_repository.upsert_endereco(pessoa_id, endereco_data)
                
        return pessoas_repository.get_pessoa_by_id(pessoa_id)
        
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))