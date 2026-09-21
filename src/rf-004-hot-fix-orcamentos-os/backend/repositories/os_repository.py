import sys
import os
from typing import Dict, Any, List

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "rf-001-gestao-identidade", "backend"))
if _BASE_DIR not in sys.path:
    sys.path.append(_BASE_DIR)

from database import get_supabase_client

def get_orcamento(orcamento_id: str) -> Dict:
    with get_supabase_client() as client:
        resp = client.get(f"/rest/v1/orcamentos?id=eq.{orcamento_id}&select=*")
        if resp.status_code == 200 and len(resp.json()) > 0:
            return resp.json()[0]
        return None

def buscar_ou_criar_pessoa_por_cpf(nome: str, cpf: str) -> str:
    """Busca pessoa pelo CPF. Se não achar, cria silenciosamente e retorna o ID."""
    with get_supabase_client() as client:
        resp_busca = client.get(f"/rest/v1/pessoas?cpf=eq.{cpf}&select=id")
        if resp_busca.status_code == 200 and len(resp_busca.json()) > 0:
            return resp_busca.json()[0]["id"]
        
        
        nova_pessoa = {"nome": nome, "cpf": cpf}
        resp_cria = client.post("/rest/v1/pessoas", json=nova_pessoa, headers={"Prefer": "return=representation"})
        if resp_cria.status_code in (200, 201):
            return resp_cria.json()[0]["id"]
    return None

def get_produto_estoque(produto_id: str) -> Dict:
    with get_supabase_client() as client:
        resp = client.get(f"/rest/v1/produtos?id=eq.{produto_id}&select=id,nome,quantidade_estoque")
        return resp.json()[0] if (resp.status_code == 200 and len(resp.json()) > 0) else None

def atualizar_estoque_produto(produto_id: str, nova_quantidade: float):
    with get_supabase_client() as client:
        client.patch(f"/rest/v1/produtos?id=eq.{produto_id}", json={"quantidade_estoque": nova_quantidade})

def create_os_e_itens(os_data: Dict, itens_data: List[Dict]) -> Dict:
    headers = {"Prefer": "return=representation"}
    with get_supabase_client() as client:
        # 1. Salva a OS
        resp_os = client.post("/rest/v1/ordens_servico", json=os_data, headers=headers)
        if resp_os.status_code not in (200, 201):
            raise Exception("Erro ao criar OS")
        
        os_criada = resp_os.json()[0]
        
        # 2. Injeta o ID da OS nos itens e faz o Bulk Insert
        for item in itens_data:
            item["os_id"] = os_criada["id"]
            
        resp_itens = client.post("/rest/v1/ordens_servico_itens", json=itens_data)
        if resp_itens.status_code not in (200, 201):
            # Se falhar aqui, o ideal seria um rollback (via RPC), mas via REST lançamos exceção
            raise Exception("Erro ao salvar itens da OS")
            
        return os_criada