from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from schemas.produto_schema import ProdutoCreate, ProdutoResponse, ProdutoUpdate
from services import produto_service
from routers.auth_router import get_usuario_atual

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def _extrair_usuario_id(usuario) -> UUID:
    if hasattr(usuario, "id"):
        return usuario.id
    return usuario["id"]


@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(produto: ProdutoCreate, usuario=Depends(get_usuario_atual)):
    """Cria um novo produto e grava o usuário autenticado em criado_por."""
    usuario_id = _extrair_usuario_id(usuario)
    return produto_service.criar_produto(produto, usuario_id)


@router.get("", response_model=List[ProdutoResponse])
def listar_produtos():
    """Lista os produtos ativos (ativo == true) — produtos deletados logicamente não aparecem."""
    return produto_service.listar_produtos_ativos()


@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(produto_id: UUID):
    """Busca um produto ativo específico pelo id. 404 se não existir ou estiver inativo."""
    return produto_service.buscar_produto_ativo_por_id(produto_id)


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(produto_id: UUID, produto: ProdutoUpdate, usuario=Depends(get_usuario_atual)):
    """Atualiza um produto ativo e grava o usuário autenticado em atualizado_por."""
    usuario_id = _extrair_usuario_id(usuario)
    return produto_service.atualizar_produto(produto_id, produto, usuario_id)


@router.delete("/{produto_id}", response_model=ProdutoResponse)
def deletar_produto(produto_id: UUID, usuario=Depends(get_usuario_atual)):
    """
    Deleção lógica: NÃO remove a linha do banco (sem DROP/DELETE).

    Apenas seta ativo = false e grava o usuário autenticado em deletado_por.
    """
    usuario_id = _extrair_usuario_id(usuario)
    return produto_service.deletar_produto_logicamente(produto_id, usuario_id)