import os
import sys
from typing import Any, Dict, List
from fastapi import HTTPException, status

_DIRETORIO_MODULO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
if _DIRETORIO_MODULO not in sys.path:
    sys.path.insert(0, _DIRETORIO_MODULO)

from repositories.contatos_repository import (
    buscar_orcamento_por_id,
    listar_orcamentos_pendentes_contato,
    salvar_registro_contato,
)


def obter_pendentes_de_contato() -> List[Dict[str, Any]]:
    return listar_orcamentos_pendentes_contato()


def registrar_contato(orcamento_id: str, vendedor_id: str) -> Dict[str, Any]:
    orcamento = buscar_orcamento_por_id(orcamento_id)

    if not orcamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado."
        )

    status_orcamento = str(orcamento.get("status", "")).strip().upper()

    # Regra RN-01 e OWASP A01:2021 - Bloqueio de contato em orçamentos não pendentes
    if status_orcamento != "PENDENTE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Operação inválida: orçamento já convertido em venda"
        )

    registro = salvar_registro_contato(
        orcamento_id=orcamento_id,
        vendedor_id=vendedor_id
    )

    return {
        "mensagem": "Contato registrado com sucesso via WhatsApp",
        "orcamento_id": registro.get("orcamento_id"),
        "contatado": True,
        "vendedor_id": registro.get("vendedor_id"),
        "data_contato": registro.get("data_contato"),
    }
