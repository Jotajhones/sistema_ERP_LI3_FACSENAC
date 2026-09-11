import os
import sys
_BACKEND_RF002 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_RF001 = os.path.abspath(
    os.path.join(_BACKEND_RF002, "..", "..", "rf-001-gestao-identidade", "backend")
)

if _BACKEND_RF001 not in sys.path:
    sys.path.append(_BACKEND_RF001)

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from schemas.produto_schema import ProdutoCreate, ProdutoResponse, ProdutoUpdate
from services import produto_service
from dependencies import get_current_user, require_role

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(
    produto: ProdutoCreate,
    usuario_id: str = Depends(require_role(["ADMIN", "GESTOR"]))
):
    """Cria um produto registrando o ID do usuário em criado_por. Restrito a ADMIN/GESTOR."""
    return produto_service.criar_produto(produto, usuario_id)

@router.get("", response_model=List[ProdutoResponse])
def listar_produtos(usuario_id: str = Depends(get_current_user)):
    """Lista produtos ativos (ativo == true). Requer login, qualquer role."""
    return produto_service.listar_produtos_ativos()

@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(produto_id: UUID, usuario_id: str = Depends(get_current_user)):
    """Busca produto por ID. Requer login, qualquer role."""
    return produto_service.buscar_produto_ativo_por_id(produto_id)

@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: UUID,
    produto: ProdutoUpdate,
    usuario_id: str = Depends(require_role(["ADMIN", "GESTOR"]))
):
    """Atualiza produto registrando o ID do usuário em atualizado_por. Restrito a ADMIN/GESTOR."""
    return produto_service.atualizar_produto(produto_id, produto, usuario_id)

@router.delete("/{produto_id}", response_model=ProdutoResponse)
def deletar_produto(
    produto_id: UUID,
    usuario_id: str = Depends(require_role(["ADMIN", "GESTOR"]))
):
    """Deleção lógica: seta ativo = false e grava deletado_por. Restrito a ADMIN/GESTOR."""
    return produto_service.deletar_produto_logicamente(produto_id, usuario_id)