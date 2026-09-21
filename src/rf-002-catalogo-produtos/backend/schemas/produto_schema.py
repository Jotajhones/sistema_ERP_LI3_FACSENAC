from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class ProdutoBase(BaseModel):
    nome: str = Field(..., max_length=150)
    descricao: Optional[str] = None
    valor_venda: float = Field(..., gt=0)  
    sku: Optional[str] = Field(None, max_length=50) 
    quantidade_estoque: float = Field(default=0.0)
    unidade_medida: str = Field(default="UN", max_length=10)
    ativo: bool = True

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=150)
    descricao: Optional[str] = None
    valor_venda: Optional[float] = Field(None, gt=0)
    sku: Optional[str] = Field(None, max_length=50)
    quantidade_estoque: Optional[float] = None
    unidade_medida: Optional[str] = Field(None, max_length=10)
    ativo: Optional[bool] = None

class ProdutoResponse(ProdutoBase):
    id: UUID
    created_at: Optional[datetime] = None 
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EstoqueRecebimento(BaseModel):
    quantidade_recebida: float = Field(..., gt=0)

class RecebimentoResposta(BaseModel):
    mensagem: str
    produto_id: UUID
    saldo_anterior: float
    quantidade_recebida: float
    novo_saldo: float