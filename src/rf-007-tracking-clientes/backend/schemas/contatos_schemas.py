from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class OrcamentoContatoRegistro(BaseModel):
    orcamento_id: UUID = Field(
        ...,
        description="Identificador único do orçamento contatado"
    )
    vendedor_id: UUID = Field(
        ...,
        description="Identificador único do vendedor que realizou o contato"
    )
    contatado: bool = Field(
        default=True,
        description="Indicador booleano de confirmação de contato"
    )
    data_contato: datetime = Field(
        default_factory=datetime.utcnow,
        description="Data e hora em que a ação de contato foi realizada"
    )


class OrcamentoPendenteContatoResposta(BaseModel):
    id: UUID = Field(..., description="ID do orçamento")
    cliente_id: Optional[UUID] = Field(None, description="ID do cliente vinculado")
    nome_cliente: Optional[str] = Field("Cliente Balcão", description="Nome do cliente")
    cpf_cliente: Optional[str] = Field(None, description="CPF do cliente")
    telefone_cliente: Optional[str] = Field(None, description="Telefone de contato do cliente")
    valor_total: float = Field(..., description="Valor total do orçamento")
    status: str = Field(..., description="Status atual do orçamento (ex: PENDENTE)")
    contatado: bool = Field(default=False, description="Flag indicando se já foi contatado via WhatsApp")
    created_at: datetime = Field(..., description="Data de emissão do orçamento")


class ContatoConfirmacaoResposta(BaseModel):
    mensagem: str = Field(..., description="Mensagem de confirmação da operação")
    orcamento_id: UUID = Field(..., description="ID do orçamento marcado")
    contatado: bool = Field(..., description="Status de contato atualizado")
    vendedor_id: UUID = Field(..., description="ID do vendedor responsável pelo registro")
    data_contato: datetime = Field(..., description="Timestamp do registro")
