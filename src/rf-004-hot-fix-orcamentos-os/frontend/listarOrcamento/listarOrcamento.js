import { erpFetch } from "../../../rf-002-catalogo-produtos/frontend/scripts/authInterceptor.js";

let filtroAtual = 'pendentes';
let aguardandoRetornoWhatsApp = null; // Armazena o ID do orçamento em aberto para disparo posterior

export function initListaOrcamentos() {
    const btnPendentes = document.getElementById('btnFiltroPendentes');
    const btnNaoContatados = document.getElementById('btnFiltroNaoContatados');
    const btnTodos = document.getElementById('btnFiltroTodos');

    if (btnPendentes && btnNaoContatados && btnTodos) {
        btnPendentes.addEventListener('click', () => {
            ativarBotaoFiltro(btnPendentes);
            filtroAtual = 'pendentes';
            carregarOrcamentos();
        });

        btnNaoContatados.addEventListener('click', () => {
            ativarBotaoFiltro(btnNaoContatados);
            filtroAtual = 'nao_contatados';
            carregarOrcamentos();
        });

        btnTodos.addEventListener('click', () => {
            ativarBotaoFiltro(btnTodos);
            filtroAtual = 'todos';
            carregarOrcamentos();
        });
    }

    // Monitora o retorno do foco para a janela do ERP após clique no WhatsApp
    window.addEventListener('focus', () => {
        if (aguardandoRetornoWhatsApp) {
            const orcamentoId = aguardandoRetornoWhatsApp;
            aguardandoRetornoWhatsApp = null;
            marcarComoContatado(orcamentoId);
        }
    });

    carregarOrcamentos();
}

function ativarBotaoFiltro(botaoAtivo) {
    document.querySelectorAll('.btn-filter').forEach(btn => btn.classList.remove('active'));
    botaoAtivo.classList.add('active');
}

async function carregarOrcamentos() {
    const tbody = document.getElementById('tabelaOrcamentosBody');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="padding: 2rem; color: var(--color-text-muted);">Carregando orçamentos...</td></tr>';

    try {
        // CORREÇÃO: Usar a rota específica que cruza os dados com a tabela de contatos!
        let endpoint = '/orcamentos';
        
        if (filtroAtual === 'nao_contatados') {
            endpoint = '/orcamentos/pendentes-contato';
        }

        const response = await erpFetch(endpoint);
        if (!response.ok) throw new Error('Falha ao buscar orçamentos');

        let orcamentos = await response.json();

        // O filtro local do JS agora só se preocupa com a rota geral.
        // Se a rota for "nao_contatados", o backend já devolveu a lista mastigada!
        if (filtroAtual === 'pendentes') {
            orcamentos = orcamentos.filter(orc => orc.status !== 'CONVERTIDO' && orc.status !== 'FINALIZADA' && orc.status !== 'FINALIZADO');
        }

        tbody.innerHTML = '';

        if (orcamentos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="padding: 2rem; color: var(--color-text-muted);">Nenhum orçamento encontrado com este filtro.</td></tr>';
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
            
            // Blindando a cor da badge para aceitar os outros status de OS convertida
            const isConvertido = status === 'CONVERTIDO' || status === 'FINALIZADA' || status === 'FINALIZADO';
            const badgeClass = isConvertido ? 'convertido' : 'pendente';
            const statusTexto = isConvertido ? 'OS Gerada' : 'Pendente';

            row.innerHTML = `
                <td>${dataFormatada}</td>
                <td><strong>#${shortId}</strong></td>
                <td>
                    <div style="font-weight: 500; color: var(--color-primary-dark);">${orc.nome_cliente || 'Consumidor Final'}</div>
                    <div style="font-size: 0.8rem; color: var(--color-text-muted);">${orc.cpf_cliente || 'S/ CPF'}</div>
                </td>
                <td class="text-right" style="font-weight: 600;">${valorFormatado}</td>
                <td class="text-center"><span class="badge ${badgeClass}">${statusTexto}</span></td>
                <td class="text-center" style="display: flex; gap: 4px; justify-content: center; align-items: center;">
                    <button class="btn-icon btn-whatsapp" data-id="${orc.id}" data-telefone="${orc.telefone_cliente || ''}" data-cliente="${orc.nome_cliente || 'Cliente'}" data-valor="${valorFormatado}" title="Contatar via WhatsApp">
                        <img src="https://img.icons8.com/?size=100&id=16733&format=png&color=25D366" alt="WhatsApp" style="width: 20px; height: 20px; display: block;">
                    </button>
                    <button class="btn-icon" onclick="window.location.href = '../../../rf-007-tracking-clientes/frontend/ordemServico/ordemServico.html?id=${orc.id}'" title="Visualizar / Retomar">👁️</button>
                </td>
            `;
            tbody.appendChild(row);
        });

        // Adiciona os eventos de clique aos novos botões de WhatsApp criados
        document.querySelectorAll('.btn-whatsapp').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const dataset = e.currentTarget.dataset;
                abrirWhatsApp(dataset.id, dataset.telefone, dataset.cliente, dataset.valor);
            });
        });

    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="color: var(--color-error); padding: 2rem;">Erro ao carregar os orçamentos.</td></tr>';
    }
}
function abrirWhatsApp(idOrcamento, telefoneBruto, nomeCliente, valorTotal) {
    if (!telefoneBruto) {
        alert('Este cliente não possui um número de telefone cadastrado.');
        return;
    }

    // Remove parênteses, traços, espaços e símbolos do telefone
    const numeroLimpo = telefoneBruto.replace(/\D/g, '');

    // Dados dinâmicos do vendedor/loja (podem vir de localStorage/Sessão do ERP)
    const nomeVendedor = localStorage.getItem('erp_vendedor_nome') || 'atendente';
    const nomeLoja = localStorage.getItem('erp_loja_nome') || 'nossa loja';

    // Monta a string de mensagem solicitada
    const mensagem = `Olá ${nomeCliente}, aqui é o ${nomeVendedor} da ${nomeLoja}. Vi que você tem um orçamento em aberto no valor de R$ ${valorTotal}. Gostaria de saber se deseja prosseguir com a compra ou se tem alguma dúvida que eu possa esclarecer ??`;
    const mensagemCodificada = encodeURIComponent(mensagem);

    // Salva o ID para disparar o POST ao retornar o foco
    aguardandoRetornoWhatsApp = idOrcamento;

    // Abre o link do WhatsApp em nova aba
    const urlWhatsApp = `https://wa.me/${numeroLimpo}?text=${mensagemCodificada}`;
    window.open(urlWhatsApp, '_blank');
}

async function marcarComoContatado(idOrcamento) {
    try {
        const response = await erpFetch(`/orcamentos/${idOrcamento}/contatar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('Falha ao atualizar status de contato no backend.');
            return;
        }

        // Recarrega a tabela para refletir as alterações no filtro
        carregarOrcamentos();
    } catch (error) {
        console.error('Erro de rede ao marcar orçamento como contatado:', error);
    }
}
