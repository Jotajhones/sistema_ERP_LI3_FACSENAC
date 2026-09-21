import os
import sys

_BACKEND_RF002 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_RF001 = os.path.abspath(
    os.path.join(_BACKEND_RF002, "..", "..", "rf-001-gestao-identidade", "backend")
)
if _BACKEND_RF001 not in sys.path:
    sys.path.append(_BACKEND_RF001)

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from schemas.produto_schema import (
    ProdutoCreate,
    ProdutoResponse,
    ProdutoUpdate,
    EstoqueRecebimento,
    RecebimentoResposta
)
from services import produto_service
from dependencies import get_current_user, require_role 

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
async def criar_produto(
    produto: ProdutoCreate,
    usuario_id: str = Depends(require_role(["ADMIN", "GESTOR"]))
):
    return await produto_service.criar_produto(produto, usuario_id)

@router.get("/", response_model=List[ProdutoResponse])
async def listar_produtos(
    termo: Optional[str] = None, 
    ativo_only: bool = True,
    usuario_id: str = Depends(get_current_user) # Qualquer logado pode ver
):
    """
    Lista produtos. No frontend, passe ?ativo_only=false para ver o catálogo completo, 
    incluindo itens inativos/zerados para orçamentos sob encomenda.
    """
    return await produto_service.buscar_produtos(termo, ativo_only)

@router.get("/busca", response_model=List[ProdutoResponse])
async def buscar_produtos_autocomplete(
    termo: Optional[str] = None,
    ativo_only: bool = True,
    usuario_id: str = Depends(get_current_user)
):
    """Rota usada pelo autocomplete no balcão de orçamentos."""
    return await produto_service.buscar_produtos(termo, ativo_only)

@router.get("/{produto_id}", response_model=ProdutoResponse)
async def buscar_produto(
    produto_id: UUID, 
    usuario_id: str = Depends(get_current_user)
):
    produto = await produto_service.obter_produto_por_id(str(produto_id))
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@router.put("/{produto_id}", response_model=ProdutoResponse)
async def atualizar_produto(
    produto_id: UUID,
    produto: ProdutoUpdate,
    usuario_id: str = Depends(require_role(["ADMIN", "GESTOR"]))
):
    produto_atualizado = await produto_service.atualizar_produto(str(produto_id), produto, usuario_id)
    if not produto_atualizado:
        raise HTTPException(status_code=404, detail="Produto não encontrado ou erro ao atualizar")
    return produto_atualizado

@router.delete("/{produto_id}", response_model=ProdutoResponse)
async def deletar_produto(
    produto_id: UUID,
    usuario_id: str = Depends(require_role(["ADMIN", "GESTOR"]))
):
    return await produto_service.deletar_produto_logicamente(str(produto_id), usuario_id)

@router.post("/{produto_id}/recebimento", response_model=RecebimentoResposta)
async def registrar_recebimento_estoque(
    produto_id: UUID,
    dados_recebimento: EstoqueRecebimento,
    usuario_id: str = Depends(require_role(["ADMIN", "GESTOR"]))
):
    return await produto_service.dar_entrada_estoque(str(produto_id), dados_recebimento, usuario_id)
