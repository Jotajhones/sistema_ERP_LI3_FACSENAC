from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ItemOrcamento(BaseModel):
    produto_id: UUID
    nome: str
    quantidade: float = Field(..., gt=0, description="Quantidade do produto")
    preco_unitario: float = Field(..., ge=0, description="Preço unitário no momento da venda")

class OrcamentoCreate(BaseModel):
    nome_cliente: Optional[str] = Field("Cliente Balcão", description="Nome na nota")
    cpf_cliente: Optional[str] = Field(None, max_length=14, description="CPF opcional")
    itens: List[ItemOrcamento] = Field(..., min_length=1, description="Lista de produtos")
    cliente_id: Optional[UUID] = None

class OrcamentoResponse(BaseModel):
    id: UUID
    cliente_id: Optional[UUID] = None
    nome_cliente: Optional[str]
    cpf_cliente: Optional[str]
    itens: List[dict]
    valor_total: float
    status: str = "PENDENTE"
    vendedor_id: UUID
    created_at: datetime