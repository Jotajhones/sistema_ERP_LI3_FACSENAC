import { erpFetch } from "../../../rf-002-catalogo-produtos/frontend/scripts/authInterceptor.js";
import { getCarrinho, setCarrinho, adicionarAoCarrinho, renderizarCarrinho, formatarMoeda } from "./carrinhoService.js";
import { buscarClienteAPI } from "./clienteService.js";
import { initModalFaturamento } from "./faturamentoService.js";

let buscaTimeout = null;
let orcamentoAtualId = null; 

export function initOrcamento() {
    configurarEventosBasicos();
    initModalFaturamento(() => orcamentoAtualId);
    
    const urlParams = new URLSearchParams(window.location.search);
    const idParam = urlParams.get('id');
    if (idParam) carregarOrcamentoExistente(idParam);
}

function configurarEventosBasicos() {
    const btnBuscar = document.getElementById('btnBuscarCpf');
    const inputCpf = document.getElementById('cpfCliente');
    const form = document.getElementById('formOrcamento');
    const inputBuscaProduto = document.getElementById('inputBuscaProduto');

    if (btnBuscar) btnBuscar.addEventListener('click', () => buscarClienteAPI(inputCpf.value));

    if (inputCpf) {
        inputCpf.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '');
            e.target.value = val;
            if (val.length === 11) buscarClienteAPI(val);
        });
    }

    if (inputBuscaProduto) {
        inputBuscaProduto.addEventListener('input', (e) => {
            clearTimeout(buscaTimeout);
            const termo = e.target.value.trim();
            if (termo.length < 3) {
                document.getElementById('dropdownResultados').style.display = 'none';
                return;
            }
            buscaTimeout = setTimeout(() => pesquisarProdutosAjax(termo), 400);
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.input-group')) {
                document.getElementById('dropdownResultados').style.display = 'none';
            }
        });
    }

    if (form) form.addEventListener('submit', salvarOrcamentoAjax);
}

async function pesquisarProdutosAjax(termo) {
    const dropdown = document.getElementById('dropdownResultados');
    try {
        const response = await erpFetch(`/produtos/busca?termo=${encodeURIComponent(termo)}`);
        if (!response.ok) throw new Error('Erro na busca');
        
        const produtos = await response.json();
        dropdown.innerHTML = '';
        
        if (produtos.length === 0) {
            dropdown.innerHTML = '<div class="search-item" style="color: var(--color-text-muted);">Nenhum produto encontrado.</div>';
        } else {
            produtos.forEach(prod => {
                const item = document.createElement('div');
                item.className = 'search-item';
                item.innerHTML = `
                    <div class="search-item-info">
                        <span class="search-item-title">${prod.nome}</span>
                        <span class="search-item-sku">SKU: ${prod.sku} | Estoque: ${prod.quantidade_estoque || 0} ${prod.unidade_medida || 'UN'}</span>
                    </div>
                    <span class="search-item-price">${formatarMoeda(prod.valor_venda)}</span>
                `;
                item.addEventListener('click', () => adicionarAoCarrinho(prod));
                dropdown.appendChild(item);
            });
        }
        dropdown.style.display = 'block';
    } catch (error) {
        dropdown.innerHTML = '<div class="search-item" style="color: var(--color-error);">Erro ao buscar produtos.</div>';
        dropdown.style.display = 'block';
    }
}

