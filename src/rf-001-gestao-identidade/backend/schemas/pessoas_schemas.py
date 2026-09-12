from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

class PessoaCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=150, description="Nome do cliente")
    cpf: Optional[str] = Field(None, max_length=14, description="CPF opcional para orçamentos")
    user_id: Optional[UUID] = Field(None, description="ID do usuário (nulo para clientes de balcão)")

class PessoaResponse(BaseModel):
    id: UUID
    nome: str
    cpf: Optional[str]
    user_id: Optional[UUID]
    ativo: bool

    class Config:
        from_attributes = True