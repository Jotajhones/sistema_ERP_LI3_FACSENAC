import httpx
from typing import Optional, List, Dict, Any

try:
    from .config import SUPABASE_URL, SUPABASE_KEY
except ImportError:
    from config import SUPABASE_URL, SUPABASE_KEY

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}&select=*"
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            return data[0] if data else None
    return None

def get_pessoa_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    url = f"{SUPABASE_URL}/rest/v1/pessoas?user_id=eq.{user_id}&select=*"
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            return data[0] if data else None
    return None

def get_pessoa_by_cpf(cpf: str) -> Optional[Dict[str, Any]]:
    url = f"{SUPABASE_URL}/rest/v1/pessoas?cpf=eq.{cpf}&select=*"
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            return data[0] if data else None
    return None

def create_pessoa(pessoa_data: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{SUPABASE_URL}/rest/v1/pessoas"
    with httpx.Client(timeout=10.0) as client:
        resp = client.post(url, headers=HEADERS, json=pessoa_data)
        if resp.status_code in (200, 201):
            res_data = resp.json()
            return res_data[0] if isinstance(res_data, list) else res_data
        raise Exception(f"Supabase error ({resp.status_code}): {resp.text}")

def list_pessoas() -> List[Dict[str, Any]]:
    url = f"{SUPABASE_URL}/rest/v1/pessoas?select=*"
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, headers=HEADERS)
        if resp.status_code == 200:
            return resp.json()
    return []
