import { erpFetch } from "../../../scripts/authInterceptor.js";
import { aplicarControleDeAcesso, validarAcessibilidadeRota } from "../../../scripts/rbac.js";

let filtroAtual = 'ativos';

export function initProdutosList() {
    if (!validarAcessibilidadeRota()) return;

    const tbody = document.getElementById('tabelaProdutosBody');
    const searchInput = document.getElementById('searchInput');
    const btnAtivos = document.getElementById('btnFiltroAtivos');
    const btnTodos = document.getElementById('btnFiltroTodos');
    const btnEstoqueBaixo = document.getElementById('btnFiltroEstoqueBaixo');
    
    const formEditar = document.getElementById('formEditarProduto');
    const btnCancelarEdicao = document.getElementById('btnCancelarEdicao');
    const modalEditar = document.getElementById('modalEditarProduto');

    if (!tbody) return;

    btnAtivos.addEventListener('click', () => alterarFiltro('ativos', [btnAtivos, btnTodos, btnEstoqueBaixo]));
    btnTodos.addEventListener('click', () => alterarFiltro('todos', [btnAtivos, btnTodos, btnEstoqueBaixo]));
    btnEstoqueBaixo.addEventListener('click', () => alterarFiltro('estoque_baixo', [btnAtivos, btnTodos, btnEstoqueBaixo]));

    tbody.addEventListener('click', async (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;

        const id = btn.dataset.id;
        const action = btn.dataset.action;

        if (action === 'inativar') {
            await inativarProduto(id);
        } else if (action === 'editar') {
            await abrirModalEdicao(id);
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

    if (btnCancelarEdicao) {
        btnCancelarEdicao.addEventListener('click', () => {
            modalEditar.style.display = 'none';
        });
    }

    if (formEditar) {
        formEditar.addEventListener('submit', salvarEdicaoProduto);
    }

    carregarProdutos();
}

function alterarFiltro(novoFiltro, botoes) {
    filtroAtual = novoFiltro;
    
    botoes.forEach(btn => {
        if (btn.id === 'btnFiltroEstoqueBaixo') {
            btn.className = 'btn-filter warning';
        } else {
            btn.className = 'btn-filter';
        }
    });

    const btnAtivo = botoes.find(b => b.id === (
        novoFiltro === 'ativos' ? 'btnFiltroAtivos' :
        novoFiltro === 'todos' ? 'btnFiltroTodos' : 'btnFiltroEstoqueBaixo'
    ));
    
    if (novoFiltro === 'estoque_baixo') {
        btnAtivo.className = 'btn-filter warning active';
    } else {
        btnAtivo.className = 'btn-filter active';
    }

    carregarProdutos();
}

export async function carregarProdutos() {
    const tbody = document.getElementById('tabelaProdutosBody');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="padding: 2rem; color: var(--color-text-muted);">Carregando produtos...</td></tr>';

    try {
        let endpoint = '/produtos';
        if (filtroAtual === 'todos' || filtroAtual === 'estoque_baixo') {
            endpoint = '/produtos?ativo_only=false';
        }

        const response = await erpFetch(endpoint);
        if (!response.ok) throw new Error('Falha ao buscar produtos');

        let produtos = await response.json();

        if (filtroAtual === 'estoque_baixo') {
            produtos = produtos.filter(p => p.quantidade_estoque <= 5);
        }

        tbody.innerHTML = '';

        if (produtos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="padding: 2rem; color: var(--color-text-muted);">Nenhum produto encontrado para este filtro.</td></tr>';
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
            
            const estoqueStyle = produto.quantidade_estoque <= 5 ? "color: var(--color-error); font-weight: bold;" : "";

            const acoesHtml = isAdministrativo ? `
                <button class="btn-icon" data-action="editar" data-id="${produto.id}" title="Editar">✏️</button>
                <button class="btn-icon" data-action="inativar" data-id="${produto.id}" title="${produto.ativo ? 'Inativar' : 'Ativar'}">🗑️</button>
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
    const confirmar = confirm("Deseja alterar o status deste produto?");
    if (!confirmar) return;

    try {
        const response = await erpFetch(`/produtos/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            carregarProdutos(); 
        } else if (response.status === 403) {
            alert("Acesso negado: você não tem permissão para esta ação.");
        } else {
            const err = await response.json();
            alert(`Erro ao alterar status: ${err.detail || "Falha na requisição"}`);
        }
    } catch (error) {
        alert("Erro de comunicação com o servidor.");
    }
}

async function abrirModalEdicao(id) {
    try {
        const response = await erpFetch(`/produtos/${id}`);
        if (!response.ok) throw new Error('Falha ao buscar dados do produto');
        
        const produto = await response.json();
        
        document.getElementById('edit_id').value = produto.id;
        document.getElementById('edit_nome').value = produto.nome;
        document.getElementById('edit_sku').value = produto.sku;
        document.getElementById('edit_unidade_medida').value = produto.unidade_medida;
        document.getElementById('edit_valor_venda').value = produto.valor_venda;
        document.getElementById('edit_quantidade_estoque').value = produto.quantidade_estoque || 0;
        document.getElementById('edit_descricao').value = produto.descricao || '';
        document.getElementById('edit_ativo').checked = produto.ativo;

        document.getElementById('modalEditarProduto').style.display = 'flex';
    } catch (error) {
        alert("Não foi possível carregar os dados do produto para edição.");
    }
}

async function salvarEdicaoProduto(e) {
    e.preventDefault();

    const id = document.getElementById('edit_id').value;
    const btnSalvar = document.getElementById('btnSalvarEdicao');
    
    const payload = {
        nome: document.getElementById('edit_nome').value.trim(),
        sku: document.getElementById('edit_sku').value.trim(),
        unidade_medida: document.getElementById('edit_unidade_medida').value,
        valor_venda: parseFloat(document.getElementById('edit_valor_venda').value),
        quantidade_estoque: parseInt(document.getElementById('edit_quantidade_estoque').value) || 0,
        descricao: document.getElementById('edit_descricao').value.trim() || null,
        ativo: document.getElementById('edit_ativo').checked
    };

    btnSalvar.disabled = true;
    btnSalvar.textContent = "Salvando...";

    try {
        const response = await erpFetch(`/produtos/${id}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            document.getElementById('modalEditarProduto').style.display = 'none';
            carregarProdutos();
        } else {
            const err = await response.json();
            alert(`Erro ao atualizar: ${err.detail || "Verifique os dados."}`);
        }
    } catch (error) {
        alert("Erro de comunicação com o servidor.");
    } finally {
        btnSalvar.disabled = false;
        btnSalvar.textContent = "Salvar Alterações";
    }
}