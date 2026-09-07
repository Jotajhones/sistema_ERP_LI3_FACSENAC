from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do produto")
    descricao: Optional[str] = Field(None, description="Descrição detalhada do produto")
    preco: float = Field(..., gt=0, description="Preço unitário do produto")
    unidade_medida: Optional[str] = Field(
        None, max_length=20, description="Ex.: 'un', 'kg', 'm', 'm2', 'm3', 'saco'"
    )
    quantidade_estoque: int = Field(0, ge=0, description="Quantidade disponível em estoque")
    categoria: Optional[str] = Field(None, max_length=100, description="Categoria do produto")


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = None
    preco: Optional[float] = Field(None, gt=0)
    unidade_medida: Optional[str] = Field(None, max_length=20)
    quantidade_estoque: Optional[int] = Field(None, ge=0)
    categoria: Optional[str] = Field(None, max_length=100)


class ProdutoResponse(ProdutoBase):
    id: UUID
    ativo: bool
    criado_por: Optional[UUID] = None
    atualizado_por: Optional[UUID] = None
    deletado_por: Optional[UUID] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    deletado_em: Optional[datetime] = None

    class Config:
        from_attributes = True