async function salvarOrcamentoAjax(e) {
    e.preventDefault();
    const carrinhoAtual = getCarrinho();
    
    if (carrinhoAtual.length === 0) {
        alert("Adicione ao menos um produto para gerar o orçamento.");
        return;
    }

    const inputCpf = document.getElementById('cpfCliente');
    const inputNome = document.getElementById('nomeCliente');
    const inputId = document.getElementById('clienteId');
    const btnSalvar = document.getElementById('btnSalvarOrcamento');
    
    let clienteId = inputId.value;
    btnSalvar.disabled = true;
    btnSalvar.textContent = "Processando...";

    try {
        if (inputCpf.value && inputCpf.value.length === 11 && !clienteId) {
            if (!inputNome.value.trim()) {
                alert("O nome do cliente é obrigatório para um novo cadastro.");
                btnSalvar.disabled = false;
                btnSalvar.textContent = "Salvar Orçamento";
                return;
            }
            const resPessoa = await erpFetch('/pessoas', {
                method: 'POST',
                body: JSON.stringify({ cpf: inputCpf.value, nome: inputNome.value.trim() })
            });
            
            if (resPessoa.ok) {
                const novaPessoa = await resPessoa.json();
                clienteId = novaPessoa.id;
                inputId.value = clienteId; 
            } else {
                const err = await resPessoa.json();
                throw new Error(`Erro ao cadastrar cliente: ${err.detail || 'Dados inválidos'}`);
            }
        }

        const orcamentoPayload = {
            cliente_id: clienteId || null,
            nome_cliente: inputNome.value.trim() || "Consumidor Final",
            cpf_cliente: inputCpf.value || null,
            itens: carrinhoAtual.map(item => ({
                produto_id: item.id,
                nome: item.nome,
                quantidade: item.quantidade,
                preco_unitario: item.valor_venda 
            }))
        };

        const resOrcamento = await erpFetch('/orcamentos', { 
            method: 'POST', 
            body: JSON.stringify(orcamentoPayload) 
        });
        
        if (!resOrcamento.ok) {
            const err = await resOrcamento.json();
            let msgErro = "Falha ao salvar orçamento.";
            if (Array.isArray(err.detail)) {
                msgErro = err.detail.map(e => `Erro no campo '${e.loc[e.loc.length - 1]}': ${e.msg}`).join('\n');
            } else if (err.detail) {
                msgErro = err.detail;
            }
            throw new Error(msgErro);
        }
        
        const orcamentoSalvo = await resOrcamento.json();
        orcamentoAtualId = orcamentoSalvo.id;

        alert(`Orçamento #${orcamentoAtualId.split('-')[0]} gerado com sucesso!`);
        travarTelaParaFaturamento();

    } catch (error) {
        alert(`❌ ERRO:\n\n${error.message}`);
        btnSalvar.disabled = false;
        btnSalvar.textContent = "Salvar Orçamento";
    }
}

async function carregarOrcamentoExistente(id) {
    try {
        const res = await erpFetch(`/orcamentos/${id}`);
        if (!res.ok) throw new Error("Orçamento não encontrado.");
        
        const orcamento = await res.json();
        orcamentoAtualId = orcamento.id;

        if (orcamento.cliente_id) {
            document.getElementById('clienteId').value = orcamento.cliente_id;
        }

        if (orcamento.cpf_cliente) {
            document.getElementById('cpfCliente').value = orcamento.cpf_cliente;
            
            if (!document.getElementById('clienteId').value) {
                try {
                    const cleanCpf = orcamento.cpf_cliente.replace(/\D/g, '');
                    const resCli = await erpFetch(`/pessoas/cpf/${cleanCpf}`);
                    if (resCli.ok) {
                        const cliente = await resCli.json();
                        document.getElementById('clienteId').value = cliente.id;
                    }
                } catch (e) {
                    console.warn("Não foi possível sincronizar o cliente pelo CPF", e);
                }
            }
        }
        
        document.getElementById('nomeCliente').value = orcamento.nome_cliente || "Consumidor Final";
        
        setCarrinho(orcamento.itens.map(item => ({
            id: item.produto_id,
            nome: item.nome || "Produto Cadastrado", 
            quantidade: item.quantidade,
            valor_venda: item.preco_unitario
        })));
        renderizarCarrinho();

        travarTelaParaFaturamento(orcamento.status);

    } catch (error) {
        alert("Não foi possível carregar o orçamento. Ele pode não existir mais.");
        window.location.href = window.location.pathname; 
    }
}

function travarTelaParaFaturamento(status = 'PENDENTE') {
    document.getElementById('containerSalvar').style.display = 'none';
    document.getElementById('controlesFaturamento').style.display = 'flex';
    
    if (status === 'CONVERTIDO') {
        document.getElementById('orcamentoIdDisplay').textContent = `Orçamento #${orcamentoAtualId.split('-')[0]} (FATURADO)`;
        document.getElementById('orcamentoIdDisplay').style.color = 'var(--color-success)';
        document.getElementById('btnFaturarOS').style.display = 'none';
    } else {
        document.getElementById('orcamentoIdDisplay').textContent = `Orçamento #${orcamentoAtualId.split('-')[0]}`;
    }
    
    document.querySelectorAll('.input-qtd, .btn-remove, #inputBuscaProduto, #cpfCliente').forEach(el => el.disabled = true);
}