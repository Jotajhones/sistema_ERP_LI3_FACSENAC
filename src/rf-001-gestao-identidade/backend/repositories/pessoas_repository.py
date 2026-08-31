from typing import Optional, List, Dict, Any
from database import get_supabase_client

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    url = f"/rest/v1/users?id=eq.{user_id}&select=*"
    with get_supabase_client() as client:
        resp = client.get(url)
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]
    return None

def get_pessoa_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    url = f"/rest/v1/pessoas?user_id=eq.{user_id}&select=*"
    with get_supabase_client() as client:
        resp = client.get(url)
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]
    return None

def get_pessoa_by_cpf(cpf: str) -> Optional[Dict[str, Any]]:
    url = f"/rest/v1/pessoas?cpf=eq.{cpf}&select=*"
    with get_supabase_client() as client:
        resp = client.get(url)
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]
    return None

def create_pessoa(pessoa_data: Dict[str, Any]) -> Dict[str, Any]:
    url = "/rest/v1/pessoas"
    with get_supabase_client() as client:
        resp = client.post(url, json=pessoa_data)
        if resp.status_code in (200, 201):
            data = resp.json()
            return data[0] if isinstance(data, list) else data
        raise Exception(f"Erro no banco: {resp.text}")

def list_pessoas() -> List[Dict[str, Any]]:
    url = "/rest/v1/pessoas?select=*"
    with get_supabase_client() as client:
        resp = client.get(url)
        if resp.status_code == 200:
            return resp.json()
    return []