import httpx
from config import SUPABASE_URL, SUPABASE_KEY

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def get_supabase_client() -> httpx.Client:
    """
    Retorna um client HTTP configurado para o Supabase.
    Deve ser usado preferencialmente com 'with' (Context Manager) para fechar a conexão.
    """
    return httpx.Client(
        base_url=SUPABASE_URL,
        headers=SUPABASE_HEADERS,
        timeout=10.0
    )