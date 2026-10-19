import os
import sys
from fastapi import APIRouter, Depends, Query, status

_DIRETORIO_MODULO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
if _DIRETORIO_MODULO not in sys.path:
    sys.path.insert(0, _DIRETORIO_MODULO)

from schemas.recuperacao_schemas import (
    EsqueciSenhaRequisicao,
    EsqueciSenhaResposta,
    ValidarTokenRequisicao,
    ValidarTokenResposta,
    RedefinirSenhaRequisicao,
    RedefinirSenhaResposta,
)
from services.recuperacao_service import (
    solicitar_recuperacao,
    validar_token,
    redefinir_senha,
)
from services.rate_limiter import criar_dependencia_rate_limit

router = APIRouter(
    tags=["Sprint 7 - Recuperação de Acesso e Senha"]
)

# 1. SOLICITAÇÃO DE RECUPERAÇÃO DE SENHA (Limite OWASP A07: 3 requisições por minuto por IP)
@router.post(
    "/recuperar-senha/solicitar",
    response_model=EsqueciSenhaResposta,
    status_code=status.HTTP_200_OK,
    summary="Solicitar link/token de recuperação de senha",
    dependencies=[Depends(criar_dependencia_rate_limit("recuperacao_solicitar", limite=3, janela_segundos=60))]
)
def solicitar_link_recuperacao(dados: EsqueciSenhaRequisicao):
    return solicitar_recuperacao(dados)


@router.post(
    "/auth/esqueci-senha",
    response_model=EsqueciSenhaResposta,
    status_code=status.HTTP_200_OK,
    summary="Alias de compatibilidade sob /auth para esqueci minha senha",
    dependencies=[Depends(criar_dependencia_rate_limit("recuperacao_solicitar", limite=3, janela_segundos=60))]
)
def alias_esqueci_senha(dados: EsqueciSenhaRequisicao):
    return solicitar_recuperacao(dados)


# 2. VALIDAÇÃO DE TOKEN DE RECUPERAÇÃO
@router.get(
    "/recuperar-senha/validar",
    response_model=ValidarTokenResposta,
    status_code=status.HTTP_200_OK,
    summary="Validar token JWT de recuperação via Query Parameter (para telas web)"
)
def validar_token_via_query(token: str = Query(..., min_length=10, description="Token JWT de recuperação")):
    return validar_token(token)


@router.post(
    "/recuperar-senha/validar",
    response_model=ValidarTokenResposta,
    status_code=status.HTTP_200_OK,
    summary="Validar token JWT de recuperação via Payload JSON"
)
def validar_token_via_body(dados: ValidarTokenRequisicao):
    return validar_token(dados.token)


# 3. CONFIRMAÇÃO DA REDEFINIÇÃO DE SENHA (Limite OWASP A07: 5 requisições por minuto por IP)
@router.post(
    "/recuperar-senha/confirmar",
    response_model=RedefinirSenhaResposta,
    status_code=status.HTTP_200_OK,
    summary="Redefinir senha de acesso utilizando token de uso único",
    dependencies=[Depends(criar_dependencia_rate_limit("recuperacao_confirmar", limite=5, janela_segundos=60))]
)
def confirmar_redefinicao_senha(dados: RedefinirSenhaRequisicao):
    return redefinir_senha(dados)


@router.post(
    "/auth/redefinir-senha",
    response_model=RedefinirSenhaResposta,
    status_code=status.HTTP_200_OK,
    summary="Alias de compatibilidade sob /auth para redefinição de senha",
    dependencies=[Depends(criar_dependencia_rate_limit("recuperacao_confirmar", limite=5, janela_segundos=60))]
)
def alias_redefinir_senha(dados: RedefinirSenhaRequisicao):
    return redefinir_senha(dados)
