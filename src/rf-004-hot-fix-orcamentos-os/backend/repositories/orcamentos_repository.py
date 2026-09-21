import sys
import os
from typing import Dict, Any, List


_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "rf-001-gestao-identidade", "backend"))
if _BASE_DIR not in sys.path:
    sys.path.append(_BASE_DIR)

from database import get_supabase_client
from urllib.parse import urlencode, quote

def build_safe_query(filters: dict) -> str:
    return urlencode(
        {str(chave): str(valor) for chave, valor in filters.items()},
        quote_via=quote,
        safe="",
    )

def create_orcamento(orcamento_data: Dict[str, Any]) -> Dict[str, Any]:
    headers = {"Prefer": "return=representation"}
    with get_supabase_client() as client:
        resp = client.post("/rest/v1/orcamentos", json=orcamento_data, headers=headers)
        if resp.status_code in (200, 201):
            return resp.json()[0]
        raise Exception(f"Erro no banco ao criar orçamento: {resp.text}")

def list_orcamentos() -> List[Dict[str, Any]]:
    with get_supabase_client() as client:
        resp = client.get("/rest/v1/orcamentos?order=created_at.desc")
        if resp.status_code == 200:
            return resp.json()
    return []

def get_orcamento_by_id(orcamento_id: str) -> dict:
    query = build_safe_query({
        "id": f"eq.{orcamento_id}",
        "select": "*"
    })
    
    with get_supabase_client() as client:
        resp = client.get(f"/rest/v1/orcamentos?{query}")
        
        if resp.status_code == 200 and len(resp.json()) > 0:
            return resp.json()[0]
            
    return None

def update_status_orcamento(orcamento_id: str, novo_status: str):
    headers = {"Prefer": "return=representation"}
    with get_supabase_client() as client:
        resp = client.patch(
            f"/rest/v1/orcamentos?id=eq.{orcamento_id}", 
            json={"status": novo_status},
            headers=headers
        )
        
        if resp.status_code not in (200, 204) or not resp.json():
            raise Exception("Erro ao atualizar o status. Orçamento não encontrado ou bloqueado.")
            
        orcamento_atualizado = resp.json()[0]
        if orcamento_atualizado.get("status") != novo_status:
            raise Exception("O banco ignorou a atualização. Execute 'NOTIFY pgrst, ''reload schema'';' no SQL do Supabase.")
        