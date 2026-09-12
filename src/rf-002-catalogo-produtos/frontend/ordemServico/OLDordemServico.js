import { erpFetch } from "../scripts/authInterceptor.js";

export function initDashboard() {
  const tbody = document.getElementById('tabelaProdutosBody');
  if (!tbody) return;

  tbody.addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;

    const id = btn.dataset.id;
    const action = btn.dataset.action;

    if (action === 'editar') {
      editarProduto(id);
    } else if (action === 'inativar') {
      inativarProduto(id);
    }
  });

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
      tbody.innerHTML = '<tr><td colspan="6" class="text-center">Nenhum produto cadastrado.</td></tr>';
      return;
    }

    produtos.forEach(produto => {
      const row = document.createElement('tr');
      row.dataset.id = produto.id;

      const badgeStatus = produto.ativo
        ? '<span class="badge ativo">Ativo</span>'
        : '<span class="badge inativo">Inativo</span>';

      const dataFormatada = new Date(produto.created_at).toLocaleDateString('pt-BR');
      const valorFormatado = new Intl.NumberFormat('pt-BR', { 
        style: 'currency', 
        currency: 'BRL' 
      }).format(produto.valor_venda);

      row.innerHTML = `
        <td>
            <strong>${produto.sku}</strong>
        </td>
        <td>
            <div style="font-weight: 500; color: var(--color-primary-dark);">${produto.nome}</div>
            <div style="font-size: 0.8rem; color: var(--color-text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px;">
                ${produto.descricao || 'Sem descrição'}
            </div>
        </td>
        <td class="text-right" style="font-weight: 500;">${valorFormatado}</td>
        <td class="text-center">${badgeStatus}</td>
        <td class="text-center">${dataFormatada}</td>
        <td class="text-center">
            <button class="btn-icon" data-action="editar" data-id="${produto.id}" title="Editar">✏️</button>
            <button class="btn-icon" data-action="inativar" data-id="${produto.id}" title="Inativar">🗑️</button>
        </td>
      `;
      tbody.appendChild(row);
    });

  } catch (error) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="color: var(--color-error);">Erro ao carregar os dados. O servidor pode estar indisponível.</td></tr>';
  }
}

function editarProduto(id) {
  console.log("Abrir modal de edição para o UUID:", id);
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
    } else {
      const err = await response.json();
      alert(`Erro ao inativar: ${err.detail || "Falha na requisição"}`);
    }
  } catch (error) {
    alert("Erro de comunicação ao inativar o produto.");
  }
}