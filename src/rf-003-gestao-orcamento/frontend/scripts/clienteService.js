import { erpFetch } from "../../../rf-002-catalogo-produtos/frontend/scripts/authInterceptor.js";

export async function buscarClienteAPI(cpf) {
    const inputNome = document.getElementById('nomeCliente');
    const inputId = document.getElementById('clienteId');
    const feedback = document.getElementById('cpfFeedback');
    
    if (!cpf) {
        resetarCamposCliente(inputNome, inputId, feedback);
        return;
    }

    if (cpf.length !== 11) {
        exibirFeedback(feedback, 'CPF Inválido. Deve conter 11 dígitos.', 'var(--color-error)');
        inputNome.disabled = true;
        return;
    }

    exibirFeedback(feedback, 'Buscando cliente...', 'var(--color-text-muted)');

    try {
        const response = await erpFetch(`/pessoas/cpf/${cpf}`);
        
        if (response.status === 404) {
            exibirFeedback(feedback, 'Cliente novo detectado. Preencha o nome.', 'var(--color-primary)');
            prepararParaNovoCliente(inputNome, inputId);
        } else if (response.ok) {
            const cliente = await response.json();
            exibirFeedback(feedback, 'Cliente encontrado!', 'var(--color-success)');
            preencherClienteExistente(inputNome, inputId, cliente);
        } else {
            exibirFeedback(feedback, 'Erro ao consultar CPF.', 'var(--color-error)');
        }
    } catch (error) {
        exibirFeedback(feedback, 'Falha de comunicação com o servidor.', 'var(--color-error)');
    }
}

function resetarCamposCliente(inputNome, inputId, feedback) {
    inputNome.value = '';
    inputNome.disabled = true;
    inputNome.placeholder = "Informe o CPF ou deixe em branco para orçamento anônimo";
    inputId.value = '';
    feedback.textContent = '';
}

function exibirFeedback(elemento, mensagem, cor) {
    elemento.textContent = mensagem;
    elemento.style.color = cor;
}

function prepararParaNovoCliente(inputNome, inputId) {
    inputNome.value = '';
    inputNome.disabled = false;
    inputNome.placeholder = "Digite o nome do cliente";
    inputNome.focus();
    inputId.value = '';
}

function preencherClienteExistente(inputNome, inputId, cliente) {
    inputNome.value = cliente.nome;
    inputNome.disabled = true;
    inputId.value = cliente.id;
}