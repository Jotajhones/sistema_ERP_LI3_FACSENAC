from pydantic import BaseModel, EmailStr, Field

class AuthRequest(BaseModel):
    email: EmailStr
    senha: str

class AuthResponse(BaseModel):
    role: str
    token: str

class AlterarSenhaRequest(BaseModel):
    senha_atual: str = Field(..., min_length=1, description="Senha atual do usuário autenticado")
    nova_senha: str = Field(..., min_length=6, max_length=100, description="Nova senha de acesso")

class MensagemResposta(BaseModel):
    mensagem: str