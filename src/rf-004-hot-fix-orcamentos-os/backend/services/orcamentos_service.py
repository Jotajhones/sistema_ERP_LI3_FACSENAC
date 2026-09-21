import re
from fastapi import HTTPException
from schemas.orcamentos_schema import OrcamentoCreate
from repositories import orcamentos_repository

async def criar_orcamento(payload: OrcamentoCreate, vendedor_id: str):
    clean_cpf = re.sub(r"\D", "", payload.cpf_cliente) if payload.cpf_cliente else None
    
    if clean_cpf and len(clean_cpf) != 11:
        raise HTTPException(status_code=422, detail="CPF inválido.")

    valor_total_calculado = sum(item.quantidade * item.preco_unitario for item in payload.itens)
    itens_dict = [item.model_dump(mode="json") for item in payload.itens]

    orcamento_data = {
        "nome_cliente": payload.nome_cliente,
        "cpf_cliente": clean_cpf,
        "itens": itens_dict,
        "valor_total": valor_total_calculado,
        "vendedor_id": vendedor_id
    }

    try:
        return orcamentos_repository.create_orcamento(orcamento_data)
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))

async def listar_orcamentos():
    return orcamentos_repository.list_orcamentos()

async def obter_orcamento(orcamento_id: str):
    return orcamentos_repository.get_orcamento_by_id(orcamento_id)