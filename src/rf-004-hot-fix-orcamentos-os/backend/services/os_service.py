from fastapi import HTTPException
from schemas.os_schemas import OSConvertPayload
from repositories import os_repository
from repositories import orcamentos_repository

async def converter_orcamento(orcamento_id: str, payload: OSConvertPayload, vendedor_id: str):

    orcamento = os_repository.get_orcamento(orcamento_id)
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado.")
    
    if orcamento.get("status") == "CONVERTIDO":
        raise HTTPException(
            status_code=409, 
            detail="Ação Bloqueada de Segurança: Este orçamento já foi faturado e convertido em uma Ordem de Serviço anteriormente."
        )

    cliente_id = None
    if orcamento.get("cpf_cliente"):
        cliente_id = os_repository.buscar_ou_criar_pessoa_por_cpf(
            nome=orcamento["nome_cliente"], 
            cpf=orcamento["cpf_cliente"]
        )

    itens_orcamento = orcamento.get("itens", [])
    for item in itens_orcamento:
        prod_db = os_repository.get_produto_estoque(item["produto_id"])
        if not prod_db:
            raise HTTPException(status_code=404, detail=f"Produto {item['nome']} não existe mais no catálogo.")
        if prod_db["quantidade_estoque"] < item["quantidade"]:
            raise HTTPException(
                status_code=409, 
                detail=f"Estoque insuficiente para {item['nome']}. Solicitado: {item['quantidade']}, Disponível: {prod_db['quantidade_estoque']}"
            )

    valor_total_os = float(orcamento["valor_total"]) - payload.desconto
    if valor_total_os < 0:
        raise HTTPException(status_code=400, detail="Desconto maior que o valor total.")

    os_data = {
        "orcamento_id": orcamento_id,
        "cliente_id": cliente_id,
        "vendedor_id": vendedor_id,
        "status": "FINALIZADA", 
        "tipo_pagamento": payload.tipo_pagamento,
        "valor_total": valor_total_os,
        "desconto": payload.desconto
    }

    itens_relacionais = []
    for item in itens_orcamento:
        itens_relacionais.append({
            "produto_id": item["produto_id"],
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
            "subtotal": item["quantidade"] * item["preco_unitario"]
        })

    try:
        os_criada = os_repository.create_os_e_itens(os_data, itens_relacionais)
        orcamentos_repository.update_status_orcamento(orcamento_id, "CONVERTIDO")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return os_criada