from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from database import get_supabase_client


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    with get_supabase_client() as client:
        resp = client.get(f"/rest/v1/users?id=eq.{user_id}&select=id")
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]
    return None


def get_pessoa_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    with get_supabase_client() as client:
        resp = client.get(f"/rest/v1/pessoas?user_id=eq.{user_id}&select=id")
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]
    return None


def get_pessoa_by_cpf(cpf: str) -> Optional[Dict[str, Any]]:
    with get_supabase_client() as client:
        resp = client.get(f"/rest/v1/pessoas?cpf=eq.{cpf}&select=*,enderecos(*)")
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]
    return None


def get_pessoa_by_id(pessoa_id: str) -> Optional[Dict[str, Any]]:
    with get_supabase_client() as client:
        resp = client.get(f"/rest/v1/pessoas?id=eq.{pessoa_id}&select=*,enderecos(*)")
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]
    return None


def listar_pessoas(
    ativo: Optional[bool] = None,
    somente_clientes: bool = False
) -> List[Dict[str, Any]]:
    filtros = []

    if ativo is not None:
        filtros.append(f"ativo=eq.{str(ativo).lower()}")

    if somente_clientes:
        filtros.append("user_id=is.null")

    query = "/rest/v1/pessoas?select=*,enderecos(*)&order=nome.asc"

    if filtros:
        query += "&" + "&".join(filtros)

    with get_supabase_client() as client:
        response = client.get(query)

        if response.status_code == 200:
            return response.json()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erro ao consultar pessoas."
        )


def create_pessoa(pessoa_data: Dict[str, Any]) -> Dict[str, Any]:
    headers = {"Prefer": "return=representation"}
    with get_supabase_client() as client:
        resp = client.post("/rest/v1/pessoas", json=pessoa_data, headers=headers)
        if resp.status_code in (200, 201):
            data = resp.json()
            return data[0] if isinstance(data, list) else data
        raise Exception(f"Erro no banco ao criar pessoa: {resp.text}")


def create_endereco(endereco_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    headers = {"Prefer": "return=representation"}
    with get_supabase_client() as client:
        resp = client.post("/rest/v1/enderecos", json=endereco_data, headers=headers)
        if resp.status_code in (200, 201):
            return resp.json()
        raise Exception(f"Erro no banco ao criar endereço: {resp.text}")


def update_pessoa(pessoa_id: str, pessoa_data: dict):
    with get_supabase_client() as client:
        resp = client.patch(f"/rest/v1/pessoas?id=eq.{pessoa_id}", json=pessoa_data)
        if resp.status_code not in (200, 204):
            raise Exception("Erro ao atualizar dados do cliente.")


def upsert_endereco(pessoa_id: str, endereco_data: dict):
    with get_supabase_client() as client:
        resp_check = client.get(f"/rest/v1/enderecos?pessoa_id=eq.{pessoa_id}")
        
        if resp_check.status_code == 200 and len(resp_check.json()) > 0:
            endereco_id = resp_check.json()[0]["id"]
            resp = client.patch(f"/rest/v1/enderecos?id=eq.{endereco_id}", json=endereco_data)
        else:
            resp = client.post("/rest/v1/enderecos", json=endereco_data)
            
        if resp.status_code not in (200, 201, 204):
            raise Exception("Erro ao atualizar o endereço.")
        
def inativar_pessoa_e_usuario(pessoa_id: str) -> dict:
    with get_supabase_client() as client:
        
        resp_busca = client.get(f"/rest/v1/pessoas?id=eq.{pessoa_id}&select=*")
        if resp_busca.status_code != 200 or not resp_busca.json():
            return None
            
        alvo = resp_busca.json()[0]
        user_id = alvo.get("user_id")
        
        resp_pessoa = client.patch(f"/rest/v1/pessoas?id=eq.{pessoa_id}", json={"ativo": False})
        if resp_pessoa.status_code not in (200, 204):
            raise Exception("Erro ao inativar o cadastro da pessoa.")
        
        if user_id:
            resp_user = client.patch(f"/rest/v1/users?id=eq.{user_id}", json={"ativo": False})
            if resp_user.status_code not in (200, 204):
                raise Exception("Erro ao inativar as credenciais de login do usuário.")
            
        return alvo