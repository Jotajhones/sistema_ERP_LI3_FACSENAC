from datetime import datetime, timezone
from typing import List
from uuid import UUID

import httpx
from fastapi import HTTPException

from database import get_supabase_client
from schemas.produto_schema import ProdutoCreate, ProdutoUpdate

TABELA = "produtos"


def _timestamp_atual() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tratar_erro_supabase(resp: httpx.Response, contexto: str) -> None:
    """Converte uma resposta de erro do Supabase em HTTPException apropriada."""
    if resp.status_code >= 500:
        raise HTTPException(status_code=502, detail=f"Erro no Supabase ao {contexto}.")
    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=f"Erro ao {contexto}: {resp.text}")


def listar_produtos_ativos() -> List[dict]:
    """GET: retorna somente produtos com ativo == true (deleção lógica)."""
    with get_supabase_client() as client:
        resp = client.get(f"/{TABELA}", params={"ativo": "eq.true", "order": "criado_em.desc"})
    _tratar_erro_supabase(resp, "listar produtos")
    return resp.json()


def buscar_produto_ativo_por_id(produto_id: UUID) -> dict:
    """GET por id: 404 se o produto não existir ou já estiver inativo."""
    with get_supabase_client() as client:
        resp = client.get(f"/{TABELA}", params={"id": f"eq.{produto_id}", "ativo": "eq.true"})
    _tratar_erro_supabase(resp, "buscar produto")

    dados = resp.json()
    if not dados:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return dados[0]


def criar_produto(produto: ProdutoCreate, usuario_id: UUID) -> dict:
    """POST: insere o produto e grava o usuário autenticado em criado_por."""
    payload = produto.model_dump()
    payload["ativo"] = True
    payload["criado_por"] = str(usuario_id)
    payload["criado_em"] = _timestamp_atual()

    with get_supabase_client() as client:
        resp = client.post(f"/{TABELA}", json=payload)
    _tratar_erro_supabase(resp, "criar produto")

    criados = resp.json()
    if not criados:
        raise HTTPException(status_code=502, detail="Supabase não retornou o produto criado.")
    return criados[0]


def atualizar_produto(produto_id: UUID, produto: ProdutoUpdate, usuario_id: UUID) -> dict:
    campos_alterados = produto.model_dump(exclude_unset=True)
    if not campos_alterados:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar foi enviado.")

    campos_alterados["atualizado_por"] = str(usuario_id)
    campos_alterados["atualizado_em"] = _timestamp_atual()

    with get_supabase_client() as client:
        resp = client.patch(
            f"/{TABELA}",
            params={"id": f"eq.{produto_id}", "ativo": "eq.true"},
            json=campos_alterados,
        )
    _tratar_erro_supabase(resp, "atualizar produto")

    atualizados = resp.json()
    if not atualizados:
        raise HTTPException(status_code=404, detail="Produto não encontrado ou já está inativo.")
    return atualizados[0]


def deletar_produto_logicamente(produto_id: UUID, usuario_id: UUID) -> dict:
    """
    DELETE lógico: NUNCA executa DELETE no banco.

    Faz um UPDATE (PATCH no Supabase) setando ativo = false e gravando
    quem disparou a ação em deletado_por.
    """
    payload = {
        "ativo": False,
        "deletado_por": str(usuario_id),
        "deletado_em": _timestamp_atual(),
    }

    with get_supabase_client() as client:
        resp = client.patch(
            f"/{TABELA}",
            params={"id": f"eq.{produto_id}", "ativo": "eq.true"},
            json=payload,
        )
    _tratar_erro_supabase(resp, "remover produto")

    removidos = resp.json()
    if not removidos:
        raise HTTPException(status_code=404, detail="Produto não encontrado ou já estava inativo.")
    return removidos[0]