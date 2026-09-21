import { erpFetch } from "../../../rf-002-catalogo-produtos/frontend/scripts/authInterceptor.js";

let filtroAtual = 'pendentes';

export function initListaOrcamentos() {
    const btnPendentes = document.getElementById('btnFiltroPendentes');
    const btnTodos = document.getElementById('btnFiltroTodos');

    if (btnPendentes && btnTodos) {
        btnPendentes.addEventListener('click', () => {
            btnPendentes.className = 'btn-filter active';
            btnTodos.className = 'btn-filter';
            filtroAtual = 'pendentes';
            carregarOrcamentos();
        });

        btnTodos.addEventListener('click', () => {
            btnTodos.className = 'btn-filter active';
            btnPendentes.className = 'btn-filter';
            filtroAtual = 'todos';
            carregarOrcamentos();
        });
    }

    carregarOrcamentos();
}

async function carregarOrcamentos() {
    const tbody = document.getElementById('tabelaOrcamentosBody');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="padding: 2rem; color: var(--color-text-muted);">Carregando orçamentos...</td></tr>';

    try {
        const response = await erpFetch('/orcamentos');
        if (!response.ok) throw new Error('Falha ao buscar orçamentos');

        let orcamentos = await response.json();

        // Aplica o filtro local
        if (filtroAtual === 'pendentes') {
            orcamentos = orcamentos.filter(orc => orc.status !== 'CONVERTIDO');
        }

        tbody.innerHTML = '';

        if (orcamentos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="padding: 2rem; color: var(--color-text-muted);">Nenhum orçamento pendente encontrado.</td></tr>';
            return;
        }

        orcamentos.forEach(orc => {
            const row = document.createElement('tr');

            const dataFormatada = new Date(orc.created_at).toLocaleString('pt-BR', {
                day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
            });
            const valorFormatado = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(orc.valor_total);
            const shortId = orc.id.split('-')[0];

            const status = orc.status || 'PENDENTE';
            const badgeClass = status === 'CONVERTIDO' ? 'convertido' : 'pendente';
            const statusTexto = status === 'CONVERTIDO' ? 'OS Gerada' : 'Pendente';

            row.innerHTML = `
                <td>${dataFormatada}</td>
                <td><strong>#${shortId}</strong></td>
                <td>
                    <div style="font-weight: 500; color: var(--color-primary-dark);">${orc.nome_cliente || 'Consumidor Final'}</div>
                    <div style="font-size: 0.8rem; color: var(--color-text-muted);">${orc.cpf_cliente || 'S/ CPF'}</div>
                </td>
                <td class="text-right" style="font-weight: 600;">${valorFormatado}</td>
                <td class="text-center"><span class="badge ${badgeClass}">${statusTexto}</span></td>
                <td class="text-center">
                    <button class="btn-icon" onclick="window.location.href = '../../../rf-002-catalogo-produtos/frontend/ordemServico/ordemServico.html?id=${orc.id}'" title="Visualizar / Retomar">👁️</button>
                </td>
            `;
            tbody.appendChild(row);
        });

    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="color: var(--color-error); padding: 2rem;">Erro ao carregar os orçamentos.</td></tr>';
    }
}