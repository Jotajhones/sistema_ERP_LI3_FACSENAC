from typing import List, Optional, Dict, Any
from uuid import UUID
from database import get_supabase_client

TABELA = "produtos"

def get_produtos_ativos() -> List[Dict[str, Any]]:
    with get_supabase_client() as client:
        resp = client.get(f"/rest/v1/{TABELA}", params={"ativo": "eq.true", "order": "created_at.desc"})
        if resp.status_code == 200:
            return resp.json()
        return []

def get_produto_por_id(produto_id: UUID) -> Optional[Dict[str, Any]]:
    with get_supabase_client() as client:
        resp = client.get(f"/rest/v1/{TABELA}", params={"id": f"eq.{produto_id}", "ativo": "eq.true"})
        if resp.status_code == 200:
            dados = resp.json()
            return dados[0] if dados else None
        return None

def create_produto(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    headers = {"Prefer": "return=representation"}
    with get_supabase_client() as client:
        resp = client.post(f"/rest/v1/{TABELA}", json=payload, headers=headers)
        if resp.status_code in (200, 201):
            dados = resp.json()
            return dados[0] if isinstance(dados, list) and dados else dados
        return None

def update_produto(produto_id: UUID, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    headers = {"Prefer": "return=representation"}
    with get_supabase_client() as client:
        resp = client.patch(
            f"/rest/v1/{TABELA}",
            params={"id": f"eq.{produto_id}", "ativo": "eq.true"},
            json=payload,
            headers=headers
        )
        if resp.status_code == 200:
            dados = resp.json()
            return dados[0] if isinstance(dados, list) and dados else dados
        return None