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