from datetime import date

from pydantic import BaseModel, Field


class PeriodoResponse(BaseModel):
    data_inicio: date = Field(..., description="Início do período (inclusivo).")
    data_fim: date = Field(..., description="Fim do período (inclusivo), como enviado pelo cliente.")


class ConversaoOrcamentosResponse(BaseModel):
    periodo: PeriodoResponse
    total_orcamentos: int = Field(..., ge=0)
    orcamentos_convertidos: int = Field(..., ge=0)
    orcamentos_pendentes: int = Field(..., ge=0)
    taxa_conversao: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentual de orçamentos convertidos em OS (0 a 100, 2 casas). 0 quando não há orçamentos."
    )
    valor_total_orcado: float = Field(..., ge=0)
    valor_total_convertido: float = Field(..., ge=0)
