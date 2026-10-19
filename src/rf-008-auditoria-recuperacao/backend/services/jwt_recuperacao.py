import os
import time
import json
import uuid
import hmac
import hashlib
import base64
from typing import Tuple, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status

_JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("SUPABASE_KEY") or "senac-erp-secret-key-recuperacao-acesso-2026"

def _b64url_encode(data: bytes) -> str:
    """Codifica bytes em Base64 URL-Safe sem padding '='."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64url_decode(segmento: str) -> bytes:
    """Decodifica string Base64 URL-Safe adicionando o padding necessário."""
    resto = len(segmento) % 4
    if resto:
        segmento += "=" * (4 - resto)
    return base64.urlsafe_b64decode(segmento.encode("utf-8"))

def gerar_token_recuperacao(
    user_id: str,
    email: str,
    validade_minutos: int = 15
) -> Tuple[str, str, datetime]:
    """
    Gera um token JWT assinado padrão RFC 7519 (HS256) temporário e de uso único.
    Retorna (token_jwt, token_jti, data_expiracao).
    """
    agora_epoch = int(time.time())
    expira_epoch = agora_epoch + (validade_minutos * 60)
    data_expiracao = datetime.now(timezone.utc) + timedelta(minutes=validade_minutos)
    
    jti = str(uuid.uuid4())
    
    cabecalho = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    payload = {
        "sub": str(user_id),
        "email": str(email).lower().strip(),
        "purpose": "recuperacao_senha",
        "jti": jti,
        "iat": agora_epoch,
        "exp": expira_epoch
    }
    
    cabecalho_b64 = _b64url_encode(json.dumps(cabecalho, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    
    conteudo_assinatura = f"{cabecalho_b64}.{payload_b64}".encode("utf-8")
    assinatura = hmac.new(
        _JWT_SECRET.encode("utf-8"),
        conteudo_assinatura,
        hashlib.sha256
    ).digest()
    assinatura_b64 = _b64url_encode(assinatura)
    
    token_jwt = f"{cabecalho_b64}.{payload_b64}.{assinatura_b64}"
    return token_jwt, jti, data_expiracao

def decodificar_e_validar_jwt(token: str) -> Dict[str, Any]:
    """
    Valida a assinatura, formato e expiração de um token JWT de recuperação.
    Lança HTTPException em caso de irregularidade.
    """
    partes = token.strip().split(".")
    if len(partes) != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de token de recuperação inválido"
        )
    
    cabecalho_b64, payload_b64, assinatura_b64 = partes
    conteudo_assinatura = f"{cabecalho_b64}.{payload_b64}".encode("utf-8")
    
    assinatura_esperada = hmac.new(
        _JWT_SECRET.encode("utf-8"),
        conteudo_assinatura,
        hashlib.sha256
    ).digest()
    
    try:
        assinatura_recebida = _b64url_decode(assinatura_b64)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assinatura do token de recuperação inválida"
        )
    
    if not hmac.compare_digest(assinatura_esperada, assinatura_recebida):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assinatura do token de recuperação inválida ou adulterada"
        )
    
    try:
        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conteúdo do token de recuperação ilegível"
        )
    
    # Validação do propósito
    if payload.get("purpose") != "recuperacao_senha":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Finalidade do token incompatível com recuperação de senha"
        )
    
    # Validação de expiração
    agora_epoch = int(time.time())
    exp_epoch = payload.get("exp", 0)
    if agora_epoch > exp_epoch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O token de recuperação de senha expirou. Solicite um novo link."
        )
    
    if not payload.get("sub") or not payload.get("jti"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token incompleto ou sem identificadores de controle"
        )
    
    return payload
