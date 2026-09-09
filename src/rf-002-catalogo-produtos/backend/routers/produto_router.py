from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from schemas.produto_schema import ProdutoCreate, ProdutoResponse, ProdutoUpdate
from services import produto_service
from dependencies import get_current_user

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(produto: ProdutoCreate, usuario_id: str = Depends(get_current_user)):
    """Cria um produto registrando o ID do usuário em criado_por."""
    return produto_service.criar_produto(produto, usuario_id)

@router.get("", response_model=List[ProdutoResponse])
def listar_produtos():
    """Lista produtos ativos (ativo == true)."""
    return produto_service.listar_produtos_ativos()

@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(produto_id: UUID):
    """Busca produto por ID."""
    return produto_service.buscar_produto_ativo_por_id(produto_id)

@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: UUID, 
    produto: ProdutoUpdate, 
    usuario_id: str = Depends(get_current_user)
):
    """Atualiza produto registrando o ID do usuário em atualizado_por."""
    return produto_service.atualizar_produto(produto_id, produto, usuario_id)

@router.delete("/{produto_id}", response_model=ProdutoResponse)
def deletar_produto(
    produto_id: UUID, 
    usuario_id: str = Depends(get_current_user)
):
    """Deleção lógica: seta ativo = false e grava deletado_por."""
    return produto_service.deletar_produto_logicamente(produto_id, usuario_id)