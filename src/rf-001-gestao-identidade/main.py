import bcrypt

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import text

from database import engine
from schemas import AuthRequest, AuthResponse

app = FastAPI(
    title="RF-001 Gestão de Identidade",
    description="API de autenticação e gestão de identidade",
    version="1.0.0"
)

_DUMMY_HASH = bcrypt.hashpw(
    b"dummy-password",
    bcrypt.gensalt()
)


@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "RF-001 Gestão de Identidade"
    }


@app.post(
    "/auth",
    response_model=AuthResponse,
    tags=["Autenticação"]
)
def autenticar(payload: AuthRequest):

    with engine.connect() as conn:

        resultado = conn.execute(
            text(
                """
                SELECT
                    id,
                    email,
                    password_hash,
                    user_role
                FROM users
                WHERE email = :email
                """
            ),
            {"email": payload.email}
        )

        usuario = resultado.mappings().first()

    if not usuario:

        bcrypt.checkpw(
            payload.senha.encode("utf-8"),
            _DUMMY_HASH
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos"
        )

    senha_valida = bcrypt.checkpw(
        payload.senha.encode("utf-8"),
        usuario["password_hash"].encode("utf-8")
    )

    if not senha_valida:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos"
        )

    return AuthResponse(
        role=usuario["user_role"]
    )


@app.get(
    "/usuarios/{email}",
    tags=["Usuários"]
)
def obter_usuario(email: str):

    with engine.connect() as conn:

        resultado = conn.execute(
            text(
                """
                SELECT
                    u.id,
                    u.email,
                    u.user_role,
                    u.created_at,
                    p.nome,
                    p.cpf
                FROM users u
                LEFT JOIN pessoas p
                    ON p.user_id = u.id
                WHERE u.email = :email
                """
            ),
            {"email": email}
        )

        usuario = resultado.mappings().first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return dict(usuario)