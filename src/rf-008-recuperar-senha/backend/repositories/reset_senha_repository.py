from fastapi import HTTPException, status
from database import get_supabase_client


def resetar_senha_usuario(user_id: str, hash_padrao: str) -> bool:
    """
    Reescreve o password_hash do usuário e revoga todas as suas sessões ativas.
    Retorna False se o usuário não existir.
    """
    with get_supabase_client() as client:
        resposta_update = client.patch(
            "/rest/v1/users",
            params={"id": f"eq.{user_id}"},
            json={"password_hash": hash_padrao},
            headers={"Prefer": "return=representation"}
        )

        if resposta_update.status_code not in (200, 204):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Não foi possível atualizar a senha no banco de dados."
            )

        if not resposta_update.json():
            return False

        # DELETE FROM sessoes WHERE user_id = {id} (OWASP A07 - sessões zumbis)
        resposta_delete = client.delete(
            "/rest/v1/sessoes",
            params={"user_id": f"eq.{user_id}"}
        )

        if resposta_delete.status_code not in (200, 204):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Senha resetada, mas não foi possível revogar as sessões ativas."
            )

    return True
