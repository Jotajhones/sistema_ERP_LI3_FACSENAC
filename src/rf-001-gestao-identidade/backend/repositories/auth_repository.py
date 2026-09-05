from typing import Optional, Dict, Any
from database import get_supabase_client

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Busca um usuário no banco pelo e-mail."""

    url = f"/rest/v1/users?email=eq.{email}&select=id,email,password_hash,user_role"
    
    with get_supabase_client() as client:
        response = client.get(url)
        
        if response.status_code == 200:
            data = response.json()

            return data[0] if data else None
            
    return None

_LOCAL_SESSIONS: Dict[str, Dict[str, Any]] = {}

def create_session(user_id: str, token_uuid: str) -> Optional[Dict[str, Any]]:
    session_data = {"user_id": user_id, "token_uuid": token_uuid}
    _LOCAL_SESSIONS[token_uuid] = session_data

    try:
        url = "/rest/v1/sessoes"
        with get_supabase_client() as client:
            response = client.post(url, json=session_data)
            if response.status_code in (200, 201) and response.json():
                data = response.json()
                return data[0] if isinstance(data, list) and data else data
    except Exception:
        pass

    return session_data

def get_session_by_token(token_uuid: str) -> Optional[Dict[str, Any]]:
    try:
        url = f"/rest/v1/sessoes?token_uuid=eq.{token_uuid}&select=id,user_id,token_uuid,criado_em"
        with get_supabase_client() as client:
            response = client.get(url)
            if response.status_code == 200 and response.json():
                return response.json()[0]
    except Exception:
        pass

    return _LOCAL_SESSIONS.get(token_uuid)