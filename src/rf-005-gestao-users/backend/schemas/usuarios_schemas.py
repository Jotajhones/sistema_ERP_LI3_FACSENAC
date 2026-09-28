from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    cpf: Optional[str] = Field(None, max_length=14)
    role: str = Field(..., description="ADMIN, GESTOR ou VENDEDOR")


class UsuarioResponse(BaseModel):
    id: str
    pessoa_id: str
    nome: str
    email: EmailStr
    role: str
    ativo: bool