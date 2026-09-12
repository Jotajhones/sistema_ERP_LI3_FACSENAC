from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=150, description="Nome do produto")
    descricao: Optional[str] = Field(None, description="Descrição detalhada")
    valor_venda: float = Field(..., ge=0, description="Preço de venda (maior ou igual a 0)")
    sku: str = Field(..., min_length=1, max_length=100, description="Código SKU único")
    quantidade_estoque: float = Field(0.0, ge=0, description="Quantidade física no estoque")
    unidade_medida: str = Field(..., max_length=20, description="Unidade de medida (ex: UN, M3, PALETE)")

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=150)
    descricao: Optional[str] = None
    valor_venda: Optional[float] = Field(None, ge=0)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    quantidade_estoque: Optional[float] = Field(None, ge=0)
    unidade_medida: Optional[str] = Field(None, max_length=20)

class ProdutoResponse(ProdutoBase):
    id: UUID
    ativo: bool
    criado_por: Optional[UUID] = None
    atualizado_por: Optional[UUID] = None
    deletado_por: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True