from uuid import UUID
from fastapi import HTTPException, status
from urllib.parse import urlencode, quote
from database import get_supabase_client

async def criar_produto(produto_data, usuario_id: str):
    data = produto_data.model_dump()
    data["criado_por"] = usuario_id 
    
    headers = {"Prefer": "return=representation"}
    
    with get_supabase_client() as client:
        resp = client.post("/rest/v1/produtos", json=data, headers=headers)
        if resp.status_code not in (200, 201):
            raise HTTPException(status_code=400, detail=f"Erro no banco: {resp.text}")
        
        dados = resp.json()
        return dados[0] if isinstance(dados, list) and dados else dados

async def buscar_produtos(termo: str = None, ativo_only: bool = True):
    filtros = {"select": "*", "order": "nome.asc"}
    
    if ativo_only:
        filtros["ativo"] = "eq.true"
        
    if termo:
        termo_limpo = termo.strip()
        filtros["or"] = f"(nome.ilike.*{termo_limpo}*,descricao.ilike.*{termo_limpo}*)"
        
    query = urlencode({str(k): str(v) for k, v in filtros.items()}, quote_via=quote, safe=".*()")
    
    with get_supabase_client() as client:
        resp = client.get(f"/rest/v1/produtos?{query}")
        if resp.status_code == 200:
            return resp.json()
        return []

async def obter_produto_por_id(produto_id: str):
    with get_supabase_client() as client:
        resp = client.get("/rest/v1/produtos", params={"id": f"eq.{produto_id}"})
        if resp.status_code == 200:
            dados = resp.json()
            return dados[0] if dados else None
        return None

async def atualizar_produto(produto_id: str, produto_data, usuario_id: str):
    data = produto_data.model_dump(exclude_unset=True) 
    if not data:
        return await obter_produto_por_id(produto_id)
        
    data["atualizado_por"] = usuario_id 
    headers = {"Prefer": "return=representation"}
    
    with get_supabase_client() as client:
        resp = client.patch(
            "/rest/v1/produtos", 
            params={"id": f"eq.{produto_id}"}, 
            json=data, 
            headers=headers
        )
        if resp.status_code in (200, 204):
            dados = resp.json()
            return dados[0] if isinstance(dados, list) and dados else dados
        return None

async def deletar_produto_logicamente(produto_id: str, usuario_id: str):

    headers = {"Prefer": "return=representation"}
    payload = {"ativo": False, "atualizado_por": usuario_id}
    
    with get_supabase_client() as client:
        resp = client.patch("/rest/v1/produtos", params={"id": f"eq.{produto_id}"}, json=payload, headers=headers)
        if resp.status_code in (200, 204):
            dados = resp.json()
            return dados[0] if isinstance(dados, list) and dados else dados
        raise HTTPException(status_code=404, detail="Produto não encontrado")

async def dar_entrada_estoque(produto_id: str, dados_recebimento, usuario_id: str):
    produto = await obter_produto_por_id(produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    saldo_anterior = float(produto.get("quantidade_estoque") or 0.0)
    quantidade_recebida = float(dados_recebimento.quantidade_recebida)
    novo_saldo = round(saldo_anterior + quantidade_recebida, 3)

    headers = {"Prefer": "return=representation"}
    payload = {"quantidade_estoque": novo_saldo, "atualizado_por": usuario_id}
    
    with get_supabase_client() as client:
        client.patch("/rest/v1/produtos", params={"id": f"eq.{produto_id}"}, json=payload, headers=headers)

    return {
        "mensagem": "Recebimento de lote registrado com sucesso",
        "produto_id": produto_id,
        "saldo_anterior": saldo_anterior,
        "quantidade_recebida": quantidade_recebida,
        "novo_saldo": novo_saldo
    }