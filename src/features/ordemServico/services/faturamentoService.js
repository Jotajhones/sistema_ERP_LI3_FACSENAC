import { erpFetch } from "../../../scripts/authInterceptor.js";
import { aplicarControleDeAcesso } from "../../../scripts/rbac.js";

export function initModalFaturamento(getOrcamentoAtualId) {
    const btnFaturar = document.getElementById('btnFaturarOS');
    const modal = document.getElementById('modalFaturamento');
    const btnCancelar = document.getElementById('btnCancelarFaturamento');
    const btnConfirmar = document.getElementById('btnConfirmarFaturamento');
    const btnNovo = document.getElementById('btnNovoOrcamento');
    const inputCep = document.getElementById('cepEntrega');

    if (btnFaturar) {
        btnFaturar.addEventListener('click', () => {
            prepararModalEndereco();
            modal.style.display = 'flex';
        });
    }
    
    if (btnCancelar) btnCancelar.addEventListener('click', () => modal.style.display = 'none');
    if (btnNovo) btnNovo.addEventListener('click', () => window.location.href = window.location.pathname);
    
    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', () => faturarOS(getOrcamentoAtualId(), modal, btnConfirmar));
    }

    if (inputCep) {
        inputCep.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '');
            
            if (val.length > 5) {
                e.target.value = val.replace(/^(\d{5})(\d)/, '$1-$2');
            } else {
                e.target.value = val;
            }

            if (val.length === 8) buscarCepViaAPI(val);
        });
    }
}

async function buscarCepViaAPI(cepLimpo) {
    try {
        const res = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`);
        const data = await res.json();
        
        if (!data.erro) {
            document.getElementById('logradouroEntrega').value = data.logradouro || '';
            document.getElementById('bairroEntrega').value = data.bairro || '';
            document.getElementById('cidadeEntrega').value = data.localidade || '';
            document.getElementById('ufEntrega').value = data.uf || '';
            
            document.getElementById('numeroEntrega').focus();
        }
    } catch (e) {
        console.error("Erro ao buscar ViaCEP", e);
    }
}

async function prepararModalEndereco() {
    let clienteId = document.getElementById('clienteId').value;
    const cpfInput = document.getElementById('cpfCliente').value.replace(/\D/g, '');
    const fieldset = document.getElementById('formEnderecoEntrega');
    const aviso = document.getElementById('avisoEndereco');

    document.querySelectorAll('#formEnderecoEntrega input').forEach(inp => inp.value = '');

    if (!clienteId && cpfInput.length === 11) {
        try {
            const resCli = await erpFetch(`/pessoas/cpf/${cpfInput}`);
            if (resCli.ok) {
                const cliente = await resCli.json();
                clienteId = cliente.id;
                document.getElementById('clienteId').value = cliente.id;
            }
        } catch (e) {
            console.warn("Falha ao sincronizar cliente via CPF no modal", e);
        }
    }

    if (!clienteId) {
        fieldset.disabled = true;
        aviso.style.display = 'block';
        aplicarControleDeAcesso();
        return;
    }

    fieldset.disabled = false;
    aviso.style.display = 'none';

    try {
        const res = await erpFetch(`/pessoas/${clienteId}`);
        if (res.ok) {
            const cliente = await res.json();
            if (cliente.enderecos && cliente.enderecos.length > 0) {
                const end = cliente.enderecos[0];
                document.getElementById('cepEntrega').value = end.cep || '';
                document.getElementById('logradouroEntrega').value = end.logradouro || '';
                document.getElementById('numeroEntrega').value = end.numero || '';
                document.getElementById('bairroEntrega').value = end.bairro || '';
                document.getElementById('cidadeEntrega').value = end.cidade || '';
                document.getElementById('ufEntrega').value = end.estado || '';
            }
        }
    } catch (e) {
        console.log("Falha ao buscar endereço do cliente", e);
    }

    aplicarControleDeAcesso();
}

async function faturarOS(orcamentoId, modal, btnConfirmar) {
    if (!orcamentoId) {
        alert("Erro interno: Orçamento ID não encontrado.");
        return;
    }

    const displayId = document.getElementById('orcamentoIdDisplay').textContent;

    if (displayId.includes("FATURADO")) {
        alert("Ação Bloqueada: Este orçamento já foi faturado e não pode ser convertido novamente.");
        modal.style.display = 'none';
        return; 
    }

    const clienteId = document.getElementById('clienteId').value;
    const cep = document.getElementById('cepEntrega').value.replace(/\D/g, '');
    const logradouro = document.getElementById('logradouroEntrega').value.trim();

    btnConfirmar.disabled = true;
    btnConfirmar.textContent = "Processando OS...";

    try {

        if (clienteId && (cep || logradouro)) {
            const payloadEndereco = {
                endereco: {
                    cep: cep || null,
                    logradouro: logradouro || null,
                    numero: document.getElementById('numeroEntrega').value.trim() || null,
                    bairro: document.getElementById('bairroEntrega').value.trim() || null,
                    cidade: document.getElementById('cidadeEntrega').value.trim() || null,
                    estado: document.getElementById('ufEntrega').value.trim().toUpperCase() || null
                }
            };

            const resEnd = await erpFetch(`/pessoas/${clienteId}`, {
                method: 'PUT',
                body: JSON.stringify(payloadEndereco)
            });

            if (!resEnd.ok) {
                const errEnd = await resEnd.json();
                console.warn("Aviso ao salvar endereço:", errEnd);
                if (resEnd.status === 403) alert("Bloqueio de Segurança: " + errEnd.detail);
            }
        }

        const payloadOS = {
            tipo_pagamento: document.getElementById('tipoPagamento').value,
            desconto: parseFloat(document.getElementById('valorDesconto').value) || 0.0
        };

        const resOS = await erpFetch(`/ordens-servico/converter/${orcamentoId}`, {
            method: 'POST',
            body: JSON.stringify(payloadOS)
        });

        if (resOS.ok) {
            alert("SUCESSO! Ordem de Serviço gerada e estoque atualizado.");
            window.location.href = window.location.pathname; 
        } else if (resOS.status === 409) {
            const err = await resOS.json();
            alert(`❌ VENDA BLOQUEADA: ${err.detail}`);
            modal.style.display = 'none';
        } else {
            const err = await resOS.json();
            alert(`Erro ao gerar OS: ${err.detail || "Erro inesperado."}`);
        }
    } catch (err) {
        alert("Falha na comunicação com o servidor.");
    } finally {
        btnConfirmar.disabled = false;
        btnConfirmar.textContent = "Confirmar Venda";
    }
}