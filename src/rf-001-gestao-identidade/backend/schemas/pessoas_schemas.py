from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

class EnderecoBase(BaseModel):
    cep: Optional[str] = Field(None, max_length=9)
    logradouro: Optional[str] = Field(None, max_length=255)
    numero: Optional[str] = Field(None, max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)

class EnderecoCreate(EnderecoBase):
    pass

class EnderecoUpdate(BaseModel):
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None

class EnderecoResponse(EnderecoBase):
    id: UUID
    pessoa_id: UUID

    class Config:
        from_attributes = True
        
class PessoaCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=150, description="Nome do cliente")
    cpf: Optional[str] = Field(None, max_length=14, description="CPF opcional para orçamentos")
    user_id: Optional[str] = None  
    endereco: Optional[EnderecoCreate] = None
    
class PessoaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=150)
    telefone: Optional[str] = Field(None, description="Novo celular/WhatsApp")
    endereco: Optional[EnderecoUpdate] = None

class PessoaResponse(BaseModel):
    id: UUID
    nome: str
    cpf: Optional[str]
    user_id: Optional[UUID]
    ativo: bool

    class Config:
        from_attributes = True        