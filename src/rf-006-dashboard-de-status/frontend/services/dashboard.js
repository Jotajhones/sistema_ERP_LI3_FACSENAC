import { erpFetch } from "../../../../rf-002-catalogo-produtos/frontend/scripts/authInterceptor.js";

const elementos = {
    dataInicio: document.getElementById('dataInicio'),
    dataFim: document.getElementById('dataFim'),
    btnAplicarFiltro: document.getElementById('btnAplicarFiltro'),

    dashboardContent: document.getElementById('dashboardContent'),
    dashboardLoading: document.getElementById('dashboardLoading'),
    dashboardError: document.getElementById('dashboardError'),
    dashboardErrorText: document.getElementById('dashboardErrorText'),
    dashboardForbidden: document.getElementById('dashboardForbidden'),
    dashboardEmpty: document.getElementById('dashboardEmpty'),

    taxaConversao: document.getElementById('taxaConversao'),
    totalOrcamentos: document.getElementById('totalOrcamentos'),
    convertidos: document.getElementById('convertidos'),
    pendentes: document.getElementById('pendentes'),
    valorTotalOrcado: document.getElementById('valorTotalOrcado'),
    valorTotalConvertido: document.getElementById('valorTotalConvertido')
};

function formatarMoeda(valor) {
    const numero = Number(valor);

    if (!Number.isFinite(numero)) {
        return 'R$ 0,00';
    }

    return numero.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

function formatarNumero(valor) {
    const numero = Number(valor);

    if (!Number.isFinite(numero)) {
        return '0';
    }

    return numero.toLocaleString('pt-BR');
}

function formatarPorcentagem(valor) {
    const numero = Number(valor);

    if (!Number.isFinite(numero)) {
        return '0,00%';
    }

    return numero.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + '%';
}

function esconderTodosOsEstados() {
    elementos.dashboardLoading.hidden = true;
    elementos.dashboardError.hidden = true;
    elementos.dashboardForbidden.hidden = true;
    elementos.dashboardEmpty.hidden = true;
}

function mostrarLoading() {
    esconderTodosOsEstados();
    elementos.dashboardContent.hidden = true;
    elementos.dashboardLoading.hidden = false;
}

function mostrarErro(mensagem) {
    esconderTodosOsEstados();
    elementos.dashboardContent.hidden = true;
    elementos.dashboardErrorText.textContent = mensagem;
    elementos.dashboardError.hidden = false;
}

function mostrarForbidden() {
    esconderTodosOsEstados();
    elementos.dashboardContent.hidden = true;
    elementos.dashboardForbidden.hidden = false;
}

function mostrarVazio() {
    esconderTodosOsEstados();
    elementos.dashboardContent.hidden = true;
    elementos.dashboardEmpty.hidden = false;
}

function mostrarConteudo() {
    esconderTodosOsEstados();
    elementos.dashboardContent.hidden = false;
}

function limparCampos() {
    elementos.taxaConversao.textContent = '0,00%';
    elementos.totalOrcamentos.textContent = '0';
    elementos.convertidos.textContent = '0';
    elementos.pendentes.textContent = '0';
    elementos.valorTotalOrcado.textContent = 'R$ 0,00';
    elementos.valorTotalConvertido.textContent = 'R$ 0,00';
}

function renderizarDashboard(dados) {
    elementos.taxaConversao.textContent =
        formatarPorcentagem(dados.taxa_conversao);

    elementos.totalOrcamentos.textContent =
        formatarNumero(dados.total_orcamentos);

    elementos.convertidos.textContent =
        formatarNumero(dados.convertidos);

    elementos.pendentes.textContent =
        formatarNumero(dados.pendentes);

    elementos.valorTotalOrcado.textContent =
        formatarMoeda(dados.valor_total_orcado);

    elementos.valorTotalConvertido.textContent =
        formatarMoeda(dados.valor_total_convertido);
}

function montarEndpoint() {
    const parametros = new URLSearchParams();

    const dataInicio = elementos.dataInicio.value;
    const dataFim = elementos.dataFim.value;

    if (dataInicio) {
        parametros.append('data_inicio', dataInicio);
    }

    if (dataFim) {
        parametros.append('data_fim', dataFim);
    }

    const queryString = parametros.toString();

    if (!queryString) {
        return '/dashboard/conversao-orcamentos';
    }

    return `/dashboard/conversao-orcamentos?${queryString}`;
}

function validarPeriodo() {
    const dataInicio = elementos.dataInicio.value;
    const dataFim = elementos.dataFim.value;

    if (!dataInicio || !dataFim) {
        return true;
    }

    if (dataInicio > dataFim) {
        mostrarErro('A data de início não pode ser posterior à data de fim.');
        return false;
    }

    return true;
}

async function carregarDashboard() {
    if (!validarPeriodo()) {
        return;
    }

    mostrarLoading();
    elementos.btnAplicarFiltro.disabled = true;

    try {
        const endpoint = montarEndpoint();
        const resposta = await erpFetch(endpoint);

        if (!resposta) {
            throw new Error('Não foi possível obter uma resposta da API.');
        }

        if (resposta.status === 403) {
            mostrarForbidden();
            return;
        }

        if (!resposta.ok) {
            throw new Error(
                'Não foi possível carregar os dados do dashboard.'
            );
        }

        let dados = await resposta.json();

        if (dados && dados.data) {
            dados = dados.data;
        }

        if (typeof dados === 'string') {
            try {
                dados = JSON.parse(dados);
            } catch (erro) {
                throw new Error(
                    'A API retornou dados em um formato inválido.'
                );
            }
        }

        if (!dados || typeof dados !== 'object') {
            throw new Error(
                'A API retornou dados em um formato inválido.'
            );
        }

        const totalOrcamentos = Number(dados.total_orcamentos);

        if (!Number.isFinite(totalOrcamentos) || totalOrcamentos === 0) {
            limparCampos();
            mostrarVazio();
            return;
        }

        renderizarDashboard(dados);
        mostrarConteudo();

    } catch (erro) {
        console.error('Erro ao carregar dashboard:', erro);

        mostrarErro(
            'Não foi possível carregar os dados. Tente novamente.'
        );

    } finally {
        elementos.btnAplicarFiltro.disabled = false;
    }
}

export function initDashboard() {
    elementos.btnAplicarFiltro.addEventListener(
        'click',
        carregarDashboard
    );

    elementos.dataInicio.addEventListener('change', () => {
        elementos.dashboardError.hidden = true;
    });

    elementos.dataFim.addEventListener('change', () => {
        elementos.dashboardError.hidden = true;
    });

    carregarDashboard();
}