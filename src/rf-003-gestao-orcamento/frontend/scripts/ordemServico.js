import { erpFetch } from "../../../rf-002-catalogo-produtos/frontend/scripts/authInterceptor.js";
let carrinho = [];
let buscaTimeout = null;

export function initOrcamento() {
    const btnBuscar = document.getElementById('btnBuscarCpf');
    const inputCpf = document.getElementById('cpfCliente');
    const form = document.getElementById('formOrcamento');
    const inputBuscaProduto = document.getElementById('inputBuscaProduto');

    if (btnBuscar) btnBuscar.addEventListener('click', buscarCliente);

    if (inputCpf) {
        inputCpf.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '');
            e.target.value = val;
            if (val.length === 11) buscarCliente();
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

            buscaTimeout = setTimeout(() => pesquisarProdutos(termo), 400);
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.input-group')) {
                document.getElementById('dropdownResultados').style.display = 'none';
            }
        });
    }

    if (form) form.addEventListener('submit', salvarOrcamento);
}

async function pesquisarProdutos(termo) {
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

function adicionarAoCarrinho(produto) {
    const existente = carrinho.find(item => item.id === produto.id);
    
    if (existente) {
        existente.quantidade += 1;
    } else {
        carrinho.push({
            id: produto.id,
            nome: produto.nome,
            valor_venda: produto.valor_venda,
            quantidade: 1
        });
    }
    
    document.getElementById('inputBuscaProduto').value = '';
    document.getElementById('dropdownResultados').style.display = 'none';
    renderizarCarrinho();
}

function renderizarCarrinho() {
    const tbody = document.getElementById('carrinhoBody');
    const totalEl = document.getElementById('totalOrcamento');
    let total = 0;

    tbody.innerHTML = '';

    if (carrinho.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="padding: 2rem; color: var(--color-text-muted);">Nenhum produto adicionado.</td></tr>';
        totalEl.textContent = 'R$ 0,00';
        return;
    }

    carrinho.forEach((item, index) => {
        const subtotal = item.quantidade * item.valor_venda;
        total += subtotal;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.nome}</td>
            <td class="text-center">
                <input type="number" min="1" class="input-qtd" value="${item.quantidade}" data-index="${index}">
            </td>
            <td class="text-right">${formatarMoeda(item.valor_venda)}</td>
            <td class="text-right" style="font-weight: 500;">${formatarMoeda(subtotal)}</td>
            <td class="text-center">
                <button type="button" class="btn-remove" data-index="${index}" title="Remover">🗑️</button>
            </td>
        `;
        tbody.appendChild(row);
    });

    totalEl.textContent = formatarMoeda(total);

    document.querySelectorAll('.input-qtd').forEach(input => {
        input.addEventListener('change', (e) => {
            const idx = e.target.dataset.index;
            let val = parseInt(e.target.value);
            if (val < 1 || isNaN(val)) val = 1;
            carrinho[idx].quantidade = val;
            renderizarCarrinho();
        });
    });

    document.querySelectorAll('.btn-remove').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = e.currentTarget.dataset.index;
            carrinho.splice(idx, 1);
            renderizarCarrinho();
        });
    });
}

function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
}


async function buscarCliente() {
    const inputCpf = document.getElementById('cpfCliente');
    const inputNome = document.getElementById('nomeCliente');
    const inputId = document.getElementById('clienteId');
    const feedback = document.getElementById('cpfFeedback');
    
    const cpf = inputCpf.value;

    if (!cpf) {
        inputNome.value = '';
        inputNome.disabled = true;
        inputNome.placeholder = "Informe o CPF ou deixe em branco para orçamento anônimo";
        inputId.value = '';
        feedback.textContent = '';
        return;
    }

    if (cpf.length !== 11) {
        feedback.textContent = 'CPF Inválido. Deve conter 11 dígitos numéricos.';
        feedback.style.color = 'var(--color-error)';
        inputNome.disabled = true;
        return;
    }

    feedback.textContent = 'Buscando cliente...';
    feedback.style.color = 'var(--color-text-muted)';

    try {
        const response = await erpFetch(`/pessoas/${cpf}`);
        
        if (response.status === 404) {
            feedback.textContent = 'Cliente novo detectado. Preencha o nome.';
            feedback.style.color = 'var(--color-primary)';
            inputNome.value = '';
            inputNome.disabled = false;
            inputNome.placeholder = "Digite o nome do cliente";
            inputNome.focus();
            inputId.value = '';
        } else if (response.ok) {
            const cliente = await response.json();
            feedback.textContent = 'Cliente encontrado!';
            feedback.style.color = 'var(--color-success)';
            inputNome.value = cliente.nome;
            inputNome.disabled = true;
            inputId.value = cliente.id;
        } else {
            feedback.textContent = 'Erro ao consultar CPF.';
            feedback.style.color = 'var(--color-error)';
        }
    } catch (error) {
        feedback.textContent = 'Falha de comunicação com o servidor.';
        feedback.style.color = 'var(--color-error)';
    }
}

async function salvarOrcamento(e) {
    e.preventDefault();
    
    if (carrinho.length === 0) {
        alert("Adicione ao menos um produto para gerar o orçamento.");
        return;
    }

    const inputCpf = document.getElementById('cpfCliente');
    const inputNome = document.getElementById('nomeCliente');
    const inputId = document.getElementById('clienteId');
    const btnSalvar = document.getElementById('btnSalvarOrcamento');
    
    const cpf = inputCpf.value;
    const nome = inputNome.value.trim();
    let clienteId = inputId.value;

    btnSalvar.disabled = true;
    btnSalvar.textContent = "Processando...";

    try {
        if (cpf && cpf.length === 11 && !clienteId) {
            if (!nome) {
                alert("O nome do cliente é obrigatório para um novo cadastro.");
                btnSalvar.disabled = false;
                btnSalvar.textContent = "Salvar Orçamento";
                return;
            }
            
            const resPessoa = await erpFetch('/pessoas', {
                method: 'POST',
                body: JSON.stringify({ cpf, nome })
            });
            
            if (resPessoa.ok) {
                const novaPessoa = await resPessoa.json();
                clienteId = novaPessoa.id;
                inputId.value = clienteId; 
            } else {
                const err = await resPessoa.json();
                alert(`Erro ao cadastrar cliente silenciosamente: ${err.detail || 'Dados inválidos'}`);
                btnSalvar.disabled = false;
                btnSalvar.textContent = "Salvar Orçamento";
                return;
            }
        }

        const orcamentoPayload = {
            cliente_id: clienteId || null,
            itens: carrinho.map(item => ({
                produto_id: item.id,
                quantidade: item.quantidade
            }))
        };

        // Simulação do envio (será ativado quando a API de OS for desenvolvida)
        // const resOrcamento = await erpFetch('/orcamentos', { method: 'POST', body: JSON.stringify(orcamentoPayload) });
        
        console.log("Payload pronto para envio:", orcamentoPayload);
        alert(`Orçamento gerado com sucesso! ${clienteId ? '(Vinculado)' : '(Anônimo)'}`);
        
        // Reset completo
        e.target.reset();
        inputId.value = '';
        inputNome.disabled = true;
        inputNome.placeholder = "Informe o CPF ou deixe em branco para orçamento anônimo";
        document.getElementById('cpfFeedback').textContent = '';
        carrinho = [];
        renderizarCarrinho();

    } catch (error) {
        alert("Falha de rede ao tentar processar o orçamento.");
    } finally {
        btnSalvar.disabled = false;
        btnSalvar.textContent = "Salvar Orçamento";
    }
}