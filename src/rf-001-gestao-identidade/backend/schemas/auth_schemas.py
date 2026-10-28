from pydantic import BaseModel, ConfigDict, EmailStr, Field

class AuthRequest(BaseModel):
    email: EmailStr
    senha: str

class AuthResponse(BaseModel):
    role: str
    token: str
    usuario_id: str
    email: EmailStr

class AlterarSenhaRequest(BaseModel):
    # Anti-IDOR: o alvo vem só do token; qualquer campo extra (ex.: user_id) gera 422
    model_config = ConfigDict(extra="forbid")

    senha_atual: str = Field(..., min_length=1, description="Senha atual do usuário autenticado")
    nova_senha: str = Field(..., min_length=6, max_length=100, description="Nova senha de acesso")

class MensagemResposta(BaseModel):
    mensagem: str
