import uuid
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from database import get_supabase_client

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Busca um usuário no banco pelo e-mail."""
    url = f"/rest/v1/users?email=eq.{email}&select=id,email,password_hash,user_role,ativo"
    
    with get_supabase_client() as client:
        response = client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erro ao consultar serviço de dados."
        )

def create_session(user_id: str, token_uuid: str) -> Dict[str, Any]:
    """Persiste a sessão no banco com o token UUID."""
    session_payload = {
        "user_id": user_id, 
        "token_uuid": token_uuid
    }
    
    headers = {"Prefer": "return=representation"}
    url = "/rest/v1/sessoes"
    
    with get_supabase_client() as client:
        response = client.post(url, json=session_payload, headers=headers)
        
        if response.status_code in (200, 201):
            data = response.json()
            return data[0] if isinstance(data, list) and data else data
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível criar a sessão no banco de dados."
        )

def get_session_by_token(token_str: str) -> Optional[Dict[str, Any]]:
    """Busca a sessão ativa a partir do token UUID."""
    try:
        
        token_uuid = str(uuid.UUID(token_str))
    except ValueError:
        return None

    url = f"/rest/v1/sessoes?token_uuid=eq.{token_uuid}&select=id,user_id,token_uuid,criado_em"
    
    with get_supabase_client() as client:
        response = client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
            
    return None