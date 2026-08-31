from pydantic import BaseModel, Field
from uuid import UUID

class PessoaCreate(BaseModel):
    user_id: UUID
    nome: str = Field(..., min_length=3, max_length=150)
    cpf: str = Field(..., min_length=11, max_length=14)

class PessoaResponse(BaseModel):
    id: UUID
    user_id: UUID
    nome: str
    cpf: str