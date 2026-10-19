from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class EsqueciSenhaRequisicao(BaseModel):
    """Payload para solicitação de link/token de recuperação de senha."""
    email: EmailStr = Field(
        ...,
        description="E-mail cadastrado do usuário para recuperação de acesso",
        examples=["vendedor@empresa.com"]
    )


class EsqueciSenhaResposta(BaseModel):
    """Resposta padronizada para solicitação de recuperação de senha (Anti-Enumeração OWASP A07)."""
    mensagem: str = Field(
        ...,
        description="Mensagem informativa neutra contra enumeração de contas"
    )
    expira_em_minutos: int = Field(
        15,
        description="Tempo de validade do token gerado em minutos"
    )
    debug_token: Optional[str] = Field(
        None,
        description="Token JWT exposto apenas em ambiente de desenvolvimento/teste para facilitar a homologação"
    )


class ValidarTokenRequisicao(BaseModel):
    """Payload para validação de integridade e validade do token de recuperação."""
    token: str = Field(
        ...,
        min_length=10,
        description="Token JWT temporário recebido pelo usuário"
    )


class ValidarTokenResposta(BaseModel):
    """Resposta indicando se o token está apto para redefinição."""
    valido: bool = Field(..., description="Indica se o token é válido e pode ser utilizado")
    mensagem: str = Field(..., description="Detalhes sobre a validade do token")
    email_mascarado: Optional[str] = Field(
        None,
        description="E-mail mascarado para conferência visual segura do usuário"
    )


class RedefinirSenhaRequisicao(BaseModel):
    """Payload para confirmação da redefinição de senha com o token de uso único."""
    token: str = Field(
        ...,
        min_length=10,
        description="Token JWT de uso único gerado na solicitação"
    )
    nova_senha: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Nova senha de acesso desejada pelo usuário"
    )
    confirmacao_senha: Optional[str] = Field(
        None,
        min_length=6,
        max_length=100,
        description="Confirmação da nova senha para prevenir erros de digitação"
    )


class RedefinirSenhaResposta(BaseModel):
    """Resposta de sucesso da redefinição de senha."""
    sucesso: bool = Field(True, description="Indica se a senha foi alterada com sucesso")
    mensagem: str = Field(..., description="Mensagem de sucesso para o usuário")
