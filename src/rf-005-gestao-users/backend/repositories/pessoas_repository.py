from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from database import get_supabase_client


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