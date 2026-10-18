import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

_DIRETORIO_BASE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "rf-001-gestao-identidade",
        "backend",
    )
)
if _DIRETORIO_BASE not in sys.path:
    sys.path.append(_DIRETORIO_BASE)

from database import get_supabase_client

# Fallback em memória para contingência caso a migração DDL ainda não tenha sido aplicada no Supabase remoto
_CONTATOS_CACHE_CONTINGENCIA: Dict[str, Dict[str, Any]] = {}


def buscar_orcamento_por_id(orcamento_id: str) -> Optional[Dict[str, Any]]:
    with get_supabase_client() as cliente:
        resposta = cliente.get(
            f"/rest/v1/orcamentos?id=eq.{orcamento_id}&select=*"
        )
        if resposta.status_code == 200 and resposta.json():
            return resposta.json()[0]
    return None


def obter_contatos_registrados() -> Dict[str, Dict[str, Any]]:
    contatos_map: Dict[str, Dict[str, Any]] = {}
    with get_supabase_client() as cliente:
        resposta = cliente.get(
            "/rest/v1/orcamentos_contatos?select=orcamento_id,vendedor_id,contatado,data_contato"
        )
        if resposta.status_code == 200:
            for item in resposta.json():
                orc_id = str(item.get("orcamento_id"))
                contatos_map[orc_id] = item
        else:
            # Em caso de 404 (tabela não criada ainda no Supabase), usa cache local de contingência
            contatos_map.update(_CONTATOS_CACHE_CONTINGENCIA)
    return contatos_map


def listar_orcamentos_pendentes_contato() -> List[Dict[str, Any]]:
    with get_supabase_client() as cliente:
        resposta = cliente.get(
            "/rest/v1/orcamentos?status=eq.PENDENTE&order=created_at.desc"
        )
        if resposta.status_code != 200:
            return []

        todos_pendentes = resposta.json()
        contatos_map = obter_contatos_registrados()

        resultado: List[Dict[str, Any]] = []
        for orc in todos_pendentes:
            orc_id = str(orc.get("id"))
            registro_contato = contatos_map.get(orc_id)

            ja_contatado = bool(
                registro_contato.get("contatado", False)
            ) if registro_contato else False

            # Retorna apenas os que ainda NÃO foram contatados
            if not ja_contatado:
                orc_copia = dict(orc)
                orc_copia["contatado"] = False
                resultado.append(orc_copia)

        return resultado


def salvar_registro_contato(
    orcamento_id: str,
    vendedor_id: str
) -> Dict[str, Any]:
    agora = datetime.utcnow().isoformat()
    dados_contato = {
        "orcamento_id": orcamento_id,
        "vendedor_id": vendedor_id,
        "contatado": True,
        "data_contato": agora,
    }

    # Salva no cache de contingência
    _CONTATOS_CACHE_CONTINGENCIA[orcamento_id] = dados_contato

    cabecalhos = {
        "Prefer": "resolution=merge-duplicates,return=representation"
    }

    with get_supabase_client() as cliente:
        resposta = cliente.post(
            "/rest/v1/orcamentos_contatos",
            json=dados_contato,
            headers=cabecalhos
        )
        if resposta.status_code in (200, 201) and resposta.json():
            return resposta.json()[0]

    # Retorna o registro consolidado
    return dados_contato
