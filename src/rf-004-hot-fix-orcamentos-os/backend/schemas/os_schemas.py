from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class OSConvertPayload(BaseModel):
    tipo_pagamento: str = Field(..., description="PIX, DINHEIRO, CARTAO_CREDITO, CARTAO_DEBITO")
    desconto: float = Field(0.0, ge=0.0, description="Valor do desconto aplicado na conversão")

class OSResponse(BaseModel):
    id: UUID
    cliente_id: Optional[UUID]
    vendedor_id: UUID
    orcamento_id: Optional[UUID]
    status: str
    tipo_pagamento: str
    valor_total: float
    desconto: float
    created_at: datetime