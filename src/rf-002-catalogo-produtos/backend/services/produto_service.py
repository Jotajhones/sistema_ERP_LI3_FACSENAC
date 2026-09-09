from uuid import UUID
from typing import List
from fastapi import HTTPException, status
from repositories import produto_repository
from schemas.produto_schema import ProdutoCreate, ProdutoUpdate

def listar_produtos_ativos() -> List[dict]:
    return produto_repository.get_produtos_ativos()

def buscar_produto_ativo_por_id(produto_id: UUID) -> dict:
    produto = produto_repository.get_produto_por_id(produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Produto não encontrado ou inativo."
        )
    return produto

def criar_produto(produto: ProdutoCreate, usuario_id: str) -> dict:
    payload = produto.model_dump()
    payload["ativo"] = True
    payload["criado_por"] = usuario_id

    resultado = produto_repository.create_produto(payload)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao cadastrar produto. Verifique se o SKU já está em uso."
        )
    return resultado

def atualizar_produto(produto_id: UUID, produto: ProdutoUpdate, usuario_id: str) -> dict:
    campos_alterados = produto.model_dump(exclude_unset=True)
    if not campos_alterados:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Nenhum campo fornecido para atualização."
        )

    campos_alterados["atualizado_por"] = usuario_id

    resultado = produto_repository.update_produto(produto_id, campos_alterados)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Produto não encontrado para atualização."
        )
    return resultado

def deletar_produto_logicamente(produto_id: UUID, usuario_id: str) -> dict:
    payload = {
        "ativo": False,
        "deletado_por": usuario_id
    }

    resultado = produto_repository.update_produto(produto_id, payload)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Produto não encontrado ou já inativado."
        )
    return resultado