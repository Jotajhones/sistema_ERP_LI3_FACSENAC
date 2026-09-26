from typing import Dict, Any
from fastapi import HTTPException, status
from database import get_supabase_client


def criar_usuario_funcionario(
    nome: str,
    email: str,
    cpf: str | None,
    role: str,
    password_hash: str
) -> Dict[str, Any]:

    payload = {
        "p_nome": nome,
        "p_email": email,
        "p_cpf": cpf,
        "p_user_role": role,
        "p_password_hash": password_hash
    }

    with get_supabase_client() as client:

        response = client.post(
            "/rest/v1/rpc/rf005_criar_usuario_funcionario",
            json=payload
        )

        if response.status_code in (200, 201):
            data = response.json()

            if isinstance(data, list):
                return data[0] if data else {}

            return data

        if response.status_code == 409:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail ou CPF já cadastrado."
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar funcionário: {response.text}"
        )
