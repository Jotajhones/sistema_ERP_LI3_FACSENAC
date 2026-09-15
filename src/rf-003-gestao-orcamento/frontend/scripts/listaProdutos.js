// src/features/produtos/listaProdutos.js
import { erpFetch } from "../../../rf-002-catalogo-produtos/frontend/scripts/authInterceptor.js";
import { aplicarControleDeAcesso, validarAcessibilidadeRota } from "./rbac.js";

export function initProdutosList() {
    if (!validarAcessibilidadeRota()) return;

    const tbody = document.getElementById('tabelaProdutosBody');
    const searchInput = document.getElementById('searchInput');

    if (!tbody) return;

    tbody.addEventListener('click', async (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;

        const id = btn.dataset.id;
        const action = btn.dataset.action;

        if (action === 'inativar') {
            await inativarProduto(id);
        } else if (action === 'editar') {
            console.log("Editar produto:", id);
        }
    });

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {

            const termo = e.target.value.toLowerCase();
            const linhas = tbody.querySelectorAll('tr[data-produto-row]');
            
            linhas.forEach(linha => {
                const textoLinha = linha.textContent.toLowerCase();
                linha.style.display = textoLinha.includes(termo) ? '' : 'none';
            });
        });
    }

    carregarProdutos();
}

export async function carregarProdutos() {
    const tbody = document.getElementById('tabelaProdutosBody');
    if (!tbody) return;

    try {
        const response = await erpFetch('/produtos');
        if (!response.ok) throw new Error('Falha ao buscar produtos');

        const produtos = await response.json();
        tbody.innerHTML = '';

        if (produtos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="padding: 2rem; color: var(--color-text-muted);">Nenhum produto cadastrado.</td></tr>';
            return;
        }

        const userRole = localStorage.getItem('userRole');
        const roleNormalizada = userRole ? userRole.toUpperCase().trim() : '';
        const isAdministrativo = roleNormalizada === 'ADMIN' || roleNormalizada === 'GESTOR';

        produtos.forEach(produto => {
            const row = document.createElement('tr');
            row.setAttribute('data-produto-row', 'true');
            row.dataset.id = produto.id;

            const badgeStatus = produto.ativo
                ? '<span class="badge ativo">Ativo</span>'
                : '<span class="badge inativo">Inativo</span>';

            const valorFormatado = new Intl.NumberFormat('pt-BR', { 
                style: 'currency', 
                currency: 'BRL' 
            }).format(produto.valor_venda);
            
            const estoqueStyle = produto.quantidade_estoque <= 0 ? "color: var(--color-error); font-weight: bold;" : "";

            const acoesHtml = isAdministrativo ? `
                <button class="btn-icon" data-action="editar" data-id="${produto.id}" title="Editar">✏️</button>
                <button class="btn-icon" data-action="inativar" data-id="${produto.id}" title="Inativar">🗑️</button>
            ` : `<span style="color: var(--color-text-muted); font-size: 0.85rem;">-</span>`;

            row.innerHTML = `
                <td><strong>${produto.sku}</strong></td>
                <td>
                    <div style="font-weight: 500; color: var(--color-primary-dark);">${produto.nome}</div>
                    <div style="font-size: 0.8rem; color: var(--color-text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 250px;">
                        ${produto.descricao || 'Sem descrição'}
                    </div>
                </td>
                <td class="text-center" style="font-weight: 500;">${produto.unidade_medida || 'UN'}</td>
                <td class="text-right" style="${estoqueStyle}">${produto.quantidade_estoque || 0}</td>
                <td class="text-right" style="font-weight: 500;">${valorFormatado}</td>
                <td class="text-center">${badgeStatus}</td>
                <td class="text-center">${acoesHtml}</td>
            `;
            tbody.appendChild(row);
        });

        aplicarControleDeAcesso();

    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="color: var(--color-error); padding: 2rem;">Erro ao carregar os dados do servidor.</td></tr>';
    }
}

async function inativarProduto(id) {
    const confirmar = confirm("Deseja realmente inativar este produto?");
    if (!confirmar) return;

    try {
        const response = await erpFetch(`/produtos/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert("Produto inativado com sucesso!");
            carregarProdutos(); 
        } else if (response.status === 403) {
            alert("Acesso negado: você não tem permissão para esta ação.");
        } else {
            const err = await response.json();
            alert(`Erro ao inativar: ${err.detail || "Falha na requisição"}`);
        }
    } catch (error) {
        alert("Erro de comunicação com o servidor.");
    }
}