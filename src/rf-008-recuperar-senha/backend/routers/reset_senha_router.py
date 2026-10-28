from uuid import UUID
from fastapi import APIRouter, Depends, status

from dependencies import RequireRole, get_current_user
from schemas.auth_schemas import AlterarSenhaRequest, MensagemResposta
from schemas.reset_senha_schemas import ResetSenhaResposta
from services.auth_service import alterar_senha_usuario
from services.reset_senha_service import resetar_senha


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


@router.post(
    "/{user_id}/reset-senha",
    response_model=ResetSenhaResposta,
    status_code=status.HTTP_200_OK,
    summary="Resetar senha de funcionário para o padrão (exclusivo GESTOR/ADMIN)",
    description=(
        "Rota exclusiva para os perfis **GESTOR** e **ADMIN** "
        "(`RequireRole([\"ADMIN\", \"GESTOR\"])`); VENDEDOR recebe 403. "
        "Não recebe body: a senha padrão é definida no backend, criptografada com "
        "bcrypt (12 rounds) e gravada em `users.password_hash`. Em seguida todas as "
        "sessões do usuário alvo são apagadas (`DELETE FROM sessoes WHERE user_id = {id}`). "
        "GESTOR não pode resetar a senha de um ADMIN."
    ),
    responses={
        401: {"description": "Token ausente, inválido ou sessão expirada"},
        403: {"description": "Perfil sem permissão (VENDEDOR, ou GESTOR tentando resetar um ADMIN)"},
        404: {"description": "Usuário não encontrado"},
    }
)
def resetar_senha_usuario(
    user_id: UUID,
    usuario_id: str = Depends(RequireRole(["ADMIN", "GESTOR"]))
):
    return resetar_senha(
        user_id_alvo=str(user_id),
        usuario_logado_id=usuario_id
    )


@router.put(
    "/minha-senha",
    response_model=MensagemResposta,
    status_code=status.HTTP_200_OK,
    summary="Alterar a própria senha (qualquer usuário autenticado)",
    description=(
        "Usado pelo funcionário no Meu Painel após o reset. Altera apenas a senha "
        "do usuário dono do token (RN-03), exigindo a senha atual. "
        "Mesma regra de `PUT/PATCH /auth/senha`."
    ),
    responses={
        400: {"description": "Senha atual incorreta ou nova senha igual à atual"},
        401: {"description": "Token ausente, inválido ou sessão expirada"},
    }
)
def alterar_minha_senha(
    requisicao: AlterarSenhaRequest,
    usuario_id: str = Depends(get_current_user)
):
    return alterar_senha_usuario(usuario_id, requisicao)
