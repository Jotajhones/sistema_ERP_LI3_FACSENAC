import re
import bcrypt

from fastapi import HTTPException, status

from repositories.usuarios_repository import criar_usuario_funcionario
from repositories import pessoas_repository

from schemas.usuarios_schemas import UsuarioCreate
from repositories.auth_repository import obter_usuario_por_id


ROLES_VALIDAS = {
    "ADMIN",
    "GESTOR",
    "VENDEDOR"
}

SENHA_PADRAO = "senha123"


def normalizar_role(role: str) -> str:
    role_normalizada = role.strip().upper()

    if role_normalizada not in ROLES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Perfil inválido. Use ADMIN, GESTOR ou VENDEDOR."
        )

    return role_normalizada


def criar_usuario(
    payload: UsuarioCreate,
    usuario_logado_id: str
):

    usuario_logado = obter_usuario_por_id(usuario_logado_id)

    if not usuario_logado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário autenticado não encontrado."
        )

    if not usuario_logado.get("ativo", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo."
        )

    role_logado = str(
        usuario_logado.get("user_role", "")
    ).upper()

    if role_logado not in {"ADMIN", "GESTOR"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas ADMIN ou GESTOR podem criar usuários."
        )

    role_nova = normalizar_role(payload.role)

    if role_logado == "GESTOR" and role_nova == "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="GESTOR não pode criar usuário ADMIN."
        )

    nome = payload.nome.strip()
    email = payload.email.strip().lower()

    cpf = None

    if payload.cpf:
        cpf = re.sub(r"\D", "", payload.cpf)

        if len(cpf) != 11:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="CPF inválido. Deve conter 11 dígitos."
            )

    senha_hash = bcrypt.hashpw(
        SENHA_PADRAO.encode("utf-8"),
        bcrypt.gensalt(12)
    ).decode("utf-8")

    usuario_criado = criar_usuario_funcionario(
        nome=nome,
        email=email,
        cpf=cpf,
        role=role_nova,
        password_hash=senha_hash
    )

    return usuario_criado


def listar_pessoas(
    usuario_logado_id: str,
    ativo: bool | None = None
):

    usuario = obter_usuario_por_id(usuario_logado_id)

    if not usuario or not usuario.get("ativo", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo."
        )

    role = str(
        usuario.get("user_role", "")
    ).upper()

    if role not in {"ADMIN", "GESTOR", "VENDEDOR"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado."
        )

    vendedor = role == "VENDEDOR"

    return pessoas_repository.listar_pessoas(
        ativo=ativo,
        somente_clientes=vendedor
    )